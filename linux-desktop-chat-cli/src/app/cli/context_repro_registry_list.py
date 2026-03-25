"""
List repro registry entries from a derived registry JSON file.

Deterministic ordering (failure_id). sort_keys=True. No UI.
"""

import json
import sys
from pathlib import Path

from app.context.replay.canonicalize import canonicalize
from app.context.replay.repro_registry_query import query_all
from app.context.replay.repro_registry_store import load_repro_registry


def run_registry_list(registry_path: str | Path) -> str:
    """Load registry and return JSON with sorted entries."""
    entries = query_all(load_repro_registry(registry_path))
    rows = [e.to_dict() for e in entries]
    payload = canonicalize({"entries": rows, "entry_count": len(rows)})
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2)


def main() -> int:
    """Usage: python -m app.cli.context_repro_registry_list <registry.json>"""
    if len(sys.argv) != 2:
        sys.stderr.write(
            "Usage: python -m app.cli.context_repro_registry_list <registry.json>\n"
        )
        return 1
    path = Path(sys.argv[1])
    if not path.exists():
        sys.stderr.write(f"Registry file not found: {path}\n")
        return 1
    try:
        print(run_registry_list(path))
        return 0
    except (json.JSONDecodeError, OSError, ValueError) as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

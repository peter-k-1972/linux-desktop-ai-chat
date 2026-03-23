"""
Rebuild repro registry JSON from a repro case directory (derived index only).

Deterministic output. sort_keys=True. No UI.
"""

import json
import sys
from pathlib import Path

from app.context.replay.canonicalize import canonicalize
from app.context.replay.repro_failure_indexer import rebuild_repro_registry


def run_registry_rebuild(repro_root: str | Path, registry_path: str | Path) -> str:
    """
    Scan repro_root and write registry_path. Return summary JSON string.
    """
    entries = rebuild_repro_registry(repro_root, registry_path)
    payload = canonicalize({
        "entry_count": len(entries),
        "registry_path": str(Path(registry_path).resolve()),
        "repro_root": str(Path(repro_root).resolve()),
    })
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2)


def main() -> int:
    """Usage: python -m app.cli.context_repro_registry_rebuild <repro_root> <registry.json>"""
    if len(sys.argv) != 3:
        sys.stderr.write(
            "Usage: python -m app.cli.context_repro_registry_rebuild "
            "<repro_root> <registry.json>\n"
        )
        return 1
    try:
        print(run_registry_rebuild(sys.argv[1], sys.argv[2]))
        return 0
    except (OSError, NotADirectoryError, ValueError) as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

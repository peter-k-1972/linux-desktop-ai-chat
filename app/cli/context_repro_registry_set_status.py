"""
Set repro registry status on the source repro case JSON (not only the index).

Optional fourth argument rebuilds the derived registry file after the patch.

Deterministic file writes. No UI.
"""

import json
import sys
from pathlib import Path

from app.context.replay.canonicalize import canonicalize
from app.context.replay.repro_registry_status_service import update_status_by_failure_id


def run_registry_set_status(
    repro_root: str | Path,
    failure_id: str,
    status: str,
    registry_path: str | Path | None = None,
) -> str:
    """
    Patch registry.status on the repro artifact; optionally rebuild index.
    Return JSON describing the updated row.
    """
    entry = update_status_by_failure_id(
        repro_root,
        failure_id,
        status,
        registry_path=registry_path,
    )
    payload = canonicalize(
        {
            "entry": entry.to_dict(),
            "failure_id": entry.failure_id,
            "registry_rebuilt": registry_path is not None,
            "repro_root": str(Path(repro_root).resolve()),
            "status": entry.status,
        }
    )
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, indent=2)


def main() -> int:
    """
    Usage:
      python -m app.cli.context_repro_registry_set_status \\
          <repro_root> <failure_id> <status> [<registry.json>]
    """
    if len(sys.argv) not in (4, 5):
        sys.stderr.write(
            "Usage: python -m app.cli.context_repro_registry_set_status "
            "<repro_root> <failure_id> <status> [<registry.json>]\n"
        )
        return 1
    repro_root = sys.argv[1]
    failure_id = sys.argv[2]
    status = sys.argv[3]
    registry_path: str | Path | None = sys.argv[4] if len(sys.argv) == 5 else None
    try:
        print(run_registry_set_status(repro_root, failure_id, status, registry_path))
        return 0
    except FileNotFoundError as e:
        sys.stderr.write(f"{e}\n")
        return 1
    except (json.JSONDecodeError, OSError, ValueError) as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

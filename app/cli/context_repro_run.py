"""
Context repro run CLI – run one repro case JSON, print structured JSON result.

Deterministic output only. sort_keys=True. No UI dependencies.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict

from app.context.replay.canonicalize import canonicalize
from app.context.replay.repro_case_runner import (
    ReproRunResult,
    run_repro_case_from_file,
)


def _result_to_dict(result: ReproRunResult, *, file_path: str = "") -> Dict[str, Any]:
    """Convert ReproRunResult to JSON-serializable dict. Deterministic."""
    content_diff_dict: Any = None
    if result.content_diff is not None:
        content_diff_dict = dict(result.content_diff)
    out: Dict[str, Any] = {
        "passed": result.passed,
        "content_identical": result.content_identical,
        "signature_match": result.signature_match,
        "drift_types": list(result.drift_types),
        "expected_signature": result.expected_signature,
        "actual_signature": result.actual_signature,
    }
    if file_path:
        out["file"] = file_path
    if content_diff_dict is not None:
        out["content_diff"] = content_diff_dict
    return out


def run_repro(file_path: str | Path) -> str:
    """
    Run one repro case JSON file. Return structured JSON result.
    Deterministic. sort_keys=True.
    """
    logging.disable(logging.CRITICAL)
    try:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Repro case file not found: {path}")
        result = run_repro_case_from_file(path)
        out = _result_to_dict(result, file_path=str(path.resolve()))
        out = canonicalize(out)
        return json.dumps(out, sort_keys=True, ensure_ascii=False, indent=2)
    finally:
        logging.disable(logging.NOTSET)


def main() -> int:
    """CLI entry point. Usage: python -m app.cli.context_repro_run <repro_case.json>"""
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python -m app.cli.context_repro_run <repro_case.json>\n")
        return 1
    try:
        output = run_repro(sys.argv[1])
        print(output)
        return 0
    except FileNotFoundError as e:
        sys.stderr.write(f"{e}\n")
        return 1
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as e:
        sys.stderr.write(f"Error: {e}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())

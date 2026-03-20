"""
Context repro batch CLI – run all repro case JSON files in a directory.

Sorted file processing. Deterministic output only. sort_keys=True. No UI dependencies.
"""

import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List

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


def run_repro_batch(dir_path: str | Path) -> str:
    """
    Run all repro case JSON files in directory. Sorted file order.
    Return structured JSON result list. Deterministic. sort_keys=True.
    """
    logging.disable(logging.CRITICAL)
    try:
        path = Path(dir_path)
        if not path.is_dir():
            raise FileNotFoundError(f"Directory not found: {path}")
        json_files = sorted(path.glob("*.json"))
        results: List[Dict[str, Any]] = []
        for f in json_files:
            try:
                result = run_repro_case_from_file(f)
                out = _result_to_dict(result, file_path=str(f.resolve()))
                results.append(out)
            except Exception as e:
                results.append({
                    "file": str(f.resolve()),
                    "passed": False,
                    "error": str(e),
                    "content_identical": False,
                    "signature_match": False,
                    "drift_types": [],
                    "expected_signature": "",
                    "actual_signature": "",
                })
        output = {"results": results, "total": len(results), "passed": sum(1 for r in results if r.get("passed", False))}
        output = canonicalize(output)
        return json.dumps(output, sort_keys=True, ensure_ascii=False, indent=2)
    finally:
        logging.disable(logging.NOTSET)


def main() -> int:
    """CLI entry point. Usage: python -m app.cli.context_repro_batch <directory>"""
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: python -m app.cli.context_repro_batch <directory>\n")
        return 1
    try:
        output = run_repro_batch(sys.argv[1])
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

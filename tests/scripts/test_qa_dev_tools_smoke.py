from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DOC = ROOT / "qa" / "dev_tools.md"
SUGGEST_SCRIPT = ROOT / "scripts" / "dev" / "suggest_test_scope.py"
CLASSIFY_SCRIPT = ROOT / "scripts" / "dev" / "classify_pytest_failures.py"


def run_help(script_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script_path), "--help"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )


def test_qa_dev_tools_doc_examples_and_help_flags_stay_in_sync():
    doc_text = DOC.read_text(encoding="utf-8")

    suggest_help = run_help(SUGGEST_SCRIPT)
    assert suggest_help.returncode == 0, suggest_help.stderr
    for flag in (
        "--format",
        "--include-stats",
        "--include-match-details",
        "--include-file-targets",
        "--include-match-counts",
    ):
        assert flag in suggest_help.stdout
        assert flag in doc_text

    classify_help = run_help(CLASSIFY_SCRIPT)
    assert classify_help.returncode == 0, classify_help.stderr
    for flag in (
        "--top-class-only",
        "--class-counts",
        "--class-sequence",
        "--first-nodeids",
        "--class-counts-sequence",
    ):
        assert flag in classify_help.stdout
        assert flag in doc_text

    for command in (
        "python scripts/dev/suggest_test_scope.py app/chat/service.py",
        "python scripts/dev/classify_pytest_failures.py --class-counts",
        "python scripts/dev/classify_pytest_failures.py --top-class-only",
    ):
        assert command in doc_text

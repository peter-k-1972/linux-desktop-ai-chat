"""
QA Autopilot v3 – Dry-Run und Determinismus.

- dry-run schreibt keine Dateien
- gleicher Input + --timestamp => gleicher Output
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from .conftest import run_autopilot_v3


def _parse_first_json(text: str) -> dict:
    """Parst das erste JSON-Objekt aus stdout."""
    decoder = json.JSONDecoder()
    obj, _ = decoder.raw_decode(text)
    return obj


def test_dry_run_writes_no_files(autopilot_v3_fixtures_dir: Path) -> None:
    """Dry-Run: keine Dateien werden geschrieben."""
    out_path = autopilot_v3_fixtures_dir / "QA_AUTOPILOT_V3.json"
    trace_path = autopilot_v3_fixtures_dir / "feedback_loop" / "autopilot_v3_trace.json"

    exit_code, _, _ = run_autopilot_v3(
        [
            "--input-incidents", str(autopilot_v3_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(autopilot_v3_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(autopilot_v3_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(autopilot_v3_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(autopilot_v3_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--dry-run",
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2026-01-01T00:00:00Z",
        ],
        cwd=autopilot_v3_fixtures_dir,
    )

    assert exit_code == 0
    assert not out_path.exists()
    assert not trace_path.exists()


def test_dry_run_stdout_no_files(autopilot_v3_fixtures_dir: Path) -> None:
    """Dry-Run mit --output -: keine Dateien geschrieben."""
    out_path = autopilot_v3_fixtures_dir / "output.json"
    trace_path = autopilot_v3_fixtures_dir / "trace.json"

    exit_code, stdout, _ = run_autopilot_v3(
        [
            "--input-incidents", str(autopilot_v3_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(autopilot_v3_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(autopilot_v3_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(autopilot_v3_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(autopilot_v3_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--dry-run",
            "--output", "-",
            "--trace-output", str(trace_path),
            "--timestamp", "2026-01-01T00:00:00Z",
        ],
        cwd=autopilot_v3_fixtures_dir,
    )

    assert exit_code == 0
    assert not out_path.exists()
    output = _parse_first_json(stdout)
    assert "summary" in output


def test_determinism_same_input_same_output(autopilot_v3_fixtures_dir: Path) -> None:
    """Determinismus: gleicher Input + --timestamp => gleicher Output."""
    args = [
        "--input-incidents", str(autopilot_v3_fixtures_dir / "incidents" / "index.json"),
        "--input-analytics", str(autopilot_v3_fixtures_dir / "incidents" / "analytics.json"),
        "--input-autopilot", str(autopilot_v3_fixtures_dir / "QA_AUTOPILOT_V2.json"),
        "--input-control-center", str(autopilot_v3_fixtures_dir / "QA_CONTROL_CENTER.json"),
        "--input-priority-score", str(autopilot_v3_fixtures_dir / "QA_PRIORITY_SCORE.json"),
        "--dry-run",
        "--output", "-",
        "--trace-output", str(autopilot_v3_fixtures_dir / "trace_det.json"),
        "--timestamp", "2026-01-01T00:00:00Z",
    ]

    exit_code1, stdout1, _ = run_autopilot_v3(args, cwd=autopilot_v3_fixtures_dir)
    exit_code2, stdout2, _ = run_autopilot_v3(args, cwd=autopilot_v3_fixtures_dir)

    assert exit_code1 == 0
    assert exit_code2 == 0
    hash1 = hashlib.md5(stdout1.encode()).hexdigest()
    hash2 = hashlib.md5(stdout2.encode()).hexdigest()
    assert hash1 == hash2, "Zwei Läufe mit gleichem Input liefern unterschiedlichen Output"

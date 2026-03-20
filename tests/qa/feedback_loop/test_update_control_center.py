"""
Acceptance Tests: update_control_center.py.

Blocking acceptance tests from QA_FEEDBACK_LOOP_ACCEPTANCE_CHECKLIST:
- HP-CC-Full: Happy Path Control Center
- DRY-CC: Dry-run write-free
- MISS-Autopilot-CC: Fehlende Autopilot-Datei → Exit 1
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import ACCEPTANCE_TIMESTAMP, run_generator_script


def _cc_args(fixtures_dir: Path, out_path: Path | None = None, trace_path: Path | None = None) -> list[str]:
    inc_dir = fixtures_dir / "incidents"
    base = [
        "--input-incidents", str(inc_dir / "index.json"),
        "--input-analytics", str(inc_dir / "analytics.json"),
        "--input-autopilot", str(fixtures_dir / "QA_AUTOPILOT_V2.json"),
        "--input-control-center", str(fixtures_dir / "QA_CONTROL_CENTER.json"),
        "--input-priority-score", str(fixtures_dir / "QA_PRIORITY_SCORE.json"),
        "--timestamp", ACCEPTANCE_TIMESTAMP,
    ]
    if out_path is not None:
        base.extend(["--output", str(out_path)])
    if trace_path is not None:
        base.extend(["--trace-output", str(trace_path)])
    return base


# -----------------------------------------------------------------------------
# HP-CC-Full: Happy Path Control Center
# -----------------------------------------------------------------------------


def test_hp_cc_full(acceptance_fixtures_dir: Path) -> None:
    """HP-CC-Full: Alle Dateien vorhanden → Exit 0; Output und Trace geschrieben."""
    out_path = acceptance_fixtures_dir / "QA_CONTROL_CENTER.json"
    trace_path = acceptance_fixtures_dir / "feedback_loop" / "control_center_feedback_trace.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_control_center.py",
        _cc_args(acceptance_fixtures_dir, out_path, trace_path),
        cwd=acceptance_fixtures_dir,
    )

    assert exit_code == 0
    assert out_path.exists()
    assert trace_path.exists()

    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "current_focus" in output
    assert "governance_alerts" in output
    assert "escalations" in output
    assert "pilot_tracking" in output
    assert output["generated_at"] == ACCEPTANCE_TIMESTAMP


# -----------------------------------------------------------------------------
# DRY-CC: Dry-run Control Center
# -----------------------------------------------------------------------------


def test_dry_cc(acceptance_fixtures_dir: Path) -> None:
    """DRY-CC: --dry-run; alle Inputs vorhanden → Exit 0; keine Datei geschrieben; JSON auf stdout."""
    out_path = acceptance_fixtures_dir / "OUT_DRY.json"
    trace_path = acceptance_fixtures_dir / "feedback_loop" / "trace_dry.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_control_center.py",
        _cc_args(acceptance_fixtures_dir, out_path, trace_path) + ["--dry-run"],
        cwd=acceptance_fixtures_dir,
    )

    assert exit_code == 0
    assert not out_path.exists()
    assert not trace_path.exists()

    output = json.loads(stdout)
    assert "current_focus" in output
    assert "governance_alerts" in output
    assert "escalations" in output
    assert "pilot_tracking" in output


# -----------------------------------------------------------------------------
# MISS-Autopilot-CC: Fehlende Autopilot-Datei
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# OUT-Stdout: Output auf stdout
# -----------------------------------------------------------------------------


def test_out_stdout_cc(acceptance_fixtures_dir: Path) -> None:
    """OUT-Stdout: --output - liefert JSON auf stdout; Trace-Datei trotzdem geschrieben."""
    trace_path = acceptance_fixtures_dir / "feedback_loop" / "trace_stdout.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_control_center.py",
        [
            "--input-incidents", str(acceptance_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(acceptance_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(acceptance_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(acceptance_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(acceptance_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", "-",
            "--trace-output", str(trace_path),
            "--timestamp", ACCEPTANCE_TIMESTAMP,
        ],
        cwd=acceptance_fixtures_dir,
    )

    assert exit_code == 0
    decoder = json.JSONDecoder()
    output, _ = decoder.raw_decode(stdout)
    assert "current_focus" in output
    assert "governance_alerts" in output
    assert trace_path.exists()


# -----------------------------------------------------------------------------
# MISS-Autopilot-CC: Fehlende Autopilot-Datei
# -----------------------------------------------------------------------------


def test_miss_autopilot_cc(no_autopilot_fixtures_dir: Path) -> None:
    """MISS-Autopilot-CC: QA_AUTOPILOT_V2.json fehlt → Exit 1; keine Schreibvorgänge."""
    out_path = no_autopilot_fixtures_dir / "out.json"
    trace_path = no_autopilot_fixtures_dir / "trace.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_control_center.py",
        [
            "--input-incidents", str(no_autopilot_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(no_autopilot_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(no_autopilot_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(no_autopilot_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(no_autopilot_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", ACCEPTANCE_TIMESTAMP,
        ],
        cwd=no_autopilot_fixtures_dir,
    )

    assert exit_code == 1
    assert "QA_AUTOPILOT_V2" in stderr or "fehlt" in stderr.lower()
    assert not out_path.exists()

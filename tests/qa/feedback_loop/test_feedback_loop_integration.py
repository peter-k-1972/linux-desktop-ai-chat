"""
Integration Test: QA Feedback Loop Pipeline.

Simulates a realistic QA cycle:
1. Incident dataset
2. Analytics generation
3. Feedback loop execution (run_feedback_loop.py)
4. Governance update (update_control_center, update_priority_scores, update_risk_radar)
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from .conftest import (
    ACCEPTANCE_TIMESTAMP,
    _copy_static_fixtures,
    run_generator_script,
)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def run_feedback_loop(input_dir: Path, output_path: Path | None = None) -> tuple[int, str, str]:
    """Führt run_feedback_loop.py aus."""
    script_path = _PROJECT_ROOT / "scripts" / "qa" / "run_feedback_loop.py"
    args = ["--input-dir", str(input_dir)]
    if output_path is not None:
        args.extend(["--output", str(output_path)])
    result = subprocess.run(
        [sys.executable, str(script_path)] + args,
        cwd=str(input_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.returncode, result.stdout, result.stderr


@pytest.fixture
def pipeline_fixtures_dir(tmp_path: Path) -> Path:
    """Vollständiges Fixture-Verzeichnis für die Pipeline (Incidents, Analytics, Autopilot, Baselines)."""
    return _copy_static_fixtures(tmp_path)


def test_feedback_loop_pipeline(pipeline_fixtures_dir: Path) -> None:
    """
    Integration: Incident → Analytics → Feedback Loop → Governance Update.

    Steps:
    1. Prepare fixtures (incidents, analytics, QA_AUTOPILOT_V2, baselines)
    2. Run run_feedback_loop.py
    3. Run update_control_center, update_priority_scores, update_risk_radar
    4. Validate outputs
    """
    base = pipeline_fixtures_dir
    inc_dir = base / "incidents"
    trace_dir = base / "feedback_loop"
    trace_dir.mkdir(parents=True, exist_ok=True)

    # --- Step 1: Fixtures are prepared by pipeline_fixtures_dir ---
    assert (inc_dir / "index.json").exists()
    assert (inc_dir / "analytics.json").exists()
    assert (base / "QA_AUTOPILOT_V2.json").exists()
    assert (base / "QA_CONTROL_CENTER.json").exists()
    assert (base / "QA_PRIORITY_SCORE.json").exists()
    assert (base / "QA_RISK_RADAR.md").exists()

    # --- Step 2: Run feedback loop ---
    report_path = base / "FEEDBACK_LOOP_REPORT.json"
    exit_code, stdout, stderr = run_feedback_loop(base, report_path)
    assert exit_code == 0, f"run_feedback_loop failed: {stderr}"
    assert report_path.exists()
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert "per_subsystem_results" in report or "rule_results" in report

    # --- Step 3: Run governance update scripts ---
    cc_out = base / "QA_CONTROL_CENTER.json"
    ps_out = base / "QA_PRIORITY_SCORE.json"
    rr_out = base / "QA_RISK_RADAR.json"

    cc_args = [
        "--input-incidents", str(inc_dir / "index.json"),
        "--input-analytics", str(inc_dir / "analytics.json"),
        "--input-autopilot", str(base / "QA_AUTOPILOT_V2.json"),
        "--input-control-center", str(base / "QA_CONTROL_CENTER.json"),
        "--input-priority-score", str(base / "QA_PRIORITY_SCORE.json"),
        "--output", str(cc_out),
        "--trace-output", str(trace_dir / "control_center_trace.json"),
        "--timestamp", ACCEPTANCE_TIMESTAMP,
    ]
    exit_cc, _, _ = run_generator_script("update_control_center.py", cc_args, cwd=base)
    assert exit_cc == 0

    ps_args = [
        "--input-incidents", str(inc_dir / "index.json"),
        "--input-analytics", str(inc_dir / "analytics.json"),
        "--input-autopilot", str(base / "QA_AUTOPILOT_V2.json"),
        "--input-priority-score", str(base / "QA_PRIORITY_SCORE.json"),
        "--output", str(ps_out),
        "--trace-output", str(trace_dir / "priority_score_trace.json"),
        "--timestamp", ACCEPTANCE_TIMESTAMP,
    ]
    exit_ps, _, _ = run_generator_script("update_priority_scores.py", ps_args, cwd=base)
    assert exit_ps == 0

    rr_args = [
        "--input-incidents", str(inc_dir / "index.json"),
        "--input-analytics", str(inc_dir / "analytics.json"),
        "--input-autopilot", str(base / "QA_AUTOPILOT_V2.json"),
        "--input-risk-radar", str(base / "QA_RISK_RADAR.md"),
        "--input-priority-score", str(base / "QA_PRIORITY_SCORE.json"),
        "--output", str(rr_out),
        "--trace-output", str(trace_dir / "risk_radar_trace.json"),
        "--timestamp", ACCEPTANCE_TIMESTAMP,
    ]
    exit_rr, _, _ = run_generator_script("update_risk_radar.py", rr_args, cwd=base)
    assert exit_rr == 0

    # --- Step 4: Validate outputs ---
    cc = json.loads(cc_out.read_text(encoding="utf-8"))
    assert "current_focus" in cc
    assert "governance_alerts" in cc
    assert "pilot_tracking" in cc

    ps = json.loads(ps_out.read_text(encoding="utf-8"))
    assert "scores" in ps
    assert "top3_prioritaeten" in ps

    rr = json.loads(rr_out.read_text(encoding="utf-8"))
    assert "subsystems" in rr
    assert "failure_classes" in rr

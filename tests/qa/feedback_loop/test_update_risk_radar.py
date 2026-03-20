"""
Acceptance Tests: update_risk_radar.py.

Blocking acceptance tests from QA_FEEDBACK_LOOP_ACCEPTANCE_CHECKLIST:
- HP-RR-Full: Happy Path Risk Radar
- DRY-RR: Dry-run write-free
- BND-Esc-RR: Bounded Risk Escalation (max eine Stufe pro Lauf)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import ACCEPTANCE_TIMESTAMP, run_generator_script


def _rr_args(fixtures_dir: Path, out_path: Path | None = None, trace_path: Path | None = None) -> list[str]:
    inc_dir = fixtures_dir / "incidents"
    risk_radar = fixtures_dir / "QA_RISK_RADAR.md"
    if not risk_radar.exists():
        risk_radar = fixtures_dir / "QA_RISK_RADAR.json"
    base = [
        "--input-incidents", str(inc_dir / "index.json"),
        "--input-analytics", str(inc_dir / "analytics.json"),
        "--input-autopilot", str(fixtures_dir / "QA_AUTOPILOT_V2.json"),
        "--input-risk-radar", str(risk_radar),
        "--input-priority-score", str(fixtures_dir / "QA_PRIORITY_SCORE.json"),
        "--timestamp", ACCEPTANCE_TIMESTAMP,
    ]
    if out_path is not None:
        base.extend(["--output", str(out_path)])
    if trace_path is not None:
        base.extend(["--trace-output", str(trace_path)])
    return base


# -----------------------------------------------------------------------------
# HP-RR-Full: Happy Path Risk Radar
# -----------------------------------------------------------------------------


def test_hp_rr_full(acceptance_fixtures_dir: Path) -> None:
    """HP-RR-Full: Alle Dateien vorhanden → Exit 0; subsystems, failure_classes, risk_policy."""
    out_path = acceptance_fixtures_dir / "QA_RISK_RADAR.json"
    trace_path = acceptance_fixtures_dir / "feedback_loop" / "risk_radar_feedback_trace.json"

    exit_code, _, _ = run_generator_script(
        "update_risk_radar.py",
        _rr_args(acceptance_fixtures_dir, out_path, trace_path),
        cwd=acceptance_fixtures_dir,
    )

    assert exit_code == 0
    assert out_path.exists()
    assert trace_path.exists()

    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "subsystems" in output
    assert "failure_classes" in output
    assert "risk_policy" in output
    assert output["generated_at"] == ACCEPTANCE_TIMESTAMP
    assert len(output["subsystems"]) >= 1
    assert len(output["failure_classes"]) >= 1

    for sub, data in output.get("subsystems", {}).items():
        assert "old_risk_level" in data
        assert "new_risk_level" in data
        assert data["new_risk_level"] in ("low", "medium", "high", "critical")


# -----------------------------------------------------------------------------
# DRY-RR: Dry-run Risk Radar
# -----------------------------------------------------------------------------


def test_dry_rr(acceptance_fixtures_dir: Path) -> None:
    """DRY-RR: --dry-run; alle Inputs vorhanden → Exit 0; keine Datei geschrieben."""
    out_path = acceptance_fixtures_dir / "OUT_DRY_RR.json"
    trace_path = acceptance_fixtures_dir / "feedback_loop" / "trace_rr_dry.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_risk_radar.py",
        _rr_args(acceptance_fixtures_dir, out_path, trace_path) + ["--dry-run"],
        cwd=acceptance_fixtures_dir,
    )

    assert exit_code == 0
    assert not out_path.exists()
    assert not trace_path.exists()

    output = json.loads(stdout)
    assert "subsystems" in output
    assert "risk_policy" in output


# -----------------------------------------------------------------------------
# BND-Esc-RR: Bounded Risk Escalation
# -----------------------------------------------------------------------------


# -----------------------------------------------------------------------------
# OUT-Stdout: Output auf stdout
# -----------------------------------------------------------------------------


def test_out_stdout_rr(acceptance_fixtures_dir: Path) -> None:
    """OUT-Stdout: --output - liefert JSON auf stdout; Trace-Datei trotzdem geschrieben."""
    trace_path = acceptance_fixtures_dir / "feedback_loop" / "trace_rr_stdout.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_risk_radar.py",
        [
            "--input-incidents", str(acceptance_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(acceptance_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(acceptance_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-risk-radar", str(acceptance_fixtures_dir / "QA_RISK_RADAR.md"),
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
    assert "subsystems" in output
    assert trace_path.exists()


# -----------------------------------------------------------------------------
# BND-Esc-RR: Bounded Risk Escalation
# -----------------------------------------------------------------------------


def test_bnd_esc_rr(bounded_esc_fixtures_dir: Path) -> None:
    """BND-Esc-RR: old_level=low, Signale für critical → new_risk_level = medium (max eine Stufe)."""
    out_path = bounded_esc_fixtures_dir / "OUT_RR.json"
    trace_path = bounded_esc_fixtures_dir / "feedback_loop" / "trace.json"
    (bounded_esc_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)

    exit_code, _, _ = run_generator_script(
        "update_risk_radar.py",
        _rr_args(bounded_esc_fixtures_dir, out_path, trace_path),
        cwd=bounded_esc_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert output["risk_policy"]["bounded_escalation"] is True

    level_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}
    for sub, data in output.get("subsystems", {}).items():
        old_level = data.get("old_risk_level", "medium")
        new_level = data.get("new_risk_level", "medium")
        old_idx = level_order.get(old_level, 0)
        new_idx = level_order.get(new_level, 0)
        assert new_idx <= old_idx + 1, (
            f"Eskalation für {sub} überschreitet eine Stufe (old={old_level}, new={new_level})"
        )

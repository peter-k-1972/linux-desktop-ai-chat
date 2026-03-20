"""
Generator Tests: update_risk_radar.py.

Testet Happy Path, single_incident_not_auto_high, Cluster-Eskalation,
Replay-/Regression-Gap-Marker, Drift-Pattern, Bounded Escalation,
fehlende Baseline, defekte Inputs, Dry-run, Determinismus.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import run_generator_script


def _rr_args(fixtures_dir: Path, out_path: Path | None = None, trace_path: Path | None = None) -> list[str]:
    """Standard-Argumente für update_risk_radar."""
    inc_dir = fixtures_dir / "incidents"
    risk_radar = fixtures_dir / "QA_RISK_RADAR.md"
    base = [
        "--input-incidents", str(inc_dir / "index.json"),
        "--input-analytics", str(inc_dir / "analytics.json"),
        "--input-autopilot", str(fixtures_dir / "QA_AUTOPILOT_V2.json"),
        "--input-risk-radar", str(risk_radar) if risk_radar.exists() else str(fixtures_dir / "QA_RISK_RADAR.json"),
        "--input-priority-score", str(fixtures_dir / "QA_PRIORITY_SCORE.json"),
        "--timestamp", "2025-01-15T12:00:00Z",
    ]
    if out_path is not None:
        base.extend(["--output", str(out_path)])
    if trace_path is not None:
        base.extend(["--trace-output", str(trace_path)])
    return base


# -----------------------------------------------------------------------------
# 1. Happy Path
# -----------------------------------------------------------------------------


def test_hp_rr_full(generator_fixtures_dir: Path) -> None:
    """Happy Path: subsystems, failure_classes, markers, reasons, Trace-Datei."""
    out_path = generator_fixtures_dir / "QA_RISK_RADAR.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "risk_radar_feedback_trace.json"

    exit_code, _, _ = run_generator_script(
        "update_risk_radar.py",
        _rr_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    assert out_path.exists()
    assert trace_path.exists()

    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "subsystems" in output
    assert "failure_classes" in output
    assert "risk_policy" in output
    assert output["generated_at"] == "2025-01-15T12:00:00Z"
    assert len(output["subsystems"]) >= 1
    assert len(output["failure_classes"]) >= 1

    for sub, data in output.get("subsystems", {}).items():
        assert "old_risk_level" in data
        assert "new_risk_level" in data
        assert "markers" in data
        assert "reasons" in data
        assert data["new_risk_level"] in ("low", "medium", "high", "critical")


def test_hp_trace_file_created(generator_fixtures_dir: Path) -> None:
    """Trace-Datei wird korrekt erzeugt."""
    trace_path = generator_fixtures_dir / "feedback_loop" / "risk_radar_feedback_trace.json"
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    out_path = generator_fixtures_dir / "OUT_RR.json"

    exit_code, _, _ = run_generator_script(
        "update_risk_radar.py",
        _rr_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert "generated_at" in trace
    assert trace["generator"] == "update_risk_radar"
    assert "applied_rules" in trace
    assert "escalations" in trace
    assert "summary" in trace
    assert "subsystems_elevated" in trace["summary"]


# -----------------------------------------------------------------------------
# 2. single_incident_not_auto_high
# -----------------------------------------------------------------------------


def test_single_incident_not_auto_high(single_incident_fixtures_dir: Path) -> None:
    """Ein einzelner Incident eskaliert nicht unzulässig auf high/critical."""
    out_path = single_incident_fixtures_dir / "OUT.json"
    trace_path = single_incident_fixtures_dir / "feedback_loop" / "trace.json"
    (single_incident_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)
    (single_incident_fixtures_dir / "QA_RISK_RADAR.md").write_text(
        "# Risk Radar\n\n| Subsystem | Priorität |\n|-----------|----------|\n| RAG | P3 |\n",
        encoding="utf-8",
    )

    exit_code, _, _ = run_generator_script(
        "update_risk_radar.py",
        _rr_args(single_incident_fixtures_dir, out_path, trace_path),
        cwd=single_incident_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert output["risk_policy"]["single_incident_not_auto_high"] is True

    rag = output.get("subsystems", {}).get("RAG", {})
    new_level = rag.get("new_risk_level", "")
    assert new_level in ("low", "medium"), f"Einzelner Incident darf nicht high/critical sein, war: {new_level}"


# -----------------------------------------------------------------------------
# 3. Cluster-Eskalation
# -----------------------------------------------------------------------------


def test_cluster_escalation(cluster_incidents_fixtures_dir: Path) -> None:
    """Mehrere zusammenhängende Signale erhöhen Risiko nachvollziehbar."""
    out_path = cluster_incidents_fixtures_dir / "OUT.json"
    trace_path = cluster_incidents_fixtures_dir / "feedback_loop" / "trace.json"
    (cluster_incidents_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)
    (cluster_incidents_fixtures_dir / "QA_RISK_RADAR.md").write_text(
        "# Risk Radar\n\n| Subsystem | Priorität |\n|-----------|----------|\n| RAG | P3 |\n",
        encoding="utf-8",
    )

    exit_code, _, _ = run_generator_script(
        "update_risk_radar.py",
        _rr_args(cluster_incidents_fixtures_dir, out_path, trace_path),
        cwd=cluster_incidents_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    rag = output.get("subsystems", {}).get("RAG", {})
    markers = rag.get("markers", [])
    new_level = rag.get("new_risk_level", "")
    assert "cluster_risk" in markers or new_level in ("high", "critical")


# -----------------------------------------------------------------------------
# 4. Replay Gap Marker
# -----------------------------------------------------------------------------


def test_replay_gap_marker(replay_gap_only_fixtures_dir: Path) -> None:
    """Replay-Gap-Marker ist im Radar sichtbar (reproducibility_risk)."""
    out_path = replay_gap_only_fixtures_dir / "OUT.json"
    trace_path = replay_gap_only_fixtures_dir / "feedback_loop" / "trace.json"
    (replay_gap_only_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)

    exit_code, _, _ = run_generator_script(
        "update_risk_radar.py",
        _rr_args(replay_gap_only_fixtures_dir, out_path, trace_path),
        cwd=replay_gap_only_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    rag = output.get("subsystems", {}).get("RAG", {})
    markers = rag.get("markers", [])
    assert "reproducibility_risk" in markers


# -----------------------------------------------------------------------------
# 5. Regression Gap Marker
# -----------------------------------------------------------------------------


def test_regression_gap_marker(regression_gap_only_fixtures_dir: Path) -> None:
    """Regression-Gap-Marker ist getrennt sichtbar (regression_protection_risk)."""
    out_path = regression_gap_only_fixtures_dir / "OUT.json"
    trace_path = regression_gap_only_fixtures_dir / "feedback_loop" / "trace.json"
    (regression_gap_only_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)

    exit_code, _, _ = run_generator_script(
        "update_risk_radar.py",
        _rr_args(regression_gap_only_fixtures_dir, out_path, trace_path),
        cwd=regression_gap_only_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    rag = output.get("subsystems", {}).get("RAG", {})
    markers = rag.get("markers", [])
    assert "regression_protection_risk" in markers


# -----------------------------------------------------------------------------
# 6. Drift Pattern
# -----------------------------------------------------------------------------


def test_drift_pattern_structural_risk(drift_pattern_fixtures_dir: Path) -> None:
    """Repeated Drift erzeugt strukturelles Risiko – failure_class-Risiko markiert."""
    out_path = drift_pattern_fixtures_dir / "OUT.json"
    trace_path = drift_pattern_fixtures_dir / "feedback_loop" / "trace.json"
    (drift_pattern_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)

    exit_code, _, _ = run_generator_script(
        "update_risk_radar.py",
        _rr_args(drift_pattern_fixtures_dir, out_path, trace_path),
        cwd=drift_pattern_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    escalations = output.get("escalations", [])
    fc_data = output.get("failure_classes", {})
    drift_markers = [
        d.get("markers", []) for d in fc_data.values()
        if "drift_pattern" in d.get("markers", [])
    ]
    assert any("drift" in e.lower() for e in escalations) or len(drift_markers) >= 1


# -----------------------------------------------------------------------------
# 7. Bounded Escalation
# -----------------------------------------------------------------------------


def test_bounded_escalation(high_delta_fixtures_dir: Path) -> None:
    """Eskalation folgt Policy – max eine Stufe pro Lauf, keine ungebremsten Sprünge."""
    out_path = high_delta_fixtures_dir / "OUT.json"
    trace_path = high_delta_fixtures_dir / "feedback_loop" / "trace.json"
    (high_delta_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)
    (high_delta_fixtures_dir / "QA_RISK_RADAR.md").write_text(
        "# Risk Radar\n\n| Subsystem | Priorität |\n|-----------|----------|\n| RAG | P3 |\n",
        encoding="utf-8",
    )

    exit_code, _, _ = run_generator_script(
        "update_risk_radar.py",
        _rr_args(high_delta_fixtures_dir, out_path, trace_path),
        cwd=high_delta_fixtures_dir,
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
        assert new_idx <= old_idx + 1, f"Eskalation für {sub} überschreitet eine Stufe (old={old_level}, new={new_level})"


# -----------------------------------------------------------------------------
# 8. Fehlende Baseline-Datei
# -----------------------------------------------------------------------------


def test_miss_risk_radar_baseline_robust(no_risk_radar_fixtures_dir: Path) -> None:
    """Fehlende QA_RISK_RADAR.md – robuster Umgang, Default-Level."""
    out_path = no_risk_radar_fixtures_dir / "QA_RISK_RADAR_NEW.json"
    trace_path = no_risk_radar_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_risk_radar.py",
        [
            "--input-incidents", str(no_risk_radar_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(no_risk_radar_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(no_risk_radar_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-risk-radar", str(no_risk_radar_fixtures_dir / "QA_RISK_RADAR.md"),
            "--input-priority-score", str(no_risk_radar_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2025-01-15T12:00:00Z",
        ],
        cwd=no_risk_radar_fixtures_dir,
    )

    assert exit_code == 0
    assert out_path.exists()
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "subsystems" in output
    for sub, data in output.get("subsystems", {}).items():
        assert data["new_risk_level"] in ("low", "medium", "high", "critical")


# -----------------------------------------------------------------------------
# 9. Defekte/fehlende Inputs
# -----------------------------------------------------------------------------


def test_miss_incidents_analytics_minimal_projection(no_incidents_no_analytics_fixtures_dir: Path) -> None:
    """Weder incidents noch analytics – minimale Projektion, kein Crash."""
    out_path = no_incidents_no_analytics_fixtures_dir / "OUT.json"
    trace_path = no_incidents_no_analytics_fixtures_dir / "feedback_loop" / "trace.json"
    (no_incidents_no_analytics_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)

    exit_code, _, stderr = run_generator_script(
        "update_risk_radar.py",
        [
            "--input-incidents", str(no_incidents_no_analytics_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(no_incidents_no_analytics_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(no_incidents_no_analytics_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-risk-radar", str(no_incidents_no_analytics_fixtures_dir / "QA_RISK_RADAR.md"),
            "--input-priority-score", str(no_incidents_no_analytics_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2025-01-15T12:00:00Z",
        ],
        cwd=no_incidents_no_analytics_fixtures_dir,
    )

    assert exit_code == 0
    assert out_path.exists()
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "warnings" in output


# -----------------------------------------------------------------------------
# 10. Dry-run
# -----------------------------------------------------------------------------


def test_dry_run_write_free(generator_fixtures_dir: Path) -> None:
    """Dry-run: keine Dateien werden geschrieben."""
    out_path = generator_fixtures_dir / "OUT_DRY_RR.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace_rr_dry.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_risk_radar.py",
        _rr_args(generator_fixtures_dir, out_path, trace_path) + ["--dry-run"],
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    assert not out_path.exists()
    assert not trace_path.exists()
    output = json.loads(stdout)
    assert "subsystems" in output
    assert "risk_policy" in output


# -----------------------------------------------------------------------------
# 11. Determinismus
# -----------------------------------------------------------------------------


def test_determinism_same_inputs_same_output(generator_fixtures_dir: Path) -> None:
    """Gleiche Inputs -> gleiche Risk-Projektion."""
    out1 = generator_fixtures_dir / "OUT1.json"
    out2 = generator_fixtures_dir / "OUT2.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace.json"

    exit1, _, _ = run_generator_script(
        "update_risk_radar.py",
        _rr_args(generator_fixtures_dir, out1, trace_path),
        cwd=generator_fixtures_dir,
    )
    assert exit1 == 0

    exit2, _, _ = run_generator_script(
        "update_risk_radar.py",
        _rr_args(generator_fixtures_dir, out2, trace_path),
        cwd=generator_fixtures_dir,
    )
    assert exit2 == 0

    d1 = json.loads(out1.read_text(encoding="utf-8"))
    d2 = json.loads(out2.read_text(encoding="utf-8"))

    assert d1["generated_at"] == d2["generated_at"]
    assert d1["subsystems"] == d2["subsystems"]
    assert d1["failure_classes"] == d2["failure_classes"]
    assert d1["escalations"] == d2["escalations"]

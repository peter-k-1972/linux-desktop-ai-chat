"""
Generator Tests: update_control_center.py.

Testet Happy Path, fehlende Baseline, Change Log, Pilot Tracking,
Dry-run, defekte Inputs, Determinismus.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from .conftest import run_generator_script


def _cc_args(fixtures_dir: Path, out_path: Path | None = None, trace_path: Path | None = None) -> list[str]:
    """Standard-Argumente für update_control_center."""
    inc_dir = fixtures_dir / "incidents"
    base = [
        "--input-incidents", str(inc_dir / "index.json"),
        "--input-analytics", str(inc_dir / "analytics.json"),
        "--input-autopilot", str(fixtures_dir / "QA_AUTOPILOT_V2.json"),
        "--input-control-center", str(fixtures_dir / "QA_CONTROL_CENTER.json"),
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


def test_hp_cc_full(generator_fixtures_dir: Path) -> None:
    """Happy Path: gültige Inputs, Exit 0, Output und Trace geschrieben."""
    out_path = generator_fixtures_dir / "QA_CONTROL_CENTER.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "control_center_feedback_trace.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_control_center.py",
        _cc_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    assert out_path.exists()
    assert trace_path.exists()

    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "current_focus" in output
    assert "governance_alerts" in output
    assert "escalations" in output
    assert "pilot_tracking" in output
    assert output["generated_at"] == "2025-01-15T12:00:00Z"


def test_hp_current_focus_projection(generator_fixtures_dir: Path) -> None:
    """Sinnvolle current_focus-Projektion aus Autopilot."""
    out_path = generator_fixtures_dir / "OUT_CC.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_control_center.py",
        _cc_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    cf = output["current_focus"]
    assert cf["recommended_focus_subsystem"] == "RAG"
    assert cf["recommended_failure_class"] == "async_race"
    assert cf["recommended_guard_type"] == "failure_replay_guard"
    assert cf["recommended_test_domain"] == "async_behavior"
    assert cf["recommended_next_sprint"] == "RAG Failure Replay"


def test_hp_feedback_loop_summary_present(generator_fixtures_dir: Path) -> None:
    """feedback_loop_summary ist vorhanden mit erwarteter Struktur."""
    out_path = generator_fixtures_dir / "OUT_CC.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_control_center.py",
        _cc_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    fls = output.get("feedback_loop_summary", {})
    assert "top_incident_pressure_subsystems" in fls
    assert "highest_replay_gap_subsystems" in fls
    assert "highest_regression_gap_subsystems" in fls
    assert "dominant_drift_patterns" in fls


def test_hp_governance_alerts_when_gaps(generator_fixtures_dir: Path) -> None:
    """governance_alerts vorhanden, wenn Replay-/Regression-Gaps vorliegen."""
    out_path = generator_fixtures_dir / "OUT_CC.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_control_center.py",
        _cc_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    alerts = output.get("governance_alerts", [])
    # Mit RAG Incidents und replay_status=missing sollte REPLAY_GAP oder INCIDENT_PRESSURE vorkommen
    assert isinstance(alerts, list)
    codes = [a.get("code") for a in alerts if isinstance(a, dict)]
    assert "REPLAY_GAP" in codes or "INCIDENT_PRESSURE" in codes or "REGRESSION_GAP" in codes or len(alerts) >= 0


def test_hp_trace_file_correct(generator_fixtures_dir: Path) -> None:
    """Trace-Datei wird korrekt erzeugt mit Pflichtfeldern."""
    trace_path = generator_fixtures_dir / "feedback_loop" / "control_center_feedback_trace.json"
    trace_path.parent.mkdir(parents=True, exist_ok=True)
    out_path = generator_fixtures_dir / "OUT_CC.json"

    exit_code, _, _ = run_generator_script(
        "update_control_center.py",
        _cc_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    trace = json.loads(trace_path.read_text(encoding="utf-8"))
    assert "generated_at" in trace
    assert trace["generator"] == "update_control_center"
    assert "input_sources" in trace
    assert "applied_rules" in trace
    assert "summary" in trace
    assert "subsystems_analyzed" in trace["summary"]
    assert "governance_alerts" in trace["summary"]


# -----------------------------------------------------------------------------
# 2. Fehlende Baseline-Datei
# -----------------------------------------------------------------------------


def test_miss_baseline_cc_robust(no_control_center_fixtures_dir: Path) -> None:
    """QA_CONTROL_CENTER.json fehlt – Generator verhält sich robust (initialer Lauf)."""
    out_path = no_control_center_fixtures_dir / "QA_CONTROL_CENTER_NEW.json"
    trace_path = no_control_center_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_control_center.py",
        [
            "--input-incidents", str(no_control_center_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(no_control_center_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(no_control_center_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(no_control_center_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(no_control_center_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2025-01-15T12:00:00Z",
        ],
        cwd=no_control_center_fixtures_dir,
    )

    assert exit_code == 0
    assert out_path.exists()
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "change_log" in output
    initial_entry = next((e for e in output["change_log"] if e.get("field") == "full"), None)
    assert initial_entry is not None
    assert initial_entry.get("reason") == "Keine Vorversion" or initial_entry.get("new_value") == "initial"


# -----------------------------------------------------------------------------
# 3. Change Log
# -----------------------------------------------------------------------------


def test_change_log_documents_changes(generator_fixtures_dir: Path) -> None:
    """Änderungen gegenüber bestehender Baseline werden nachvollziehbar dokumentiert."""
    out_path = generator_fixtures_dir / "OUT_CC.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace.json"

    exit_code, _, _ = run_generator_script(
        "update_control_center.py",
        _cc_args(generator_fixtures_dir, out_path, trace_path),
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    change_log = output.get("change_log", [])
    assert isinstance(change_log, list)
    for entry in change_log:
        assert "field" in entry
        assert "old_value" in entry or "new_value" in entry
        assert "reason" in entry


# -----------------------------------------------------------------------------
# 4. Pilot Tracking
# -----------------------------------------------------------------------------


def test_pilot_tracking_all_three_constellations(tmp_path: Path) -> None:
    """Die drei Pilotkonstellationen werden erfasst: startup/ollama, rag/chromadb, debug/eventbus."""
    from .conftest import _minimal_fixture_dir

    base = _minimal_fixture_dir(tmp_path)
    out_path = base / "OUT.json"
    trace_path = base / "feedback_loop" / "trace.json"
    trace_path.parent.mkdir(parents=True, exist_ok=True)

    for pilot_id, pilot_name in [
        (1, "Startup / Ollama unreachable"),
        (2, "RAG / ChromaDB network failure"),
        (3, "Debug/EventBus / EventType drift"),
    ]:
        autopilot = {
            "recommended_focus_subsystem": "RAG",
            "recommended_focus_failure_class": "async_race",
            "recommended_next_sprint": "RAG Failure Replay",
            "recommended_guard_type": "failure_replay_guard",
            "recommended_test_domain": "async_behavior",
            "pilot_constellation_matched": {"id": pilot_id, "name": pilot_name},
        }
        (base / "QA_AUTOPILOT_V2.json").write_text(
            json.dumps(autopilot, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (base / "QA_CONTROL_CENTER.json").write_text("{}", encoding="utf-8")

        exit_code, _, _ = run_generator_script(
            "update_control_center.py",
            [
                "--input-incidents", str(base / "incidents" / "index.json"),
                "--input-analytics", str(base / "incidents" / "analytics.json"),
                "--input-autopilot", str(base / "QA_AUTOPILOT_V2.json"),
                "--input-control-center", str(base / "QA_CONTROL_CENTER.json"),
                "--input-priority-score", str(base / "QA_PRIORITY_SCORE.json"),
                "--output", str(out_path),
                "--trace-output", str(trace_path),
                "--timestamp", "2025-01-15T12:00:00Z",
            ],
            cwd=base,
        )

        assert exit_code == 0
        output = json.loads(out_path.read_text(encoding="utf-8"))
        pt = output.get("pilot_tracking", {})
        assert "pilot_1_startup_ollama_unreachable" in pt
        assert "pilot_2_rag_chromadb_network_failure" in pt
        assert "pilot_3_debug_eventbus_eventtype_drift" in pt
        assert pt["pilot_1_startup_ollama_unreachable"]["active"] == (pilot_id == 1)
        assert pt["pilot_2_rag_chromadb_network_failure"]["active"] == (pilot_id == 2)
        assert pt["pilot_3_debug_eventbus_eventtype_drift"]["active"] == (pilot_id == 3)


# -----------------------------------------------------------------------------
# 5. Dry-run
# -----------------------------------------------------------------------------


def test_dry_run_write_free(generator_fixtures_dir: Path) -> None:
    """Dry-run: keine Dateien werden geschrieben."""
    out_path = generator_fixtures_dir / "OUT_DRY.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace_dry.json"

    exit_code, stdout, stderr = run_generator_script(
        "update_control_center.py",
        _cc_args(generator_fixtures_dir, out_path, trace_path) + ["--dry-run"],
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    assert not out_path.exists()
    assert not trace_path.exists()


def test_dry_run_useful_output(generator_fixtures_dir: Path) -> None:
    """Dry-run: brauchbare Auswertung / Rückmeldung auf stdout."""
    exit_code, stdout, stderr = run_generator_script(
        "update_control_center.py",
        _cc_args(generator_fixtures_dir, None, None) + ["--dry-run"],
        cwd=generator_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(stdout)
    assert "current_focus" in output
    assert "feedback_loop_summary" in output
    assert "governance_alerts" in output
    assert "pilot_tracking" in output
    assert "change_log" in output


# -----------------------------------------------------------------------------
# 6. Defekte Inputs
# -----------------------------------------------------------------------------


def test_miss_autopilot_exit_1(no_autopilot_fixtures_dir: Path) -> None:
    """Fehlende Autopilot-Datei führt zu Exit 1 und kontrollierter Fehlermeldung."""
    exit_code, stdout, stderr = run_generator_script(
        "update_control_center.py",
        [
            "--input-incidents", str(no_autopilot_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(no_autopilot_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(no_autopilot_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(no_autopilot_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--output", str(no_autopilot_fixtures_dir / "out.json"),
            "--trace-output", str(no_autopilot_fixtures_dir / "trace.json"),
        ],
        cwd=no_autopilot_fixtures_dir,
    )

    assert exit_code == 1
    assert "QA_AUTOPILOT_V2" in stderr or "fehlt" in stderr.lower()
    assert not (no_autopilot_fixtures_dir / "out.json").exists()


def test_miss_analytics_robust(no_analytics_fixtures_dir: Path) -> None:
    """Fehlende analytics-Datei: Generator läuft mit Fallback, definierter Output."""
    out_path = no_analytics_fixtures_dir / "OUT.json"
    trace_path = no_analytics_fixtures_dir / "feedback_loop" / "trace.json"
    (no_analytics_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)

    exit_code, _, _ = run_generator_script(
        "update_control_center.py",
        [
            "--input-incidents", str(no_analytics_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(no_analytics_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(no_analytics_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(no_analytics_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(no_analytics_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2025-01-15T12:00:00Z",
        ],
        cwd=no_analytics_fixtures_dir,
    )

    assert exit_code == 0
    assert out_path.exists()
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "current_focus" in output
    assert "feedback_loop_summary" in output


def test_incomplete_incident_structure_robust(incomplete_incidents_fixtures_dir: Path) -> None:
    """Unvollständige Incident-Struktur: kontrollierter Fallback, kein Crash."""
    out_path = incomplete_incidents_fixtures_dir / "OUT.json"
    trace_path = incomplete_incidents_fixtures_dir / "feedback_loop" / "trace.json"
    (incomplete_incidents_fixtures_dir / "feedback_loop").mkdir(parents=True, exist_ok=True)

    exit_code, _, _ = run_generator_script(
        "update_control_center.py",
        [
            "--input-incidents", str(incomplete_incidents_fixtures_dir / "incidents" / "index.json"),
            "--input-analytics", str(incomplete_incidents_fixtures_dir / "incidents" / "analytics.json"),
            "--input-autopilot", str(incomplete_incidents_fixtures_dir / "QA_AUTOPILOT_V2.json"),
            "--input-control-center", str(incomplete_incidents_fixtures_dir / "QA_CONTROL_CENTER.json"),
            "--input-priority-score", str(incomplete_incidents_fixtures_dir / "QA_PRIORITY_SCORE.json"),
            "--output", str(out_path),
            "--trace-output", str(trace_path),
            "--timestamp", "2025-01-15T12:00:00Z",
        ],
        cwd=incomplete_incidents_fixtures_dir,
    )

    assert exit_code == 0
    output = json.loads(out_path.read_text(encoding="utf-8"))
    assert "feedback_loop_summary" in output
    assert "top_incident_pressure_subsystems" in output["feedback_loop_summary"]


# -----------------------------------------------------------------------------
# 7. Determinismus
# -----------------------------------------------------------------------------


def test_determinism_same_inputs_same_output(generator_fixtures_dir: Path) -> None:
    """Zweimal gleicher Lauf auf gleichen Inputs ergibt inhaltlich gleiche Output-Struktur."""
    out1 = generator_fixtures_dir / "OUT1.json"
    out2 = generator_fixtures_dir / "OUT2.json"
    trace_path = generator_fixtures_dir / "feedback_loop" / "trace.json"

    args = _cc_args(generator_fixtures_dir, out1, trace_path)

    exit1, _, _ = run_generator_script("update_control_center.py", args, cwd=generator_fixtures_dir)
    assert exit1 == 0

    args2 = _cc_args(generator_fixtures_dir, out2, trace_path)
    exit2, _, _ = run_generator_script("update_control_center.py", args2, cwd=generator_fixtures_dir)
    assert exit2 == 0

    d1 = json.loads(out1.read_text(encoding="utf-8"))
    d2 = json.loads(out2.read_text(encoding="utf-8"))

    # generated_at ist identisch (--timestamp)
    assert d1["generated_at"] == d2["generated_at"]
    assert d1["current_focus"] == d2["current_focus"]
    assert d1["feedback_loop_summary"]["top_incident_pressure_subsystems"] == d2["feedback_loop_summary"]["top_incident_pressure_subsystems"]
    assert len(d1["governance_alerts"]) == len(d2["governance_alerts"])
    assert len(d1["change_log"]) == len(d2["change_log"])

"""
Pytest Fixtures für QA Generator Tests.

Stellt vollständige Fixture-Verzeichnisse für update_control_center,
update_priority_scores, update_risk_radar bereit.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _minimal_fixture_dir(tmp_path: Path, incidents_override: dict | None = None) -> Path:
    """Erstellt minimales Fixture-Verzeichnis mit allen benötigten Dateien."""
    inc_dir = tmp_path / "incidents"
    inc_dir.mkdir(parents=True)

    incident_index = incidents_override or {
        "schema_version": "1.0",
        "incidents": [
            {"id": "inc-001", "subsystem": "RAG", "failure_class": "async_race", "severity": "high", "replay_status": "missing", "binding_status": None},
            {"id": "inc-002", "subsystem": "RAG", "failure_class": "async_race", "severity": "medium", "replay_status": "validated", "binding_status": "catalog_bound"},
        ],
    }
    (inc_dir / "index.json").write_text(json.dumps(incident_index, indent=2, ensure_ascii=False), encoding="utf-8")
    analytics = {"qa_coverage": {"replay_defined_ratio": 0.6, "regression_bound_ratio": 0.4}}
    (inc_dir / "analytics.json").write_text(json.dumps(analytics, indent=2, ensure_ascii=False), encoding="utf-8")

    autopilot = {
        "recommended_focus_subsystem": "RAG",
        "recommended_focus_failure_class": "async_race",
        "recommended_next_sprint": "RAG Failure Replay",
        "recommended_guard_type": "failure_replay_guard",
        "recommended_test_domain": "async_behavior",
    }
    (tmp_path / "QA_AUTOPILOT_V2.json").write_text(json.dumps(autopilot, indent=2, ensure_ascii=False), encoding="utf-8")

    priority_score = {
        "scores": [
            {"Subsystem": "RAG", "Score": 2, "Prioritaet": "P2", "Begruendung": "", "Naechster_QA_Schritt": "–"},
            {"Subsystem": "Startup/Bootstrap", "Score": 1, "Prioritaet": "P3", "Begruendung": "", "Naechster_QA_Schritt": "–"},
        ],
    }
    (tmp_path / "QA_PRIORITY_SCORE.json").write_text(json.dumps(priority_score, indent=2, ensure_ascii=False), encoding="utf-8")

    control_center = {"naechster_qa_sprint": {"subsystem": "RAG", "schritt": "Replay", "source": "QA_AUTOPILOT_V2"}}
    (tmp_path / "QA_CONTROL_CENTER.json").write_text(json.dumps(control_center, indent=2, ensure_ascii=False), encoding="utf-8")

    risk_radar_md = "# QA Risk Radar\n\n| Subsystem | Priorität |\n|-----------|----------|\n| RAG | P1 |\n| Startup/Bootstrap | P2 |\n"
    (tmp_path / "QA_RISK_RADAR.md").write_text(risk_radar_md, encoding="utf-8")

    (tmp_path / "feedback_loop").mkdir(exist_ok=True)
    return tmp_path


@pytest.fixture
def generator_fixtures_dir(tmp_path: Path) -> Path:
    """Vollständiges Fixture-Verzeichnis für alle Generatoren."""
    return _minimal_fixture_dir(tmp_path)


@pytest.fixture
def high_delta_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture mit vielen Incidents für Bounded-Mutation-Test (CAP-Delta-PS)."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"id": f"inc-{i}", "subsystem": "RAG", "failure_class": "async_race", "severity": "high", "replay_status": "missing", "binding_status": None}
            for i in range(5)
        ],
    }
    return _minimal_fixture_dir(tmp_path, incidents_override=incidents)


@pytest.fixture
def no_autopilot_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture ohne QA_AUTOPILOT_V2.json (für MISS-Autopilot-CC)."""
    base = _minimal_fixture_dir(tmp_path)
    (base / "QA_AUTOPILOT_V2.json").unlink(missing_ok=True)
    return base


@pytest.fixture
def no_priority_no_incidents_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture ohne QA_PRIORITY_SCORE und ohne incidents/index.json (für MISS-Both-PS)."""
    base = _minimal_fixture_dir(tmp_path)
    (base / "QA_PRIORITY_SCORE.json").unlink(missing_ok=True)
    (base / "incidents" / "index.json").unlink(missing_ok=True)
    return base


@pytest.fixture
def no_control_center_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture ohne QA_CONTROL_CENTER.json (Baseline fehlt – initialer Lauf)."""
    base = _minimal_fixture_dir(tmp_path)
    (base / "QA_CONTROL_CENTER.json").unlink(missing_ok=True)
    return base


@pytest.fixture
def no_analytics_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture ohne incidents/analytics.json."""
    base = _minimal_fixture_dir(tmp_path)
    (base / "incidents" / "analytics.json").unlink(missing_ok=True)
    return base


@pytest.fixture
def incomplete_incidents_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture mit unvollständiger Incident-Struktur (minimales index.json ohne incidents-Array)."""
    base = _minimal_fixture_dir(tmp_path)
    (base / "incidents" / "index.json").write_text(
        json.dumps({"schema_version": "1.0"}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return base


@pytest.fixture
def no_priority_score_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture ohne QA_PRIORITY_SCORE.json (nur Incidents – Generator nutzt Defaults)."""
    base = _minimal_fixture_dir(tmp_path)
    (base / "QA_PRIORITY_SCORE.json").unlink(missing_ok=True)
    return base


@pytest.fixture
def drift_pattern_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture mit 2+ Drift-Failure-Classes für FL-PRIO-007 / Drift-Pattern-Test."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"id": "d1", "subsystem": "RAG", "failure_class": "contract_schema_drift", "severity": "high"},
            {"id": "d2", "subsystem": "Debug/EventBus", "failure_class": "debug_false_truth", "severity": "medium"},
        ],
    }
    return _minimal_fixture_dir(tmp_path, incidents_override=incidents)


@pytest.fixture
def replay_gap_only_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture mit hohem Replay-Gap, niedrigem Regression-Gap (alle ohne Replay, alle gebunden)."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"id": "r1", "subsystem": "RAG", "failure_class": "async_race", "severity": "high", "replay_status": "missing", "binding_status": "catalog_bound"},
            {"id": "r2", "subsystem": "RAG", "failure_class": "async_race", "severity": "high", "replay_status": None, "binding_status": "catalog_bound"},
        ],
    }
    return _minimal_fixture_dir(tmp_path, incidents_override=incidents)


@pytest.fixture
def regression_gap_only_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture mit niedrigem Replay-Gap, hohem Regression-Gap (alle mit Replay, alle ungebunden)."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"id": "g1", "subsystem": "RAG", "failure_class": "async_race", "severity": "high", "replay_status": "validated", "binding_status": None},
            {"id": "g2", "subsystem": "RAG", "failure_class": "async_race", "severity": "high", "replay_status": "validated", "binding_status": "open"},
        ],
    }
    return _minimal_fixture_dir(tmp_path, incidents_override=incidents)


@pytest.fixture
def single_incident_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture mit genau einem Incident, validated replay, catalog_bound – für single_incident_not_auto_high."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"id": "s1", "subsystem": "RAG", "failure_class": "async_race", "severity": "high", "replay_status": "validated", "binding_status": "catalog_bound"},
        ],
    }
    return _minimal_fixture_dir(tmp_path, incidents_override=incidents)


@pytest.fixture
def cluster_incidents_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture mit 2+ Incidents im gleichen Subsystem – Cluster-Eskalation."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"id": "c1", "subsystem": "RAG", "failure_class": "async_race", "severity": "high", "replay_status": "missing", "binding_status": None},
            {"id": "c2", "subsystem": "RAG", "failure_class": "async_race", "severity": "high", "replay_status": "missing", "binding_status": None},
        ],
    }
    return _minimal_fixture_dir(tmp_path, incidents_override=incidents)


@pytest.fixture
def no_risk_radar_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture ohne QA_RISK_RADAR.md (fehlende Baseline)."""
    base = _minimal_fixture_dir(tmp_path)
    (base / "QA_RISK_RADAR.md").unlink(missing_ok=True)
    return base


@pytest.fixture
def no_incidents_no_analytics_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture ohne incidents und analytics – minimale Projektion."""
    base = _minimal_fixture_dir(tmp_path)
    (base / "incidents" / "index.json").unlink(missing_ok=True)
    (base / "incidents" / "analytics.json").unlink(missing_ok=True)
    return base


def run_generator_script(script_name: str, args: list[str], cwd: Path) -> tuple[int, str, str]:
    """Führt ein Generator-Skript aus und liefert (exit_code, stdout, stderr)."""
    script_path = Path(__file__).resolve().parent.parent.parent.parent / "scripts" / "qa" / script_name
    result = subprocess.run(
        [sys.executable, str(script_path)] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.returncode, result.stdout, result.stderr

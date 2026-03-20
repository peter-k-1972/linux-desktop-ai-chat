"""
Pytest Fixtures für QA Autopilot v3 Tests.

Stellt Fixture-Verzeichnisse für Happy Path, Gap Detection, Translation Gaps,
Robustheit und Fehlerfälle bereit.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_SCRIPT_PATH = _PROJECT_ROOT / "scripts" / "qa" / "generate_autopilot_v3.py"


def _base_analytics() -> dict:
    return {"qa_coverage": {"replay_defined_ratio": 0.5, "regression_bound_ratio": 0.3}}


def _base_autopilot() -> dict:
    return {
        "recommended_focus_subsystem": "RAG",
        "recommended_focus_failure_class": "async_race",
        "recommended_next_sprint": "RAG Failure Replay",
        "recommended_guard_type": "failure_replay_guard",
        "recommended_test_domain": "async_behavior",
    }


def _base_priority_score() -> dict:
    return {
        "scores": [
            {"Subsystem": "RAG", "Score": 10, "Prioritaet": "P1", "Begruendung": "", "Naechster_QA_Schritt": "–"},
            {"Subsystem": "Startup/Bootstrap", "Score": 5, "Prioritaet": "P2", "Begruendung": "", "Naechster_QA_Schritt": "–"},
            {"Subsystem": "Chat", "Score": 3, "Prioritaet": "P3", "Begruendung": "", "Naechster_QA_Schritt": "–"},
        ],
    }


def _base_control_center() -> dict:
    return {"naechster_qa_sprint": {"subsystem": "RAG", "schritt": "Replay", "source": "QA_AUTOPILOT_V2"}}


def _write_fixture_dir(
    base: Path,
    incidents: dict,
    analytics: dict | None = None,
    autopilot: dict | None = None,
    priority_score: dict | None = None,
    control_center: dict | None = None,
) -> Path:
    """Schreibt vollständiges Fixture-Verzeichnis."""
    inc_dir = base / "incidents"
    inc_dir.mkdir(parents=True, exist_ok=True)

    (inc_dir / "index.json").write_text(json.dumps(incidents, indent=2, ensure_ascii=False), encoding="utf-8")
    (inc_dir / "analytics.json").write_text(
        json.dumps(analytics or _base_analytics(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (base / "QA_AUTOPILOT_V2.json").write_text(
        json.dumps(autopilot or _base_autopilot(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (base / "QA_PRIORITY_SCORE.json").write_text(
        json.dumps(priority_score or _base_priority_score(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (base / "QA_CONTROL_CENTER.json").write_text(
        json.dumps(control_center or _base_control_center(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return base


@pytest.fixture
def autopilot_v3_fixtures_dir(tmp_path: Path) -> Path:
    """Happy Path: gültige Inputs, alle Dateien vorhanden."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {
                "incident_id": "INC-001",
                "subsystem": "RAG",
                "failure_class": "async_race",
                "severity": "high",
                "replay_status": "missing",
                "binding_status": None,
                "status": "classified",
            },
            {
                "incident_id": "INC-002",
                "subsystem": "RAG",
                "failure_class": "async_race",
                "severity": "medium",
                "replay_status": None,
                "binding_status": None,
                "status": "replay_defined",
            },
        ],
    }
    return _write_fixture_dir(tmp_path, incidents)


@pytest.fixture
def replay_gap_fixtures_dir(tmp_path: Path) -> Path:
    """Test Gap: 2+ Incidents, replay_gap >= 50% => missing_replay_test."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"incident_id": "r1", "subsystem": "RAG", "failure_class": "async_race", "replay_status": "missing", "binding_status": None, "status": "classified"},
            {"incident_id": "r2", "subsystem": "RAG", "failure_class": "async_race", "replay_status": None, "binding_status": "catalog_bound", "status": "closed"},
        ],
    }
    analytics = {"qa_coverage": {"replay_defined_ratio": 0.2, "regression_bound_ratio": 0.5}}
    return _write_fixture_dir(tmp_path, incidents, analytics=analytics)


@pytest.fixture
def regression_gap_fixtures_dir(tmp_path: Path) -> Path:
    """Test Gap: 2+ Incidents, regression_gap >= 30% => missing_regression_test."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"incident_id": "g1", "subsystem": "RAG", "failure_class": "async_race", "replay_status": "validated", "binding_status": None, "status": "replay_verified"},
            {"incident_id": "g2", "subsystem": "RAG", "failure_class": "async_race", "replay_status": "validated", "binding_status": "open", "status": "replay_verified"},
        ],
    }
    analytics = {"qa_coverage": {"replay_defined_ratio": 0.9, "regression_bound_ratio": 0.2}}
    return _write_fixture_dir(tmp_path, incidents, analytics=analytics)


@pytest.fixture
def drift_gap_fixtures_dir(tmp_path: Path) -> Path:
    """Test Gap: 2+ Drift-Incidents => missing_contract_test."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"incident_id": "d1", "subsystem": "Debug/EventBus", "failure_class": "contract_schema_drift", "replay_status": "missing", "binding_status": None, "status": "classified"},
            {"incident_id": "d2", "subsystem": "Debug/EventBus", "failure_class": "contract_schema_drift", "replay_status": None, "binding_status": None, "status": "classified"},
        ],
    }
    return _write_fixture_dir(tmp_path, incidents)


@pytest.fixture
def guard_network_fixtures_dir(tmp_path: Path) -> Path:
    """Guard Gap: 2+ network failure incidents => failure_replay_guard."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"incident_id": "n1", "subsystem": "RAG", "failure_class": "rag_silent_failure", "replay_status": "missing", "binding_status": None, "status": "classified"},
            {"incident_id": "n2", "subsystem": "RAG", "failure_class": "async_race", "replay_status": "missing", "binding_status": None, "status": "classified"},
        ],
    }
    return _write_fixture_dir(tmp_path, incidents)


@pytest.fixture
def guard_event_drift_fixtures_dir(tmp_path: Path) -> Path:
    """Guard Gap: 1+ event/contract drift => event_contract_guard."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"incident_id": "e1", "subsystem": "Chat", "failure_class": "ui_state_drift", "replay_status": "missing", "binding_status": None, "status": "new"},
        ],
    }
    return _write_fixture_dir(tmp_path, incidents)


@pytest.fixture
def guard_startup_fixtures_dir(tmp_path: Path) -> Path:
    """Guard Gap: 1+ startup degradation => startup_degradation_guard."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"incident_id": "s1", "subsystem": "Startup/Bootstrap", "failure_class": "startup_ordering", "replay_status": "missing", "binding_status": None, "status": "classified"},
        ],
    }
    return _write_fixture_dir(tmp_path, incidents)


@pytest.fixture
def translation_no_replay_fixtures_dir(tmp_path: Path) -> Path:
    """Translation Gap: incidents without replay => incident_not_bound_to_replay."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"incident_id": "tr1", "subsystem": "RAG", "failure_class": "async_race", "replay_status": None, "binding_status": None, "status": "classified"},
        ],
    }
    return _write_fixture_dir(tmp_path, incidents)


@pytest.fixture
def translation_no_regression_fixtures_dir(tmp_path: Path) -> Path:
    """Translation Gap: incidents without regression binding => incident_not_bound_to_regression."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"incident_id": "tg1", "subsystem": "RAG", "failure_class": "async_race", "replay_status": "validated", "binding_status": "open", "status": "replay_verified"},
        ],
    }
    return _write_fixture_dir(tmp_path, incidents)


@pytest.fixture
def translation_pilot_fixtures_dir(tmp_path: Path) -> Path:
    """Translation Gap: pilot active but focus not in top 3 => pilot_not_sufficiently_translated."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"incident_id": "p1", "subsystem": "RAG", "failure_class": "async_race", "replay_status": "missing", "binding_status": None, "status": "classified"},
        ],
    }
    autopilot = {
        "recommended_focus_subsystem": "RAG",
        "recommended_focus_failure_class": "async_race",
        "pilot_constellation_matched": {"id": 2, "name": "RAG / ChromaDB network failure"},
    }
    priority_score = {
        "scores": [
            {"Subsystem": "Startup/Bootstrap", "Score": 10, "Prioritaet": "P1", "Begruendung": "", "Naechster_QA_Schritt": "–"},
            {"Subsystem": "Chat", "Score": 8, "Prioritaet": "P2", "Begruendung": "", "Naechster_QA_Schritt": "–"},
            {"Subsystem": "Debug/EventBus", "Score": 5, "Prioritaet": "P3", "Begruendung": "", "Naechster_QA_Schritt": "–"},
        ],
    }
    return _write_fixture_dir(tmp_path, incidents, autopilot=autopilot, priority_score=priority_score)


@pytest.fixture
def missing_incidents_fixtures_dir(tmp_path: Path) -> Path:
    """Fehlerfall: incidents/index.json fehlt (Datei wurde gelöscht)."""
    base = _write_fixture_dir(tmp_path, {"schema_version": "1.0", "incidents": [{"incident_id": "i1", "subsystem": "RAG"}]})
    (base / "incidents" / "index.json").unlink(missing_ok=True)
    return base


@pytest.fixture
def missing_analytics_fixtures_dir(tmp_path: Path) -> Path:
    """Fehlerfall: incidents/analytics.json fehlt."""
    base = _write_fixture_dir(tmp_path, {"schema_version": "1.0", "incidents": [{"incident_id": "i1", "subsystem": "RAG", "failure_class": "async_race"}]})
    (base / "incidents" / "analytics.json").unlink(missing_ok=True)
    return base


@pytest.fixture
def missing_autopilot_fixtures_dir(tmp_path: Path) -> Path:
    """Fehlerfall: QA_AUTOPILOT_V2.json fehlt (Release-Blocker)."""
    base = _write_fixture_dir(tmp_path, {"schema_version": "1.0", "incidents": [{"incident_id": "i1", "subsystem": "RAG"}]})
    (base / "QA_AUTOPILOT_V2.json").unlink(missing_ok=True)
    return base


@pytest.fixture
def empty_json_incidents_fixtures_dir(tmp_path: Path) -> Path:
    """Fehlerfall: incidents/index.json ist leeres JSON {}."""
    base = _write_fixture_dir(tmp_path, {"schema_version": "1.0", "incidents": []})
    (base / "incidents" / "index.json").write_text("{}", encoding="utf-8")
    return base


@pytest.fixture
def invalid_json_incidents_fixtures_dir(tmp_path: Path) -> Path:
    """Fehlerfall: incidents/index.json ist ungültiges JSON."""
    base = _write_fixture_dir(tmp_path, {"schema_version": "1.0", "incidents": []})
    (base / "incidents" / "index.json").write_text("{invalid json}", encoding="utf-8")
    return base


@pytest.fixture
def unknown_subsystem_fixtures_dir(tmp_path: Path) -> Path:
    """Robustheit: unbekanntes subsystem (sollte nicht crashen)."""
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"incident_id": "u1", "subsystem": "UnknownSubsystem", "failure_class": "async_race", "replay_status": "missing", "binding_status": None, "status": "classified"},
        ],
    }
    return _write_fixture_dir(tmp_path, incidents)


@pytest.fixture
def invalid_priority_score_fixtures_dir(tmp_path: Path) -> Path:
    """Robustheit: QA_PRIORITY_SCORE mit ungültigem Score (sollte nicht crashen)."""
    incidents = {"schema_version": "1.0", "incidents": [{"incident_id": "i1", "subsystem": "RAG", "failure_class": "async_race"}]}
    priority_score = {
        "scores": [
            {"Subsystem": "RAG", "Score": "high", "Prioritaet": "P1", "Begruendung": "", "Naechster_QA_Schritt": "–"},
            {"Subsystem": "Chat", "Score": "", "Prioritaet": "P2", "Begruendung": "", "Naechster_QA_Schritt": "–"},
        ],
    }
    return _write_fixture_dir(tmp_path, incidents, priority_score=priority_score)


def run_autopilot_v3(args: list[str], cwd: Path) -> tuple[int, str, str]:
    """Führt generate_autopilot_v3.py aus und liefert (exit_code, stdout, stderr)."""
    result = subprocess.run(
        [sys.executable, str(_SCRIPT_PATH)] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.returncode, result.stdout, result.stderr

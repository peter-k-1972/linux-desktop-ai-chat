"""
Pytest Fixtures für QA Feedback Loop Tests.

Stellt Fixture-Verzeichnisse, minimale JSON-Strukturen und FeedbackLoopInputs bereit.
Alle Tests nutzen tmp_path – keine Abhängigkeit von docs/qa.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from scripts.qa.feedback_loop import (
    FeedbackLoopInputs,
    load_feedback_inputs_from_paths,
    run_feedback_projections,
)


# --- Minimale gültige JSON-Strukturen ---

MINIMAL_INCIDENT_INDEX = {
    "schema_version": "1.0",
    "incidents": [
        {
            "id": "inc-001",
            "subsystem": "RAG",
            "failure_class": "async_race",
            "severity": "high",
            "replay_status": "missing",
            "binding_status": None,
        },
        {
            "id": "inc-002",
            "subsystem": "RAG",
            "failure_class": "async_race",
            "severity": "medium",
            "replay_status": "validated",
            "binding_status": "catalog_bound",
        },
    ],
}

MINIMAL_ANALYTICS = {
    "qa_coverage": {
        "replay_defined_ratio": 0.6,
        "regression_bound_ratio": 0.4,
    },
}

MINIMAL_AUTOPILOT = {
    "recommended_focus_subsystem": "RAG",
    "recommended_focus_failure_class": "async_race",
    "recommended_next_sprint": "RAG Failure Replay",
    "recommended_guard_type": "failure_replay_guard",
    "recommended_test_domain": "async_behavior",
}

MINIMAL_PRIORITY_SCORE = {
    "scores": [
        {"Subsystem": "RAG", "Score": 2, "Prioritaet": "P2", "Begruendung": "", "Naechster_QA_Schritt": "–"},
        {"Subsystem": "Startup/Bootstrap", "Score": 1, "Prioritaet": "P3", "Begruendung": "", "Naechster_QA_Schritt": "–"},
    ],
}

MINIMAL_CONTROL_CENTER = {
    "naechster_qa_sprint": {"subsystem": "RAG", "schritt": "Replay", "source": "QA_AUTOPILOT_V2"},
}

RISK_RADAR_MD = """# QA Risk Radar

| Subsystem | Priorität |
|-----------|-----------|
| RAG | P1 |
| Startup/Bootstrap | P2 |
| Debug/EventBus | P3 |
"""


@pytest.fixture
def feedback_loop_fixtures_dir(tmp_path: Path) -> Path:
    """Erstellt ein Fixture-Verzeichnis mit minimalen gültigen Dateien."""
    inc_dir = tmp_path / "incidents"
    inc_dir.mkdir(parents=True)

    (inc_dir / "index.json").write_text(
        json.dumps(MINIMAL_INCIDENT_INDEX, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (inc_dir / "analytics.json").write_text(
        json.dumps(MINIMAL_ANALYTICS, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (tmp_path / "QA_AUTOPILOT_V2.json").write_text(
        json.dumps(MINIMAL_AUTOPILOT, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (tmp_path / "QA_PRIORITY_SCORE.json").write_text(
        json.dumps(MINIMAL_PRIORITY_SCORE, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (tmp_path / "QA_CONTROL_CENTER.json").write_text(
        json.dumps(MINIMAL_CONTROL_CENTER, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (tmp_path / "QA_RISK_RADAR.md").write_text(RISK_RADAR_MD, encoding="utf-8")

    return tmp_path


@pytest.fixture
def feedback_loop_inputs(feedback_loop_fixtures_dir: Path) -> FeedbackLoopInputs:
    """Geladene FeedbackLoopInputs aus dem Fixture-Verzeichnis."""
    inc_dir = feedback_loop_fixtures_dir / "incidents"
    return load_feedback_inputs_from_paths(
        incident_index_path=inc_dir / "index.json",
        analytics_path=inc_dir / "analytics.json",
        autopilot_path=feedback_loop_fixtures_dir / "QA_AUTOPILOT_V2.json",
        control_center_path=feedback_loop_fixtures_dir / "QA_CONTROL_CENTER.json",
        priority_score_path=feedback_loop_fixtures_dir / "QA_PRIORITY_SCORE.json",
    )


@pytest.fixture
def feedback_loop_report(feedback_loop_inputs: FeedbackLoopInputs) -> object:
    """FeedbackProjectionReport mit deterministischem Timestamp."""
    return run_feedback_projections(
        feedback_loop_inputs,
        optional_timestamp="2025-01-15T12:00:00Z",
    )


@pytest.fixture
def empty_incidents_index(tmp_path: Path) -> Path:
    """index.json mit leeren Incidents."""
    inc_dir = tmp_path / "incidents"
    inc_dir.mkdir(parents=True)
    data = {"schema_version": "1.0", "incidents": []}
    (inc_dir / "index.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return inc_dir / "index.json"


@pytest.fixture
def drift_incidents_index(tmp_path: Path) -> Path:
    """index.json mit Drift-Failure-Classes (contract_schema_drift, debug_false_truth)."""
    inc_dir = tmp_path / "incidents"
    inc_dir.mkdir(parents=True)
    data = {
        "schema_version": "1.0",
        "incidents": [
            {"id": "d1", "subsystem": "RAG", "failure_class": "contract_schema_drift", "severity": "high"},
            {"id": "d2", "subsystem": "Debug/EventBus", "failure_class": "debug_false_truth", "severity": "medium"},
        ],
    }
    (inc_dir / "index.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return inc_dir / "index.json"


@pytest.fixture
def high_delta_incidents_index(tmp_path: Path) -> Path:
    """index.json mit vielen Incidents für Bounded-Mutation-Test (raw_delta > 10)."""
    inc_dir = tmp_path / "incidents"
    inc_dir.mkdir(parents=True)
    incidents = [
        {
            "id": f"inc-{i}",
            "subsystem": "RAG",
            "failure_class": "async_race",
            "severity": "high",
            "replay_status": "missing",
            "binding_status": None,
        }
        for i in range(5)
    ]
    data = {"schema_version": "1.0", "incidents": incidents}
    (inc_dir / "index.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return inc_dir / "index.json"


@pytest.fixture
def pilot_matched_autopilot(tmp_path: Path) -> Path:
    """QA_AUTOPILOT_V2.json mit pilot_constellation_matched."""
    data = {
        **MINIMAL_AUTOPILOT,
        "pilot_constellation_matched": {"id": 2, "name": "RAG / ChromaDB network failure"},
    }
    p = tmp_path / "QA_AUTOPILOT_V2.json"
    tmp_path.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return p


# --- Acceptance Test Fixtures (QA_FEEDBACK_LOOP_ACCEPTANCE_CHECKLIST) ---

ACCEPTANCE_TIMESTAMP = "2026-01-01T00:00:00Z"
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_STATIC_FIXTURES = _PROJECT_ROOT / "tests" / "fixtures" / "feedback_loop"


def run_generator_script(script_name: str, args: list[str], cwd: Path) -> tuple[int, str, str]:
    """Führt ein Generator-Skript aus und liefert (exit_code, stdout, stderr)."""
    script_path = _PROJECT_ROOT / "scripts" / "qa" / script_name
    result = subprocess.run(
        [sys.executable, str(script_path)] + args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.returncode, result.stdout, result.stderr


def _copy_static_fixtures(tmp_path: Path) -> Path:
    """Kopiert tests/fixtures/feedback_loop/ nach tmp_path."""
    if _STATIC_FIXTURES.exists():
        shutil.copytree(_STATIC_FIXTURES, tmp_path, dirs_exist_ok=True)
    else:
        # Fallback: build from conftest templates
        inc_dir = tmp_path / "incidents"
        inc_dir.mkdir(parents=True)
        (inc_dir / "index.json").write_text(
            json.dumps(MINIMAL_INCIDENT_INDEX, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (inc_dir / "analytics.json").write_text(
            json.dumps(MINIMAL_ANALYTICS, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (tmp_path / "QA_AUTOPILOT_V2.json").write_text(
            json.dumps(MINIMAL_AUTOPILOT, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (tmp_path / "QA_PRIORITY_SCORE.json").write_text(
            json.dumps(MINIMAL_PRIORITY_SCORE, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (tmp_path / "QA_CONTROL_CENTER.json").write_text(
            json.dumps(MINIMAL_CONTROL_CENTER, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        (tmp_path / "QA_RISK_RADAR.md").write_text(RISK_RADAR_MD, encoding="utf-8")
    (tmp_path / "feedback_loop").mkdir(exist_ok=True)
    return tmp_path


@pytest.fixture
def acceptance_fixtures_dir(tmp_path: Path) -> Path:
    """Vollständiges Fixture-Verzeichnis für Acceptance Tests (Happy Path)."""
    return _copy_static_fixtures(tmp_path)


@pytest.fixture
def no_autopilot_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture ohne QA_AUTOPILOT_V2.json (MISS-Autopilot-CC)."""
    base = _copy_static_fixtures(tmp_path)
    (base / "QA_AUTOPILOT_V2.json").unlink(missing_ok=True)
    return base


@pytest.fixture
def no_priority_no_incidents_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture ohne QA_PRIORITY_SCORE und ohne incidents/index.json (MISS-Both-PS)."""
    base = _copy_static_fixtures(tmp_path)
    (base / "QA_PRIORITY_SCORE.json").unlink(missing_ok=True)
    (base / "incidents" / "index.json").unlink(missing_ok=True)
    return base


@pytest.fixture
def cap_delta_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture für CAP-Delta-PS: raw_delta > 10 (viele Incidents + Gaps + Autopilot-Focus)."""
    base = _copy_static_fixtures(tmp_path)
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {
                "id": f"inc-{i}",
                "subsystem": "RAG",
                "failure_class": "async_race",
                "severity": "high",
                "replay_status": "missing",
                "binding_status": None,
            }
            for i in range(8)
        ],
    }
    (base / "incidents" / "index.json").write_text(
        json.dumps(incidents, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    # Niedriger alter Score -> großer Delta
    priority = {"scores": [{"Subsystem": "RAG", "Score": 1, "Prioritaet": "P3", "Begruendung": "", "Naechster_QA_Schritt": "–"}]}
    (base / "QA_PRIORITY_SCORE.json").write_text(
        json.dumps(priority, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return base


@pytest.fixture
def bounded_esc_fixtures_dir(tmp_path: Path) -> Path:
    """Fixture für BND-Esc-RR: old_level=low (P3), 3+ Incidents, hohe Gaps."""
    base = _copy_static_fixtures(tmp_path)
    incidents = {
        "schema_version": "1.0",
        "incidents": [
            {"id": f"b{i}", "subsystem": "RAG", "failure_class": "async_race", "severity": "high", "replay_status": "missing", "binding_status": None}
            for i in range(4)
        ],
    }
    (base / "incidents" / "index.json").write_text(
        json.dumps(incidents, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    # RAG mit P3 (low) als Baseline
    (base / "QA_RISK_RADAR.md").write_text(
        "# Risk Radar\n\n| Subsystem | Priorität |\n|-----------|----------|\n| RAG | P3 |\n",
        encoding="utf-8",
    )
    return base

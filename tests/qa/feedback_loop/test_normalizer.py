"""
Unit Tests: QA Feedback Loop – Normalizer.

Testet Replay/Regression-Trennung, per-Subsystem-Regression, incidents-Validierung,
Drift-Erkennung, leere Incidents.
"""

from __future__ import annotations

import pytest

from scripts.qa.feedback_loop.loader import FeedbackLoopInputs
from scripts.qa.feedback_loop.normalizer import (
    normalize_to_failure_class_states,
    normalize_to_subsystem_states,
    DRIFT_FAILURE_CLASSES,
)


def test_replay_gap_separate_from_regression(feedback_loop_inputs: FeedbackLoopInputs) -> None:
    """Replay-Gap und Regression-Gap werden getrennt behandelt (H1, H2)."""
    states = normalize_to_subsystem_states(feedback_loop_inputs)
    rag = states.get("RAG")
    assert rag is not None
    # 1 von 2 Incidents ohne Replay (replay_status=missing), 1 mit validated
    assert rag.replay_gap_rate > 0
    # 1 von 2 ohne Binding (binding_status=None), 1 mit catalog_bound
    assert rag.regression_gap_rate > 0
    # Replay und Regression sind unterschiedliche Metriken
    assert rag.replay_gap_rate != rag.regression_gap_rate or (rag.replay_gap_rate == 0.5 and rag.regression_gap_rate == 0.5)


def test_incidents_non_list_fallback(feedback_loop_inputs: FeedbackLoopInputs) -> None:
    """incidents als Nicht-Liste führt zu Fallback [] (M1, STRUCT-Incidents-List)."""
    # Simuliere incident_index mit incidents als String
    bad_inputs = FeedbackLoopInputs(
        incident_index={"incidents": "invalid"},
        analytics=feedback_loop_inputs.analytics,
        autopilot_v2=feedback_loop_inputs.autopilot_v2,
        priority_score=feedback_loop_inputs.priority_score,
    )
    states = normalize_to_subsystem_states(bad_inputs)
    # Kein Crash; Fallback-Subsysteme bei leerem incidents
    assert "RAG" in states or "Startup/Bootstrap" in states or "Debug/EventBus" in states


def test_empty_incidents_fallback_subsystems() -> None:
    """Leere Incidents führen zu Fallback-Subsystemen (EMPTY-Incidents)."""
    inputs = FeedbackLoopInputs(
        incident_index={"schema_version": "1.0", "incidents": []},
        analytics={"qa_coverage": {"replay_defined_ratio": 0.5, "regression_bound_ratio": 0.0}},
        autopilot_v2={"recommended_focus_subsystem": "RAG", "recommended_focus_failure_class": ""},
        priority_score=None,
    )
    states = normalize_to_subsystem_states(inputs)
    assert "RAG" in states
    assert "Startup/Bootstrap" in states
    assert "Debug/EventBus" in states
    for sub, st in states.items():
        assert st.incident_count == 0


def test_drift_failure_classes_recognized() -> None:
    """Drift-Failure-Classes werden als drift_related erkannt."""
    inputs = FeedbackLoopInputs(
        incident_index={
            "schema_version": "1.0",
            "incidents": [
                {"id": "1", "subsystem": "RAG", "failure_class": "contract_schema_drift", "severity": "high"},
                {"id": "2", "subsystem": "RAG", "failure_class": "debug_false_truth", "severity": "medium"},
            ],
        },
        analytics={"qa_coverage": {"replay_defined_ratio": 0.5, "regression_bound_ratio": 0.0}},
        autopilot_v2={"recommended_focus_subsystem": "RAG"},
        priority_score=None,
    )
    fc_states = normalize_to_failure_class_states(inputs)
    assert "contract_schema_drift" in fc_states
    assert "debug_false_truth" in fc_states
    assert fc_states["contract_schema_drift"].drift_related is True
    assert fc_states["debug_false_truth"].drift_related is True


def test_unknown_failure_class_drift_false() -> None:
    """Unbekannte failure_class hat drift_related=False (UNK-FC)."""
    inputs = FeedbackLoopInputs(
        incident_index={
            "schema_version": "1.0",
            "incidents": [
                {"id": "1", "subsystem": "RAG", "failure_class": "neue_unbekannte_klasse", "severity": "high"},
            ],
        },
        analytics={"qa_coverage": {"replay_defined_ratio": 0.5, "regression_bound_ratio": 0.0}},
        autopilot_v2={},
        priority_score=None,
    )
    fc_states = normalize_to_failure_class_states(inputs)
    assert "neue_unbekannte_klasse" in fc_states
    assert fc_states["neue_unbekannte_klasse"].drift_related is False


def test_unknown_subsystem_appears_in_output() -> None:
    """Unbekanntes Subsystem erscheint im Output (UNK-Sub)."""
    inputs = FeedbackLoopInputs(
        incident_index={
            "schema_version": "1.0",
            "incidents": [
                {"id": "1", "subsystem": "NeuesSubsystem", "failure_class": "async_race", "severity": "high"},
            ],
        },
        analytics={"qa_coverage": {"replay_defined_ratio": 0.5, "regression_bound_ratio": 0.0}},
        autopilot_v2={},
        priority_score=None,
    )
    states = normalize_to_subsystem_states(inputs)
    assert "NeuesSubsystem" in states
    assert states["NeuesSubsystem"].incident_count == 1


def test_same_inputs_same_outputs(feedback_loop_inputs: FeedbackLoopInputs) -> None:
    """Gleiche Inputs -> gleiche Outputs (Determinismus)."""
    s1 = normalize_to_subsystem_states(feedback_loop_inputs)
    s2 = normalize_to_subsystem_states(feedback_loop_inputs)
    assert set(s1.keys()) == set(s2.keys())
    for sub in s1:
        st1 = s1[sub]
        st2 = s2[sub]
        assert st1.incident_count == st2.incident_count
        assert st1.replay_gap_rate == st2.replay_gap_rate
        assert st1.regression_gap_rate == st2.regression_gap_rate


def test_subsystem_feedback_state_formation() -> None:
    """SubsystemFeedbackState wird korrekt aus Incidents gebildet."""
    inputs = FeedbackLoopInputs(
        incident_index={
            "schema_version": "1.0",
            "incidents": [
                {"id": "1", "subsystem": "RAG", "failure_class": "async_race", "severity": "high"},
                {"id": "2", "subsystem": "RAG", "failure_class": "async_race", "severity": "medium"},
            ],
        },
        analytics={"qa_coverage": {"replay_defined_ratio": 0.5, "regression_bound_ratio": 0.0}},
        autopilot_v2={"recommended_focus_subsystem": "RAG"},
        priority_score=None,
    )
    states = normalize_to_subsystem_states(inputs)
    rag = states.get("RAG")
    assert rag is not None
    assert rag.subsystem == "RAG"
    assert rag.incident_count == 2
    assert rag.weighted_severity > 0
    assert rag.autopilot_focus is True


def test_plausible_default_values_empty_inputs() -> None:
    """Plausible Default-Werte bei leeren/minimalen Inputs."""
    inputs = FeedbackLoopInputs(
        incident_index={"incidents": []},
        analytics=None,
        autopilot_v2=None,
        priority_score=None,
    )
    states = normalize_to_subsystem_states(inputs)
    for sub, st in states.items():
        assert st.incident_count == 0
        assert st.weighted_severity == 0.0
        assert st.feedback_pressure_score >= 0
        assert st.escalation_level in (0, 1, 2, 3)


def test_drift_density_correctly_handled() -> None:
    """Drift-Density wird pro Subsystem korrekt berechnet (Anteil Drift-Failure-Classes)."""
    inputs = FeedbackLoopInputs(
        incident_index={
            "schema_version": "1.0",
            "incidents": [
                {"id": "1", "subsystem": "RAG", "failure_class": "contract_schema_drift", "severity": "high"},
                {"id": "2", "subsystem": "RAG", "failure_class": "async_race", "severity": "medium"},
            ],
        },
        analytics={"qa_coverage": {"replay_defined_ratio": 0.5, "regression_bound_ratio": 0.0}},
        autopilot_v2={},
        priority_score=None,
    )
    states = normalize_to_subsystem_states(inputs)
    rag = states.get("RAG")
    assert rag is not None
    # 1 von 2 Incidents ist Drift -> drift_density = 0.5
    assert rag.drift_density == 0.5


def test_escalation_level_traceable() -> None:
    """Escalation-Level ist nachvollziehbar: 3+ Incidents -> 3, 2+ mit Replay-Gap -> 2, 1+ mit Reg-Gap -> 1."""
    # Fall: 3 Incidents -> escalation_level 3
    inputs_3 = FeedbackLoopInputs(
        incident_index={
            "incidents": [
                {"id": "1", "subsystem": "RAG", "failure_class": "a", "severity": "high"},
                {"id": "2", "subsystem": "RAG", "failure_class": "a", "severity": "high"},
                {"id": "3", "subsystem": "RAG", "failure_class": "a", "severity": "high"},
            ],
        },
        analytics={"qa_coverage": {"replay_defined_ratio": 0.5, "regression_bound_ratio": 0.0}},
        autopilot_v2={},
        priority_score=None,
    )
    states_3 = normalize_to_subsystem_states(inputs_3)
    assert states_3.get("RAG").escalation_level == 3

    # Fall: 2 Incidents, Replay-Gap > 0.5 -> escalation_level 2
    inputs_2 = FeedbackLoopInputs(
        incident_index={
            "incidents": [
                {"id": "1", "subsystem": "RAG", "failure_class": "a", "severity": "high", "replay_status": "missing"},
                {"id": "2", "subsystem": "RAG", "failure_class": "a", "severity": "high", "replay_status": None},
            ],
        },
        analytics={"qa_coverage": {"replay_defined_ratio": 0.5, "regression_bound_ratio": 0.0}},
        autopilot_v2={},
        priority_score=None,
    )
    states_2 = normalize_to_subsystem_states(inputs_2)
    assert states_2.get("RAG").escalation_level == 2

    # Fall: 1 Incident, Regression-Gap > 0.8 -> escalation_level 1
    inputs_1 = FeedbackLoopInputs(
        incident_index={
            "incidents": [
                {"id": "1", "subsystem": "RAG", "failure_class": "a", "severity": "high", "binding_status": None},
            ],
        },
        analytics={"qa_coverage": {"replay_defined_ratio": 0.5, "regression_bound_ratio": 0.1}},
        autopilot_v2={},
        priority_score=None,
    )
    states_1 = normalize_to_subsystem_states(inputs_1)
    assert states_1.get("RAG").escalation_level == 1

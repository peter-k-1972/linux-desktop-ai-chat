"""
QA Autopilot v3 – Unit-Tests für Rules (insbesondere _safe_score).

Testet apply_gap_rules direkt mit gemockten Inputs, um _safe_score bei ungültigen
Score-Werten zu verifizieren, ohne den Feedback-Loop zu durchlaufen.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from scripts.qa.autopilot_v3.rules import apply_gap_rules


def _make_subsystem_state(incident_count: int = 0, **kwargs: object) -> MagicMock:
    """Erstellt Mock SubsystemFeedbackState."""
    state = MagicMock()
    state.incident_count = incident_count
    state.replay_gap_rate = kwargs.get("replay_gap_rate", 0.0)
    state.regression_gap_rate = kwargs.get("regression_gap_rate", 0.0)
    state.drift_density = kwargs.get("drift_density", 0.0)
    return state


def _make_failure_class_state(incident_count: int = 0) -> MagicMock:
    """Erstellt Mock FailureClassFeedbackState."""
    state = MagicMock()
    state.incident_count = incident_count
    return state


def test_safe_score_with_invalid_priority_score_no_crash() -> None:
    """Rules: priority_score mit ungültigen Score-Werten (str, leer) crasht nicht."""
    subsystem_states = {"RAG": _make_subsystem_state(1, replay_gap_rate=0.6, regression_gap_rate=0.4)}
    failure_class_states = {"async_race": _make_failure_class_state(1)}
    incidents = [{"incident_id": "i1", "subsystem": "RAG", "failure_class": "async_race", "replay_status": "missing", "binding_status": None, "status": "classified"}]
    autopilot = {
        "recommended_focus_subsystem": "RAG",
        "recommended_focus_failure_class": "async_race",
        "pilot_constellation_matched": {"id": 2, "name": "RAG"},
    }
    priority_score = {
        "scores": [
            {"Subsystem": "RAG", "Score": "high", "Prioritaet": "P1"},
            {"Subsystem": "Chat", "Score": "", "Prioritaet": "P2"},
            {"Subsystem": "Startup/Bootstrap", "Score": None, "Prioritaet": "P3"},
        ],
    }

    test_gaps, guard_gaps, translation_gaps = apply_gap_rules(
        subsystem_states,
        failure_class_states,
        incidents,
        autopilot,
        priority_score,
    )

    assert isinstance(test_gaps, list)
    assert isinstance(guard_gaps, list)
    assert isinstance(translation_gaps, list)

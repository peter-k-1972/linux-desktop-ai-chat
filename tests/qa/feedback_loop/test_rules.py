"""
Unit Tests: QA Feedback Loop – Regeln und Projektionen.

Testet Rule-IDs, bounded mutation (0–10), max_delta pro Subsystem,
wiederholte Drift-Signale eskalieren strukturell.
"""

from __future__ import annotations

import pytest

from scripts.qa.feedback_loop.loader import FeedbackLoopInputs
from scripts.qa.feedback_loop.models import (
    FailureClassFeedbackState,
    SubsystemFeedbackState,
    FL_PRIO_001,
    FL_PRIO_002,
    FL_RISK_001,
    FL_RISK_005,
)
from scripts.qa.feedback_loop.normalizer import (
    normalize_to_failure_class_states,
    normalize_to_subsystem_states,
)
from scripts.qa.feedback_loop.rules import (
    apply_priority_rules,
    apply_risk_rules,
)


def _make_subsystem_state(
    subsystem: str,
    incident_count: int = 0,
    replay_gap_rate: float = 0.0,
    regression_gap_rate: float = 0.0,
    drift_density: float = 0.0,
    autopilot_focus: bool = False,
    dependency_weight: float = 1.0,
) -> SubsystemFeedbackState:
    return SubsystemFeedbackState(
        subsystem=subsystem,
        incident_count=incident_count,
        weighted_severity=incident_count * 2.0,
        replay_gap_rate=replay_gap_rate,
        regression_gap_rate=regression_gap_rate,
        drift_density=drift_density,
        cluster_density=0.0,
        autopilot_focus=autopilot_focus,
        dependency_weight=dependency_weight,
        feedback_pressure_score=1.0,
        escalation_level=0,
    )


def test_rule_ids_correctly_assigned() -> None:
    """Rule-IDs werden korrekt den FeedbackRuleResults zugeordnet."""
    subsystem_states = {
        "RAG": _make_subsystem_state("RAG", incident_count=3, replay_gap_rate=0.6),
    }
    failure_class_states = {"async_race": FailureClassFeedbackState(
        failure_class="async_race",
        incident_count=3,
        subsystem_count=1,
        weighted_severity=6.0,
        replay_gap_rate=0.0,
        regression_gap_rate=0.0,
        drift_related=False,
        feedback_pressure_score=1.0,
        escalation_level=0,
    )}
    current_priority = {"RAG": 0}

    results = apply_priority_rules(
        subsystem_states,
        failure_class_states,
        autopilot_focus_subsystem="",
        autopilot_focus_failure_class="",
        current_priority_scores=current_priority,
    )
    rule_ids = [r_id for r in results for r_id in r.applied_rule_ids]
    assert FL_PRIO_001 in rule_ids
    assert FL_PRIO_002 in rule_ids


def test_bounded_mutation_score_capped_0_to_10() -> None:
    """Bounded mutation: new_value wird auf [0, 10] begrenzt."""
    subsystem_states = {
        "RAG": _make_subsystem_state("RAG", incident_count=5, replay_gap_rate=0.6, regression_gap_rate=0.4),
    }
    failure_class_states: dict[str, FailureClassFeedbackState] = {}
    current_priority = {"RAG": 9}

    results = apply_priority_rules(
        subsystem_states,
        failure_class_states,
        autopilot_focus_subsystem="",
        autopilot_focus_failure_class="",
        current_priority_scores=current_priority,
    )
    for r in results:
        if r.target_artifact == "QA_PRIORITY_SCORE" and "Score" in r.target_key:
            assert 0 <= r.new_value <= 10, f"new_value {r.new_value} außerhalb [0, 10]"


def test_max_delta_per_run_respected_via_cap() -> None:
    """Score-Delta führt zu max 10 als new_value (Regel begrenzt explizit)."""
    subsystem_states = {
        "RAG": _make_subsystem_state("RAG", incident_count=5, autopilot_focus=True),
    }
    failure_class_states: dict[str, FailureClassFeedbackState] = {}
    current_priority = {"RAG": 0}

    results = apply_priority_rules(
        subsystem_states,
        failure_class_states,
        autopilot_focus_subsystem="RAG",
        autopilot_focus_failure_class="",
        current_priority_scores=current_priority,
    )
    for r in results:
        if r.target_artifact == "QA_PRIORITY_SCORE":
            assert r.new_value <= 10


def test_single_incident_no_auto_high_priority() -> None:
    """Einzelner Incident ohne weitere Signale führt nicht zu hoher Prioritätserhöhung."""
    subsystem_states = {
        "RAG": _make_subsystem_state("RAG", incident_count=1, replay_gap_rate=0.3, regression_gap_rate=0.2),
    }
    failure_class_states: dict[str, FailureClassFeedbackState] = {}
    current_priority = {"RAG": 0}

    results = apply_priority_rules(
        subsystem_states,
        failure_class_states,
        autopilot_focus_subsystem="",
        autopilot_focus_failure_class="",
        current_priority_scores=current_priority,
    )
    prio_results = [r for r in results if r.target_artifact == "QA_PRIORITY_SCORE"]
    assert len(prio_results) <= 1
    for r in prio_results:
        assert r.new_value <= 2


def test_repeated_drift_signals_escalate_structurally() -> None:
    """Wiederholte Drift-Signale (2+ drift-related failure classes) eskalieren strukturell (FL-RISK-005)."""
    inputs = FeedbackLoopInputs(
        incident_index={
            "schema_version": "1.0",
            "incidents": [
                {"id": "1", "subsystem": "RAG", "failure_class": "contract_schema_drift", "severity": "high"},
                {"id": "2", "subsystem": "Debug/EventBus", "failure_class": "debug_false_truth", "severity": "medium"},
            ],
        },
        analytics={"qa_coverage": {"replay_defined_ratio": 0.5, "regression_bound_ratio": 0.0}},
        autopilot_v2={},
        priority_score=None,
    )
    subsystem_states = normalize_to_subsystem_states(inputs)
    failure_class_states = normalize_to_failure_class_states(inputs)

    risk_results = apply_risk_rules(subsystem_states, failure_class_states)
    drift_structural = [r for r in risk_results if "structural.drift_risk" in r.target_key]
    assert len(drift_structural) >= 1
    assert any(FL_RISK_005 in r.applied_rule_ids for r in drift_structural)


def test_repeated_drift_priority_rule_fl_prio_007() -> None:
    """FL-PRIO-007: Wiederholte Drift-Pattern erhöhen contract_priority für Subsysteme mit drift_density > 0."""
    subsystem_states = {
        "RAG": _make_subsystem_state("RAG", incident_count=1, drift_density=0.5),
    }
    failure_class_states = {
        "contract_schema_drift": FailureClassFeedbackState(
            failure_class="contract_schema_drift",
            incident_count=1,
            subsystem_count=1,
            weighted_severity=2.0,
            replay_gap_rate=0.0,
            regression_gap_rate=0.0,
            drift_related=True,
            feedback_pressure_score=1.0,
            escalation_level=0,
        ),
        "debug_false_truth": FailureClassFeedbackState(
            failure_class="debug_false_truth",
            incident_count=1,
            subsystem_count=1,
            weighted_severity=2.0,
            replay_gap_rate=0.0,
            regression_gap_rate=0.0,
            drift_related=True,
            feedback_pressure_score=1.0,
            escalation_level=0,
        ),
    }
    current_priority = {"RAG": 0}

    results = apply_priority_rules(
        subsystem_states,
        failure_class_states,
        autopilot_focus_subsystem="",
        autopilot_focus_failure_class="",
        current_priority_scores=current_priority,
    )
    contract_prio = [r for r in results if "contract_priority" in r.target_key]
    assert len(contract_prio) >= 1
    assert any("FL-PRIO-007" in r.applied_rule_ids for r in contract_prio)


def test_risk_rule_fl_risk_001_incident_cluster() -> None:
    """FL-RISK-001: Incident-Cluster (>=2) erzeugt cluster_risk."""
    subsystem_states = {
        "RAG": _make_subsystem_state("RAG", incident_count=2),
    }
    failure_class_states: dict[str, FailureClassFeedbackState] = {}

    results = apply_risk_rules(subsystem_states, failure_class_states)
    cluster_risk = [r for r in results if "cluster_risk" in r.target_key]
    assert len(cluster_risk) >= 1
    assert any(FL_RISK_001 in r.applied_rule_ids for r in cluster_risk)

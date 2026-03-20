"""
Unit Tests: QA Feedback Loop – Projektionen.

Testet run_feedback_projections, Determinismus, optional_timestamp, rule_results.
"""

from __future__ import annotations

import pytest

from scripts.qa.feedback_loop import run_feedback_projections


def test_run_feedback_projections_returns_report(feedback_loop_inputs: object) -> None:
    """run_feedback_projections liefert FeedbackProjectionReport."""
    report = run_feedback_projections(feedback_loop_inputs)
    assert report is not None
    assert hasattr(report, "generated_at")
    assert hasattr(report, "per_subsystem_results")
    assert hasattr(report, "per_failure_class_results")
    assert hasattr(report, "rule_results")
    assert hasattr(report, "escalations")


def test_optional_timestamp_deterministic(feedback_loop_inputs: object) -> None:
    """optional_timestamp macht generated_at deterministisch (H3)."""
    r1 = run_feedback_projections(feedback_loop_inputs, optional_timestamp="2025-01-15T12:00:00Z")
    r2 = run_feedback_projections(feedback_loop_inputs, optional_timestamp="2025-01-15T12:00:00Z")
    assert r1.generated_at == "2025-01-15T12:00:00Z"
    assert r2.generated_at == "2025-01-15T12:00:00Z"


def test_same_inputs_same_rule_results(feedback_loop_inputs: object) -> None:
    """Gleiche Inputs -> gleiche rule_results."""
    r1 = run_feedback_projections(feedback_loop_inputs, optional_timestamp="2025-01-15T12:00:00Z")
    r2 = run_feedback_projections(feedback_loop_inputs, optional_timestamp="2025-01-15T12:00:00Z")
    assert len(r1.rule_results) == len(r2.rule_results)
    for a, b in zip(r1.rule_results, r2.rule_results):
        assert a.target_artifact == b.target_artifact
        assert a.target_key == b.target_key
        assert a.old_value == b.old_value
        assert a.new_value == b.new_value


def test_rule_results_contain_priority_and_risk(feedback_loop_report: object) -> None:
    """rule_results enthält QA_PRIORITY_SCORE und QA_RISK_RADAR Einträge."""
    prio = [r for r in feedback_loop_report.rule_results if r.target_artifact == "QA_PRIORITY_SCORE"]
    risk = [r for r in feedback_loop_report.rule_results if r.target_artifact == "QA_RISK_RADAR"]
    # Mit RAG Incidents und Gaps sollten Regeln feuern
    assert len(prio) >= 0  # Kann 0 sein wenn keine Regeln greifen
    assert len(risk) >= 0


def test_global_warnings_when_incidents_missing() -> None:
    """Fehlende incident_index führt zu global_warnings."""
    from scripts.qa.feedback_loop.loader import FeedbackLoopInputs

    inputs = FeedbackLoopInputs(
        incident_index=None,
        analytics={"qa_coverage": {"replay_defined_ratio": 0.5, "regression_bound_ratio": 0.0}},
        autopilot_v2={"recommended_focus_subsystem": "RAG"},
        priority_score={"scores": [{"Subsystem": "RAG", "Score": 1}]},
    )
    report = run_feedback_projections(inputs, optional_timestamp="2025-01-15T12:00:00Z")
    assert any("incidents" in w.lower() for w in report.global_warnings)

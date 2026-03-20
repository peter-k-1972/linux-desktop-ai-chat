"""
Tests für Phase 3 Gap-Priorisierung.
"""

from __future__ import annotations

import pytest

from scripts.qa.gap_prioritization import (
    compute_gap_priority,
    build_prioritized_gaps,
    CRITICAL_SUBSYSTEMS,
)


def test_orphan_test_fixed_low_score() -> None:
    """orphan_test bleibt low, priority_score fix."""
    gap = {"gap_type": "orphan_test", "gap_id": "o1", "test_id": "t1"}
    result = compute_gap_priority(gap, {})
    assert result["severity"] == "low"
    assert result["priority_score"] == 10
    assert result["escalation_factors"] == []


def test_failure_class_uncovered_basis_high() -> None:
    """failure_class_uncovered hat Basis high."""
    gap = {
        "gap_id": "GAP-FC-1",
        "axis": "failure_class",
        "gap_type": "failure_class_uncovered",
        "value": "rag_silent_failure",
    }
    result = compute_gap_priority(gap, {})
    assert result["severity"] == "high"
    assert result["priority_score"] >= 30


def test_regression_requirement_escalates_with_incident() -> None:
    """regression_requirement mit Incident und kritischem Subsystem eskaliert."""
    gap = {
        "gap_id": "GAP-RR-001",
        "axis": "regression_requirement",
        "gap_type": "regression_requirement_unbound",
        "value": "INC-20260315-001",
    }
    context = {
        "incidents": [
            {"incident_id": "INC-20260315-001", "subsystem": "Chat", "severity": "high"},
        ],
    }
    result = compute_gap_priority(gap, context)
    assert "incident" in result["escalation_factors"]
    assert "critical_subsystem" in result["escalation_factors"]
    assert result["priority_score"] >= 50


def test_build_prioritized_gaps_sorts_by_score() -> None:
    """prioritized_gaps sind nach score absteigend sortiert."""
    gaps = {
        "failure_class": [
            {"gap_id": "GAP-FC-1", "axis": "failure_class", "gap_type": "failure_class_uncovered", "value": "x"},
        ],
        "guard": [],
        "regression_requirement": [],
        "replay_binding": [],
    }
    governance = {"semantic_binding_gaps": []}
    context = {}
    result = build_prioritized_gaps(gaps, governance, context)
    assert len(result) >= 1
    scores = [g.get("priority_score", 0) for g in result]
    assert scores == sorted(scores, reverse=True)

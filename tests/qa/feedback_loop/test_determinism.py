"""
Determinismus- und Snapshot-Tests: QA Feedback Loop.

Testet gleiche Inputs -> gleiche Outputs, sort_keys, optional_timestamp.
"""

from __future__ import annotations

import json

import pytest

from scripts.qa.feedback_loop import run_feedback_projections, report_to_dict


def test_det_same_inputs_same_output_structure(feedback_loop_inputs: object) -> None:
    """DET-JSON: Gleiche Inputs -> gleiche Output-Struktur (ohne generated_at)."""
    r1 = run_feedback_projections(feedback_loop_inputs, optional_timestamp="2025-01-15T12:00:00Z")
    r2 = run_feedback_projections(feedback_loop_inputs, optional_timestamp="2025-01-15T12:00:00Z")

    d1 = report_to_dict(r1)
    d2 = report_to_dict(r2)

    d1.pop("generated_at", None)
    d2.pop("generated_at", None)

    assert json.dumps(d1, sort_keys=True) == json.dumps(d2, sort_keys=True)


def test_det_timestamp_format(feedback_loop_report: object) -> None:
    """DET-Timestamp: generated_at im ISO-8601-Format."""
    ts = feedback_loop_report.generated_at
    assert "T" in ts
    assert "Z" in ts or "+" in ts
    assert len(ts) >= 20


def test_det_rule_results_stable(feedback_loop_inputs: object) -> None:
    """Rule-Ergebnisse sind bei gleichen Inputs stabil."""
    r1 = run_feedback_projections(feedback_loop_inputs, optional_timestamp="2025-01-15T12:00:00Z")
    r2 = run_feedback_projections(feedback_loop_inputs, optional_timestamp="2025-01-15T12:00:00Z")

    keys1 = [(r.target_artifact, r.target_key) for r in r1.rule_results]
    keys2 = [(r.target_artifact, r.target_key) for r in r2.rule_results]
    assert keys1 == keys2


def test_det_subsystem_keys_sorted(feedback_loop_report: object) -> None:
    """Subsystem-Keys sind sortiert (Determinismus)."""
    keys = list(feedback_loop_report.per_subsystem_results.keys())
    assert keys == sorted(keys)


def test_det_failure_class_keys_sorted(feedback_loop_report: object) -> None:
    """Failure-Class-Keys sind sortiert (Determinismus)."""
    keys = list(feedback_loop_report.per_failure_class_results.keys())
    assert keys == sorted(keys)

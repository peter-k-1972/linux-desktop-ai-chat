"""
Unit Tests: QA Feedback Loop – Trace-Erzeugung.

Testet report_to_dict, Pflichtfelder, stabiler Inhalt bei gleichen Inputs,
keine unerwarteten Nebeneffekte.
"""

from __future__ import annotations

import json
import logging

import pytest

from scripts.qa.feedback_loop import run_feedback_projections, report_to_dict, trace_report


def test_report_to_dict_contains_required_fields(feedback_loop_report: object) -> None:
    """report_to_dict enthält alle Pflichtfelder."""
    d = report_to_dict(feedback_loop_report)
    required = [
        "generated_at",
        "generator",
        "input_sources",
        "global_warnings",
        "per_subsystem_results",
        "per_failure_class_results",
        "escalations",
        "suppressed_changes",
        "rule_results",
    ]
    for key in required:
        assert key in d, f"Pflichtfeld '{key}' fehlt in report_to_dict"


def test_report_to_dict_json_serializable(feedback_loop_report: object) -> None:
    """report_to_dict ist JSON-serialisierbar ohne Fehler."""
    d = report_to_dict(feedback_loop_report)
    s = json.dumps(d, indent=2, ensure_ascii=False)
    assert len(s) > 0
    parsed = json.loads(s)
    assert parsed["generator"] == "feedback_loop"


def test_report_to_dict_stable_content_same_inputs(feedback_loop_inputs: object) -> None:
    """Stabiler Inhalt bei gleichen Inputs – report_to_dict identisch (ohne generated_at)."""
    r1 = run_feedback_projections(feedback_loop_inputs, optional_timestamp="2025-01-15T12:00:00Z")
    r2 = run_feedback_projections(feedback_loop_inputs, optional_timestamp="2025-01-15T12:00:00Z")

    d1 = report_to_dict(r1)
    d2 = report_to_dict(r2)

    assert d1["generated_at"] == d2["generated_at"]
    assert d1["generator"] == d2["generator"]
    assert d1["input_sources"] == d2["input_sources"]
    assert set(d1["per_subsystem_results"].keys()) == set(d2["per_subsystem_results"].keys())
    assert len(d1["rule_results"]) == len(d2["rule_results"])


def test_trace_report_no_side_effects(feedback_loop_report: object, caplog: pytest.LogCaptureFixture) -> None:
    """trace_report hat keine unerwarteten Nebeneffekte – nur Logging."""
    caplog.set_level(logging.INFO)
    trace_report(feedback_loop_report, level=logging.INFO)
    assert "FeedbackProjectionReport" in caplog.text or "feedback_loop" in caplog.text.lower()


def test_trace_report_does_not_raise(feedback_loop_report: object) -> None:
    """trace_report wirft keine Exception."""
    trace_report(feedback_loop_report, level=logging.DEBUG)


def test_per_subsystem_results_dict_structure(feedback_loop_report: object) -> None:
    """per_subsystem_results enthält SubsystemFeedbackState-ähnliche Struktur."""
    d = report_to_dict(feedback_loop_report)
    for sub, state_dict in d["per_subsystem_results"].items():
        assert isinstance(sub, str)
        assert isinstance(state_dict, dict)
        assert "subsystem" in state_dict
        assert "incident_count" in state_dict
        assert "replay_gap_rate" in state_dict
        assert "regression_gap_rate" in state_dict
        assert "escalation_level" in state_dict


def test_rule_results_dict_structure(feedback_loop_report: object) -> None:
    """rule_results enthält target_artifact, target_key, applied_rule_ids."""
    d = report_to_dict(feedback_loop_report)
    for r in d["rule_results"]:
        assert "target_artifact" in r
        assert "target_key" in r
        assert "applied_rule_ids" in r
        assert isinstance(r["applied_rule_ids"], list)

"""
QA Feedback Loop – Tracing.

Strukturierte Nachverfolgbarkeit der Feedback-Loop-Ausführung.
Keine Side-Effects, nur Logging/Trace-Ausgabe.
"""

from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Any

from .models import FeedbackProjectionReport, FeedbackRuleResult

LOG = logging.getLogger(__name__)


def trace_report(report: FeedbackProjectionReport, level: int = logging.INFO) -> None:
    """
    Schreibt strukturierte Trace-Informationen zum Report.
    level: logging.DEBUG für Details, INFO für Zusammenfassung.
    """
    LOG.log(level, "FeedbackProjectionReport: generated_at=%s, generator=%s", report.generated_at, report.generator)
    LOG.log(level, "  input_sources: %s", report.input_sources)
    if report.global_warnings:
        for w in report.global_warnings:
            LOG.warning("  global_warning: %s", w)
    if report.escalations:
        for e in report.escalations:
            LOG.warning("  escalation: %s", e)
    LOG.log(level, "  subsystems: %d", len(report.per_subsystem_results))
    LOG.log(level, "  failure_classes: %d", len(report.per_failure_class_results))
    LOG.log(level, "  rule_results: %d", len(report.rule_results))
    LOG.log(level, "  suppressed_changes: %d", len(report.suppressed_changes))

    if level <= logging.DEBUG:
        for sub, state in report.per_subsystem_results.items():
            LOG.debug(
                "  subsystem %s: incident_count=%d pressure=%.2f escalation=%d",
                sub, state.incident_count, state.feedback_pressure_score, state.escalation_level,
            )
        for r in report.rule_results:
            LOG.debug(
                "  rule_result: %s -> %s (rules: %s)",
                r.target_artifact, r.target_key, r.applied_rule_ids,
            )


def trace_rule_result(result: FeedbackRuleResult, level: int = logging.DEBUG) -> None:
    """Trace einer einzelnen Regel-Anwendung."""
    LOG.log(
        level,
        "FeedbackRuleResult: %s.%s old=%s new=%s delta=%s rules=%s",
        result.target_artifact,
        result.target_key,
        result.old_value,
        result.new_value,
        result.delta,
        result.applied_rule_ids,
    )


def report_to_dict(report: FeedbackProjectionReport) -> dict[str, Any]:
    """Serialisiert FeedbackProjectionReport zu einem JSON-kompatiblen Dict."""
    def _state_to_dict(obj: Any) -> dict:
        try:
            return asdict(obj)
        except TypeError:
            return {}

    def _rule_to_dict(r: FeedbackRuleResult) -> dict:
        return {
            "target_artifact": r.target_artifact,
            "target_key": r.target_key,
            "old_value": r.old_value,
            "new_value": r.new_value,
            "delta": r.delta,
            "reasons": list(r.reasons),
            "applied_rule_ids": list(r.applied_rule_ids),
        }

    return {
        "generated_at": report.generated_at,
        "generator": report.generator,
        "input_sources": report.input_sources,
        "global_warnings": report.global_warnings,
        "per_subsystem_results": {
            k: _state_to_dict(v) for k, v in report.per_subsystem_results.items()
        },
        "per_failure_class_results": {
            k: _state_to_dict(v) for k, v in report.per_failure_class_results.items()
        },
        "escalations": report.escalations,
        "suppressed_changes": [_rule_to_dict(r) for r in report.suppressed_changes],
        "rule_results": [_rule_to_dict(r) for r in report.rule_results],
    }

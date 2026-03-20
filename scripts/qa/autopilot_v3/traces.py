"""
QA Autopilot v3 – Trace-Ausgabe.
"""

from __future__ import annotations

from typing import Any

from .models import (
    AutopilotV3Output,
    GuardGapFinding,
    RecommendedTestBacklogItem,
    TestGapFinding,
    TranslationGapFinding,
)


def _finding_to_dict(f: TestGapFinding | GuardGapFinding | TranslationGapFinding) -> dict[str, Any]:
    """Konvertiert Finding zu Dict."""
    if isinstance(f, TestGapFinding):
        return {
            "id": f.id,
            "subsystem": f.subsystem,
            "failure_class": f.failure_class,
            "gap_type": f.gap_type,
            "reasons": list(f.reasons),
            "incident_count": f.incident_count,
            "priority": f.priority,
        }
    if isinstance(f, GuardGapFinding):
        return {
            "id": f.id,
            "subsystem": f.subsystem,
            "failure_class": f.failure_class,
            "guard_type": f.guard_type,
            "reasons": list(f.reasons),
            "pilot_id": f.pilot_id,
            "priority": f.priority,
        }
    return {
        "id": f.id,
        "incident_id": f.incident_id,
        "subsystem": f.subsystem,
        "failure_class": f.failure_class,
        "gap_type": f.gap_type,
        "reasons": list(f.reasons),
        "priority": f.priority,
    }


def _backlog_item_to_dict(b: RecommendedTestBacklogItem) -> dict[str, Any]:
    """Konvertiert Backlog-Item zu Dict."""
    return {
        "id": b.id,
        "title": b.title,
        "subsystem": b.subsystem,
        "failure_class": b.failure_class,
        "test_domain": b.test_domain,
        "test_type": b.test_type,
        "guard_type": b.guard_type,
        "priority": b.priority,
        "reasons": list(b.reasons),
    }


def output_to_dict(output: AutopilotV3Output) -> dict[str, Any]:
    """Konvertiert AutopilotV3Output zu JSON-serialisierbarem Dict."""
    return {
        "schema_version": output.schema_version,
        "generated_at": output.generated_at,
        "summary": output.summary,
        "test_gap_findings": [_finding_to_dict(f) for f in output.test_gap_findings],
        "guard_gap_findings": [_finding_to_dict(f) for f in output.guard_gap_findings],
        "translation_gap_findings": [_finding_to_dict(f) for f in output.translation_gap_findings],
        "recommended_test_backlog": [_backlog_item_to_dict(b) for b in output.recommended_test_backlog],
        "warnings": output.warnings,
        "escalations": output.escalations,
        "supporting_evidence": output.supporting_evidence,
        "input_sources": output.input_sources,
    }


def build_autopilot_v3_trace(output: AutopilotV3Output) -> dict[str, Any]:
    """Baut Trace-Dict für autopilot_v3_trace.json."""
    return {
        "generated_at": output.generated_at,
        "generator": "autopilot_v3",
        "input_sources": output.input_sources,
        "summary": output.summary,
        "test_gap_count": len(output.test_gap_findings),
        "guard_gap_count": len(output.guard_gap_findings),
        "translation_gap_count": len(output.translation_gap_findings),
        "backlog_count": len(output.recommended_test_backlog),
        "warnings_count": len(output.warnings),
        "escalations_count": len(output.escalations),
    }

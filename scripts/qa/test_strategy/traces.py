"""
QA Test Strategy Engine – Trace-Ausgabe.
"""

from __future__ import annotations

from typing import Any

from .models import (
    GuardRequirement,
    RecommendedFocusDomain,
    RegressionRequirement,
    TestDomain,
    TestStrategyOutput,
)


def _test_domain_to_dict(d: TestDomain) -> dict[str, Any]:
    """Konvertiert TestDomain zu Dict."""
    return {
        "domain": d.domain,
        "priority": d.priority,
        "recommendation_count": d.recommendation_count,
        "subsystems": list(d.subsystems),
        "failure_classes": list(d.failure_classes),
    }


def _guard_requirement_to_dict(g: GuardRequirement) -> dict[str, Any]:
    """Konvertiert GuardRequirement zu Dict."""
    return {
        "id": g.id,
        "subsystem": g.subsystem,
        "guard_type": g.guard_type,
        "failure_class": g.failure_class,
        "priority": g.priority,
        "pilot_id": g.pilot_id,
        "reasons": list(g.reasons),
    }


def _regression_requirement_to_dict(r: RegressionRequirement) -> dict[str, Any]:
    """Konvertiert RegressionRequirement zu Dict."""
    return {
        "id": r.id,
        "incident_id": r.incident_id,
        "subsystem": r.subsystem,
        "failure_class": r.failure_class,
        "priority": r.priority,
        "reasons": list(r.reasons),
    }


def _focus_domain_to_dict(f: RecommendedFocusDomain) -> dict[str, Any]:
    """Konvertiert RecommendedFocusDomain zu Dict."""
    return {
        "domain": f.domain,
        "subsystem": f.subsystem,
        "failure_class": f.failure_class,
        "priority": f.priority,
        "pilot_related": f.pilot_related,
    }


def output_to_dict(output: TestStrategyOutput) -> dict[str, Any]:
    """Konvertiert TestStrategyOutput zu JSON-serialisierbarem Dict."""
    return {
        "escalations": output.escalations,
        "generated_at": output.generated_at,
        "guard_requirements": [_guard_requirement_to_dict(g) for g in output.guard_requirements],
        "input_sources": output.input_sources,
        "recommended_focus_domains": [_focus_domain_to_dict(f) for f in output.recommended_focus_domains],
        "regression_requirements": [_regression_requirement_to_dict(r) for r in output.regression_requirements],
        "schema_version": output.schema_version,
        "supporting_evidence": output.supporting_evidence,
        "test_domains": [_test_domain_to_dict(d) for d in output.test_domains],
        "warnings": output.warnings,
    }


def build_test_strategy_trace(output: TestStrategyOutput) -> dict[str, Any]:
    """Baut Trace-Dict für test_strategy_trace.json."""
    return {
        "generated_at": output.generated_at,
        "generator": "test_strategy_engine",
        "input_sources": output.input_sources,
        "summary": {
            "test_domain_count": len(output.test_domains),
            "guard_requirement_count": len(output.guard_requirements),
            "regression_requirement_count": len(output.regression_requirements),
            "recommended_focus_count": len(output.recommended_focus_domains),
            "warnings_count": len(output.warnings),
            "escalations_count": len(output.escalations),
        },
        "warnings": output.warnings,
        "escalations": output.escalations,
    }

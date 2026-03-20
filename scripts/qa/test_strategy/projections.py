"""
QA Test Strategy Engine – Projektionen.

Baut TestStrategyOutput aus Autopilot-v3-Erkenntnissen und Strategie-Regeln.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .models import TestStrategyOutput
from .rules import apply_strategy_rules


def _build_supporting_evidence(
    autopilot_v3: dict[str, Any],
    test_domain_count: int,
    guard_count: int,
    regression_count: int,
    focus_count: int,
) -> dict[str, Any]:
    """Baut supporting_evidence."""
    evidence = autopilot_v3.get("supporting_evidence") or {}
    return {
        "subsystems_analyzed": evidence.get("subsystems_analyzed", []),
        "failure_classes_analyzed": evidence.get("failure_classes_analyzed", []),
        "incident_count": evidence.get("incident_count", 0),
        "test_domain_count": test_domain_count,
        "guard_requirement_count": guard_count,
        "regression_requirement_count": regression_count,
        "recommended_focus_count": focus_count,
    }


def run_test_strategy_projections(
    inputs: Any,
    optional_timestamp: str | None = None,
) -> TestStrategyOutput:
    """
    Führt Test Strategy Projektion durch.
    Übersetzt Autopilot-v3-Erkenntnisse in strukturierte QA-Teststrategie.
    """
    autopilot_v3 = inputs.autopilot_v3
    if not autopilot_v3:
        raise ValueError("QA_AUTOPILOT_V3.json fehlt – Abbruch")

    generated_at = (
        optional_timestamp
        if optional_timestamp is not None
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    test_domains, guard_requirements, regression_requirements, recommended_focus = (
        apply_strategy_rules(autopilot_v3, inputs.control_center)
    )

    warnings: list[str] = list(autopilot_v3.get("warnings") or [])
    escalations: list[str] = list(autopilot_v3.get("escalations") or [])

    supporting_evidence = _build_supporting_evidence(
        autopilot_v3,
        len(test_domains),
        len(guard_requirements),
        len(regression_requirements),
        len(recommended_focus),
    )

    return TestStrategyOutput(
        schema_version="1.0",
        generated_at=generated_at,
        input_sources=inputs.loaded_sources,
        test_domains=test_domains,
        guard_requirements=guard_requirements,
        regression_requirements=regression_requirements,
        recommended_focus_domains=recommended_focus,
        warnings=warnings,
        escalations=escalations,
        supporting_evidence=supporting_evidence,
    )

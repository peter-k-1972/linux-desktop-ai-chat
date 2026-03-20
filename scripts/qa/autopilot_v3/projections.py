"""
QA Autopilot v3 – Projektionen.

Baut AutopilotV3Output aus Feedback-Report und Gap-Regeln.
"""

from __future__ import annotations

from typing import Any

from scripts.qa.feedback_loop import run_feedback_projections

from .models import (
    FAILURE_CLASS_TO_TEST_DOMAIN,
    DEFAULT_TEST_DOMAIN,
    AutopilotV3Output,
    GuardGapFinding,
    PILOT_CONSTELLATIONS,
    RecommendedTestBacklogItem,
    TestGapFinding,
    TranslationGapFinding,
)
from .rules import apply_gap_rules


def _gap_type_to_test_type(gap_type: str) -> str:
    """Mappt gap_type auf test_type."""
    if "replay" in gap_type:
        return "replay"
    if "regression" in gap_type:
        return "regression"
    if "contract" in gap_type:
        return "contract"
    return "replay"


def _build_recommended_test_backlog(
    test_gaps: list[TestGapFinding],
    guard_gaps: list[GuardGapFinding],
) -> list[RecommendedTestBacklogItem]:
    """Baut recommended_test_backlog aus Test- und Guard-Gaps."""
    backlog: list[RecommendedTestBacklogItem] = []
    seen: set[tuple[str, str, str]] = set()
    bid = 0

    for tg in test_gaps:
        key = (tg.subsystem, tg.failure_class, tg.gap_type)
        if key in seen:
            continue
        seen.add(key)
        bid += 1
        test_domain = FAILURE_CLASS_TO_TEST_DOMAIN.get(tg.failure_class, DEFAULT_TEST_DOMAIN)
        guard_type = "failure_replay_guard"
        if "contract" in tg.gap_type:
            guard_type = "event_contract_guard"
        elif "regression" in tg.gap_type:
            guard_type = "failure_replay_guard"

        backlog.append(RecommendedTestBacklogItem(
            id=f"RTB-{bid:03d}",
            title=f"{tg.subsystem} – {tg.failure_class} ({tg.gap_type.replace('_', ' ')})",
            subsystem=tg.subsystem,
            failure_class=tg.failure_class,
            test_domain=test_domain,
            test_type=_gap_type_to_test_type(tg.gap_type),
            guard_type=guard_type,
            priority=tg.priority,
            reasons=tg.reasons,
        ))

    for gg in guard_gaps:
        key = (gg.subsystem, gg.failure_class, gg.guard_type)
        if key in seen:
            continue
        seen.add(key)
        bid += 1
        test_domain = FAILURE_CLASS_TO_TEST_DOMAIN.get(gg.failure_class, DEFAULT_TEST_DOMAIN)
        backlog.append(RecommendedTestBacklogItem(
            id=f"RTB-{bid:03d}",
            title=f"{gg.subsystem} – {gg.guard_type} gap",
            subsystem=gg.subsystem,
            failure_class=gg.failure_class,
            test_domain=test_domain,
            test_type="replay" if "replay" in gg.guard_type else "contract",
            guard_type=gg.guard_type,
            priority=gg.priority,
            reasons=gg.reasons,
        ))

    return sorted(backlog, key=lambda x: (0 if x.priority == "high" else 1 if x.priority == "medium" else 2, x.subsystem))


def _build_summary(
    test_gaps: list[TestGapFinding],
    guard_gaps: list[GuardGapFinding],
    translation_gaps: list[TranslationGapFinding],
    backlog: list[RecommendedTestBacklogItem],
) -> dict[str, Any]:
    """Baut summary-Dict."""
    high_prio = sum(1 for b in backlog if b.priority == "high")
    return {
        "total_test_gaps": len(test_gaps),
        "total_guard_gaps": len(guard_gaps),
        "total_translation_gaps": len(translation_gaps),
        "recommended_backlog_count": len(backlog),
        "high_priority_backlog_count": high_prio,
    }


def _build_supporting_evidence(
    report: Any,
    inputs: Any,
) -> dict[str, Any]:
    """Baut supporting_evidence aus Report und Inputs."""
    return {
        "subsystems_analyzed": list(report.per_subsystem_results.keys()) if report else [],
        "failure_classes_analyzed": list(report.per_failure_class_results.keys()) if report else [],
        "incident_count": sum(
            getattr(s, "incident_count", 0)
            for s in (report.per_subsystem_results.values() if report else [])
        ),
        "input_sources": inputs.loaded_sources if inputs else [],
    }


def run_autopilot_v3_projections(
    inputs: Any,
    optional_timestamp: str | None = None,
) -> AutopilotV3Output:
    """
    Führt Autopilot v3 Projektion durch.
    Nutzt run_feedback_projections und wendet Gap-Regeln an.
    """
    from datetime import datetime, timezone

    generated_at = (
        optional_timestamp
        if optional_timestamp is not None
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    report = run_feedback_projections(inputs, optional_timestamp=optional_timestamp)
    autopilot = inputs.autopilot_v2 or {}
    priority_score = inputs.priority_score

    incidents_raw = getattr(inputs, "incident_index", None) or {}
    incidents = incidents_raw.get("incidents", []) if isinstance(incidents_raw, dict) else []
    if not isinstance(incidents, list):
        incidents = []

    test_gaps, guard_gaps, translation_gaps = apply_gap_rules(
        report.per_subsystem_results,
        report.per_failure_class_results,
        incidents,
        autopilot,
        priority_score,
    )

    backlog = _build_recommended_test_backlog(test_gaps, guard_gaps)
    summary = _build_summary(test_gaps, guard_gaps, translation_gaps, backlog)

    warnings: list[str] = list(report.global_warnings) if report else []
    if not inputs.incident_index:
        warnings.append("incidents/index.json fehlt – Projektion eingeschränkt")
    if not inputs.analytics:
        warnings.append("incidents/analytics.json fehlt – Fallback auf Defaults")

    escalations: list[str] = list(report.escalations) if report else []
    if len(test_gaps) >= 5:
        escalations.append(f"Hohe Anzahl Test-Gaps: {len(test_gaps)}")
    if len(translation_gaps) >= 10:
        escalations.append(f"Hohe Anzahl Translation-Gaps: {len(translation_gaps)}")

    supporting_evidence = _build_supporting_evidence(report, inputs)

    return AutopilotV3Output(
        schema_version="3.0",
        generated_at=generated_at,
        summary=summary,
        test_gap_findings=test_gaps,
        guard_gap_findings=guard_gaps,
        translation_gap_findings=translation_gaps,
        recommended_test_backlog=backlog,
        warnings=warnings,
        escalations=escalations,
        supporting_evidence=supporting_evidence,
        input_sources=inputs.loaded_sources if hasattr(inputs, "loaded_sources") else [],
    )

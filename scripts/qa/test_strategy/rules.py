"""
QA Test Strategy Engine – Strategie-Regeln.

1. Domain Priorisierung: viele Empfehlungen im selben Testdomain → Domain Priorität erhöhen
2. Guard Requirements: guard_gap_findings vorhanden → guard requirement erzeugen
3. Regression Requirements: translation_gap = incident_not_bound_to_regression → regression requirement
4. Pilotkonstellationen: startup/ollama unreachable, rag/chromadb network failure, debug/eventbus event drift
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .models import (
    PILOT_CONSTELLATIONS,
    GuardRequirement,
    RecommendedFocusDomain,
    RegressionRequirement,
    TestDomain,
)


def _domain_priority_rule(
    recommended_test_backlog: list[dict[str, Any]],
) -> list[TestDomain]:
    """
    Domain Priorisierung: wenn viele Empfehlungen im selben Testdomain,
    dann Domain Priorität erhöhen.
    """
    domain_counts: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in recommended_test_backlog or []:
        domain = item.get("test_domain") or "failure_modes"
        domain_counts[domain].append(item)

    # Sortiere Domains nach Anzahl (absteigend), dann alphabetisch für Determinismus
    sorted_domains = sorted(
        domain_counts.items(),
        key=lambda x: (-len(x[1]), x[0]),
    )

    result: list[TestDomain] = []
    for priority, (domain, items) in enumerate(sorted_domains, start=1):
        subsystems = tuple(sorted({i.get("subsystem", "") for i in items if i.get("subsystem")}))
        failure_classes = tuple(sorted({i.get("failure_class", "") for i in items if i.get("failure_class")}))
        result.append(TestDomain(
            domain=domain,
            priority=priority,
            recommendation_count=len(items),
            subsystems=subsystems,
            failure_classes=failure_classes,
        ))
    return result


def _guard_requirements_rule(
    guard_gap_findings: list[dict[str, Any]],
) -> list[GuardRequirement]:
    """
    Guard Requirements: wenn guard_gap_findings vorhanden,
    dann guard requirement erzeugen.
    """
    result: list[GuardRequirement] = []
    for g in guard_gap_findings or []:
        result.append(GuardRequirement(
            id=g.get("id", ""),
            subsystem=g.get("subsystem", ""),
            guard_type=g.get("guard_type", ""),
            failure_class=g.get("failure_class", ""),
            priority=g.get("priority", "medium"),
            pilot_id=g.get("pilot_id"),
            reasons=tuple(g.get("reasons", []) or []),
        ))
    return result


def _regression_requirements_rule(
    translation_gap_findings: list[dict[str, Any]],
) -> list[RegressionRequirement]:
    """
    Regression Requirements: wenn translation_gap = incident_not_bound_to_regression,
    dann regression requirement setzen.
    """
    result: list[RegressionRequirement] = []
    for t in translation_gap_findings or []:
        if t.get("gap_type") != "incident_not_bound_to_regression":
            continue
        result.append(RegressionRequirement(
            id=t.get("id", ""),
            incident_id=t.get("incident_id", ""),
            subsystem=t.get("subsystem", ""),
            failure_class=t.get("failure_class", ""),
            priority=t.get("priority", "medium"),
            reasons=tuple(t.get("reasons", []) or []),
        ))
    return result


def _recommended_focus_domains_rule(
    recommended_test_backlog: list[dict[str, Any]],
    guard_gap_findings: list[dict[str, Any]],
    control_center: dict[str, Any] | None,
) -> list[RecommendedFocusDomain]:
    """
    Empfohlene Fokus-Domains aus Backlog und Guard-Gaps.
    Berücksichtigt Pilotkonstellationen.
    """
    pilot_tracking = (control_center or {}).get("pilot_tracking") or {}
    current_matched = pilot_tracking.get("current_matched") or {}
    active_pilot_id = current_matched.get("id")
    active_pilot_subsystems: set[str] = set()
    if active_pilot_id:
        for p in PILOT_CONSTELLATIONS:
            if p.get("id") == active_pilot_id:
                active_pilot_subsystems = p.get("subsystems", set())
                break

    seen: set[tuple[str, str, str]] = set()
    result: list[RecommendedFocusDomain] = []

    for item in recommended_test_backlog or []:
        domain = item.get("test_domain") or "failure_modes"
        sub = item.get("subsystem", "")
        fc = item.get("failure_class", "")
        key = (domain, sub, fc)
        if key in seen:
            continue
        seen.add(key)
        pilot_related = sub in active_pilot_subsystems
        result.append(RecommendedFocusDomain(
            domain=domain,
            subsystem=sub,
            failure_class=fc,
            priority=item.get("priority", "medium"),
            pilot_related=pilot_related,
        ))

    for g in guard_gap_findings or []:
        sub = g.get("subsystem", "")
        fc = g.get("failure_class", "")
        domain = _guard_type_to_domain(g.get("guard_type", ""))
        key = (domain, sub, fc)
        if key in seen:
            continue
        seen.add(key)
        pilot_related = sub in active_pilot_subsystems
        result.append(RecommendedFocusDomain(
            domain=domain,
            subsystem=sub,
            failure_class=fc,
            priority=g.get("priority", "medium"),
            pilot_related=pilot_related,
        ))

    # Priorisiere: pilot_related first, dann priority
    def _sort_key(r: RecommendedFocusDomain) -> tuple[int, int, str, str]:
        pilot = 0 if r.pilot_related else 1
        prio = 0 if r.priority == "high" else 1 if r.priority == "medium" else 2
        return (pilot, prio, r.subsystem, r.domain)

    return sorted(result, key=_sort_key)


def _guard_type_to_domain(guard_type: str) -> str:
    """Mappt guard_type auf Test-Domain."""
    if "startup" in guard_type:
        return "startup"
    if "event" in guard_type or "contract" in guard_type:
        return "contracts"
    return "async_behavior"


def apply_strategy_rules(
    autopilot_v3: dict[str, Any],
    control_center: dict[str, Any] | None,
) -> tuple[
    list[TestDomain],
    list[GuardRequirement],
    list[RegressionRequirement],
    list[RecommendedFocusDomain],
]:
    """Wendet alle Strategie-Regeln an."""
    backlog = autopilot_v3.get("recommended_test_backlog") or []
    guard_gaps = autopilot_v3.get("guard_gap_findings") or []
    translation_gaps = autopilot_v3.get("translation_gap_findings") or []

    test_domains = _domain_priority_rule(backlog)
    guard_requirements = _guard_requirements_rule(guard_gaps)
    regression_requirements = _regression_requirements_rule(translation_gaps)
    recommended_focus = _recommended_focus_domains_rule(
        backlog, guard_gaps, control_center
    )

    return test_domains, guard_requirements, regression_requirements, recommended_focus

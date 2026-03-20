"""
Phase 3 – Gap-Priorisierung.

Berechnet priority_score, escalation_factors und finale severity für Gaps.
Entspricht PHASE3_GAP_PRIORITIZATION.md.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CRITICAL_SUBSYSTEMS = frozenset({
    "Startup/Bootstrap",
    "RAG",
    "Chat",
    "Provider/Ollama",
})

SEVERITY_ORDER = ("low", "medium", "high", "critical")


def _load_config(qa_dir: Path | None = None) -> dict[str, Any]:
    if qa_dir is None:
        qa_dir = Path(__file__).resolve().parent.parent.parent / "docs" / "qa"
    path = qa_dir / "config" / "phase3_gap_prioritization.json"
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _escalate_severity(severity: str, steps: int = 1) -> str:
    """Erhöht severity um steps Stufen (max. critical)."""
    order = list(SEVERITY_ORDER)
    try:
        idx = order.index(severity)
    except ValueError:
        return severity
    new_idx = min(idx + steps, len(order) - 1)
    return order[new_idx]


def _get_subsystem_for_gap(gap: dict[str, Any], context: dict[str, Any]) -> str | None:
    """Extrahiert Subsystem aus Gap oder Kontext."""
    if gap.get("subsystem"):
        return gap["subsystem"]
    axis = gap.get("axis", "")
    value = gap.get("value")
    incidents = context.get("incidents") or []
    if axis == "regression_requirement" and value:
        for inc in incidents:
            if inc.get("incident_id") == value:
                return inc.get("subsystem")
    if axis == "replay_binding" and value:
        for inc in incidents:
            if inc.get("incident_id") == value:
                return inc.get("subsystem")
    if axis == "failure_class" and value:
        for inc in incidents:
            if inc.get("failure_class") == value:
                return inc.get("subsystem")
    if axis == "guard":
        for gr in (context.get("guard_requirements") or []):
            if gr.get("guard_type") == value:
                return gr.get("subsystem")
    return None


def _get_incident_id_for_gap(gap: dict[str, Any]) -> str | None:
    """Extrahiert incident_id aus Gap falls vorhanden."""
    if gap.get("incident_id"):
        return gap["incident_id"]
    axis = gap.get("axis", "")
    value = gap.get("value")
    if axis in ("regression_requirement", "replay_binding") and value and str(value).startswith("INC-"):
        return value
    return None


def _is_in_strategy(gap: dict[str, Any], context: dict[str, Any]) -> bool:
    """Prüft ob Gap in recommended_focus_domains oder guard_requirements."""
    value = gap.get("value")
    axis = gap.get("axis", "")
    for rfd in (context.get("recommended_focus_domains") or []):
        if rfd.get("failure_class") == value or rfd.get("subsystem") == value:
            return True
    for gr in (context.get("guard_requirements") or []):
        if gr.get("guard_type") == value or gr.get("failure_class") == value:
            return True
    return False


def _is_in_autopilot_backlog(gap: dict[str, Any], context: dict[str, Any]) -> bool:
    """Prüft ob Gap in recommended_test_backlog."""
    backlog = context.get("recommended_test_backlog") or []
    value = gap.get("value")
    axis = gap.get("axis", "")
    for item in backlog:
        if item.get("id") == value or item.get("guard_type") == value:
            return True
        if axis == "autopilot_recommendation" and item.get("id"):
            return True
    return False


def _get_incident_severity(incident_id: str, context: dict[str, Any]) -> str | None:
    """Holt severity aus incidents für incident_id."""
    for inc in (context.get("incidents") or []):
        if inc.get("incident_id") == incident_id:
            return inc.get("severity")
    return None


def compute_gap_priority(
    gap: dict[str, Any],
    context: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Berechnet priority_score, escalation_factors, severity für einen Gap.
    Mutiert gap nicht; gibt angereicherte Kopie zurück.
    """
    cfg = config or _load_config(context.get("qa_dir"))
    weights = cfg.get("severity_weights") or {}
    bonus = cfg.get("bonus_weights") or {}
    basis_map = cfg.get("basis_severity_by_gap_type") or {}
    critical_subsystems = set(cfg.get("critical_subsystems", list(CRITICAL_SUBSYSTEMS)))
    orphan_fixed = cfg.get("orphan_fixed_score", 10)

    gap_type = gap.get("gap_type", "")
    if gap_type == "orphan_test":
        return {
            **gap,
            "severity": "low",
            "priority_score": orphan_fixed,
            "escalation_factors": [],
        }

    basis_sev = basis_map.get(gap_type, "medium")
    if gap.get("severity") and gap["severity"] in SEVERITY_ORDER:
        basis_sev = gap["severity"]

    escalation_factors: list[str] = []
    severity = basis_sev

    incident_id = _get_incident_id_for_gap(gap)
    subsystem = _get_subsystem_for_gap(gap, context)
    in_strategy = _is_in_strategy(gap, context)
    in_autopilot = _is_in_autopilot_backlog(gap, context)

    if incident_id:
        escalation_factors.append("incident")
        inc_sev = _get_incident_severity(incident_id, context)
        if inc_sev == "high":
            severity = _escalate_severity(severity, 1)
            escalation_factors.append("incident_severity_high")
    if in_strategy:
        escalation_factors.append("strategy")
        severity = _escalate_severity(severity, 1)
    if in_autopilot:
        escalation_factors.append("autopilot")
    if subsystem and subsystem in critical_subsystems:
        escalation_factors.append("critical_subsystem")
        severity = _escalate_severity(severity, 1)

    base_score = weights.get(severity, 20)
    incident_bonus = bonus.get("incident", 25) if incident_id else 0
    strategy_bonus = bonus.get("strategy", 15) if in_strategy else 0
    autopilot_bonus = bonus.get("autopilot", 10) if in_autopilot else 0
    subsystem_bonus = bonus.get("subsystem", 10) if (subsystem and subsystem in critical_subsystems) else 0

    priority_score = base_score + incident_bonus + strategy_bonus + autopilot_bonus + subsystem_bonus
    priority_score = min(100, priority_score)

    return {
        **gap,
        "severity": severity,
        "priority_score": priority_score,
        "escalation_factors": escalation_factors,
        "subsystem": subsystem,
        "incident_id": incident_id,
        "strategy_relevant": in_strategy,
        "autopilot_relevant": in_autopilot,
    }


def build_prioritized_gaps(
    gaps: dict[str, list[dict[str, Any]]],
    governance: dict[str, Any],
    context: dict[str, Any],
    config: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """
    Flacht alle Gaps, wendet Priorisierung an, sortiert nach priority_score.
    """
    all_gaps: list[dict[str, Any]] = []
    for axis, items in gaps.items():
        for g in items:
            enriched = compute_gap_priority(g, context, config)
            all_gaps.append(enriched)

    for sg in governance.get("semantic_binding_gaps") or []:
        gap = {
            "gap_id": f"GAP-SB-{sg.get('failure_class', 'unknown')}",
            "axis": "semantic_binding",
            "gap_type": "semantic_binding_gap",
            "value": sg.get("failure_class"),
            "expected_test_domain": sg.get("expected_test_domain"),
            "actual_test_count": sg.get("actual_test_count", 0),
            "evidence": sg.get("evidence", ""),
        }
        enriched = compute_gap_priority(gap, context, config)
        all_gaps.append(enriched)

    backlog = (context.get("autopilot_v3") or {}).get("recommended_test_backlog") or []
    for item in backlog:
        if item.get("covered"):
            continue
        gap = {
            "gap_id": item.get("id", "RTB-unknown"),
            "axis": "autopilot_recommendation",
            "gap_type": "autopilot_recommendation_uncovered",
            "value": item.get("id"),
            "subsystem": item.get("subsystem"),
            "failure_class": item.get("failure_class"),
            "guard_type": item.get("guard_type"),
            "title": item.get("title"),
        }
        enriched = compute_gap_priority(gap, context, config)
        all_gaps.append(enriched)

    def _sort_key(g: dict[str, Any]) -> tuple[int, int, str]:
        score = -g.get("priority_score", 0)
        order = {"failure_class_uncovered": 0, "regression_requirement_unbound": 1, "replay_unbound": 2, "guard_missing": 3, "autopilot_recommendation_uncovered": 4, "semantic_binding_gap": 5, "orphan_test": 6}
        return (score, order.get(g.get("gap_type", ""), 7), g.get("gap_id", ""))

    all_gaps.sort(key=_sort_key)
    return all_gaps

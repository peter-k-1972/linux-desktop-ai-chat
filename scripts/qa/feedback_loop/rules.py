"""
QA Feedback Loop – Regellogik.

Wendet Feedback-Regeln auf normalisierte Zustände an.
Erzeugt FeedbackRuleResult für Projektionen.
Deterministisch.
"""

from __future__ import annotations

from typing import Any

from .models import (
    FailureClassFeedbackState,
    FeedbackRuleResult,
    SubsystemFeedbackState,
    FL_PRIO_001,
    FL_PRIO_002,
    FL_PRIO_003,
    FL_PRIO_004,
    FL_PRIO_005,
    FL_PRIO_006,
    FL_PRIO_007,
    FL_RISK_001,
    FL_RISK_002,
    FL_RISK_003,
    FL_RISK_004,
    FL_RISK_005,
    FL_CTRL_001,
    FL_CTRL_002,
    FL_CTRL_003,
    FL_CTRL_004,
    FL_CTRL_005,
)
from .thresholds import (
    INCIDENT_COUNT_PRESSURE,
    INCIDENT_COUNT_CLUSTER,
    REPLAY_GAP_WARNING,
    REGRESSION_GAP_WARNING,
    DRIFT_COUNT_ESCALATION,
)


def apply_priority_rules(
    subsystem_states: dict[str, SubsystemFeedbackState],
    failure_class_states: dict[str, FailureClassFeedbackState],
    autopilot_focus_subsystem: str,
    autopilot_focus_failure_class: str,
    current_priority_scores: dict[str, int],
) -> list[FeedbackRuleResult]:
    """FL-PRIO-001 bis FL-PRIO-007."""
    results: list[FeedbackRuleResult] = []

    for sub, state in subsystem_states.items():
        old_score = current_priority_scores.get(sub, 0)
        delta = 0
        reasons: list[str] = []
        rule_ids: list[str] = []

        # FL-PRIO-001: repeated incident pressure
        if state.incident_count >= INCIDENT_COUNT_PRESSURE:
            delta += 1
            reasons.append(f"Incident pressure: {state.incident_count} incidents")
            rule_ids.append(FL_PRIO_001)

        # FL-PRIO-002: replay gap (nur bei Incidents im Subsystem)
        if state.incident_count > 0 and state.replay_gap_rate >= REPLAY_GAP_WARNING:
            delta += 1
            reasons.append(f"Replay gap: {state.replay_gap_rate:.0%}")
            rule_ids.append(FL_PRIO_002)

        # FL-PRIO-003: regression gap (nur bei Incidents im Subsystem)
        if state.incident_count > 0 and state.regression_gap_rate >= REGRESSION_GAP_WARNING:
            delta += 1
            reasons.append(f"Regression gap: {state.regression_gap_rate:.0%}")
            rule_ids.append(FL_PRIO_003)

        # FL-PRIO-004: autopilot focus match
        if state.autopilot_focus:
            delta += 1
            reasons.append("Autopilot focus match")
            rule_ids.append(FL_PRIO_004)

        # FL-PRIO-005: dependency sensitivity
        if state.dependency_weight > 1.0 and delta > 0:
            delta = int(delta * state.dependency_weight)
            reasons.append(f"Dependency weight amplifies: {state.dependency_weight}")
            rule_ids.append(FL_PRIO_005)

        if rule_ids and delta != 0:
            new_score = max(0, min(10, old_score + delta))
            results.append(FeedbackRuleResult(
                target_artifact="QA_PRIORITY_SCORE",
                target_key=f"scores.{sub}.Score",
                old_value=old_score,
                new_value=new_score,
                delta=delta,
                reasons=tuple(reasons),
                applied_rule_ids=tuple(rule_ids),
            ))

    # FL-PRIO-006: failure class frequency
    for fc, fc_state in failure_class_states.items():
        if fc_state.incident_count >= INCIDENT_COUNT_PRESSURE and fc == autopilot_focus_failure_class:
            results.append(FeedbackRuleResult(
                target_artifact="QA_PRIORITY_SCORE",
                target_key=f"failure_class.{fc}.priority_boost",
                old_value=0,
                new_value=1,
                delta=1,
                reasons=(f"Failure class {fc} frequency: {fc_state.incident_count}",),
                applied_rule_ids=(FL_PRIO_006,),
            ))

    # FL-PRIO-007: drift pattern
    drift_count = sum(1 for fc, s in failure_class_states.items() if s.drift_related and s.incident_count >= 1)
    if drift_count >= DRIFT_COUNT_ESCALATION:
        for sub, state in subsystem_states.items():
            if state.drift_density > 0:
                results.append(FeedbackRuleResult(
                    target_artifact="QA_PRIORITY_SCORE",
                    target_key=f"scores.{sub}.contract_priority",
                    old_value=0,
                    new_value=1,
                    delta=1,
                    reasons=(f"Drift pattern: {drift_count} drift-related failure classes",),
                    applied_rule_ids=(FL_PRIO_007,),
                ))
                break

    return results


def apply_risk_rules(
    subsystem_states: dict[str, SubsystemFeedbackState],
    failure_class_states: dict[str, FailureClassFeedbackState],
) -> list[FeedbackRuleResult]:
    """FL-RISK-001 bis FL-RISK-005."""
    results: list[FeedbackRuleResult] = []

    for sub, state in subsystem_states.items():
        # FL-RISK-001: incident cluster
        if state.incident_count >= INCIDENT_COUNT_CLUSTER:
            results.append(FeedbackRuleResult(
                target_artifact="QA_RISK_RADAR",
                target_key=f"subsystem.{sub}.cluster_risk",
                old_value=None,
                new_value="elevated",
                delta="elevated",
                reasons=(f"Incident cluster: {state.incident_count} incidents",),
                applied_rule_ids=(FL_RISK_001,),
            ))

        # FL-RISK-002: replay gap
        if state.replay_gap_rate >= REPLAY_GAP_WARNING and state.incident_count > 0:
            results.append(FeedbackRuleResult(
                target_artifact="QA_RISK_RADAR",
                target_key=f"subsystem.{sub}.reproducibility_risk",
                old_value=None,
                new_value="replay_gap",
                delta="replay_gap",
                reasons=(f"Replay gap: {state.replay_gap_rate:.0%}",),
                applied_rule_ids=(FL_RISK_002,),
            ))

        # FL-RISK-003: regression gap
        if state.regression_gap_rate >= REGRESSION_GAP_WARNING and state.incident_count > 0:
            results.append(FeedbackRuleResult(
                target_artifact="QA_RISK_RADAR",
                target_key=f"subsystem.{sub}.regression_protection_risk",
                old_value=None,
                new_value="regression_gap",
                delta="regression_gap",
                reasons=(f"Regression gap: {state.regression_gap_rate:.0%}",),
                applied_rule_ids=(FL_RISK_003,),
            ))

    # FL-RISK-004: repeated failure cluster
    for fc, fc_state in failure_class_states.items():
        if fc_state.incident_count >= INCIDENT_COUNT_CLUSTER:
            results.append(FeedbackRuleResult(
                target_artifact="QA_RISK_RADAR",
                target_key=f"failure_class.{fc}.severity",
                old_value=None,
                new_value="elevated",
                delta="elevated",
                reasons=(f"Failure cluster: {fc_state.incident_count} incidents",),
                applied_rule_ids=(FL_RISK_004,),
            ))

    # FL-RISK-005: drift pattern
    drift_fcs = [fc for fc, s in failure_class_states.items() if s.drift_related and s.incident_count >= 1]
    if len(drift_fcs) >= DRIFT_COUNT_ESCALATION:
        results.append(FeedbackRuleResult(
            target_artifact="QA_RISK_RADAR",
            target_key="structural.drift_risk",
            old_value=None,
            new_value="escalated",
            delta="escalated",
            reasons=(f"Drift pattern: {len(drift_fcs)} failure classes",),
            applied_rule_ids=(FL_RISK_005,),
        ))

    return results


def apply_control_center_rules(
    subsystem_states: dict[str, SubsystemFeedbackState],
    autopilot_data: dict[str, Any],
    current_control_center: dict[str, Any] | None,
) -> list[FeedbackRuleResult]:
    """FL-CTRL-001 bis FL-CTRL-005."""
    results: list[FeedbackRuleResult] = []

    ap_focus = autopilot_data.get("recommended_focus_subsystem") or ""
    ap_sprint = autopilot_data.get("recommended_next_sprint") or ""
    pilot_matched = autopilot_data.get("pilot_constellation_matched")

    # FL-CTRL-001: autopilot recommendation updates current focus
    if ap_focus:
        old_focus = (current_control_center or {}).get("naechster_qa_sprint", {})
        old_sub = old_focus.get("subsystem", "") if isinstance(old_focus, dict) else ""
        if old_sub != ap_focus:
            results.append(FeedbackRuleResult(
                target_artifact="QA_CONTROL_CENTER",
                target_key="naechster_qa_sprint",
                old_value=old_focus,
                new_value={"subsystem": ap_focus, "schritt": ap_sprint, "source": "QA_AUTOPILOT_V2"},
                delta="updated",
                reasons=(f"Autopilot focus: {ap_focus}",),
                applied_rule_ids=(FL_CTRL_001,),
            ))

    # FL-CTRL-002: replay gap governance alert
    replay_ratio = 1.0
    if autopilot_data.get("supporting_evidence"):
        refs = autopilot_data["supporting_evidence"].get("replay_gap_refs") or []
        if refs:
            replay_ratio = refs[0].get("replay_defined_ratio", 0.5)
    if replay_ratio < 0.5:
        results.append(FeedbackRuleResult(
            target_artifact="QA_CONTROL_CENTER",
            target_key="warnsignale.replay_gap",
            old_value=None,
            new_value="governance_alert",
            delta="governance_alert",
            reasons=(f"Replay gap: {1-replay_ratio:.0%} without replay",),
            applied_rule_ids=(FL_CTRL_002,),
        ))

    # FL-CTRL-003: regression gap governance alert
    reg_ratio = 0.0
    if autopilot_data.get("supporting_evidence"):
        refs = autopilot_data["supporting_evidence"].get("replay_gap_refs") or []
        if refs:
            reg_ratio = refs[0].get("regression_bound_ratio", 0.0)
    if reg_ratio < 0.3:
        results.append(FeedbackRuleResult(
            target_artifact="QA_CONTROL_CENTER",
            target_key="warnsignale.regression_gap",
            old_value=None,
            new_value="governance_alert",
            delta="governance_alert",
            reasons=(f"Regression gap: {1-reg_ratio:.0%} without binding",),
            applied_rule_ids=(FL_CTRL_003,),
        ))

    # FL-CTRL-004: repeated drift escalation
    escalations = autopilot_data.get("escalations") or []
    drift_esc = [e for e in escalations if "DRIFT" in str(e.get("code", ""))]
    if drift_esc:
        results.append(FeedbackRuleResult(
            target_artifact="QA_CONTROL_CENTER",
            target_key="escalations.drift",
            old_value=None,
            new_value="escalation",
            delta="escalation",
            reasons=("Drift pattern escalation from Autopilot",),
            applied_rule_ids=(FL_CTRL_004,),
        ))

    # FL-CTRL-005: pilot constellation status
    if pilot_matched:
        results.append(FeedbackRuleResult(
            target_artifact="QA_CONTROL_CENTER",
            target_key="pilot_constellation_status",
            old_value=None,
            new_value=pilot_matched,
            delta="updated",
            reasons=(f"Pilot {pilot_matched.get('id')}: {pilot_matched.get('name')}",),
            applied_rule_ids=(FL_CTRL_005,),
        ))

    return results

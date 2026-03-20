"""
QA Feedback Loop – Projektionen.

Baut FeedbackProjectionReport aus normalisierten Zuständen und Regel-Ergebnissen.
Projiziert Vorschläge auf QA_CONTROL_CENTER, QA_PRIORITY_SCORE, QA_RISK_RADAR.
Schreibt NICHT in Dateien – liefert nur den Report.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .loader import FeedbackLoopInputs
from .models import (
    FailureClassFeedbackState,
    FeedbackProjectionReport,
    FeedbackRuleResult,
    SubsystemFeedbackState,
)
from .normalizer import normalize_to_failure_class_states, normalize_to_subsystem_states
from .rules import (
    apply_control_center_rules,
    apply_priority_rules,
    apply_risk_rules,
)


def _extract_current_priority_scores(priority_data: dict[str, Any] | None) -> dict[str, int]:
    out: dict[str, int] = {}
    if not priority_data:
        return out
    for s in priority_data.get("scores", []):
        sub = s.get("Subsystem")
        if sub:
            out[sub] = int(s.get("Score", 0))
    return out


def run_feedback_projections(
    inputs: FeedbackLoopInputs,
    optional_timestamp: str | None = None,
) -> FeedbackProjectionReport:
    """
    Führt den vollständigen Feedback-Projektionslauf durch.
    Deterministisch: gleiche Inputs -> gleiche Outputs.
    optional_timestamp: Falls gesetzt, wird statt datetime.now() verwendet (für Tests/Reproduzierbarkeit).
    """
    generated_at = (
        optional_timestamp
        if optional_timestamp is not None
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    # 1. Normalisieren
    subsystem_states = normalize_to_subsystem_states(inputs)
    failure_class_states = normalize_to_failure_class_states(inputs)

    # 2. Autopilot-Daten
    autopilot = inputs.autopilot_v2 or {}
    ap_focus_sub = autopilot.get("recommended_focus_subsystem") or ""
    ap_focus_fc = autopilot.get("recommended_focus_failure_class") or ""

    # 3. Aktuelle Governance-Werte
    current_priority = _extract_current_priority_scores(inputs.priority_score)
    current_cc = inputs.control_center

    # 4. Regeln anwenden
    priority_results = apply_priority_rules(
        subsystem_states,
        failure_class_states,
        ap_focus_sub,
        ap_focus_fc,
        current_priority,
    )
    risk_results = apply_risk_rules(subsystem_states, failure_class_states)
    ctrl_results = apply_control_center_rules(
        subsystem_states,
        autopilot,
        current_cc,
    )

    all_rule_results = priority_results + risk_results + ctrl_results

    # 5. Global Warnings
    global_warnings: list[str] = []
    if not inputs.incident_index:
        global_warnings.append("incidents/index.json fehlt – Projektion eingeschränkt")
    if not inputs.analytics:
        global_warnings.append("incidents/analytics.json fehlt – Projektion eingeschränkt")
    if not inputs.autopilot_v2:
        global_warnings.append("QA_AUTOPILOT_V2.json fehlt – Autopilot-Fokus nicht verfügbar")

    for w in inputs.analytics.get("warnings", []) if inputs.analytics else []:
        msg = w.get("message", str(w))
        if msg and msg not in global_warnings:
            global_warnings.append(msg)

    # 6. Eskalationen
    escalations: list[str] = []
    for e in autopilot.get("escalations", []) or []:
        code = e.get("code", "")
        msg = e.get("message", "")
        if code or msg:
            escalations.append(f"{code}: {msg}" if code else msg)

    for sub, state in subsystem_states.items():
        if state.escalation_level >= 2:
            escalations.append(f"Subsystem {sub}: escalation_level={state.escalation_level}")

    # 7. Suppressed Changes (z.B. wenn Zielartefakt fehlt)
    suppressed: list[FeedbackRuleResult] = []
    for r in all_rule_results:
        if r.target_artifact == "QA_PRIORITY_SCORE" and not inputs.priority_score:
            suppressed.append(r)
        elif r.target_artifact == "QA_RISK_RADAR" and not inputs.risk_radar_raw:
            suppressed.append(r)
        elif r.target_artifact == "QA_CONTROL_CENTER" and not inputs.control_center:
            suppressed.append(r)

    # 8. Report bauen
    return FeedbackProjectionReport(
        generated_at=generated_at,
        generator="feedback_loop",
        input_sources=inputs.loaded_sources,
        global_warnings=global_warnings,
        per_subsystem_results=subsystem_states,
        per_failure_class_results=failure_class_states,
        escalations=escalations,
        suppressed_changes=suppressed,
        rule_results=all_rule_results,
    )

"""
QA Autopilot v3 – Gap-Erkennungsregeln.

1. Test Gap: high pressure + replay gap => missing_replay_test, etc.
2. Guard Gap: network failure cluster => failure_replay_guard gap, etc.
3. Translation Gap: incident without replay => incident_not_bound_to_replay, etc.
"""

from __future__ import annotations

from typing import Any

from .models import (
    DRIFT_FAILURE_CLASSES,
    GuardGapFinding,
    PILOT_CONSTELLATIONS,
    TestGapFinding,
    TranslationGapFinding,
)

# Schwellen
INCIDENT_PRESSURE_HIGH = 2
REPLAY_GAP_THRESHOLD = 0.5
REGRESSION_GAP_THRESHOLD = 0.3
DRIFT_COUNT_FOR_CONTRACT = 2


def _detect_test_gaps(
    subsystem_states: dict[str, Any],
    failure_class_states: dict[str, Any],
    incidents: list[dict],
) -> list[TestGapFinding]:
    """Test Gap: high incident pressure + replay/regression gap => missing test."""
    findings: list[TestGapFinding] = []
    seen: set[tuple[str, str, str]] = set()
    fid = 0

    for sub, state in subsystem_states.items():
        inc_count = getattr(state, "incident_count", 0)
        replay_gap = getattr(state, "replay_gap_rate", 0.0)
        reg_gap = getattr(state, "regression_gap_rate", 0.0)
        drift = getattr(state, "drift_density", 0.0)

        if inc_count < 1:
            continue

        # 1. high pressure + replay gap => missing_replay_test
        if inc_count >= INCIDENT_PRESSURE_HIGH and replay_gap >= REPLAY_GAP_THRESHOLD:
            key = (sub, "replay", "missing_replay_test")
            if key not in seen:
                seen.add(key)
                fid += 1
                findings.append(TestGapFinding(
                    id=f"TG-{fid:03d}",
                    subsystem=sub,
                    failure_class=_dominant_failure_class(incidents, sub),
                    gap_type="missing_replay_test",
                    reasons=(f"Incident pressure: {inc_count}, Replay gap: {replay_gap:.0%}",),
                    incident_count=inc_count,
                    priority="high" if inc_count >= 3 else "medium",
                ))

        # 2. high pressure + regression gap => missing_regression_test
        if inc_count >= INCIDENT_PRESSURE_HIGH and reg_gap >= REGRESSION_GAP_THRESHOLD:
            key = (sub, "regression", "missing_regression_test")
            if key not in seen:
                seen.add(key)
                fid += 1
                findings.append(TestGapFinding(
                    id=f"TG-{fid:03d}",
                    subsystem=sub,
                    failure_class=_dominant_failure_class(incidents, sub),
                    gap_type="missing_regression_test",
                    reasons=(f"Incident pressure: {inc_count}, Regression gap: {reg_gap:.0%}",),
                    incident_count=inc_count,
                    priority="high" if inc_count >= 3 else "medium",
                ))

    # 3. repeated drift => missing_contract_test
    for fc, state in failure_class_states.items():
        if fc not in DRIFT_FAILURE_CLASSES:
            continue
        inc_count = getattr(state, "incident_count", 0)
        if inc_count >= DRIFT_COUNT_FOR_CONTRACT:
            subs = _subsystems_for_failure_class(incidents, fc)
            for sub in subs:
                key = (sub, fc, "missing_contract_test")
                if key not in seen:
                    seen.add(key)
                    fid += 1
                    findings.append(TestGapFinding(
                        id=f"TG-{fid:03d}",
                        subsystem=sub,
                        failure_class=fc,
                        gap_type="missing_contract_test",
                        reasons=(f"Repeated drift: {inc_count} incidents with {fc}",),
                        incident_count=inc_count,
                        priority="high",
                    ))

    return findings


def _detect_guard_gaps(
    subsystem_states: dict[str, Any],
    failure_class_states: dict[str, Any],
    incidents: list[dict],
) -> list[GuardGapFinding]:
    """Guard Gap: network failure cluster => failure_replay_guard gap, etc."""
    findings: list[GuardGapFinding] = []
    seen: set[tuple[str, str, str]] = set()
    fid = 0

    # Network-failure-ähnliche Failure-Classes
    NETWORK_FAILURE_FC = {"rag_silent_failure", "optional_dependency_missing", "async_race", "degraded_mode_failure"}
    EVENT_CONTRACT_FC = {"contract_schema_drift", "debug_false_truth", "ui_state_drift"}
    STARTUP_FC = {"startup_ordering", "degraded_mode_failure", "optional_dependency_missing"}

    for sub, state in subsystem_states.items():
        inc_count = getattr(state, "incident_count", 0)
        if inc_count < 1:
            continue

        sub_incidents = [i for i in incidents if i.get("subsystem") == sub]
        fc_counts: dict[str, int] = {}
        for inc in sub_incidents:
            fc = inc.get("failure_class") or ""
            if fc:
                fc_counts[fc] = fc_counts.get(fc, 0) + 1

        pilot_match = _pilot_for_subsystem(sub)

        # 1. network failure cluster => failure_replay_guard gap
        network_count = sum(fc_counts.get(fc, 0) for fc in NETWORK_FAILURE_FC)
        if network_count >= 2:
            key = (sub, "failure_replay_guard", "guard")
            if key not in seen:
                seen.add(key)
                fid += 1
                findings.append(GuardGapFinding(
                    id=f"GG-{fid:03d}",
                    subsystem=sub,
                    failure_class=_dominant_failure_class(incidents, sub),
                    guard_type="failure_replay_guard",
                    reasons=(f"Network failure cluster: {network_count} incidents",),
                    pilot_id=pilot_match["id"] if pilot_match and pilot_match.get("subsystems", set()) & {sub} else None,
                    priority="high" if network_count >= 3 else "medium",
                ))

        # 2. event_contract_drift => event_contract_guard gap
        drift_count = sum(fc_counts.get(fc, 0) for fc in EVENT_CONTRACT_FC)
        if drift_count >= 1:
            key = (sub, "event_contract_guard", "guard")
            if key not in seen:
                seen.add(key)
                fid += 1
                findings.append(GuardGapFinding(
                    id=f"GG-{fid:03d}",
                    subsystem=sub,
                    failure_class=_dominant_failure_class(incidents, sub, prefer=EVENT_CONTRACT_FC),
                    guard_type="event_contract_guard",
                    reasons=(f"Event/contract drift: {drift_count} incidents",),
                    pilot_id=3 if sub == "Debug/EventBus" else None,
                    priority="high" if drift_count >= 2 else "medium",
                ))

        # 3. startup degradation pattern => startup_degradation_guard gap
        startup_count = sum(fc_counts.get(fc, 0) for fc in STARTUP_FC)
        if startup_count >= 1 and sub in {"Startup/Bootstrap", "Provider/Ollama", "RAG"}:
            key = (sub, "startup_degradation_guard", "guard")
            if key not in seen:
                seen.add(key)
                fid += 1
                findings.append(GuardGapFinding(
                    id=f"GG-{fid:03d}",
                    subsystem=sub,
                    failure_class=_dominant_failure_class(incidents, sub, prefer=STARTUP_FC),
                    guard_type="startup_degradation_guard",
                    reasons=(f"Startup degradation pattern: {startup_count} incidents",),
                    pilot_id=1 if sub in {"Startup/Bootstrap", "Provider/Ollama"} else (2 if sub == "RAG" else None),
                    priority="high" if startup_count >= 2 else "medium",
                ))

    return findings


def _detect_translation_gaps(
    incidents: list[dict],
    autopilot: dict,
    priority_score: dict | None,
) -> list[TranslationGapFinding]:
    """Translation Gap: incident without replay/regression => not bound."""
    findings: list[TranslationGapFinding] = []
    fid = 0

    ap_focus = autopilot.get("recommended_focus_subsystem") or ""

    for inc in incidents:
        inc_id = inc.get("id") or inc.get("incident_id") or f"inc-{fid}"
        sub = inc.get("subsystem") or ""
        fc = inc.get("failure_class") or ""
        replay_status = inc.get("replay_status")
        binding_status = inc.get("binding_status")

        # 1. incident without replay => incident_not_bound_to_replay
        if replay_status is None or replay_status in ("", "missing"):
            fid += 1
            findings.append(TranslationGapFinding(
                id=f"TR-{fid:03d}",
                incident_id=str(inc_id),
                subsystem=sub,
                failure_class=fc,
                gap_type="incident_not_bound_to_replay",
                reasons=(f"Replay status: {replay_status or 'missing'}",),
                priority="medium",
            ))

        # 2. incident without regression => incident_not_bound_to_regression
        # Bound if: binding_status == catalog_bound OR qa.status in (bound_to_regression, closed)
        inc_status = inc.get("status")
        is_bound = (
            binding_status == "catalog_bound"
            or inc_status in ("bound_to_regression", "closed")
        )
        if not is_bound:
            fid += 1
            findings.append(TranslationGapFinding(
                id=f"TR-{fid:03d}",
                incident_id=str(inc_id),
                subsystem=sub,
                failure_class=fc,
                gap_type="incident_not_bound_to_regression",
                reasons=(f"Binding status: {binding_status or 'open'}",),
                priority="medium",
            ))

    # 3. pilot active but not reflected in backlog => pilot_not_sufficiently_translated
    pilot_matched = autopilot.get("pilot_constellation_matched")
    if pilot_matched and ap_focus and priority_score:
        scores = [s for s in (priority_score.get("scores") or []) if isinstance(s, dict)]
        top3_subs = {
            s.get("Subsystem")
            for s in sorted(scores, key=lambda x: -_safe_score(x))[:3]
            if s.get("Subsystem")
        }
        if top3_subs and ap_focus not in top3_subs:
            fid += 1
            findings.append(TranslationGapFinding(
                id=f"TR-{fid:03d}",
                incident_id="pilot",
                subsystem=ap_focus,
                failure_class=autopilot.get("recommended_focus_failure_class", ""),
                gap_type="pilot_not_sufficiently_translated",
                reasons=(f"Pilot {pilot_matched.get('name', '')} active, focus not in top 3 priorities",),
                priority="high",
            ))

    return findings


def _safe_score(x: Any) -> int:
    """Sichere Extraktion von Score aus Priority-Score-Eintrag."""
    if not isinstance(x, dict):
        return 0
    v = x.get("Score")
    try:
        return int(v) if v is not None and v != "" else 0
    except (ValueError, TypeError):
        return 0


def _dominant_failure_class(
    incidents: list[dict],
    subsystem: str,
    prefer: set[str] | None = None,
) -> str:
    """Dominante Failure-Class für Subsystem."""
    sub_inc = [i for i in incidents if i.get("subsystem") == subsystem]
    if not sub_inc:
        return "async_race"
    fc_counts: dict[str, int] = {}
    for inc in sub_inc:
        fc = inc.get("failure_class") or ""
        if fc:
            fc_counts[fc] = fc_counts.get(fc, 0) + 1
    if not fc_counts:
        return "async_race"
    if prefer:
        for fc in sorted(fc_counts, key=lambda x: -fc_counts[x]):
            if fc in prefer:
                return fc
    return max(fc_counts, key=fc_counts.get)


def _subsystems_for_failure_class(incidents: list[dict], failure_class: str) -> set[str]:
    """Subsysteme mit gegebener Failure-Class."""
    return {i.get("subsystem") for i in incidents if i.get("failure_class") == failure_class and i.get("subsystem")}


def _pilot_for_subsystem(subsystem: str) -> dict | None:
    """Pilotkonstellation für Subsystem."""
    for p in PILOT_CONSTELLATIONS:
        if subsystem in p.get("subsystems", set()):
            return p
    return None


def apply_gap_rules(
    subsystem_states: dict[str, Any],
    failure_class_states: dict[str, Any],
    incidents: list[dict],
    autopilot: dict,
    priority_score: dict | None,
) -> tuple[list[TestGapFinding], list[GuardGapFinding], list[TranslationGapFinding]]:
    """Wendet alle Gap-Regeln an."""
    test_gaps = _detect_test_gaps(subsystem_states, failure_class_states, incidents)
    guard_gaps = _detect_guard_gaps(subsystem_states, failure_class_states, incidents)
    translation_gaps = _detect_translation_gaps(incidents, autopilot, priority_score)
    return test_gaps, guard_gaps, translation_gaps

"""
QA Feedback Loop – Normalisierung.

Transformiert geladene Inputs in SubsystemFeedbackState und FailureClassFeedbackState.
Deterministisch, gleiche Inputs -> gleiche Outputs.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from .loader import FeedbackLoopInputs
from .models import FailureClassFeedbackState, SubsystemFeedbackState
from .thresholds import (
    DEPENDENCY_WEIGHT_HIGH,
    DEPENDENCY_WEIGHT_LOW,
    DEPENDENCY_WEIGHT_MEDIUM,
    SEVERITY_WEIGHTS,
)
from .utils import safe_get

# Startup-kritische Subsysteme (höhere dependency_weight)
STARTUP_CRITICAL = {"Startup/Bootstrap", "Provider/Ollama", "RAG", "Persistenz/SQLite"}

# Drift-relevante Failure-Classes
DRIFT_FAILURE_CLASSES = {"contract_schema_drift", "debug_false_truth", "metrics_false_success"}


def _severity_weight(sev: str) -> float:
    return SEVERITY_WEIGHTS.get((sev or "").lower(), 2.0)


def _normalize_analytics_qa_coverage(analytics: dict[str, Any] | None) -> tuple[float, float]:
    """Replay- und Regression-Ratio aus analytics. Gibt (replay_defined_ratio, regression_bound_ratio)."""
    if not analytics:
        return 0.5, 0.0
    qa = analytics.get("qa_coverage") or analytics
    replay = qa.get("replay_defined_ratio")
    reg = qa.get("regression_bound_ratio")
    if replay is None:
        replay = 0.5
    if reg is None:
        reg = 0.0
    return float(replay), float(reg)


def _subsystem_incident_counts(incidents: list[dict]) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for inc in incidents:
        sub = inc.get("subsystem") or "_unknown"
        if sub != "_unknown":
            out[sub] += 1
    return dict(out)


def _failure_class_counts(incidents: list[dict]) -> dict[str, int]:
    out: dict[str, int] = defaultdict(int)
    for inc in incidents:
        fc = inc.get("failure_class") or "_unknown"
        if fc != "_unknown":
            out[fc] += 1
    return dict(out)


def _subsystem_weighted_severity(incidents: list[dict]) -> dict[str, float]:
    out: dict[str, float] = defaultdict(float)
    for inc in incidents:
        sub = inc.get("subsystem") or "_unknown"
        if sub != "_unknown":
            out[sub] += _severity_weight(inc.get("severity"))
    return dict(out)


def _failure_class_weighted_severity(incidents: list[dict]) -> dict[str, float]:
    out: dict[str, float] = defaultdict(float)
    for inc in incidents:
        fc = inc.get("failure_class") or "_unknown"
        if fc != "_unknown":
            out[fc] += _severity_weight(inc.get("severity"))
    return dict(out)


def _subsystem_replay_gap(incidents: list[dict]) -> dict[str, float]:
    """Anteil Incidents pro Subsystem ohne Replay (replay_status fehlt oder nicht verified)."""
    total: dict[str, int] = defaultdict(int)
    no_replay: dict[str, int] = defaultdict(int)
    for inc in incidents:
        sub = inc.get("subsystem") or "_unknown"
        if sub == "_unknown":
            continue
        total[sub] += 1
        status = inc.get("replay_status")
        if status is None or status in ("", "missing"):
            no_replay[sub] += 1
    return {
        sub: (no_replay[sub] / total[sub]) if total[sub] > 0 else 0.0
        for sub in total
    }


def _subsystem_regression_gap(incidents: list[dict]) -> dict[str, float]:
    """Anteil Incidents pro Subsystem ohne Regression-Binding."""
    total: dict[str, int] = defaultdict(int)
    no_binding: dict[str, int] = defaultdict(int)
    for inc in incidents:
        sub = inc.get("subsystem") or "_unknown"
        if sub == "_unknown":
            continue
        total[sub] += 1
        has_binding = (
            inc.get("binding_status") == "catalog_bound"
            or inc.get("status") in ("bound_to_regression", "closed")
        )
        if not has_binding:
            no_binding[sub] += 1
    return {
        sub: (no_binding[sub] / total[sub]) if total[sub] > 0 else 0.0
        for sub in total
    }


def _subsystem_drift_density(incidents: list[dict]) -> dict[str, float]:
    """Anteil Drift-Failure-Classes pro Subsystem."""
    total: dict[str, int] = defaultdict(int)
    drift: dict[str, int] = defaultdict(int)
    for inc in incidents:
        sub = inc.get("subsystem") or "_unknown"
        if sub == "_unknown":
            continue
        total[sub] += 1
        if inc.get("failure_class") in DRIFT_FAILURE_CLASSES:
            drift[sub] += 1
    return {
        sub: (drift[sub] / total[sub]) if total[sub] > 0 else 0.0
        for sub in total
    }


def _subsystem_cluster_density(
    incidents: list[dict],
    clusters: dict[str, Any] | list[Any],
) -> dict[str, float]:
    """Cluster-Dichte pro Subsystem. Cluster aus index oder analytics."""
    sub_counts: dict[str, int] = defaultdict(int)
    for inc in incidents:
        sub = inc.get("subsystem") or "_unknown"
        if sub != "_unknown":
            sub_counts[sub] += 1
    total_inc = sum(sub_counts.values()) or 1
    if isinstance(clusters, dict):
        ss_cluster = clusters.get("subsystem") or {}
        if isinstance(ss_cluster, dict):
            return {
                sub: (ss_cluster.get(sub, 0) / total_inc) if total_inc > 0 else 0.0
                for sub in set(sub_counts) | set(ss_cluster)
            }
    return {sub: 0.0 for sub in sub_counts}


def normalize_to_subsystem_states(inputs: FeedbackLoopInputs) -> dict[str, SubsystemFeedbackState]:
    """Erzeugt SubsystemFeedbackState pro Subsystem."""
    incidents_raw = safe_get(inputs.incident_index, "incidents") or []
    incidents = incidents_raw if isinstance(incidents_raw, list) else []
    analytics = inputs.analytics or {}
    autopilot = inputs.autopilot_v2 or {}
    clusters = safe_get(inputs.incident_index, "clusters") or analytics.get("clusters") or {}

    replay_ratio, reg_ratio = _normalize_analytics_qa_coverage(analytics)
    replay_gap = 1.0 - replay_ratio
    reg_gap = 1.0 - reg_ratio

    inc_by_sub = _subsystem_incident_counts(incidents)
    sev_by_sub = _subsystem_weighted_severity(incidents)
    replay_by_sub = _subsystem_replay_gap(incidents)
    regression_by_sub = _subsystem_regression_gap(incidents)
    drift_by_sub = _subsystem_drift_density(incidents)
    cluster_by_sub = _subsystem_cluster_density(incidents, clusters)

    autopilot_focus_sub = autopilot.get("recommended_focus_subsystem") or ""

    all_subs = set(inc_by_sub.keys())
    if inputs.priority_score:
        for s in inputs.priority_score.get("scores", []):
            sub = s.get("Subsystem")
            if sub:
                all_subs.add(sub)
    if not all_subs:
        all_subs = {"RAG", "Startup/Bootstrap", "Debug/EventBus"}

    result: dict[str, SubsystemFeedbackState] = {}
    for sub in sorted(all_subs):
        inc_count = inc_by_sub.get(sub, 0)
        w_sev = sev_by_sub.get(sub, 0.0)
        sub_replay_gap = replay_by_sub.get(sub, replay_gap if inc_count > 0 else 0.0)
        sub_reg_gap = regression_by_sub.get(sub, reg_gap if inc_count > 0 else 0.0)
        drift = drift_by_sub.get(sub, 0.0)
        cluster = cluster_by_sub.get(sub, 0.0)
        ap_focus = sub == autopilot_focus_sub
        dep_weight = DEPENDENCY_WEIGHT_HIGH if sub in STARTUP_CRITICAL else DEPENDENCY_WEIGHT_MEDIUM

        pressure = (
            inc_count * 2.0
            + w_sev * 0.5
            + sub_replay_gap * 3.0
            + sub_reg_gap * 3.0
            + drift * 2.0
            + cluster * 1.5
            + (3.0 if ap_focus else 0.0)
        ) * dep_weight

        esc_level = 0
        if inc_count >= 3:
            esc_level = 3
        elif inc_count >= 2 and sub_replay_gap > 0.5:
            esc_level = 2
        elif inc_count >= 1 and sub_reg_gap > 0.8:
            esc_level = 1

        result[sub] = SubsystemFeedbackState(
            subsystem=sub,
            incident_count=inc_count,
            weighted_severity=w_sev,
            replay_gap_rate=sub_replay_gap,
            regression_gap_rate=sub_reg_gap,
            drift_density=drift,
            cluster_density=cluster,
            autopilot_focus=ap_focus,
            dependency_weight=dep_weight,
            feedback_pressure_score=round(pressure, 2),
            escalation_level=esc_level,
        )
    return result


def normalize_to_failure_class_states(
    inputs: FeedbackLoopInputs,
) -> dict[str, FailureClassFeedbackState]:
    """Erzeugt FailureClassFeedbackState pro Failure-Class."""
    incidents_raw = safe_get(inputs.incident_index, "incidents") or []
    incidents = incidents_raw if isinstance(incidents_raw, list) else []
    analytics = inputs.analytics or {}
    autopilot = inputs.autopilot_v2 or {}

    replay_ratio, reg_ratio = _normalize_analytics_qa_coverage(analytics)
    replay_gap = 1.0 - replay_ratio
    reg_gap = 1.0 - reg_ratio

    fc_counts = _failure_class_counts(incidents)
    fc_sev = _failure_class_weighted_severity(incidents)
    fc_subs: dict[str, set[str]] = defaultdict(set)
    for inc in incidents:
        fc = inc.get("failure_class")
        sub = inc.get("subsystem")
        if fc and sub:
            fc_subs[fc].add(sub)

    ap_fc = autopilot.get("recommended_focus_failure_class") or ""

    all_fc = set(fc_counts.keys())
    fc_freq = analytics.get("risk_signals", {}).get("failure_class_frequency") or {}
    if isinstance(fc_freq, dict):
        all_fc.update(fc_freq.keys())
    if not all_fc:
        all_fc = {"rag_silent_failure", "async_race", "ui_state_drift"}

    result: dict[str, FailureClassFeedbackState] = {}
    for fc in sorted(all_fc):
        inc_count = fc_counts.get(fc, 0)
        w_sev = fc_sev.get(fc, 0.0)
        sub_count = len(fc_subs.get(fc, set()))
        drift = fc in DRIFT_FAILURE_CLASSES
        ap_focus = fc == ap_fc

        pressure = (
            inc_count * 2.0
            + w_sev * 0.5
            + replay_gap * 1.5
            + reg_gap * 1.5
            + (2.0 if drift else 0.0)
            + (2.0 if ap_focus else 0.0)
        )

        esc_level = 0
        if inc_count >= 3 and drift:
            esc_level = 2
        elif inc_count >= 2:
            esc_level = 1

        result[fc] = FailureClassFeedbackState(
            failure_class=fc,
            incident_count=inc_count,
            subsystem_count=sub_count,
            weighted_severity=w_sev,
            replay_gap_rate=replay_gap,
            regression_gap_rate=reg_gap,
            drift_related=drift,
            feedback_pressure_score=round(pressure, 2),
            escalation_level=esc_level,
        )
    return result

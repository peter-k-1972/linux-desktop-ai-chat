#!/usr/bin/env python3
"""
QA Autopilot v2 Generator – Linux Desktop Chat.

Konsolidiert QA-Artefakte und Incident-Analytics zu einer QA-Empfehlung.

Inputs:
- docs/qa/QA_PRIORITY_SCORE.json
- docs/qa/QA_HEATMAP.json
- docs/qa/QA_STABILITY_INDEX.json
- docs/qa/incidents/index.json
- docs/qa/incidents/analytics.json

Optional: QA_RISK_RADAR.md, QA_DEPENDENCY_GRAPH.md, QA_CONTROL_CENTER.json

Output:
- docs/qa/QA_AUTOPILOT_V2.json

Verwendung:
  python scripts/qa/generate_autopilot_v2.py
  python scripts/qa/generate_autopilot_v2.py --input-dir docs/qa --output docs/qa/QA_AUTOPILOT_V2.json --pretty
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Projekt-Root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_INPUT_DIR = _PROJECT_ROOT / "docs" / "qa"
_DEFAULT_OUTPUT = _PROJECT_ROOT / "docs" / "qa" / "QA_AUTOPILOT_V2.json"

# Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOG = logging.getLogger(__name__)

# Gewichtung incident-based (reale Signale stärker)
WEIGHT_SUBSYSTEM_RISK_SCORE = 1.5
WEIGHT_INCIDENT_FREQUENCY = 1.5
WEIGHT_REPLAY_GAP_RATIO = 1.3
WEIGHT_REGRESSION_GAP_RATIO = 1.3
WEIGHT_FAILURE_CLASS_FREQUENCY = 1.2

# Gewichtung risk-based
WEIGHT_PRIORITY_SCORE = 1.0
WEIGHT_HEATMAP_WEAK_SPOTS = 0.8
WEIGHT_STARTUP_CRITICALITY = 1.2
WEIGHT_DRIFT_SIGNALS = 1.2

# Supporting
WEIGHT_STABILITY_INDEX = 0.5

# Startup-kritische Subsysteme
STARTUP_CRITICAL_SUBSYSTEMS = {"Startup/Bootstrap", "Provider/Ollama", "RAG", "Persistenz/SQLite"}

# Drift-Signal-Failure-Classes
DRIFT_FAILURE_CLASSES = {"contract_schema_drift", "debug_false_truth", "metrics_false_success"}

# Failure Class -> Test Domain
FAILURE_CLASS_TO_TEST_DOMAIN = {
    "rag_silent_failure": "failure_modes",
    "optional_dependency_missing": "failure_modes",
    "startup_ordering": "startup",
    "degraded_mode_failure": "startup",
    "contract_schema_drift": "contract",
    "debug_false_truth": "drift_governance",
    "async_race": "async_behavior",
    "ui_state_drift": "drift_governance",
    "cross_layer_incident": "cross_layer",
}
DEFAULT_TEST_DOMAIN = "failure_modes"

# Failure Class -> Guard Type
FAILURE_CLASS_TO_GUARD_TYPE = {
    "startup_ordering": "startup_degradation_guard",
    "degraded_mode_failure": "startup_degradation_guard",
    "rag_silent_failure": "failure_replay_guard",
    "optional_dependency_missing": "failure_replay_guard",
    "contract_schema_drift": "event_contract_guard",
    "debug_false_truth": "event_contract_guard",
    "async_race": "cross_layer_guard",
    "ui_state_drift": "event_contract_guard",
    "cross_layer_incident": "cross_layer_guard",
}
DEFAULT_GUARD_TYPE = "failure_replay_guard"

# Drei Pilotkonstellationen (QA_AUTOPILOT_V2_PILOT_CONSTELLATIONS.md)
# 1. Startup / Ollama unreachable
# 2. RAG / ChromaDB network/dependency failure
# 3. Debug/EventBus / EventType drift
PILOT_CONSTELLATIONS = (
    {
        "id": 1,
        "name": "Startup / Ollama unreachable",
        "subsystems": {"Startup/Bootstrap", "Provider/Ollama"},
        "failure_classes": {"startup_ordering", "degraded_mode_failure", "optional_dependency_missing"},
        "guard_type": "startup_degradation_guard",
        "guard_type_secondary": "contract_guard",
        "keywords": ("ollama", "init-reihenfolge", "nicht erreichbar", "degraded_mode"),
    },
    {
        "id": 2,
        "name": "RAG / ChromaDB network/dependency failure",
        "subsystems": {"RAG"},
        "failure_classes": {"rag_silent_failure", "optional_dependency_missing", "degraded_mode_failure"},
        "guard_type": "failure_replay_guard",
        "guard_type_secondary": None,
        "keywords": ("chroma", "embedding", "netzwerk", "dependency"),
    },
    {
        "id": 3,
        "name": "Debug/EventBus / EventType drift",
        "subsystems": {"Debug/EventBus"},
        "failure_classes": {"debug_false_truth", "contract_schema_drift"},
        "guard_type": "event_contract_guard",
        "guard_type_secondary": None,
        "keywords": ("drift", "eventtype", "registry", "timeline"),
    },
)

# Subsystem -> Sprint-Komponente (lesbarer Name)
SUBSYSTEM_SPRINT_NAMES = {
    "Startup/Bootstrap": "Startup Degradation",
    "RAG": "RAG Failure Replay",
    "Provider/Ollama": "Ollama Init Contract",
    "Debug/EventBus": "EventType Drift Sentinel",
    "Chat": "Chat Cross-Layer",
    "Agentensystem": "Agent Cross-Layer",
    "Prompt-System": "Prompt Failure",
    "Metrics": "Metrics Cross-Layer",
    "Persistenz/SQLite": "DB Contract",
    "Tools": "Tools Async",
}


def load_json(path: Path) -> dict | None:
    """Lädt JSON-Datei. Gibt None bei Fehler."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        LOG.warning("Konnte %s nicht laden: %s", path, e)
        return None


def safe_load_optional(path: Path, warn_if_missing: bool = True) -> dict | None:
    """Lädt optionale JSON-Datei. WARN wenn fehlend und warn_if_missing."""
    data = load_json(path)
    if data is None and warn_if_missing:
        LOG.warning("Optionaler Input fehlt: %s", path)
    return data


def extract_priority_scores(data: dict | None) -> dict[str, dict]:
    """Extrahiert Subsystem -> {score, prioritaet, naechster_schritt, begruendung}."""
    result: dict[str, dict] = {}
    if not data:
        return result
    for s in data.get("scores", []):
        sub = s.get("Subsystem", "").strip()
        if sub:
            result[sub] = {
                "score": s.get("Score", 0),
                "prioritaet": s.get("Prioritaet", ""),
                "naechster_schritt": s.get("Naechster_QA_Schritt", ""),
                "begruendung": s.get("Begruendung", ""),
            }
    return result


def extract_heatmap_signals(data: dict | None) -> tuple[dict[str, dict], list[dict]]:
    """Extrahiert Heatmap pro Subsystem und top3_hotspots."""
    heatmap_by_sub: dict[str, dict] = {}
    hotspots: list[dict] = []
    if not data:
        return heatmap_by_sub, hotspots
    for row in data.get("heatmap", []):
        sub = row.get("Subsystem", "").strip()
        if sub:
            heatmap_by_sub[sub] = dict(row)
    hotspots = data.get("top3_hotspots", [])
    return heatmap_by_sub, hotspots


def extract_stability_signals(data: dict | None) -> dict:
    """Extrahiert Stability-Index-Signale."""
    result = {
        "index": 0,
        "stabilitaetsklasse": "",
        "belastungsfaktoren": [],
        "naechster_qa_sprint": [],
    }
    if not data:
        return result
    result["index"] = data.get("index", 0)
    result["stabilitaetsklasse"] = data.get("stabilitaetsklasse", "")
    result["belastungsfaktoren"] = data.get("belastungsfaktoren", [])
    result["naechster_qa_sprint"] = data.get("naechster_qa_sprint", [])
    return result


def extract_incident_signals(data: dict | None) -> dict:
    """Extrahiert Signale aus incidents/index.json."""
    result = {
        "incidents": [],
        "clusters": {"failure_class": {}, "subsystem": {}},
        "metrics": {"open_incidents": 0, "replay_defined": 0, "bound_to_regression": 0},
        "warnings": [],
    }
    if not data:
        return result
    result["incidents"] = data.get("incidents", [])
    result["clusters"] = data.get("clusters", result["clusters"])
    result["metrics"] = data.get("metrics", result["metrics"])
    result["warnings"] = data.get("warnings", [])
    return result


def extract_analytics_signals(data: dict | None) -> dict:
    """Extrahiert Signale aus incidents/analytics.json."""
    result = {
        "subsystem_risk_score": {},
        "failure_class_frequency": {},
        "replay_defined_ratio": 0.5,
        "regression_bound_ratio": 0.0,
        "clusters": [],
        "warnings": [],
        "autopilot_hints": {},
    }
    if not data:
        return result
    risk = data.get("risk_signals", {})
    if isinstance(risk.get("subsystem_risk_score"), dict):
        result["subsystem_risk_score"] = risk.get("subsystem_risk_score", {})
    elif isinstance(risk.get("subsystem_risk_score"), list):
        for item in risk.get("subsystem_risk_score", []):
            sub = item.get("subsystem", "")
            if sub:
                result["subsystem_risk_score"][sub] = item.get("score", 0)
    if isinstance(risk.get("failure_class_frequency"), dict):
        result["failure_class_frequency"] = risk.get("failure_class_frequency", {})
    elif isinstance(risk.get("failure_class_frequency"), list):
        for item in risk.get("failure_class_frequency", []):
            fc = item.get("failure_class", "")
            if fc:
                result["failure_class_frequency"][fc] = item.get("count", 0)
    qa = data.get("qa_coverage", {})
    result["replay_defined_ratio"] = qa.get("replay_defined_ratio", 0.5)
    result["regression_bound_ratio"] = qa.get("regression_bound_ratio", 0.0)
    result["clusters"] = data.get("clusters", [])
    result["warnings"] = data.get("warnings", [])
    result["autopilot_hints"] = data.get("autopilot_hints", {})
    return result


def compute_subsystem_candidates(
    priority_scores: dict[str, dict],
    heatmap_by_sub: dict[str, dict],
    stability: dict,
    incident_signals: dict,
    analytics: dict,
) -> list[dict]:
    """
    Berechnet gewichtete Kandidaten pro Subsystem.
    Berücksichtigt: subsystem_risk_score, incident_frequency, replay_gap, regression_gap,
    failure_class_frequency, priority_score, heatmap_weak_spots, startup_criticality, drift_signals.
    """
    all_subs = set()
    all_subs.update(priority_scores.keys())
    all_subs.update(heatmap_by_sub.keys())
    all_subs.update(analytics.get("subsystem_risk_score", {}).keys())
    for inc in incident_signals.get("incidents", []):
        sub = inc.get("subsystem", "")
        if sub:
            all_subs.add(sub)
    ss_clusters = incident_signals.get("clusters", {}).get("subsystem", {})
    if isinstance(ss_clusters, dict):
        all_subs.update(ss_clusters.keys())

    incident_count_by_sub: dict[str, int] = defaultdict(int)
    for inc in incident_signals.get("incidents", []):
        sub = inc.get("subsystem", "")
        if sub:
            incident_count_by_sub[sub] += 1

    replay_gap = 1.0 - analytics.get("replay_defined_ratio", 0.5)
    regression_gap = 1.0 - analytics.get("regression_bound_ratio", 0.0)

    candidates = []
    for sub in all_subs:
        ps = priority_scores.get(sub, {})
        hm = heatmap_by_sub.get(sub, {})
        ss_risk = analytics.get("subsystem_risk_score", {}).get(sub, 0)
        inc_freq = incident_count_by_sub.get(sub, 0)
        fc_freq_sum = 0
        for inc in incident_signals.get("incidents", []):
            if inc.get("subsystem") == sub:
                fc = inc.get("failure_class", "")
                fc_freq_sum += analytics.get("failure_class_frequency", {}).get(fc, 1)

        priority_score = ps.get("score", 0)
        weak_spots = sum(
            1 for k in ("Failure_Coverage", "Contract_Coverage", "Async_Coverage", "Cross_Layer_Coverage", "Drift_Governance_Coverage")
            if isinstance(hm.get(k), (int, float)) and hm.get(k) == 1
        )
        startup_crit = 1.0 if sub in STARTUP_CRITICAL_SUBSYSTEMS else 0.0
        drift_signal = 0.0
        for inc in incident_signals.get("incidents", []):
            if inc.get("subsystem") == sub and inc.get("failure_class") in DRIFT_FAILURE_CLASSES:
                drift_signal = 1.0
                break

        stability_factor = 1.0 - (stability.get("index", 93) / 100.0) * 0.3  # 0.7..1.0

        # Gewichtete Summe
        incident_part = (
            ss_risk * WEIGHT_SUBSYSTEM_RISK_SCORE
            + inc_freq * 3 * WEIGHT_INCIDENT_FREQUENCY  # inc_freq oft 0/1, skaliert
            + fc_freq_sum * WEIGHT_FAILURE_CLASS_FREQUENCY
        )
        risk_part = (
            priority_score * WEIGHT_PRIORITY_SCORE
            + weak_spots * 2 * WEIGHT_HEATMAP_WEAK_SPOTS
            + startup_crit * 3 * WEIGHT_STARTUP_CRITICALITY
            + drift_signal * 3 * WEIGHT_DRIFT_SIGNALS
        )
        gap_part = (replay_gap * WEIGHT_REPLAY_GAP_RATIO + regression_gap * WEIGHT_REGRESSION_GAP_RATIO) * (
            1.0 + 0.5 * inc_freq
        )
        stab_part = stability_factor * WEIGHT_STABILITY_INDEX

        total = incident_part + risk_part + gap_part + stab_part
        candidates.append({
            "subsystem": sub,
            "weighted_score": round(total, 2),
            "incident_count": inc_freq,
            "subsystem_risk_score": ss_risk,
            "priority_score": priority_score,
            "weak_spots": weak_spots,
            "startup_critical": startup_crit > 0,
            "naechster_schritt": ps.get("naechster_schritt", ""),
        })
    return sorted(candidates, key=lambda c: -c["weighted_score"])


def select_top_subsystem(candidates: list[dict]) -> str:
    """Wählt das Top-Subsystem aus."""
    if not candidates:
        return "RAG"  # sinnvoller Default
    return candidates[0]["subsystem"]


def select_failure_class(
    incidents: list[dict],
    analytics: dict,
    top_subsystem: str,
) -> str:
    """Wählt die fokussierte Failure-Class (aus Incidents oder Analytics)."""
    hints = analytics.get("autopilot_hints", {})
    fc_hint = hints.get("recommended_focus_failure_class", "")
    if fc_hint:
        return fc_hint
    fc_freq = analytics.get("failure_class_frequency", {})
    sub_incidents = [i for i in incidents if i.get("subsystem") == top_subsystem]
    if sub_incidents:
        fc_by_count: dict[str, int] = defaultdict(int)
        for inc in sub_incidents:
            fc = inc.get("failure_class", "")
            if fc:
                fc_by_count[fc] += fc_freq.get(fc, 1)
        if fc_by_count:
            return max(fc_by_count, key=fc_by_count.get)
    if fc_freq:
        return max(fc_freq, key=fc_freq.get)
    return "rag_silent_failure"  # Default für RAG/Startup


def detect_pilot_constellation(
    subsystem: str,
    failure_class: str,
    priority_scores: dict[str, dict],
    analytics: dict,
) -> dict | None:
    """
    Prüft, ob die Eingangsdaten zu einer der drei Pilotkonstellationen passen.
    Returns: Pilot-Dict mit id, name, guard_type, guard_type_secondary oder None.
    """
    for pilot in PILOT_CONSTELLATIONS:
        sub_match = subsystem in pilot["subsystems"]
        fc_match = failure_class in pilot["failure_classes"]
        # Zusätzlich: Keywords in Priority-Score-Begründung/Nächster-Schritt
        ps = priority_scores.get(subsystem, {})
        text = f"{ps.get('begruendung', '')} {ps.get('naechster_schritt', '')}".lower()
        kw_match = any(kw in text for kw in pilot["keywords"])
        if (sub_match and fc_match) or (sub_match and kw_match):
            return pilot
    return None


def map_test_domain(failure_class: str, subsystem: str) -> str:
    """Mappt Failure-Class und Subsystem auf Test-Domain."""
    domain = FAILURE_CLASS_TO_TEST_DOMAIN.get(failure_class, DEFAULT_TEST_DOMAIN)
    if subsystem == "Startup/Bootstrap" and failure_class not in FAILURE_CLASS_TO_TEST_DOMAIN:
        return "startup"
    return domain


def map_guard_type(
    failure_class: str,
    replay_gap_high: bool,
    pilot_constellation: dict | None = None,
) -> str:
    """
    Mappt Failure-Class und Replay-Gap auf Guard-Type.
    Bei Pilotkonstellation-Match: bevorzugter Guard-Typ aus Pilot.
    """
    if pilot_constellation:
        return pilot_constellation["guard_type"]
    guard = FAILURE_CLASS_TO_GUARD_TYPE.get(failure_class, DEFAULT_GUARD_TYPE)
    if replay_gap_high and failure_class in ("rag_silent_failure", "optional_dependency_missing", "async_race"):
        return "failure_replay_guard"
    return guard


def build_sprint_name(
    top_subsystem: str,
    top_failure_class: str,
    candidates: list[dict],
) -> str:
    """Bildet einen lesbaren Sprint-Namen."""
    parts = []
    name1 = SUBSYSTEM_SPRINT_NAMES.get(top_subsystem, top_subsystem.replace("/", " "))
    parts.append(name1)
    seen = {top_subsystem}
    for c in candidates[1:4]:
        sub = c.get("subsystem", "")
        if sub and sub not in seen and c.get("incident_count", 0) + c.get("priority_score", 0) > 0:
            n = SUBSYSTEM_SPRINT_NAMES.get(sub, sub.replace("/", " "))
            if n and n not in str(parts):
                parts.append(n)
                seen.add(sub)
            if len(parts) >= 2:
                break
    return " + ".join(parts[:2]) if len(parts) > 1 else (parts[0] if parts else "RAG Failure Replay + Chroma Degradation")


def merge_warnings(
    incident_warnings: list[dict],
    analytics_warnings: list[dict],
    replay_ratio: float,
    regression_ratio: float,
    cluster_count: int,
    incidents: list[dict],
) -> tuple[list[dict], list[dict]]:
    """Merge Warnings und erzeugt Eskalationen. Eigene Regeln zuerst, dann externe."""
    warnings: list[dict] = []
    escalations: list[dict] = []
    seen_codes: set[str] = set()

    def add_warning(code: str, msg: str, **kw):
        if code not in seen_codes:
            seen_codes.add(code)
            warnings.append({"code": code, "message": msg, **kw})

    def add_escalation(code: str, msg: str, **kw):
        if code not in seen_codes:
            seen_codes.add(code)
            escalations.append({"code": code, "message": msg, **kw})

    # 1. Eigene Regeln zuerst (Eskalationen haben Vorrang)
    if replay_ratio < 0.2:
        add_escalation("REPLAY_GAP_CRITICAL", f"Replay Coverage < 20% (aktuell: {replay_ratio:.0%})")
    elif replay_ratio < 0.5:
        add_warning("REPLAY_GAP", f"Replay Coverage unter 50%: {replay_ratio:.0%}")

    if regression_ratio < 0.2:
        add_escalation("REGRESSION_BINDING_GAP", f"Regression Binding < 20% (aktuell: {regression_ratio:.0%})")
    elif regression_ratio < 0.3:
        add_warning("REGRESSION_BINDING_GAP", f"Regression Binding unter 30%: {regression_ratio:.0%}")

    if cluster_count >= 3:
        add_escalation("REAL_INCIDENT_CLUSTER", f"Incident-Cluster Count >= 3 ({cluster_count})")

    high_severity_startup = [
        i for i in incidents
        if i.get("subsystem") in STARTUP_CRITICAL_SUBSYSTEMS
        and i.get("severity") in ("high", "critical", "blocker")
    ]
    if high_severity_startup:
        add_escalation("STARTUP_RISK_ESCALATION", f"Startup-kritisches Subsystem mit hoher Schwere: {len(high_severity_startup)}")

    drift_incidents = [i for i in incidents if i.get("failure_class") in DRIFT_FAILURE_CLASSES]
    if drift_incidents:
        add_warning("DRIFT_PATTERN_DETECTED", f"Drift-Muster in {len(drift_incidents)} Incident(s)")

    # 2. Externe Warnings (nur wenn Code noch nicht vergeben – Eskalation hat Vorrang)
    for w in incident_warnings + analytics_warnings:
        code = w.get("code", "")
        msg = w.get("message", str(w))
        if code and code not in seen_codes:
            seen_codes.add(code)
            warnings.append({"code": code, "message": msg})

    return warnings, escalations


def compute_confidence(
    has_incidents: bool,
    has_analytics: bool,
    incident_count: int,
    analytics_strength: float,
) -> float:
    """Berechnet Confidence 0..1."""
    base = 0.5
    if has_incidents and incident_count > 0:
        base += 0.2
    if has_analytics and analytics_strength > 0:
        base += 0.15
    if has_incidents and has_analytics:
        base += 0.1
    return min(0.95, round(base, 2))


def build_reasoning_summary(
    top_subsystem: str,
    top_failure_class: str,
    recommendation_basis: str,
    candidates: list[dict],
    incident_count: int,
    pilot_constellation: dict | None = None,
) -> str:
    """Kurze Begründung der Empfehlung. Inkl. Pilotkonstellation wenn erkannt."""
    parts = []
    if pilot_constellation:
        parts.append(
            f"[Pilotkonstellation {pilot_constellation['id']}: {pilot_constellation['name']}] "
        )
    if recommendation_basis == "incident_dominant":
        parts.append("Empfehlung basiert primär auf Incident-Daten und Replay-Gaps.")
        if incident_count > 0:
            parts.append(f"Top-Subsystem {top_subsystem} hat {incident_count} Incident(s).")
    elif recommendation_basis == "risk_dominant":
        parts.append("Empfehlung basiert primär auf Risk-Artefakten (Priority Score, Heatmap).")
        if incident_count > 0:
            parts.append(f"Risk-Signale überwiegen trotz {incident_count} Incident(s).")
        else:
            parts.append("Keine Incident-Signale – Fallback auf theoretische Risiken.")
    else:
        parts.append("Empfehlung balanciert aus Incident- und Risk-Signalen.")
        if incident_count > 0:
            parts.append(f"{incident_count} Incident(s) einbezogen.")
    top = candidates[0] if candidates else {}
    if top:
        parts.append(f"Gewichteter Score für {top_subsystem}: {top.get('weighted_score', 0):.2f}.")
    parts.append(f"Failure-Class {top_failure_class} als Fokus gewählt.")
    if pilot_constellation:
        guard_sec = pilot_constellation.get("guard_type_secondary")
        if guard_sec:
            parts.append(f"Guard-Typ: {pilot_constellation['guard_type']} + {guard_sec}.")
        else:
            parts.append(f"Guard-Typ: {pilot_constellation['guard_type']}.")
    return " ".join(parts)


def build_autopilot_v2(
    input_dir: Path,
    output_path: Path,
) -> dict:
    """Hauptlogik: Lädt Inputs, berechnet Empfehlung, baut Output-Dict."""
    # Pfade
    docs_qa = input_dir
    incidents_dir = docs_qa / "incidents"

    # Inputs laden
    priority_data = load_json(docs_qa / "QA_PRIORITY_SCORE.json")
    heatmap_data = load_json(docs_qa / "QA_HEATMAP.json")
    stability_data = load_json(docs_qa / "QA_STABILITY_INDEX.json")
    index_data = load_json(incidents_dir / "index.json")
    analytics_data = load_json(incidents_dir / "analytics.json")

    # Optionale Inputs
    control_data = safe_load_optional(docs_qa / "QA_CONTROL_CENTER.json", warn_if_missing=False)

    input_sources_used: list[str] = []
    if priority_data:
        input_sources_used.append("QA_PRIORITY_SCORE.json")
    else:
        LOG.warning("QA_PRIORITY_SCORE.json fehlt – verwende Defaults")
    if heatmap_data:
        input_sources_used.append("QA_HEATMAP.json")
    else:
        LOG.warning("QA_HEATMAP.json fehlt – verwende Defaults")
    if stability_data:
        input_sources_used.append("QA_STABILITY_INDEX.json")
    else:
        LOG.warning("QA_STABILITY_INDEX.json fehlt – verwende Defaults")
    if index_data:
        input_sources_used.append("incidents/index.json")
    else:
        LOG.warning("incidents/index.json fehlt – Fallback risk_dominant")
    if analytics_data:
        input_sources_used.append("incidents/analytics.json")
    else:
        LOG.warning("incidents/analytics.json fehlt – verwende Defaults")

    # Signale extrahieren
    priority_scores = extract_priority_scores(priority_data)
    heatmap_by_sub, heatmap_hotspots = extract_heatmap_signals(heatmap_data)
    stability = extract_stability_signals(stability_data)
    incident_signals = extract_incident_signals(index_data)
    analytics = extract_analytics_signals(analytics_data)

    incidents = incident_signals.get("incidents", [])
    replay_ratio = analytics.get("replay_defined_ratio", 0.5)
    regression_ratio = analytics.get("regression_bound_ratio", 0.0)
    cluster_count = len(analytics.get("clusters", []))
    if not analytics.get("clusters") and incidents:
        fc_clusters = incident_signals.get("clusters", {}).get("failure_class", {})
        if isinstance(fc_clusters, dict):
            cluster_count = sum(1 for v in fc_clusters.values() if v >= 2)

    # Kandidaten berechnen
    candidates = compute_subsystem_candidates(
        priority_scores, heatmap_by_sub, stability, incident_signals, analytics
    )

    # Empfehlungen ableiten
    top_subsystem = select_top_subsystem(candidates)
    top_failure_class = select_failure_class(incidents, analytics, top_subsystem)
    pilot_constellation = detect_pilot_constellation(
        top_subsystem, top_failure_class, priority_scores, analytics
    )
    test_domain = map_test_domain(top_failure_class, top_subsystem)
    replay_gap_high = replay_ratio < 0.5
    guard_type = map_guard_type(top_failure_class, replay_gap_high, pilot_constellation)
    sprint_name = build_sprint_name(top_subsystem, top_failure_class, candidates)

    # Recommendation Basis
    incident_strength = (
        len(incidents) * 2
        + sum(analytics.get("subsystem_risk_score", {}).values())
        + sum(analytics.get("failure_class_frequency", {}).values())
    )
    risk_strength = sum(ps.get("score", 0) for ps in priority_scores.values()) + len(heatmap_hotspots) * 3
    if incident_strength > risk_strength * 1.2:
        recommendation_basis = "incident_dominant"
    elif risk_strength > incident_strength * 1.2:
        recommendation_basis = "risk_dominant"
    else:
        recommendation_basis = "balanced"

    # Warnings / Escalations
    warnings, escalations = merge_warnings(
        incident_signals.get("warnings", []),
        analytics.get("warnings", []),
        replay_ratio,
        regression_ratio,
        cluster_count,
        incidents,
    )

    # Top Risk / Incident Signals
    top_risk_signals: list[dict] = []
    for h in heatmap_hotspots[:5]:
        top_risk_signals.append({"subsystem": h.get("sub", ""), "reason": h.get("reason", "")})
    top_incident_signals: list[dict] = []
    for inc in incidents[:5]:
        top_incident_signals.append({
            "incident_id": inc.get("incident_id", ""),
            "subsystem": inc.get("subsystem", ""),
            "failure_class": inc.get("failure_class", ""),
            "severity": inc.get("severity", ""),
        })

    # Supporting Evidence
    priority_score_refs = [{"subsystem": c["subsystem"], "score": c["priority_score"]} for c in candidates[:3]]
    heatmap_refs = [{"subsystem": h.get("sub", ""), "reason": h.get("reason", "")} for h in heatmap_hotspots[:3]]
    incident_cluster_refs: list[dict] = []
    if analytics.get("clusters"):
        for cl in analytics["clusters"][:5]:
            incident_cluster_refs.append({
                "failure_class": cl.get("failure_class", ""),
                "subsystem": cl.get("subsystem", ""),
                "incident_count": cl.get("incident_count", 0),
            })
    else:
        fc_clusters = incident_signals.get("clusters", {}) or {}
        fc_data = fc_clusters.get("failure_class", {}) if isinstance(fc_clusters, dict) else {}
        if isinstance(fc_data, dict):
            incident_cluster_refs = [{"failure_class": k, "count": v} for k, v in list(fc_data.items())[:5]]
    replay_gap_refs = [{"replay_defined_ratio": replay_ratio, "regression_bound_ratio": regression_ratio}]
    stability_refs = [{"index": stability.get("index"), "klasse": stability.get("stabilitaetsklasse")}]

    # Confidence
    analytics_strength = (
        sum(analytics.get("subsystem_risk_score", {}).values())
        + sum(analytics.get("failure_class_frequency", {}).values())
    )
    confidence = compute_confidence(
        bool(index_data),
        bool(analytics_data),
        len(incidents),
        analytics_strength,
    )

    # Reasoning
    reasoning_summary = build_reasoning_summary(
        top_subsystem,
        top_failure_class,
        recommendation_basis,
        candidates,
        len(incidents),
        pilot_constellation,
    )

    overall = f"{sprint_name} priorisieren."
    if escalations:
        overall = f"[ESKALATION] {overall}"

    pilot_matched = None
    if pilot_constellation:
        pilot_matched = {
            "id": pilot_constellation["id"],
            "name": pilot_constellation["name"],
            "guard_type": pilot_constellation["guard_type"],
            "guard_type_secondary": pilot_constellation.get("guard_type_secondary"),
        }

    return {
        "schema_version": "2.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "overall_recommendation": overall,
        "pilot_constellation_matched": pilot_matched,
        "recommended_focus_subsystem": top_subsystem,
        "recommended_focus_failure_class": top_failure_class,
        "recommended_test_domain": test_domain,
        "recommended_guard_type": guard_type,
        "recommended_next_sprint": sprint_name,
        "top_risk_signals": top_risk_signals,
        "top_incident_signals": top_incident_signals,
        "warnings": warnings,
        "escalations": escalations,
        "supporting_evidence": {
            "priority_score_refs": priority_score_refs,
            "heatmap_refs": heatmap_refs,
            "incident_cluster_refs": incident_cluster_refs,
            "replay_gap_refs": replay_gap_refs,
            "stability_refs": stability_refs,
        },
        "confidence": confidence,
        "reasoning_summary": reasoning_summary,
        "recommendation_basis": recommendation_basis,
        "input_sources_used": input_sources_used,
    }


def save_output(data: dict, path: Path, pretty: bool = True) -> None:
    """Schreibt QA_AUTOPILOT_V2.json."""
    path.parent.mkdir(parents=True, exist_ok=True)
    indent = 2 if pretty else None
    path.write_text(
        json.dumps(data, indent=indent, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="QA Autopilot v2 Generator")
    parser.add_argument("--input-dir", type=Path, default=_DEFAULT_INPUT_DIR, help="Eingabeverzeichnis (docs/qa)")
    parser.add_argument("--output", type=Path, default=_DEFAULT_OUTPUT, help="Output-Pfad für QA_AUTOPILOT_V2.json")
    parser.add_argument("--pretty", action="store_true", default=True, help="Pretty-Print JSON (default: True)")
    parser.add_argument("--no-pretty", action="store_false", dest="pretty", help="Kompaktes JSON")
    args = parser.parse_args()

    try:
        data = build_autopilot_v2(args.input_dir, args.output)
        save_output(data, args.output, pretty=args.pretty)
        print("QA Autopilot v2 – generiert")
        print(f"  Empfehlung: {data.get('overall_recommendation', '')}")
        print(f"  Fokus: {data.get('recommended_focus_subsystem', '')} / {data.get('recommended_focus_failure_class', '')}")
        print(f"  Sprint: {data.get('recommended_next_sprint', '')}")
        print(f"  Confidence: {data.get('confidence', 0)}")
        print(f"  → {args.output}")
        return 0
    except Exception as e:
        LOG.exception("Generator fehlgeschlagen: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
QA Incident Replay – Incident Analytics Engine.

Analysiert docs/qa/incidents/index.json und erzeugt analytics.json.

Erkennt:
- häufige Fehlerklassen
- riskante Subsysteme
- Drift-Muster
- Replay-Lücken
- Regression-Gaps

Input für: QA_RISK_RADAR, QA_HEATMAP, QA_AUTOPILOT, QA_CONTROL_CENTER
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Projekt-Root: scripts/qa/incidents/ -> Projekt-Root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_INCIDENTS_DIR = _PROJECT_ROOT / "docs" / "qa" / "incidents"
_INDEX_PATH = _INCIDENTS_DIR / "index.json"
_ANALYTICS_PATH = _INCIDENTS_DIR / "analytics.json"

# Warnungsklassen
REPLAY_GAP = "REPLAY_GAP"
REGRESSION_GAP = "REGRESSION_GAP"
FAILURE_CLUSTER = "FAILURE_CLUSTER"
SUBSYSTEM_RISK = "SUBSYSTEM_RISK"
DRIFT_PATTERN = "DRIFT_PATTERN"

# Schweregrad-Gewichtung für Risk Scores
SEVERITY_WEIGHTS = {"blocker": 5, "critical": 4, "high": 3, "medium": 2, "low": 1, "cosmetic": 0}

# Schwellen für Warnungen
REPLAY_GAP_THRESHOLD = 0.5  # Warnung wenn replay_defined_ratio < 50%
REGRESSION_GAP_THRESHOLD = 0.3  # Warnung wenn regression_bound_ratio < 30%
FAILURE_CLUSTER_THRESHOLD = 2  # Warnung wenn failure_class ≥ 2 Incidents
SUBSYSTEM_RISK_THRESHOLD = 2  # Warnung wenn Subsystem ≥ 2 Incidents mit severity ≥ high


def _load_index(path: Path) -> dict | None:
    """Lädt index.json."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _compute_distributions(incidents: list[dict]) -> tuple[dict, dict, dict]:
    """Berechnet failure_class, subsystem, runtime_layer Verteilungen (sortiert nach Count)."""
    fc_dist: dict[str, int] = defaultdict(int)
    ss_dist: dict[str, int] = defaultdict(int)
    rl_dist: dict[str, int] = defaultdict(int)

    for inc in incidents:
        fc = inc.get("failure_class") or "_unknown"
        ss = inc.get("subsystem") or "_unknown"
        rl = inc.get("runtime_layer") or "_unknown"
        fc_dist[fc] += 1
        ss_dist[ss] += 1
        rl_dist[rl] += 1

    def to_sorted_list(d: dict) -> list[dict]:
        return [{"key": k, "count": v} for k, v in sorted(d.items(), key=lambda x: -x[1])]

    return (
        {"distribution": to_sorted_list(fc_dist), "total": sum(fc_dist.values())},
        {"distribution": to_sorted_list(ss_dist), "total": sum(ss_dist.values())},
        {"distribution": to_sorted_list(rl_dist), "total": sum(rl_dist.values())},
    )


def _compute_clusters(incidents: list[dict]) -> list[dict]:
    """Cluster nach failure_class × subsystem × runtime_layer."""
    cluster_map: dict[tuple[str, str, str], list[str]] = defaultdict(list)

    for inc in incidents:
        fc = inc.get("failure_class") or "_unknown"
        ss = inc.get("subsystem") or "_unknown"
        rl = inc.get("runtime_layer") or "_unknown"
        key = (fc, ss, rl)
        cluster_map[key].append(inc.get("incident_id") or "")

    clusters = []
    for i, ((fc, ss, rl), ids) in enumerate(sorted(cluster_map.items(), key=lambda x: -len(x[1]))):
        clusters.append({
            "cluster_id": f"C{i+1:03d}",
            "failure_class": fc,
            "subsystem": ss,
            "runtime_layer": rl,
            "incident_count": len(ids),
            "incident_ids": ids,
        })
    return clusters


def _compute_risk_signals(incidents: list[dict]) -> dict:
    """Berechnet subsystem_risk_score, failure_class_frequency, incident_growth_rate."""
    # Subsystem Risk Score: gewichtete Summe nach Severity
    ss_scores: dict[str, float] = defaultdict(float)
    for inc in incidents:
        ss = inc.get("subsystem") or "_unknown"
        sev = inc.get("severity") or "medium"
        weight = SEVERITY_WEIGHTS.get(sev, 2)
        ss_scores[ss] += weight

    subsystem_risk_score = [
        {"subsystem": k, "score": round(v, 1)}
        for k, v in sorted(ss_scores.items(), key=lambda x: -x[1])
    ]

    # Failure Class Frequency
    fc_freq: dict[str, int] = defaultdict(int)
    for inc in incidents:
        fc = inc.get("failure_class") or "_unknown"
        fc_freq[fc] += 1
    failure_class_frequency = [
        {"failure_class": k, "count": v}
        for k, v in sorted(fc_freq.items(), key=lambda x: -x[1])
    ]

    # Incident Growth Rate: aus detected_at (falls vorhanden)
    dates = []
    for inc in incidents:
        dt = inc.get("detected_at")
        if dt:
            try:
                if "T" in dt:
                    d = datetime.fromisoformat(dt.replace("Z", "+00:00"))
                else:
                    d = datetime.strptime(dt[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
                dates.append(d)
            except (ValueError, TypeError):
                pass
    incident_growth_rate = None
    if len(dates) >= 2:
        dates_sorted = sorted(dates)
        span_days = (dates_sorted[-1] - dates_sorted[0]).days or 1
        incident_growth_rate = round(len(incidents) / (span_days / 30), 2)  # pro Monat

    return {
        "subsystem_risk_score": subsystem_risk_score,
        "failure_class_frequency": failure_class_frequency,
        "incident_growth_rate": incident_growth_rate,
    }


def _compute_qa_coverage(incidents: list[dict]) -> dict:
    """Berechnet incident_count, replay_defined_ratio, replay_verified_ratio, regression_bound_ratio."""
    total = len(incidents)
    if total == 0:
        return {
            "incident_count": 0,
            "replay_defined_ratio": 0.0,
            "replay_verified_ratio": 0.0,
            "regression_bound_ratio": 0.0,
            "replay_defined_count": 0,
            "replay_verified_count": 0,
            "regression_bound_count": 0,
        }

    replay_defined = sum(1 for inc in incidents if inc.get("replay_status") or inc.get("status") in ("replay_defined", "replay_verified", "bound_to_regression", "closed"))
    replay_verified = sum(1 for inc in incidents if inc.get("replay_status") in ("validated", "test_bound", "guarded") or inc.get("status") in ("replay_verified", "bound_to_regression", "closed"))
    regression_bound = sum(1 for inc in incidents if inc.get("binding_status") == "catalog_bound" or inc.get("status") in ("bound_to_regression", "closed"))

    return {
        "incident_count": total,
        "replay_defined_ratio": round(replay_defined / total, 2),
        "replay_verified_ratio": round(replay_verified / total, 2),
        "regression_bound_ratio": round(regression_bound / total, 2),
        "replay_defined_count": replay_defined,
        "replay_verified_count": replay_verified,
        "regression_bound_count": regression_bound,
    }


def _compute_autopilot_hints(incidents: list[dict], risk_signals: dict) -> dict:
    """Erzeugt Hinweise für QA_AUTOPILOT."""
    recommended_focus_subsystem = None
    recommended_focus_failure_class = None
    recommended_sprint_target = None

    # Fokus-Subsystem: höchster Risk Score mit offenen Incidents
    open_statuses = {"new", "triaged", "classified", "replay_defined", "replay_verified"}
    open_by_ss: dict[str, int] = defaultdict(int)
    for inc in incidents:
        if inc.get("status") in open_statuses:
            ss = inc.get("subsystem") or "_unknown"
            open_by_ss[ss] += 1
    if open_by_ss:
        recommended_focus_subsystem = max(open_by_ss.items(), key=lambda x: x[1])[0]
        if recommended_focus_subsystem == "_unknown":
            recommended_focus_subsystem = None

    # Fokus Failure Class: häufigste mit Replay-Lücke (catalog_candidate)
    catalog_candidates = [inc for inc in incidents if inc.get("catalog_candidate")]
    if catalog_candidates:
        fc_counts: dict[str, int] = defaultdict(int)
        for inc in catalog_candidates:
            fc = inc.get("failure_class") or "_unknown"
            fc_counts[fc] += 1
        if fc_counts:
            recommended_focus_failure_class = max(fc_counts.items(), key=lambda x: x[1])[0]
            if recommended_focus_failure_class == "_unknown":
                recommended_focus_failure_class = None

    # Sprint Target: Anzahl catalog_candidates
    recommended_sprint_target = len(catalog_candidates)

    return {
        "recommended_focus_subsystem": recommended_focus_subsystem,
        "recommended_focus_failure_class": recommended_focus_failure_class,
        "recommended_sprint_target": recommended_sprint_target,
        "catalog_candidates_count": len(catalog_candidates),
        "autopilot_eligible_count": sum(1 for inc in incidents if inc.get("autopilot_eligible")),
    }


def _compute_warnings(
    incidents: list[dict],
    qa_coverage: dict,
    clusters: list[dict],
    risk_signals: dict,
) -> list[dict]:
    """Erzeugt Warnsignale."""
    warnings: list[dict] = []

    # REPLAY_GAP: replay_defined_ratio unter Schwellwert
    if qa_coverage["incident_count"] > 0 and qa_coverage["replay_defined_ratio"] < REPLAY_GAP_THRESHOLD:
        warnings.append({
            "code": REPLAY_GAP,
            "message": f"Replay-Abdeckung niedrig: {qa_coverage['replay_defined_ratio']:.0%} (Schwelle: {REPLAY_GAP_THRESHOLD:.0%})",
            "metric": "replay_defined_ratio",
            "value": qa_coverage["replay_defined_ratio"],
        })

    # REGRESSION_GAP: regression_bound_ratio unter Schwellwert
    if qa_coverage["incident_count"] > 0 and qa_coverage["regression_bound_ratio"] < REGRESSION_GAP_THRESHOLD:
        warnings.append({
            "code": REGRESSION_GAP,
            "message": f"Regression-Abdeckung niedrig: {qa_coverage['regression_bound_ratio']:.0%} (Schwelle: {REGRESSION_GAP_THRESHOLD:.0%})",
            "metric": "regression_bound_ratio",
            "value": qa_coverage["regression_bound_ratio"],
        })

    # FAILURE_CLUSTER: failure_class mit ≥ 2 Incidents
    for c in clusters:
        if c["incident_count"] >= FAILURE_CLUSTER_THRESHOLD and c["failure_class"] != "_unknown":
            warnings.append({
                "code": FAILURE_CLUSTER,
                "message": f"Cluster {c['failure_class']}/{c['subsystem']}: {c['incident_count']} Incidents",
                "cluster_id": c["cluster_id"],
                "failure_class": c["failure_class"],
                "subsystem": c["subsystem"],
                "incident_count": c["incident_count"],
            })

    # SUBSYSTEM_RISK: Subsystem mit vielen high/critical Incidents
    ss_high: dict[str, int] = defaultdict(int)
    for inc in incidents:
        if inc.get("severity") in ("blocker", "critical", "high"):
            ss = inc.get("subsystem") or "_unknown"
            ss_high[ss] += 1
    for ss, cnt in ss_high.items():
        if cnt >= SUBSYSTEM_RISK_THRESHOLD and ss != "_unknown":
            warnings.append({
                "code": SUBSYSTEM_RISK,
                "message": f"Subsystem {ss}: {cnt} Incidents mit severity blocker/critical/high",
                "subsystem": ss,
                "high_severity_count": cnt,
            })

    # DRIFT_PATTERN: contract_schema_drift, event_contract_drift, metrics_false_success
    drift_classes = {"contract_schema_drift", "metrics_false_success", "debug_false_truth"}
    drift_count = sum(1 for inc in incidents if inc.get("failure_class") in drift_classes)
    if drift_count >= 1:
        warnings.append({
            "code": DRIFT_PATTERN,
            "message": f"Drift-Muster erkannt: {drift_count} Incidents (contract/metrics/debug drift)",
            "drift_incident_count": drift_count,
        })

    return warnings


def analyze_incidents(index_path: Path) -> dict:
    """Führt die vollständige Analyse durch."""
    index = _load_index(index_path)
    if not index:
        return {
            "schema_version": "1.0",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "error": "index.json nicht gefunden oder ungültig",
            "failure_class_distribution": {"distribution": [], "total": 0},
            "subsystem_distribution": {"distribution": [], "total": 0},
            "runtime_layer_distribution": {"distribution": [], "total": 0},
            "clusters": [],
            "risk_signals": {"subsystem_risk_score": [], "failure_class_frequency": [], "incident_growth_rate": None},
            "qa_coverage": {"incident_count": 0, "replay_defined_ratio": 0, "replay_verified_ratio": 0, "regression_bound_ratio": 0},
            "autopilot_hints": {},
            "warnings": [{"code": "PARSE_ERROR", "message": "index.json konnte nicht geladen werden"}],
        }

    incidents = index.get("incidents") or []
    if not incidents and index.get("clusters"):
        # Fallback: aus Registry-Clusters rekonstruieren (reduziert)
        incidents = []

    fc_dist, ss_dist, rl_dist = _compute_distributions(incidents)
    clusters = _compute_clusters(incidents)
    risk_signals = _compute_risk_signals(incidents)
    qa_coverage = _compute_qa_coverage(incidents)
    autopilot_hints = _compute_autopilot_hints(incidents, risk_signals)
    warnings = _compute_warnings(incidents, qa_coverage, clusters, risk_signals)

    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "failure_class_distribution": fc_dist,
        "subsystem_distribution": ss_dist,
        "runtime_layer_distribution": rl_dist,
        "clusters": clusters,
        "risk_signals": risk_signals,
        "qa_coverage": qa_coverage,
        "autopilot_hints": autopilot_hints,
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analysiert index.json und erzeugt analytics.json.",
    )
    parser.add_argument(
        "-i", "--index",
        type=Path,
        default=_INDEX_PATH,
        help=f"Pfad zu index.json (default: {_INDEX_PATH})",
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=_ANALYTICS_PATH,
        help=f"Pfad zu analytics.json (default: {_ANALYTICS_PATH})",
    )
    parser.add_argument(
        "-q", "--quiet",
        action="store_true",
        help="Keine Ausgabe außer Fehlern",
    )
    args = parser.parse_args()

    index_path = args.index
    if not index_path.is_absolute():
        index_path = (Path.cwd() / index_path).resolve()

    analytics = analyze_incidents(index_path)

    output_path = args.output
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(analytics, indent=2, ensure_ascii=False), encoding="utf-8")

    if not args.quiet:
        print(f"Analytics erzeugt: {output_path}")
        qc = analytics.get("qa_coverage") or {}
        print(f"  Incidents: {qc.get('incident_count', 0)}")
        print(f"  Replay Coverage: {qc.get('replay_defined_ratio', 0):.0%} | Regression: {qc.get('regression_bound_ratio', 0):.0%}")
        hints = analytics.get("autopilot_hints") or {}
        if hints.get("recommended_focus_subsystem"):
            print(f"  Autopilot Focus: {hints['recommended_focus_subsystem']}")
        if analytics.get("warnings"):
            print(f"  Warnungen: {len(analytics['warnings'])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

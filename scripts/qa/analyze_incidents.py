#!/usr/bin/env python3
"""
QA Incident Analytics Engine – Linux Desktop Chat.

Analysiert docs/qa/incidents/index.json und erzeugt incidents/analytics.json.

Input für: QA_AUTOPILOT_V2, QA_RISK_RADAR, QA_HEATMAP, QA_CONTROL_CENTER.

Das Script:
- Liest index.json
- Berechnet Risk Signals, QA Coverage, Clusters
- Erzeugt Warnungen
- Schreibt analytics.json

Es ändert NICHT: Incidents, Regression Catalog, Tests.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# Projekt-Root: scripts/qa/ -> Projekt-Root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_INCIDENTS_DIR = _PROJECT_ROOT / "docs" / "qa" / "incidents"
_INDEX_PATH = _INCIDENTS_DIR / "index.json"
_ANALYTICS_PATH = _INCIDENTS_DIR / "analytics.json"

# Severity-Gewichtung für Subsystem Risk Score
SEVERITY_WEIGHTS = {
    "blocker": 5,
    "critical": 4,
    "high": 3,
    "medium": 2,
    "low": 1,
    "cosmetic": 0,
}

# Warnungs-Schwellen
REPLAY_GAP_THRESHOLD = 0.3
REGRESSION_BINDING_THRESHOLD = 0.2
CLUSTER_INCIDENT_THRESHOLD = 2


def _has_replay(incident: dict) -> bool:
    """
    Prüft ob Incident ein Replay hat.

    Verwendet has_replay falls vorhanden, sonst Fallback aus replay_status,
    binding_status oder status.
    """
    if "has_replay" in incident:
        return bool(incident.get("has_replay"))
    if incident.get("replay_status"):
        return True
    if incident.get("binding_status") == "catalog_bound":
        return True
    status = incident.get("status") or ""
    return status in ("replay_defined", "replay_verified", "bound_to_regression", "closed")


def _has_regression_test(incident: dict) -> bool:
    """
    Prüft ob Incident einen Regression-Test hat.

    Verwendet has_regression_test falls vorhanden, sonst Fallback aus
    binding_status, regression_test oder status.
    """
    if "has_regression_test" in incident:
        return bool(incident.get("has_regression_test"))
    if incident.get("binding_status") == "catalog_bound":
        return True
    if incident.get("regression_test") and str(incident.get("regression_test", "")).strip():
        return True
    status = incident.get("status") or ""
    return status in ("bound_to_regression", "closed")


def load_index(path: Path) -> dict | None:
    """
    Lädt index.json.

    Returns:
        Parsed JSON oder None bei Fehler.
    """
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    except OSError:
        return None


def compute_subsystem_scores(incidents: list[dict]) -> dict[str, int]:
    """
    Berechnet Subsystem Risk Score pro Subsystem.

    Formel pro Incident:
        severity_weight + 1 (incident_count) + replay_gap + regression_gap

    replay_gap = 1 wenn kein Replay, sonst 0
    regression_gap = 1 wenn kein Regression-Test, sonst 0

    Returns:
        { subsystem: score }
    """
    scores: dict[str, int] = defaultdict(int)

    for inc in incidents:
        subsystem = inc.get("subsystem") or "_unknown"
        severity = inc.get("severity") or "medium"
        weight = SEVERITY_WEIGHTS.get(severity, 2)

        replay_gap = 0 if _has_replay(inc) else 1
        regression_gap = 0 if _has_regression_test(inc) else 1

        contribution = weight + 1 + replay_gap + regression_gap
        scores[subsystem] += contribution

    return dict(scores)


def compute_failure_class_frequency(incidents: list[dict]) -> dict[str, int]:
    """
    Zählt Incidents pro Failure Class.

    Returns:
        { failure_class: count }
    """
    freq: dict[str, int] = defaultdict(int)
    for inc in incidents:
        fc = inc.get("failure_class") or "_unknown"
        freq[fc] += 1
    return dict(freq)


def compute_clusters(incidents: list[dict]) -> list[dict]:
    """
    Cluster nach (subsystem + failure_class) mit incident_count >= 2.

    Returns:
        Liste von { cluster_id, subsystem, failure_class, incident_count }
    """
    cluster_map: dict[tuple[str, str], list[str]] = defaultdict(list)

    for inc in incidents:
        ss = inc.get("subsystem") or "_unknown"
        fc = inc.get("failure_class") or "_unknown"
        key = (ss, fc)
        cluster_map[key].append(inc.get("incident_id") or "")

    clusters = []
    for i, ((ss, fc), ids) in enumerate(
        sorted(cluster_map.items(), key=lambda x: -len(x[1])), start=1
    ):
        count = len(ids)
        if count >= CLUSTER_INCIDENT_THRESHOLD:
            clusters.append({
                "cluster_id": f"C{i:03d}",
                "subsystem": ss,
                "failure_class": fc,
                "incident_count": count,
            })
    return clusters


def compute_coverage(incidents: list[dict]) -> dict:
    """
    Berechnet Replay- und Regression-Coverage.

    replay_defined_ratio = incidents with has_replay / total
    regression_bound_ratio = incidents with has_regression_test / total

    Returns:
        { replay_defined_ratio, regression_bound_ratio }
    """
    total = len(incidents)
    if total == 0:
        return {
            "replay_defined_ratio": 0.0,
            "regression_bound_ratio": 0.0,
        }

    with_replay = sum(1 for inc in incidents if _has_replay(inc))
    with_regression = sum(1 for inc in incidents if _has_regression_test(inc))

    return {
        "replay_defined_ratio": round(with_replay / total, 2),
        "regression_bound_ratio": round(with_regression / total, 2),
    }


def detect_warnings(
    qa_coverage: dict,
    clusters: list[dict],
) -> list[dict]:
    """
    Erkennt Warnsignale.

    REPLAY_GAP_CRITICAL: replay_defined_ratio < 0.3
    REGRESSION_BINDING_GAP: regression_bound_ratio < 0.2
    REAL_INCIDENT_CLUSTER: cluster incident_count >= 2

    Returns:
        Liste von { code, message }
    """
    warnings: list[dict] = []

    replay_ratio = qa_coverage.get("replay_defined_ratio", 0)
    if replay_ratio < REPLAY_GAP_THRESHOLD:
        warnings.append({
            "code": "REPLAY_GAP_CRITICAL",
            "message": f"Replay coverage < {REPLAY_GAP_THRESHOLD:.0%}",
        })

    regression_ratio = qa_coverage.get("regression_bound_ratio", 0)
    if regression_ratio < REGRESSION_BINDING_THRESHOLD:
        warnings.append({
            "code": "REGRESSION_BINDING_GAP",
            "message": f"Regression coverage < {REGRESSION_BINDING_THRESHOLD:.0%}",
        })

    for cluster in clusters:
        if cluster.get("incident_count", 0) >= CLUSTER_INCIDENT_THRESHOLD:
            warnings.append({
                "code": "REAL_INCIDENT_CLUSTER",
                "message": f"Cluster {cluster.get('subsystem')}/{cluster.get('failure_class')}: {cluster.get('incident_count')} incidents",
            })

    return warnings


def build_analytics(incidents: list[dict]) -> dict:
    """
    Baut das vollständige analytics.json Objekt.

    Returns:
        Dict mit risk_signals, qa_coverage, clusters, warnings.
    """
    subsystem_scores = compute_subsystem_scores(incidents)
    failure_class_freq = compute_failure_class_frequency(incidents)
    clusters = compute_clusters(incidents)
    qa_coverage = compute_coverage(incidents)
    warnings = detect_warnings(qa_coverage, clusters)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "risk_signals": {
            "subsystem_risk_score": dict(
                sorted(subsystem_scores.items(), key=lambda x: -x[1])
            ),
            "failure_class_frequency": dict(
                sorted(failure_class_freq.items(), key=lambda x: -x[1])
            ),
        },
        "qa_coverage": qa_coverage,
        "clusters": clusters,
        "warnings": warnings,
    }


def save_analytics(analytics: dict, path: Path) -> None:
    """
    Schreibt analytics.json.

    Erstellt übergeordnete Verzeichnisse falls nötig.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(analytics, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def main() -> int:
    """CLI-Einstiegspunkt."""
    parser = argparse.ArgumentParser(
        description="Analysiert incidents/index.json und erzeugt analytics.json.",
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
        help="Keine Ausgabe",
    )
    args = parser.parse_args()

    index_path = args.index
    if not index_path.is_absolute():
        index_path = (Path.cwd() / index_path).resolve()

    index = load_index(index_path)
    if not index:
        if not args.quiet:
            print(f"Fehler: index.json nicht gefunden oder ungültig: {index_path}", file=sys.stderr)
        return 1

    incidents = index.get("incidents") or []
    if not incidents:
        # Leere Registry: trotzdem valides analytics.json erzeugen
        analytics = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "risk_signals": {
                "subsystem_risk_score": {},
                "failure_class_frequency": {},
            },
            "qa_coverage": {"replay_defined_ratio": 0.0, "regression_bound_ratio": 0.0},
            "clusters": [],
            "warnings": [],
        }
    else:
        analytics = build_analytics(incidents)

    output_path = args.output
    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()

    try:
        save_analytics(analytics, output_path)
    except OSError as e:
        if not args.quiet:
            print(f"Fehler beim Schreiben: {e}", file=sys.stderr)
        return 1

    if not args.quiet:
        print(f"Analytics erzeugt: {output_path}")
        qc = analytics.get("qa_coverage", {})
        print(f"  Replay: {qc.get('replay_defined_ratio', 0):.0%} | Regression: {qc.get('regression_bound_ratio', 0):.0%}")
        print(f"  Warnungen: {len(analytics.get('warnings', []))}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

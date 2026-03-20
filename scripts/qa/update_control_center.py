#!/usr/bin/env python3
"""
QA Control Center Update Generator – Linux Desktop Chat.

Projiziert Ergebnisse aus:
- incidents/index.json
- incidents/analytics.json
- QA_AUTOPILOT_V2.json

in das Governance-Artefakt:
- docs/qa/QA_CONTROL_CENTER.json

Aktualisiert NUR das Control Center und eine Trace-Datei.
Ändert NICHT: Incidents, Replay-Daten, Regression Catalog, Produktcode.

Verwendung:
  python scripts/qa/update_control_center.py
  python scripts/qa/update_control_center.py --dry-run --output -
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Projekt-Root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.qa.feedback_loop import (
    load_feedback_inputs_from_paths,
    run_feedback_projections,
    normalize_to_subsystem_states,
    normalize_to_failure_class_states,
)
from scripts.qa.feedback_loop.utils import load_json

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOG = logging.getLogger(__name__)

VERSION = "2.0"
GENERATOR = "update_control_center"

# Drei Pilotkonstellationen
PILOT_1 = {"id": 1, "name": "Startup / Ollama unreachable", "subsystems": ["Startup/Bootstrap", "Provider/Ollama"]}
PILOT_2 = {"id": 2, "name": "RAG / ChromaDB network failure", "subsystems": ["RAG"]}
PILOT_3 = {"id": 3, "name": "Debug/EventBus / EventType drift", "subsystems": ["Debug/EventBus"]}


def _build_current_focus(autopilot: dict[str, Any]) -> dict[str, Any]:
    """current_focus aus QA_AUTOPILOT_V2."""
    return {
        "recommended_focus_subsystem": autopilot.get("recommended_focus_subsystem", ""),
        "recommended_failure_class": autopilot.get("recommended_focus_failure_class", ""),
        "recommended_guard_type": autopilot.get("recommended_guard_type", ""),
        "recommended_test_domain": autopilot.get("recommended_test_domain", ""),
        "recommended_next_sprint": autopilot.get("recommended_next_sprint", ""),
    }


def _build_feedback_loop_summary(
    subsystem_states: dict[str, Any],
    failure_class_states: dict[str, Any],
) -> dict[str, Any]:
    """feedback_loop_summary: top pressure, replay gap, regression gap, drift patterns."""
    sorted_by_pressure = sorted(
        subsystem_states.items(),
        key=lambda x: x[1].feedback_pressure_score if hasattr(x[1], "feedback_pressure_score") else 0,
        reverse=True,
    )
    top_incident = [
        {"subsystem": s, "pressure": getattr(st, "feedback_pressure_score", 0), "incident_count": getattr(st, "incident_count", 0)}
        for s, st in sorted_by_pressure[:5]
    ]

    sorted_by_replay = sorted(
        subsystem_states.items(),
        key=lambda x: x[1].replay_gap_rate if hasattr(x[1], "replay_gap_rate") else 0,
        reverse=True,
    )
    highest_replay = [
        {"subsystem": s, "replay_gap_rate": getattr(st, "replay_gap_rate", 0)}
        for s, st in sorted_by_replay[:5]
        if getattr(st, "replay_gap_rate", 0) > 0
    ]

    sorted_by_regression = sorted(
        subsystem_states.items(),
        key=lambda x: x[1].regression_gap_rate if hasattr(x[1], "regression_gap_rate") else 0,
        reverse=True,
    )
    highest_regression = [
        {"subsystem": s, "regression_gap_rate": getattr(st, "regression_gap_rate", 0)}
        for s, st in sorted_by_regression[:5]
        if getattr(st, "regression_gap_rate", 0) > 0
    ]

    drift_patterns = [
        {"failure_class": fc, "incident_count": getattr(st, "incident_count", 0)}
        for fc, st in failure_class_states.items()
        if getattr(st, "drift_related", False)
    ]

    return {
        "top_incident_pressure_subsystems": top_incident,
        "highest_replay_gap_subsystems": highest_replay,
        "highest_regression_gap_subsystems": highest_regression,
        "dominant_drift_patterns": drift_patterns,
    }


def _build_governance_alerts(
    report: Any,
    autopilot: dict[str, Any],
) -> list[dict[str, Any]]:
    """Governance Alerts für replay gaps, regression gaps, incident pressure."""
    alerts: list[dict[str, Any]] = []

    for sub, state in report.per_subsystem_results.items():
        if getattr(state, "replay_gap_rate", 0) >= 0.5 and getattr(state, "incident_count", 0) > 0:
            alerts.append({
                "code": "REPLAY_GAP",
                "subsystem": sub,
                "message": f"Replay-Gap: {getattr(state, 'replay_gap_rate', 0):.0%} ohne Replay",
            })
        if getattr(state, "regression_gap_rate", 0) >= 0.5 and getattr(state, "incident_count", 0) > 0:
            alerts.append({
                "code": "REGRESSION_GAP",
                "subsystem": sub,
                "message": f"Regression-Gap: {getattr(state, 'regression_gap_rate', 0):.0%} ohne Binding",
            })
        if getattr(state, "incident_count", 0) >= 2:
            alerts.append({
                "code": "INCIDENT_PRESSURE",
                "subsystem": sub,
                "message": f"Wiederholter Incident-Druck: {getattr(state, 'incident_count', 0)} Incidents",
            })

    for w in autopilot.get("warnings", []) or []:
        alerts.append({
            "code": w.get("code", "WARNING"),
            "message": w.get("message", str(w)),
        })

    return alerts


def _build_escalations(
    report: Any,
    autopilot: dict[str, Any],
) -> list[dict[str, Any]]:
    """Escalations für repeated drift, kritische cluster, strukturelle Muster."""
    escalations: list[dict[str, Any]] = []

    for e in autopilot.get("escalations", []) or []:
        escalations.append({
            "code": e.get("code", ""),
            "message": e.get("message", ""),
        })

    drift_count = sum(
        1 for _, st in report.per_failure_class_results.items()
        if getattr(st, "drift_related", False) and getattr(st, "incident_count", 0) >= 1
    )
    if drift_count >= 2:
        escalations.append({
            "code": "REPEATED_DRIFT",
            "message": f"Wiederholtes Drift-Muster: {drift_count} Failure-Classes",
        })

    for sub, state in report.per_subsystem_results.items():
        if getattr(state, "escalation_level", 0) >= 2:
            escalations.append({
                "code": "CRITICAL_CLUSTER",
                "subsystem": sub,
                "message": f"Kritischer Cluster: escalation_level={getattr(state, 'escalation_level', 0)}",
            })

    return escalations


def _build_pilot_tracking(autopilot: dict[str, Any]) -> dict[str, Any]:
    """Pilot-Tracking: drei bekannte Pilotfälle explizit abbilden."""
    matched = autopilot.get("pilot_constellation_matched") or {}
    return {
        "pilot_1_startup_ollama_unreachable": {
            "active": matched.get("id") == 1,
            "subsystems": PILOT_1["subsystems"],
        },
        "pilot_2_rag_chromadb_network_failure": {
            "active": matched.get("id") == 2,
            "subsystems": PILOT_2["subsystems"],
        },
        "pilot_3_debug_eventbus_eventtype_drift": {
            "active": matched.get("id") == 3,
            "subsystems": PILOT_3["subsystems"],
        },
        "current_matched": matched,
    }


def _build_change_log(
    old_cc: dict[str, Any] | None,
    new_output: dict[str, Any],
) -> list[dict[str, Any]]:
    """Vergleich mit vorheriger Control-Center-Version."""
    changes: list[dict[str, Any]] = []
    if not old_cc:
        return [{"field": "full", "old_value": None, "new_value": "initial", "reason": "Keine Vorversion"}]

    def _compare(key: str, old_val: Any, new_val: Any, reason: str) -> None:
        if old_val != new_val:
            changes.append({
                "field": key,
                "old_value": old_val,
                "new_value": new_val,
                "reason": reason,
            })

    _compare(
        "current_focus.recommended_focus_subsystem",
        (old_cc.get("current_focus") or {}).get("recommended_focus_subsystem"),
        (new_output.get("current_focus") or {}).get("recommended_focus_subsystem"),
        "Autopilot-Fokus aktualisiert",
    )
    _compare(
        "naechster_qa_sprint",
        old_cc.get("naechster_qa_sprint"),
        new_output.get("naechster_qa_sprint"),
        "Nächster Sprint aus Autopilot",
    )
    old_gen = old_cc.get("generated_at") or old_cc.get("generated")
    _compare("generated_at", old_gen, new_output.get("generated_at"), "Generator-Lauf")

    return changes


def _preserve_existing_fields(old_cc: dict[str, Any] | None) -> dict[str, Any]:
    """Bewahrt Felder aus der bestehenden Control-Center-Datei."""
    if not old_cc:
        return {}
    preserve_keys = [
        "gesamtstatus", "top_risiken", "qa_wartungsbedarf", "top_stabilisatoren",
        "top5_operative_empfehlungen", "operative_fragen", "empfehlung_iteration2",
        "iteration", "eingabedaten",
    ]
    return {k: old_cc[k] for k in preserve_keys if k in old_cc}


def build_control_center_output(
    report: Any,
    inputs: Any,
    old_cc: dict[str, Any] | None,
    optional_timestamp: str | None = None,
) -> dict[str, Any]:
    """Baut die vollständige Control-Center-Ausgabe."""
    autopilot = inputs.autopilot_v2 or {}
    generated_at = (
        optional_timestamp
        if optional_timestamp is not None
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    output: dict[str, Any] = {
        "generated_at": generated_at,
        "generator": GENERATOR,
        "version": VERSION,
        "input_sources": inputs.loaded_sources,
        "current_focus": _build_current_focus(autopilot),
        "feedback_loop_summary": _build_feedback_loop_summary(
            report.per_subsystem_results,
            report.per_failure_class_results,
        ),
        "governance_alerts": _build_governance_alerts(report, autopilot),
        "escalations": _build_escalations(report, autopilot),
        "pilot_tracking": _build_pilot_tracking(autopilot),
        "supporting_evidence": autopilot.get("supporting_evidence", {}),
        "warnings": report.global_warnings + [w.get("message", str(w)) for w in autopilot.get("warnings", []) or []],
    }

    output["change_log"] = _build_change_log(old_cc, output)

    # naechster_qa_sprint für Abwärtskompatibilität
    output["naechster_qa_sprint"] = {
        "subsystem": output["current_focus"]["recommended_focus_subsystem"],
        "schritt": output["current_focus"]["recommended_next_sprint"],
        "testart": output["current_focus"].get("recommended_test_domain", ""),
        "source": "QA_AUTOPILOT_V2",
    }

    # Bestehende Felder erhalten
    preserved = _preserve_existing_fields(old_cc)
    for k, v in preserved.items():
        if k not in output:
            output[k] = v

    return output


def build_trace_output(
    report: Any,
    inputs: Any,
    output: dict[str, Any],
) -> dict[str, Any]:
    """Trace-Datei für control_center_feedback_trace.json."""
    ctrl_rules = [r for r in report.rule_results if r.target_artifact == "QA_CONTROL_CENTER"]
    return {
        "generated_at": output.get("generated_at", ""),
        "generator": GENERATOR,
        "input_sources": inputs.loaded_sources,
        "applied_rules": [
            {"rule_id": rid, "target_key": r.target_key}
            for r in ctrl_rules
            for rid in r.applied_rule_ids
        ],
        "warnings": output.get("warnings", []),
        "summary": {
            "subsystems_analyzed": len(report.per_subsystem_results),
            "failure_classes_analyzed": len(report.per_failure_class_results),
            "governance_alerts": len(output.get("governance_alerts", [])),
            "escalations": len(output.get("escalations", [])),
            "change_log_entries": len(output.get("change_log", [])),
        },
    }


def main() -> int:
    from scripts.qa.qa_paths import DOCS_QA, ARTIFACTS_JSON, INCIDENTS, FEEDBACK_LOOP

    parser = argparse.ArgumentParser(description="QA Control Center Update Generator")
    inc_dir = INCIDENTS

    parser.add_argument(
        "--input-control-center",
        type=Path,
        default=ARTIFACTS_JSON / "QA_CONTROL_CENTER.json",
        help="Vorhandenes Control Center (Vergleich, Erhalt)",
    )
    parser.add_argument(
        "--input-autopilot",
        type=Path,
        default=ARTIFACTS_JSON / "QA_AUTOPILOT_V2.json",
        help="QA_AUTOPILOT_V2.json",
    )
    parser.add_argument(
        "--input-incidents",
        type=Path,
        default=inc_dir / "index.json",
        help="incidents/index.json",
    )
    parser.add_argument(
        "--input-analytics",
        type=Path,
        default=inc_dir / "analytics.json",
        help="incidents/analytics.json",
    )
    parser.add_argument(
        "--input-priority-score",
        type=Path,
        default=ARTIFACTS_JSON / "QA_PRIORITY_SCORE.json",
        help="QA_PRIORITY_SCORE.json (für Subsystem-Liste)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ARTIFACTS_JSON / "QA_CONTROL_CENTER.json",
        help="Output Control Center (use '-' für stdout)",
    )
    parser.add_argument(
        "--trace-output",
        type=Path,
        default=FEEDBACK_LOOP / "control_center_feedback_trace.json",
        help="Trace-Datei",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Keine Dateien schreiben, nur berechnen und ausgeben",
    )
    parser.add_argument(
        "--timestamp",
        type=str,
        default=None,
        help="Optional: ISO-Format für Reproduzierbarkeit (z.B. 2025-01-15T12:00:00Z)",
    )
    args = parser.parse_args()

    # Inputs laden
    inputs = load_feedback_inputs_from_paths(
        incident_index_path=args.input_incidents,
        analytics_path=args.input_analytics,
        autopilot_path=args.input_autopilot,
        control_center_path=args.input_control_center,
        priority_score_path=args.input_priority_score,
    )

    if not inputs.autopilot_v2:
        LOG.error("QA_AUTOPILOT_V2.json fehlt – Abbruch")
        return 1

    # Altes Control Center (optional)
    old_cc = load_json(args.input_control_center) if args.input_control_center.exists() else None

    # Feedback-Projektion
    report = run_feedback_projections(inputs, optional_timestamp=args.timestamp)

    # Output bauen
    output = build_control_center_output(
        report, inputs, old_cc, optional_timestamp=args.timestamp
    )
    trace = build_trace_output(report, inputs, output)

    if args.dry_run:
        print(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True))
        print("--- TRACE ---", file=sys.stderr)
        print(json.dumps(trace, indent=2, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 0

    # Schreiben
    if str(args.output) == "-":
        print(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True))
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        try:
            args.output.write_text(
                json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            LOG.info("Control Center geschrieben: %s", args.output)
        except OSError as e:
            LOG.error("Schreibfehler %s: %s", args.output, e)
            return 1

    args.trace_output.parent.mkdir(parents=True, exist_ok=True)
    try:
        args.trace_output.write_text(
            json.dumps(trace, indent=2, ensure_ascii=False, sort_keys=True),
            encoding="utf-8",
        )
        LOG.info("Trace geschrieben: %s", args.trace_output)
    except OSError as e:
        LOG.error("Schreibfehler %s: %s", args.trace_output, e)
        return 1

    print(f"Control Center aktualisiert: {output.get('current_focus', {}).get('recommended_focus_subsystem', '?')}")
    print(f"  Governance Alerts: {len(output.get('governance_alerts', []))}")
    print(f"  Eskalationen: {len(output.get('escalations', []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

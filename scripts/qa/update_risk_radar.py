#!/usr/bin/env python3
"""
QA Risk Radar Update Generator – Linux Desktop Chat.

Projiziert Incident-Lage und Replay-/Regression-/Drift-Signale auf:
- docs/qa/QA_RISK_RADAR.json

Aktualisiert NUR das Risk Radar und die Trace-Datei.
Ändert NICHT: Incidents, Tests, Replay-Szenarien, Regression Catalog, Produktcode.

Verwendung:
  python scripts/qa/update_risk_radar.py
  python scripts/qa/update_risk_radar.py --dry-run --output -
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
)
from scripts.qa.feedback_loop.thresholds import (
    INCIDENT_COUNT_CLUSTER,
    REPLAY_GAP_WARNING,
    REGRESSION_GAP_WARNING,
    DRIFT_COUNT_ESCALATION,
)
from scripts.qa.feedback_loop.utils import load_json

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOG = logging.getLogger(__name__)

VERSION = "2.0"
GENERATOR = "update_risk_radar"

# Risk Policy
ALLOWED_LEVELS = ("low", "medium", "high", "critical")
LEVEL_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


def _parse_risk_radar_md(content: str) -> dict[str, str]:
    """
    Parst Subsystem -> Priorität aus QA_RISK_RADAR.md.
    Sucht Tabelle mit Subsystem und Priorität (P1, P2, P3).
    """
    result: dict[str, str] = {}
    lines = content.split("\n")
    in_table = False

    for line in lines:
        stripped = line.strip()
        if "| Subsystem |" in stripped and "Priorität" in stripped:
            in_table = True
            continue
        if in_table and stripped.startswith("|") and "---" not in stripped:
            parts = [p.strip().replace("**", "").strip() for p in stripped.split("|") if p.strip()]
            if len(parts) >= 2:
                sub = parts[0]
                # Priorität ist typisch letzte Spalte
                prio = ""
                for p in reversed(parts):
                    if p in ("P1", "P2", "P3"):
                        prio = p
                        break
                if sub and sub != "Subsystem" and prio:
                    result[sub] = prio
        elif in_table and stripped.startswith("##"):
            break
    return result


def _prioritaet_to_risk_level(prio: str) -> str:
    """P1 -> high, P2 -> medium, P3 -> low."""
    m = {"P1": "high", "P2": "medium", "P3": "low"}
    return m.get(prio, "medium")


def _markers_and_rules_from_rule_results(
    report: Any,
    sub: str,
) -> tuple[list[str], list[str], list[str]]:
    """
    Extrahiert markers, reasons, applied_rules aus report.rule_results (C1).
    Adapter: rule_results (target_artifact=QA_RISK_RADAR, subsystem.X.*) -> markers.
    """
    risk_rules = [
        r for r in (report.rule_results or [])
        if r.target_artifact == "QA_RISK_RADAR" and r.target_key.startswith(f"subsystem.{sub}.")
    ]
    marker_map = {
        "cluster_risk": "cluster_risk",
        "reproducibility_risk": "reproducibility_risk",
        "regression_protection_risk": "regression_protection_risk",
    }
    markers: list[str] = []
    reasons: list[str] = []
    rules: list[str] = []
    for r in risk_rules:
        suffix = r.target_key.split(".")[-1] if "." in r.target_key else ""
        if suffix in marker_map:
            markers.append(marker_map[suffix])
            reasons.extend(r.reasons)
            rules.extend(r.applied_rule_ids)
    return markers, reasons, list(dict.fromkeys(rules))


def _subsystem_risk_level_from_markers(
    state: Any,
    markers: list[str],
    old_level: str,
    single_incident_not_auto_high: bool,
) -> str:
    """Eskalationslogik: markers + state -> new_risk_level."""
    inc_count = getattr(state, "incident_count", 0)
    replay_gap = getattr(state, "replay_gap_rate", 0)
    reg_gap = getattr(state, "regression_gap_rate", 0)
    drift = getattr(state, "drift_density", 0)

    can_escalate = False
    if inc_count >= INCIDENT_COUNT_CLUSTER:
        can_escalate = True
    if replay_gap >= REPLAY_GAP_WARNING and reg_gap >= REGRESSION_GAP_WARNING and inc_count > 0:
        can_escalate = True
    if drift > 0:
        can_escalate = True

    if inc_count == 0 and not markers:
        return old_level
    if single_incident_not_auto_high and inc_count == 1 and not can_escalate:
        return "medium"
    if can_escalate:
        if inc_count >= 3 or (replay_gap >= 0.8 and reg_gap >= 0.8):
            return "critical"
        if inc_count >= 2 or len(markers) >= 2:
            return "high"
        return "high"
    return "medium" if inc_count == 1 else "low"


def _failure_class_from_rule_results(
    report: Any,
    fc: str,
) -> tuple[str, list[str], list[str]]:
    """
    Extrahiert risk_level, markers, reasons aus report.rule_results (C1).
    Adapter: rule_results (failure_class.X.severity, structural.drift_risk) -> fc output.
    """
    fc_rules = [
        r for r in (report.rule_results or [])
        if r.target_artifact == "QA_RISK_RADAR"
        and (r.target_key.startswith(f"failure_class.{fc}.") or r.target_key == "structural.drift_risk")
    ]
    drift_risk = any(r.target_key == "structural.drift_risk" for r in fc_rules)
    severity_rules = [r for r in fc_rules if r.target_key.startswith(f"failure_class.{fc}.severity")]

    inc_count = getattr(
        report.per_failure_class_results.get(fc),
        "incident_count",
        0,
    )
    drift_related = getattr(
        report.per_failure_class_results.get(fc),
        "drift_related",
        False,
    )
    drift_count = sum(
        1 for _, s in report.per_failure_class_results.items()
        if getattr(s, "drift_related", False) and getattr(s, "incident_count", 0) >= 1
    )

    markers: list[str] = []
    reasons: list[str] = []
    rules: list[str] = []

    if severity_rules:
        markers.append("failure_cluster")
        for r in severity_rules:
            reasons.extend(r.reasons)
            rules.extend(r.applied_rule_ids)
        risk_level = "high"
    elif drift_related and drift_count >= DRIFT_COUNT_ESCALATION and drift_risk:
        markers.append("drift_pattern")
        for r in fc_rules:
            if r.target_key == "structural.drift_risk":
                reasons.extend(r.reasons)
                rules.extend(r.applied_rule_ids)
                break
        risk_level = "high"
    elif inc_count == 1:
        risk_level = "medium"
    else:
        risk_level = "low"

    return risk_level, markers, reasons


def _apply_bounded_escalation(
    old_level: str,
    computed_level: str,
    bounded: bool,
) -> str:
    """Begrenzt Eskalation: maximal eine Stufe pro Lauf."""
    if not bounded:
        return computed_level
    old_idx = LEVEL_ORDER.get(old_level, 0)
    new_idx = LEVEL_ORDER.get(computed_level, 0)
    if new_idx <= old_idx + 1:
        return computed_level
    # Max eine Stufe hoch
    for level, idx in sorted(LEVEL_ORDER.items(), key=lambda x: x[1]):
        if idx == old_idx + 1:
            return level
    return old_level


def build_subsystems(
    report: Any,
    old_risk_levels: dict[str, str],
    single_incident_not_auto_high: bool,
    bounded_escalation: bool,
) -> dict[str, Any]:
    """
    Baut subsystems aus report.rule_results (C1).
    Adapter: rule_results -> markers; Eskalationslogik bleibt im Script.
    """
    result: dict[str, Any] = {}

    for sub, state in report.per_subsystem_results.items():
        old_level = old_risk_levels.get(sub, "medium")
        markers, reasons, rules = _markers_and_rules_from_rule_results(report, sub)
        new_level = _subsystem_risk_level_from_markers(
            state, markers, old_level, single_incident_not_auto_high
        )
        new_level = _apply_bounded_escalation(old_level, new_level, bounded_escalation)

        result[sub] = {
            "old_risk_level": old_level,
            "new_risk_level": new_level,
            "markers": markers,
            "reasons": reasons,
            "applied_rules": rules,
        }

    return result


def build_failure_classes(
    report: Any,
) -> dict[str, Any]:
    """Baut failure_classes aus report.rule_results (C1)."""
    result: dict[str, Any] = {}

    for fc in report.per_failure_class_results:
        risk_level, markers, reasons = _failure_class_from_rule_results(report, fc)
        result[fc] = {
            "risk_level": risk_level,
            "markers": markers,
            "reasons": reasons,
        }

    return result


def build_escalations(
    report: Any,
    autopilot: dict[str, Any],
    subsystems: dict[str, Any],
) -> list[str]:
    """Erzeugt Eskalationsliste."""
    escalations: list[str] = []

    for e in autopilot.get("escalations", []) or []:
        code = e.get("code", "")
        msg = e.get("message", "")
        if code or msg:
            escalations.append(f"{code}: {msg}" if code else msg)

    for sub, data in subsystems.items():
        if data.get("new_risk_level") in ("high", "critical"):
            markers = data.get("markers", [])
            if markers:
                escalations.append(f"Subsystem {sub}: {data['new_risk_level']} ({', '.join(markers)})")

    drift_count = sum(
        1 for _, s in report.per_failure_class_results.items()
        if getattr(s, "drift_related", False) and getattr(s, "incident_count", 0) >= 1
    )
    if drift_count >= DRIFT_COUNT_ESCALATION:
        escalations.append(f"Structural drift: {drift_count} drift-related failure classes")

    return escalations


def build_risk_radar_output(
    report: Any,
    inputs: Any,
    old_risk_levels: dict[str, str],
    single_incident_not_auto_high: bool,
    bounded_escalation: bool,
    optional_timestamp: str | None = None,
) -> dict[str, Any]:
    """Baut die vollständige QA_RISK_RADAR-Ausgabe."""
    autopilot = inputs.autopilot_v2 or {}
    generated_at = (
        optional_timestamp
        if optional_timestamp is not None
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    subsystems = build_subsystems(
        report, old_risk_levels, single_incident_not_auto_high, bounded_escalation
    )
    failure_classes = build_failure_classes(report)
    escalations = build_escalations(report, autopilot, subsystems)

    warnings: list[str] = []
    if not inputs.incident_index:
        warnings.append("incidents/index.json fehlt – Projektion eingeschränkt")
    if not inputs.analytics:
        warnings.append("incidents/analytics.json fehlt – Projektion eingeschränkt")
    for w in report.global_warnings or []:
        if w not in warnings:
            warnings.append(w)

    return {
        "generated_at": generated_at,
        "generator": GENERATOR,
        "version": VERSION,
        "input_sources": inputs.loaded_sources,
        "risk_policy": {
            "allowed_levels": list(ALLOWED_LEVELS),
            "bounded_escalation": bounded_escalation,
            "single_incident_not_auto_high": single_incident_not_auto_high,
        },
        "subsystems": subsystems,
        "failure_classes": failure_classes,
        "warnings": warnings,
        "escalations": escalations,
    }


def build_trace_output(
    output: dict[str, Any],
    inputs: Any,
) -> dict[str, Any]:
    """Trace-Datei für risk_radar_feedback_trace.json."""
    rules_used: set[str] = set()
    for sub, data in output.get("subsystems", {}).items():
        rules_used.update(data.get("applied_rules", []))

    return {
        "generated_at": output.get("generated_at", ""),
        "generator": GENERATOR,
        "input_sources": inputs.loaded_sources,
        "applied_rules": sorted(rules_used),
        "warnings": output.get("warnings", []),
        "escalations": output.get("escalations", []),
        "summary": {
            "subsystems_elevated": sum(
                1 for d in output.get("subsystems", {}).values()
                if LEVEL_ORDER.get(d.get("new_risk_level", ""), 0) > LEVEL_ORDER.get(d.get("old_risk_level", ""), 0)
            ),
            "failure_classes_high": sum(
                1 for d in output.get("failure_classes", {}).values()
                if d.get("risk_level") in ("high", "critical")
            ),
            "total_escalations": len(output.get("escalations", [])),
        },
    }


def main() -> int:
    from scripts.qa.qa_paths import DOCS_QA, ARTIFACTS_JSON, ARTIFACTS_DASHBOARDS, INCIDENTS, FEEDBACK_LOOP

    parser = argparse.ArgumentParser(description="QA Risk Radar Update Generator")
    inc_dir = INCIDENTS

    parser.add_argument("--input-risk-radar", type=Path, default=ARTIFACTS_DASHBOARDS / "QA_RISK_RADAR.md")
    parser.add_argument("--input-autopilot", type=Path, default=ARTIFACTS_JSON / "QA_AUTOPILOT_V2.json")
    parser.add_argument("--input-incidents", type=Path, default=inc_dir / "index.json")
    parser.add_argument("--input-analytics", type=Path, default=inc_dir / "analytics.json")
    parser.add_argument(
        "--input-priority-score",
        type=Path,
        default=ARTIFACTS_JSON / "QA_PRIORITY_SCORE.json",
        help="QA_PRIORITY_SCORE.json (für Subsystem-Liste)",
    )
    parser.add_argument("--input-stability-index", type=Path, default=ARTIFACTS_JSON / "QA_STABILITY_INDEX.json")
    parser.add_argument("--input-heatmap", type=Path, default=ARTIFACTS_JSON / "QA_HEATMAP.json")
    parser.add_argument("--output", type=Path, default=ARTIFACTS_JSON / "QA_RISK_RADAR.json")
    parser.add_argument(
        "--trace-output",
        type=Path,
        default=FEEDBACK_LOOP / "risk_radar_feedback_trace.json",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--timestamp",
        type=str,
        default=None,
        help="Optional: ISO-Format für Reproduzierbarkeit (z.B. 2025-01-15T12:00:00Z)",
    )
    args = parser.parse_args()

    inputs = load_feedback_inputs_from_paths(
        incident_index_path=args.input_incidents,
        analytics_path=args.input_analytics,
        autopilot_path=args.input_autopilot,
        control_center_path=None,
        priority_score_path=args.input_priority_score,
    )

    if not inputs.incident_index and not inputs.analytics:
        LOG.warning("Weder incidents noch analytics gefunden – minimale Projektion")

    # Alte Risk-Level aus Markdown oder JSON
    old_risk_levels: dict[str, str] = {}
    if args.input_risk_radar.exists():
        if args.input_risk_radar.suffix == ".json":
            data = load_json(args.input_risk_radar)
            if data and "subsystems" in data:
                for sub, d in data["subsystems"].items():
                    old_risk_levels[sub] = d.get("old_risk_level") or d.get("new_risk_level", "medium")
        else:
            try:
                content = args.input_risk_radar.read_text(encoding="utf-8")
                prio_map = _parse_risk_radar_md(content)
                old_risk_levels = {k: _prioritaet_to_risk_level(v) for k, v in prio_map.items()}
            except OSError:
                pass

    report = run_feedback_projections(inputs, optional_timestamp=args.timestamp)

    output = build_risk_radar_output(
        report,
        inputs,
        old_risk_levels,
        single_incident_not_auto_high=True,
        bounded_escalation=True,
        optional_timestamp=args.timestamp,
    )
    trace = build_trace_output(output, inputs)

    if args.dry_run:
        print(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True))
        print("--- TRACE ---", file=sys.stderr)
        print(json.dumps(trace, indent=2, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 0

    if str(args.output) != "-":
        args.output.parent.mkdir(parents=True, exist_ok=True)
        try:
            args.output.write_text(
                json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            LOG.info("Risk Radar geschrieben: %s", args.output)
        except OSError as e:
            LOG.error("Schreibfehler %s: %s", args.output, e)
            return 1
    else:
        print(json.dumps(output, indent=2, ensure_ascii=False, sort_keys=True))

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

    elevated = trace.get("summary", {}).get("subsystems_elevated", 0)
    print(f"Risk Radar aktualisiert: {elevated} Subsysteme eskaliert")
    print(f"  Eskalationen: {len(output.get('escalations', []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
QA Priority Score Update Generator – Linux Desktop Chat.

Projiziert reale Incident-Signale auf:
- docs/qa/QA_PRIORITY_SCORE.json

Nachkalibriert die QA-Priorisierung.
Ändert NUR Governance-Prioritäten.
Ändert NICHT: Tests, Incidents, Regression Catalog, Replay-Daten, Produktcode.

Verwendung:
  python scripts/qa/update_priority_scores.py
  python scripts/qa/update_priority_scores.py --dry-run --output -
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
from scripts.qa.feedback_loop.utils import load_json

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOG = logging.getLogger(__name__)

VERSION = "2.0"
GENERATOR = "update_priority_scores"

# Bounded Mutation
SCORE_MIN = 0
SCORE_MAX = 100
MAX_DELTA_PER_RUN = 10

# Skalierung: QA_PRIORITY_SCORE hat typisch 1-5, wir arbeiten in 0-100
ORIGINAL_SCORE_MAX = 5
SCALE_FACTOR = SCORE_MAX / ORIGINAL_SCORE_MAX  # 20


def _extract_old_subsystem_scores(priority_data: dict[str, Any] | None) -> dict[str, int]:
    """Extrahiert Subsystem -> Score (0-100 skaliert) aus QA_PRIORITY_SCORE."""
    out: dict[str, int] = {}
    if not priority_data:
        return out
    for s in priority_data.get("scores", []):
        sub = s.get("Subsystem")
        if sub:
            raw = int(s.get("Score", 0))
            out[sub] = min(SCORE_MAX, max(SCORE_MIN, int(raw * SCALE_FACTOR)))
    return out


def _apply_bounds(
    old_score: int,
    raw_delta: int,
    smoothing: bool = False,
) -> tuple[int, int, bool]:
    """
    Wendet Bounded Mutation an.
    Returns: (capped_delta, new_score, was_suppressed)
    """
    capped_delta = max(-MAX_DELTA_PER_RUN, min(MAX_DELTA_PER_RUN, raw_delta))
    if smoothing and abs(capped_delta) > 5:
        capped_delta = int(capped_delta * 0.7)  # leichte Glättung
    new_score = max(SCORE_MIN, min(SCORE_MAX, old_score + capped_delta))
    was_suppressed = raw_delta != capped_delta
    return capped_delta, new_score, was_suppressed


def _subsystem_scores_from_rule_results(
    report: Any,
    old_scores: dict[str, int],
    smoothing_enabled: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """
    Baut subsystem_scores aus report.rule_results (C1: Single Source of Truth).
    Adapter: rule_results (target_artifact=QA_PRIORITY_SCORE) -> subsystem_scores.
    """
    prio_rules = [
        r for r in (report.rule_results or [])
        if r.target_artifact == "QA_PRIORITY_SCORE" and r.target_key.startswith("scores.")
    ]
    score_rules: dict[str, Any] = {}
    contract_rules: dict[str, int] = {}
    for r in prio_rules:
        parts = r.target_key.split(".")
        if len(parts) >= 3:
            sub = parts[1]
            if r.target_key.endswith(".Score"):
                score_rules[sub] = r
            elif r.target_key.endswith(".contract_priority"):
                contract_rules[sub] = contract_rules.get(sub, 0) + (r.delta or 0)

    scores: dict[str, Any] = {}
    suppressed: list[dict[str, Any]] = []

    all_subs = (
        set(report.per_subsystem_results.keys())
        | set(old_scores.keys())
        | set(score_rules.keys())
        | set(contract_rules.keys())
    )
    for sub in sorted(all_subs):
        state = report.per_subsystem_results.get(sub)
        old_score = old_scores.get(sub, 0)
        feedback_pressure = round(state.feedback_pressure_score, 2) if state else 0.0
        escalation_level = state.escalation_level if state else 0

        rule = score_rules.get(sub)
        contract_delta = contract_rules.get(sub, 0)
        if not rule and contract_delta == 0:
            scores[sub] = {
                "old_score": old_score,
                "new_score": old_score,
                "delta": 0,
                "feedback_pressure_score": feedback_pressure,
                "escalation_level": escalation_level,
                "reasons": [],
                "applied_rules": [],
            }
            continue

        old_val = rule.old_value if rule else 0
        new_val = rule.new_value if rule else old_val
        raw_delta_10 = (new_val - old_val) + contract_delta
        raw_delta_100 = int(raw_delta_10 * 10)
        reasons = list(rule.reasons) if rule else []
        rule_ids = list(rule.applied_rule_ids) if rule else []
        if contract_delta > 0:
            rule_ids.append("FL-PRIO-007")
            reasons.append("Drift pattern: contract priority")

        capped_delta, new_score, was_suppressed = _apply_bounds(
            old_score, raw_delta_100, smoothing_enabled
        )
        if was_suppressed:
            suppressed.append({
                "subsystem": sub,
                "raw_delta": raw_delta_100,
                "capped_delta": capped_delta,
                "reason": f"Delta {raw_delta_100} überschreitet max_delta_per_run={MAX_DELTA_PER_RUN}",
            })

        scores[sub] = {
            "old_score": old_score,
            "new_score": new_score,
            "delta": capped_delta,
            "feedback_pressure_score": feedback_pressure,
            "escalation_level": escalation_level,
            "reasons": reasons,
            "applied_rules": rule_ids,
        }

    return scores, suppressed


def _failure_class_scores_from_rule_results(report: Any) -> dict[str, Any]:
    """
    Baut failure_class_scores aus report.rule_results (C1).
    Adapter: rule_results (failure_class.*.priority_boost) -> failure_class_scores.
    """
    fc_rules = [
        r for r in (report.rule_results or [])
        if r.target_artifact == "QA_PRIORITY_SCORE"
        and r.target_key.startswith("failure_class.") and r.target_key.endswith(".priority_boost")
    ]
    fc_by_rule: dict[str, Any] = {}
    for r in fc_rules:
        parts = r.target_key.split(".")
        if len(parts) >= 3:
            fc = parts[1]
            fc_by_rule[fc] = r

    scores: dict[str, Any] = {}
    for fc in report.per_failure_class_results:
        rule = fc_by_rule.get(fc)
        if not rule:
            scores[fc] = {
                "old_score": 0,
                "new_score": 0,
                "delta": 0,
                "reasons": [],
                "applied_rules": [],
            }
            continue
        delta = rule.delta or 1
        new_val = rule.new_value or 1
        scores[fc] = {
            "old_score": 0,
            "new_score": new_val,
            "delta": delta,
            "reasons": list(rule.reasons),
            "applied_rules": list(rule.applied_rule_ids),
        }
    return scores


def build_updated_scores_array(
    subsystem_scores: dict[str, Any],
    priority_data: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    """Erzeugt scores[] für QA_PRIORITY_SCORE (Abwärtskompatibilität)."""
    result: list[dict[str, Any]] = []
    orig_scores = {s.get("Subsystem"): s for s in (priority_data or {}).get("scores", [])}

    for sub, data in sorted(subsystem_scores.items()):
        new_score_100 = data["new_score"]
        new_score_orig = max(1, min(ORIGINAL_SCORE_MAX, round(new_score_100 / SCALE_FACTOR)))
        orig = orig_scores.get(sub, {})
        result.append({
            "Subsystem": sub,
            "Score": new_score_orig,
            "Prioritaet": orig.get("Prioritaet", "P2"),
            "Begruendung": orig.get("Begruendung", ""),
            "Naechster_QA_Schritt": orig.get("Naechster_QA_Schritt", "–"),
            "Score_Detail": orig.get("Score_Detail", ""),
        })
    return result


def build_priority_score_output(
    report: Any,
    inputs: Any,
    old_priority: dict[str, Any] | None,
    smoothing_enabled: bool,
    optional_timestamp: str | None = None,
) -> dict[str, Any]:
    """Baut die vollständige QA_PRIORITY_SCORE-Ausgabe."""
    autopilot = inputs.autopilot_v2 or {}
    generated_at = (
        optional_timestamp
        if optional_timestamp is not None
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    old_scores = _extract_old_subsystem_scores(inputs.priority_score or old_priority)

    subsystem_scores, suppressed = _subsystem_scores_from_rule_results(
        report, old_scores, smoothing_enabled
    )
    failure_class_scores = _failure_class_scores_from_rule_results(report)

    warnings: list[str] = []
    if not inputs.incident_index:
        warnings.append("incidents/index.json fehlt – Projektion eingeschränkt")
    if not inputs.analytics:
        warnings.append("incidents/analytics.json fehlt – Projektion eingeschränkt")
    if not inputs.autopilot_v2:
        warnings.append("QA_AUTOPILOT_V2.json fehlt – Autopilot-Fokus nicht verfügbar")
    for w in (report.global_warnings or []):
        if w not in warnings:
            warnings.append(w)

    output: dict[str, Any] = {
        "generated_at": generated_at,
        "generator": GENERATOR,
        "version": VERSION,
        "input_sources": inputs.loaded_sources,
        "score_policy": {
            "score_min": SCORE_MIN,
            "score_max": SCORE_MAX,
            "max_delta_per_run": MAX_DELTA_PER_RUN,
            "smoothing_enabled": smoothing_enabled,
        },
        "subsystem_scores": subsystem_scores,
        "failure_class_scores": failure_class_scores,
        "warnings": warnings,
        "suppressed_changes": suppressed,
    }

    # Abwärtskompatibilität: scores[], top3_prioritaeten, top3_naechste_sprints
    output["scores"] = build_updated_scores_array(subsystem_scores, inputs.priority_score or old_priority)
    sorted_subs = sorted(
        subsystem_scores.items(),
        key=lambda x: x[1]["new_score"],
        reverse=True,
    )
    output["top3_prioritaeten"] = [
        {"Rang": i, "Subsystem": s, "Score": d["new_score"] // SCALE_FACTOR, "Begruendung": ""}
        for i, (s, d) in enumerate(sorted_subs[:3], 1)
    ]
    priority_data = inputs.priority_score or old_priority or {}
    orig_steps = {x.get("Subsystem"): x.get("Schritt", "–") for x in priority_data.get("top3_naechste_sprints", [])}
    output["top3_naechste_sprints"] = [
        {"Rang": i, "Subsystem": s, "Schritt": orig_steps.get(s, "–")}
        for i, (s, _) in enumerate(sorted_subs[:3], 1)
    ]
    if priority_data.get("scoring_logik"):
        output["scoring_logik"] = priority_data["scoring_logik"]
    orig_eingabe = priority_data.get("eingabedaten") or []
    output["eingabedaten"] = list(dict.fromkeys(orig_eingabe + ["incidents/index.json", "incidents/analytics.json", "QA_AUTOPILOT_V2.json"]))

    return output


def build_trace_output(
    output: dict[str, Any],
    inputs: Any,
) -> dict[str, Any]:
    """Trace-Datei für priority_score_feedback_trace.json."""
    rules_used: set[str] = set()
    for sub, data in output.get("subsystem_scores", {}).items():
        rules_used.update(data.get("applied_rules", []))
    for fc, data in output.get("failure_class_scores", {}).items():
        rules_used.update(data.get("applied_rules", []))

    return {
        "generated_at": output.get("generated_at", ""),
        "generator": GENERATOR,
        "input_sources": inputs.loaded_sources,
        "applied_rules": sorted(rules_used),
        "warnings": output.get("warnings", []),
        "suppressed_changes": output.get("suppressed_changes", []),
        "summary": {
            "subsystems_updated": sum(1 for d in output.get("subsystem_scores", {}).values() if d.get("delta", 0) != 0),
            "failure_classes_updated": sum(1 for d in output.get("failure_class_scores", {}).values() if d.get("delta", 0) != 0),
            "total_suppressed": len(output.get("suppressed_changes", [])),
        },
    }


def main() -> int:
    from scripts.qa.qa_paths import ARTIFACTS_JSON, INCIDENTS, FEEDBACK_LOOP

    parser = argparse.ArgumentParser(description="QA Priority Score Update Generator")
    inc_dir = INCIDENTS

    parser.add_argument("--input-priority-score", type=Path, default=ARTIFACTS_JSON / "QA_PRIORITY_SCORE.json")
    parser.add_argument("--input-autopilot", type=Path, default=ARTIFACTS_JSON / "QA_AUTOPILOT_V2.json")
    parser.add_argument("--input-incidents", type=Path, default=inc_dir / "index.json")
    parser.add_argument("--input-analytics", type=Path, default=inc_dir / "analytics.json")
    parser.add_argument(
        "--input-dependency-graph",
        type=Path,
        default=None,
        help="Optional: QA_DEPENDENCY_GRAPH.json oder .md",
    )
    parser.add_argument("--output", type=Path, default=ARTIFACTS_JSON / "QA_PRIORITY_SCORE.json")
    parser.add_argument(
        "--trace-output",
        type=Path,
        default=FEEDBACK_LOOP / "priority_score_feedback_trace.json",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--smoothing", action="store_true", help="Leichte Glättung gegen überaggressive Sprünge")
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

    if not inputs.priority_score and not inputs.incident_index:
        LOG.error("Weder QA_PRIORITY_SCORE.json noch incidents/index.json gefunden – Abbruch")
        return 1

    old_priority = load_json(args.input_priority_score) if args.input_priority_score.exists() else None

    report = run_feedback_projections(inputs, optional_timestamp=args.timestamp)

    output = build_priority_score_output(
        report, inputs, old_priority, args.smoothing,
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
            LOG.info("Priority Score geschrieben: %s", args.output)
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

    updated = sum(1 for d in output.get("subsystem_scores", {}).values() if d.get("delta", 0) != 0)
    print(f"Priority Scores aktualisiert: {updated} Subsysteme mit Delta")
    print(f"  Suppressed: {len(output.get('suppressed_changes', []))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

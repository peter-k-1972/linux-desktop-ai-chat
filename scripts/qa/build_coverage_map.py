#!/usr/bin/env python3
"""
QA Coverage Map Generator – Linux Desktop Chat.

Liest QA-Artefakte, aggregiert Coverage, erkennt Gaps, schreibt QA_COVERAGE_MAP.json.
Phase 2 – Learning-QA-Architektur.

Output: docs/qa/artifacts/json/QA_COVERAGE_MAP.json

Verwendung:
  python scripts/qa/build_coverage_map.py
  python scripts/qa/build_coverage_map.py --dry-run
  python scripts/qa/build_coverage_map.py --output -
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.qa.coverage_map_loader import load_all_inputs
from scripts.qa.gap_prioritization import build_prioritized_gaps
from scripts.qa.coverage_map_rules import (
    aggregate_autopilot_recommendation,
    aggregate_by_failure_class,
    aggregate_by_guard,
    aggregate_by_test_domain,
    aggregate_regression_requirement,
    aggregate_replay_binding,
    build_gap_types,
    compute_coverage_quality,
    compute_manual_review_required,
    compute_orphan_breakdown,
    detect_failure_class_gaps,
    detect_guard_gaps,
    detect_orphan_tests,
    detect_regression_requirement_gaps,
    detect_replay_binding_gaps,
    detect_semantic_binding_gaps,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOG = logging.getLogger(__name__)

from scripts.qa.qa_paths import DOCS_QA, ARTIFACTS_JSON

DEFAULT_DOCS_QA = DOCS_QA
DEFAULT_OUTPUT = ARTIFACTS_JSON / "QA_COVERAGE_MAP.json"


def build_coverage_map(
    inputs: dict,
    optional_timestamp: str | None = None,
    qa_dir: Path | None = None,
) -> dict:
    """Baut die vollständige Coverage Map."""
    inventory = inputs["inventory"]
    _qa_dir = qa_dir or DEFAULT_DOCS_QA
    test_strategy = inputs["test_strategy"]
    knowledge_graph = inputs["knowledge_graph"]
    autopilot_v3 = inputs["autopilot_v3"]
    bindings_by_incident = inputs["bindings_by_incident"]

    generated_at = (
        optional_timestamp
        if optional_timestamp is not None
        else datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    )

    # Aggregationen
    coverage_fc = aggregate_by_failure_class(inventory)
    coverage_guard = aggregate_by_guard(inventory)
    coverage_domain = aggregate_by_test_domain(inventory)
    regression_agg = aggregate_regression_requirement(
        inventory, test_strategy, autopilot_v3, bindings_by_incident
    )
    replay_agg = aggregate_replay_binding(inventory, bindings_by_incident)
    autopilot_agg = aggregate_autopilot_recommendation(inventory, autopilot_v3)

    coverage_by_axis = {
        "failure_class": coverage_fc,
        "guard": coverage_guard,
        "test_domain": coverage_domain,
        "regression_requirement": regression_agg,
        "replay_binding": replay_agg,
        "autopilot_recommendation": autopilot_agg,
    }

    # Gaps
    gaps_fc = detect_failure_class_gaps(coverage_fc)
    gaps_guard = detect_guard_gaps(coverage_guard, test_strategy.get("guard_requirements") or [])
    gaps_rr = detect_regression_requirement_gaps(regression_agg)
    gaps_rb = detect_replay_binding_gaps(replay_agg)

    gaps = {
        "failure_class": gaps_fc,
        "guard": gaps_guard,
        "regression_requirement": gaps_rr,
        "replay_binding": gaps_rb,
    }

    # Governance (Phase 3: Orphan-Governance mit breakdown)
    mrr = compute_manual_review_required(inventory)
    orphans = detect_orphan_tests(inventory, qa_dir=_qa_dir)
    orphan_breakdown = compute_orphan_breakdown(inventory, orphans, qa_dir=_qa_dir)
    semantic_gaps = detect_semantic_binding_gaps(inventory, knowledge_graph)

    governance = {
        "orphan_tests": orphans,
        "orphan_count": len(orphans),
        "orphan_breakdown": orphan_breakdown,
        "orphan_treat_as": orphan_breakdown.get("treat_as", "review_candidate"),
        "orphan_ci_blocking": orphan_breakdown.get("ci_blocking", False),
        "semantic_binding_gaps": semantic_gaps,
        "semantic_binding_gap_count": len(semantic_gaps),
        "manual_review_required": mrr,
    }

    # Summary
    total_tests = inventory.get("test_count") or len(inventory.get("tests") or [])
    inv_summary = inventory.get("summary") or {}
    manual_count = inv_summary.get("manual_review_required_count") or mrr["count"]

    coverage_strength = {
        "failure_class": _axis_strength(coverage_fc),
        "guard": _axis_strength(coverage_guard),
        "test_domain": "covered",
        "regression_requirement": regression_agg.get("coverage_strength", "n/a"),
        "replay_binding": replay_agg.get("coverage_strength", "n/a"),
        "autopilot_recommendation": autopilot_agg.get("coverage_strength", "n/a"),
    }

    quality = compute_coverage_quality(coverage_by_axis, mrr.get("share_of_total", 0))

    gap_count = {
        "failure_class": len(gaps_fc),
        "guard": len(gaps_guard),
        "regression_requirement": len(gaps_rr),
        "replay_binding": len(gaps_rb),
    }

    gap_types = build_gap_types(gaps, autopilot_agg)

    # Phase 3: Gap-Priorisierung
    # Autopilot mit aggregiertem Backlog (covered-Status) für korrekte Gap-Filterung
    autopilot_for_prioritization = dict(autopilot_v3 or {})
    backlog_with_coverage = autopilot_agg.get("backlog_items") or []
    if backlog_with_coverage:
        autopilot_for_prioritization["recommended_test_backlog"] = backlog_with_coverage

    prioritization_context = {
        "incidents": (inputs.get("incidents_index") or {}).get("incidents") or [],
        "guard_requirements": (test_strategy or {}).get("guard_requirements") or [],
        "recommended_focus_domains": (test_strategy or {}).get("recommended_focus_domains") or [],
        "recommended_test_backlog": backlog_with_coverage or (autopilot_v3 or {}).get("recommended_test_backlog") or [],
        "replay_bindings": replay_agg.get("bindings") or [],
        "autopilot_v3": autopilot_for_prioritization,
        "qa_dir": _qa_dir,
    }
    prioritized_gaps = build_prioritized_gaps(gaps, governance, prioritization_context)

    summary = {
        "total_tests": total_tests,
        "coverage_strength": coverage_strength,
        "coverage_quality": quality,
        "gap_count": gap_count,
        "gap_types": gap_types,
        "manual_review_required_count": manual_count,
    }

    inventory_snapshot = {
        "test_count": total_tests,
        "manual_review_required_count": manual_count,
        "generated_at": inventory.get("generated_at", ""),
    }

    return {
        "schema_version": "1.0",
        "generated_at": generated_at,
        "generator": "coverage_map",
        "input_sources": inputs["input_sources"],
        "inventory_snapshot": inventory_snapshot,
        "coverage_by_axis": coverage_by_axis,
        "gaps": gaps,
        "governance": governance,
        "prioritized_gaps": prioritized_gaps,
        "summary": summary,
    }


def _axis_strength(axis_data: dict) -> str:
    """Aggregiert coverage_strength für Axis (worst case)."""
    strengths = [v.get("coverage_strength") for v in axis_data.values() if isinstance(v, dict)]
    if "gap" in strengths:
        return "partial" if "covered" in strengths else "gap"
    if "partial" in strengths:
        return "partial"
    return "covered" if strengths else "n/a"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="QA Coverage Map – Aggregiert Coverage, erkennt Gaps, schreibt QA_COVERAGE_MAP.json"
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output-Pfad (use '-' for stdout)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Keine Datei schreiben, nur berechnen und ausgeben",
    )
    parser.add_argument(
        "--timestamp",
        type=str,
        default=None,
        help="Optional: ISO-Format für Reproduzierbarkeit",
    )
    parser.add_argument(
        "--qa-dir",
        type=Path,
        default=None,
        help="Pfad zu docs/qa (default: docs/qa)",
    )
    args = parser.parse_args()

    try:
        qa_dir = args.qa_dir or DEFAULT_DOCS_QA
        inputs = load_all_inputs(qa_dir)
        output_dict = build_coverage_map(inputs, optional_timestamp=args.timestamp, qa_dir=qa_dir)

        json_str = json.dumps(output_dict, indent=2, ensure_ascii=False, sort_keys=True)

        if args.dry_run:
            print(json_str)
            return 0

        if str(args.output) == "-":
            print(json_str)
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json_str, encoding="utf-8")
            LOG.info("QA Coverage Map geschrieben: %s", args.output)

        return 0

    except FileNotFoundError as e:
        LOG.error("%s", e)
        return 1
    except Exception as e:
        LOG.exception("Generator fehlgeschlagen: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())

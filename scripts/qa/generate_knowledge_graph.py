#!/usr/bin/env python3
"""
QA Knowledge Graph Generator – Linux Desktop Chat.

Modelliert explizit die Beziehungen zwischen Incidents, Failure Classes,
Guards, Test Domains und Regression Requirements.
Rein analytisch – keine Mutationen anderer Artefakte.

Output: docs/qa/QA_KNOWLEDGE_GRAPH.json
Trace: docs/qa/feedback_loop/knowledge_graph_trace.json

Verwendung:
  python scripts/qa/generate_knowledge_graph.py
  python scripts/qa/generate_knowledge_graph.py --dry-run --output -
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.qa.knowledge_graph import (
    load_knowledge_graph_inputs,
    build_knowledge_graph,
    output_to_dict,
    build_knowledge_graph_trace,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOG = logging.getLogger(__name__)

GENERATOR = "knowledge_graph"
DEFAULT_DOCS_QA = _PROJECT_ROOT / "docs" / "qa"
DEFAULT_OUTPUT = DEFAULT_DOCS_QA / "QA_KNOWLEDGE_GRAPH.json"
DEFAULT_TRACE = DEFAULT_DOCS_QA / "feedback_loop" / "knowledge_graph_trace.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="QA Knowledge Graph – Beziehungen zwischen Incidents, Failure Classes, Guards, Test Domains, Regression Requirements"
    )
    inc_dir = DEFAULT_DOCS_QA / "incidents"
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
        "--input-autopilot-v3",
        type=Path,
        default=DEFAULT_DOCS_QA / "QA_AUTOPILOT_V3.json",
        help="QA_AUTOPILOT_V3.json",
    )
    parser.add_argument(
        "--input-test-strategy",
        type=Path,
        default=DEFAULT_DOCS_QA / "QA_TEST_STRATEGY.json",
        help="QA_TEST_STRATEGY.json",
    )
    parser.add_argument(
        "--input-regression-catalog",
        type=Path,
        default=DEFAULT_DOCS_QA / "REGRESSION_CATALOG.json",
        help="REGRESSION_CATALOG.json (Fallback: REGRESSION_CATALOG.md)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Output-Pfad (use '-' for stdout)",
    )
    parser.add_argument(
        "--trace-output",
        type=Path,
        default=DEFAULT_TRACE,
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
        help="Optional: ISO-Format für Reproduzierbarkeit (z.B. 2026-01-01T00:00:00Z)",
    )
    args = parser.parse_args()

    try:
        inputs = load_knowledge_graph_inputs(
            incident_index_path=args.input_incidents,
            analytics_path=args.input_analytics,
            autopilot_v3_path=args.input_autopilot_v3,
            test_strategy_path=args.input_test_strategy,
            regression_catalog_path=args.input_regression_catalog,
        )

        output = build_knowledge_graph(inputs, optional_timestamp=args.timestamp)
        out_dict = output_to_dict(output)
        trace_dict = build_knowledge_graph_trace(output)

        if args.dry_run:
            print(json.dumps(out_dict, indent=2, ensure_ascii=False, sort_keys=True))
            if str(args.trace_output) != "-":
                print("--- TRACE ---", file=sys.stderr)
                print(json.dumps(trace_dict, indent=2, ensure_ascii=False, sort_keys=True), file=sys.stderr)
            return 0

        if str(args.output) == "-":
            print(json.dumps(out_dict, indent=2, ensure_ascii=False, sort_keys=True))
        else:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            try:
                args.output.write_text(
                    json.dumps(out_dict, indent=2, ensure_ascii=False, sort_keys=True),
                    encoding="utf-8",
                )
                LOG.info("QA Knowledge Graph geschrieben: %s", args.output)
            except OSError as e:
                LOG.error("Schreibfehler %s: %s", args.output, e)
                return 1

        args.trace_output.parent.mkdir(parents=True, exist_ok=True)
        try:
            args.trace_output.write_text(
                json.dumps(trace_dict, indent=2, ensure_ascii=False, sort_keys=True),
                encoding="utf-8",
            )
            LOG.info("Trace geschrieben: %s", args.trace_output)
        except OSError as e:
            LOG.error("Schreibfehler Trace %s: %s", args.trace_output, e)
            return 1

        ev = output.supporting_evidence
        print(
            f"Knowledge Graph: {len(output.nodes)} Nodes, {len(output.edges)} Edges "
            f"(incidents: {ev.get('incident_count', 0)}, failure_classes: {ev.get('failure_class_count', 0)})"
        )
        return 0

    except Exception as e:
        LOG.exception("Generator fehlgeschlagen: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())

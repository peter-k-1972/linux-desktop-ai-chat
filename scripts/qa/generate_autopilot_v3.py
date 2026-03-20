#!/usr/bin/env python3
"""
QA Autopilot v3 Generator – Linux Desktop Chat.

Erkennt systematisch fehlende Testabsicherung:
- Testlücken (missing_replay_test, missing_regression_test, missing_contract_test)
- Guard-Lücken (failure_replay_guard, event_contract_guard, startup_degradation_guard)
- Translation-Gaps (incident_not_bound_to_replay, incident_not_bound_to_regression, pilot_not_sufficiently_translated)

Output: docs/qa/QA_AUTOPILOT_V3.json

Autopilot v3 darf NICHT: Tests schreiben, Incidents ändern, Replay-Daten, Regression Catalog, Produktcode.

Verwendung:
  python scripts/qa/generate_autopilot_v3.py
  python scripts/qa/generate_autopilot_v3.py --dry-run --output -
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.qa.autopilot_v3 import (
    load_autopilot_v3_inputs,
    run_autopilot_v3_projections,
    build_autopilot_v3_trace,
)
from scripts.qa.autopilot_v3.traces import output_to_dict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOG = logging.getLogger(__name__)

VERSION = "3.0"
GENERATOR = "autopilot_v3"
DEFAULT_DOCS_QA = _PROJECT_ROOT / "docs" / "qa"
DEFAULT_OUTPUT = DEFAULT_DOCS_QA / "QA_AUTOPILOT_V3.json"
DEFAULT_TRACE = DEFAULT_DOCS_QA / "feedback_loop" / "autopilot_v3_trace.json"


def main() -> int:
    parser = argparse.ArgumentParser(description="QA Autopilot v3 – Systematische Testlücken-Erkennung")
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
        "--input-autopilot",
        type=Path,
        default=DEFAULT_DOCS_QA / "QA_AUTOPILOT_V2.json",
        help="QA_AUTOPILOT_V2.json",
    )
    parser.add_argument(
        "--input-control-center",
        type=Path,
        default=DEFAULT_DOCS_QA / "QA_CONTROL_CENTER.json",
        help="QA_CONTROL_CENTER.json (optional)",
    )
    parser.add_argument(
        "--input-priority-score",
        type=Path,
        default=DEFAULT_DOCS_QA / "QA_PRIORITY_SCORE.json",
        help="QA_PRIORITY_SCORE.json",
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
        inputs = load_autopilot_v3_inputs(
            incident_index_path=args.input_incidents,
            analytics_path=args.input_analytics,
            autopilot_path=args.input_autopilot,
            control_center_path=args.input_control_center,
            priority_score_path=args.input_priority_score,
        )

        if not inputs.autopilot_v2:
            LOG.error("QA_AUTOPILOT_V2.json fehlt – Abbruch")
            return 1

        output = run_autopilot_v3_projections(inputs, optional_timestamp=args.timestamp)
        out_dict = output_to_dict(output)
        trace_dict = build_autopilot_v3_trace(output)

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
                LOG.info("QA Autopilot v3 geschrieben: %s", args.output)
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

        print(f"Autopilot v3: {output.summary.get('total_test_gaps', 0)} Test-Gaps, "
              f"{output.summary.get('total_guard_gaps', 0)} Guard-Gaps, "
              f"{output.summary.get('recommended_backlog_count', 0)} Backlog-Einträge")
        return 0

    except Exception as e:
        LOG.exception("Generator fehlgeschlagen: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())

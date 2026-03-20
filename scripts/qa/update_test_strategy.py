#!/usr/bin/env python3
"""
QA Test Strategy Engine – Linux Desktop Chat.

Übersetzt Autopilot-v3-Erkenntnisse in eine strukturierte QA-Teststrategie.
Definiert, priorisiert und empfiehlt – schreibt NICHT: Tests, Incidents, Regression Catalog, Replay.

Output: docs/qa/QA_TEST_STRATEGY.json
Trace: docs/qa/feedback_loop/test_strategy_trace.json

Verwendung:
  python scripts/qa/update_test_strategy.py
  python scripts/qa/update_test_strategy.py --dry-run --output -
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.qa.test_strategy import (
    load_test_strategy_inputs,
    run_test_strategy_projections,
    build_test_strategy_trace,
)
from scripts.qa.test_strategy.traces import output_to_dict

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
LOG = logging.getLogger(__name__)

GENERATOR = "test_strategy_engine"
DEFAULT_DOCS_QA = _PROJECT_ROOT / "docs" / "qa"
DEFAULT_OUTPUT = DEFAULT_DOCS_QA / "QA_TEST_STRATEGY.json"
DEFAULT_TRACE = DEFAULT_DOCS_QA / "feedback_loop" / "test_strategy_trace.json"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="QA Test Strategy Engine – Übersetzt Autopilot-v3 in strukturierte Teststrategie"
    )
    parser.add_argument(
        "--input-autopilot-v3",
        type=Path,
        default=DEFAULT_DOCS_QA / "QA_AUTOPILOT_V3.json",
        help="QA_AUTOPILOT_V3.json (Pflicht)",
    )
    parser.add_argument(
        "--input-control-center",
        type=Path,
        default=DEFAULT_DOCS_QA / "QA_CONTROL_CENTER.json",
        help="QA_CONTROL_CENTER.json (optional, für Pilot-Tracking)",
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
        inputs = load_test_strategy_inputs(
            autopilot_v3_path=args.input_autopilot_v3,
            control_center_path=args.input_control_center,
        )

        if not inputs.autopilot_v3:
            LOG.error("QA_AUTOPILOT_V3.json fehlt oder ungültig – Abbruch")
            return 1

        output = run_test_strategy_projections(inputs, optional_timestamp=args.timestamp)
        out_dict = output_to_dict(output)
        trace_dict = build_test_strategy_trace(output)

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
                LOG.info("QA Test Strategy geschrieben: %s", args.output)
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

        print(
            f"Test Strategy: {len(output.test_domains)} Domains, "
            f"{len(output.guard_requirements)} Guard-Requirements, "
            f"{len(output.regression_requirements)} Regression-Requirements"
        )
        return 0

    except ValueError as e:
        LOG.error("Validierungsfehler: %s", e)
        return 1
    except Exception as e:
        LOG.exception("Engine fehlgeschlagen: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())

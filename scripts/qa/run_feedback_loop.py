#!/usr/bin/env python3
"""
QA Feedback Loop – Runner.

Führt den Feedback Loop aus und gibt den Report aus.
Verwendung:
  python scripts/qa/run_feedback_loop.py
  python scripts/qa/run_feedback_loop.py --output docs/qa/FEEDBACK_LOOP_REPORT.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Projekt-Root
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

# Feedback Loop importieren
from scripts.qa.feedback_loop import (
    load_feedback_inputs,
    run_feedback_projections,
    trace_report,
    report_to_dict,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main() -> int:
    parser = argparse.ArgumentParser(description="QA Feedback Loop Runner")
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=_PROJECT_ROOT / "docs" / "qa",
        help="docs/qa Verzeichnis",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output-JSON (optional)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Ausführliche Ausgabe",
    )
    args = parser.parse_args()

    docs_qa = args.input_dir
    if (docs_qa / "QA_AUTOPILOT_V2.json").exists():
        base = docs_qa
    else:
        base = _PROJECT_ROOT

    inputs = load_feedback_inputs(base_path=base)
    if not inputs.incident_index and not inputs.analytics and not inputs.autopilot_v2:
        logging.error("Keine Input-Daten gefunden. Prüfe Pfade.")
        return 1

    report = run_feedback_projections(inputs)
    trace_report(report, level=logging.DEBUG if args.verbose else logging.INFO)

    out_dict = report_to_dict(report)
    print(f"Feedback Loop: {report.generated_at}")
    print(f"  Subsysteme: {len(report.per_subsystem_results)}")
    print(f"  Failure-Classes: {len(report.per_failure_class_results)}")
    print(f"  Regel-Ergebnisse: {len(report.rule_results)}")
    print(f"  Eskalationen: {len(report.escalations)}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(out_dict, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"  → {args.output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""
Kontext-Review – Auswertung der manuellen Bewertungen.

Lädt context_review_sheet.csv, gruppiert nach case_id,
berechnet einfache Mittelwerte je Dimension, schreibt context_review_summary.json.

Keine intelligente Schlussfolgerung – nur Aggregation.

Verwendung:
  python scripts/qa/evaluate_context_reviews.py
"""

import csv
import json
import sys
from pathlib import Path
from typing import Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
REVIEW_DIR = PROJECT_ROOT / "docs" / "qa" / "context_mode_experiments"
REVIEW_SHEET = REVIEW_DIR / "context_review_sheet.csv"
SUMMARY_FILE = REVIEW_DIR / "context_review_summary.json"

DIMENSIONS = ("brauchbarkeit", "kontextnutzen", "fokustreue", "ablenkung", "kontextkosten")


def _parse_rating(val: str) -> Optional[float]:
    """Wandelt String in float (1–5) oder None bei leer/ungültig."""
    if not val or not val.strip():
        return None
    try:
        f = float(val.strip())
        if 1 <= f <= 5:
            return f
    except ValueError:
        pass
    return None


def main() -> int:
    if not REVIEW_SHEET.exists():
        print(f"Fehler: {REVIEW_SHEET} nicht gefunden.", file=sys.stderr)
        return 1

    rows: list[dict] = []
    with open(REVIEW_SHEET, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("case_id") or not row.get("prompt_id"):
                continue
            rows.append(row)

    if not rows:
        print("Keine bewerteten Zeilen gefunden. Nur Header oder leere Zeilen?", file=sys.stderr)
        summary = {"by_case": {}, "meta": {"source": str(REVIEW_SHEET), "row_count": 0}}
        with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        return 0

    by_case: dict[str, dict] = {}
    for row in rows:
        case_id = row.get("case_id", "").strip()
        if not case_id:
            continue
        if case_id not in by_case:
            by_case[case_id] = {d: [] for d in DIMENSIONS}
        for dim in DIMENSIONS:
            r = _parse_rating(row.get(dim, ""))
            if r is not None:
                by_case[case_id][dim].append(r)

    # Mittelwerte berechnen
    summary_by_case: dict[str, dict] = {}
    for case_id, vals in sorted(by_case.items()):
        avgs = {}
        for dim in DIMENSIONS:
            lst = vals[dim]
            avgs[dim] = round(sum(lst) / len(lst), 2) if lst else None
        summary_by_case[case_id] = avgs

    summary = {
        "by_case": summary_by_case,
        "meta": {
            "source": str(REVIEW_SHEET),
            "row_count": len(rows),
            "dimensions": list(DIMENSIONS),
        },
    }

    REVIEW_DIR.mkdir(parents=True, exist_ok=True)
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    # Konsolenausgabe pro Case
    print("--- Kontext-Review Auswertung ---")
    for case_id, avgs in sorted(summary_by_case.items()):
        parts = [f"{d}={avgs[d]}" if avgs[d] is not None else f"{d}=—" for d in DIMENSIONS]
        print(f"  {case_id}: {' | '.join(parts)}")
    print(f"\nSummary: {SUMMARY_FILE}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

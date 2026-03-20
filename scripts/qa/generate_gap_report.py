#!/usr/bin/env python3
"""
Phase 3 – Gap-Report-Generator.

Liest QA_COVERAGE_MAP.json, erzeugt priorisierten Gap-Report in Markdown und/oder JSON.
Nicht blockierend; für CI-Artefakte.

Verwendung:
  python scripts/qa/generate_gap_report.py
  python scripts/qa/generate_gap_report.py --format markdown --output -
  python scripts/qa/generate_gap_report.py --format json
  python scripts/qa/generate_gap_report.py --format both
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_PROJECT_ROOT))

from scripts.qa.qa_paths import ARTIFACTS_JSON, ARTIFACTS_DASHBOARDS

DEFAULT_COVERAGE_MAP = ARTIFACTS_JSON / "QA_COVERAGE_MAP.json"


def load_coverage_map(path: Path) -> dict:
    """Lädt Coverage Map."""
    if not path.exists():
        raise FileNotFoundError(f"QA_COVERAGE_MAP nicht gefunden: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def render_markdown(coverage_map: dict, top_n: int = 20) -> str:
    """Erzeugt Markdown-Gap-Report."""
    lines: list[str] = []
    lines.append("# QA Gap Report (Phase 3)")
    lines.append("")
    lines.append(f"*Generiert aus {coverage_map.get('generated_at', '?')}*")
    lines.append("")

    prioritized = coverage_map.get("prioritized_gaps") or []
    governance = coverage_map.get("governance") or {}
    gap_types = (coverage_map.get("summary") or {}).get("gap_types") or {}

    # Blockierende Gaps (keine – alle nicht blockierend laut Phase 3)
    lines.append("## Blockierende Gaps")
    lines.append("")
    lines.append("- Keine (Phase 3: Gaps sind nicht blockierend)")
    lines.append("")

    # Warnungen
    lines.append("## Warnungen (nicht blockierend)")
    lines.append("")
    lines.append("| Gap-Typ | Anzahl | Schwere |")
    lines.append("|---------|--------|---------|")
    for gt, count in sorted(gap_types.items(), key=lambda x: -x[1]):
        if count > 0:
            sev = "medium" if "failure_class" in gt or "regression" in gt else "low"
            lines.append(f"| {gt} | {count} | {sev} |")
    orphan_count = governance.get("orphan_count", 0)
    if orphan_count > 0:
        lines.append(f"| orphan_review_backlog | {orphan_count} | low |")
    lines.append("")

    # Priorisierte Gaps (Top N)
    lines.append(f"## Priorisierte Gaps (Top {top_n})")
    lines.append("")
    lines.append("| # | Gap | Severity | Score | Faktoren |")
    lines.append("|---|-----|----------|-------|----------|")
    for i, g in enumerate(prioritized[:top_n], 1):
        gap_id = g.get("gap_id", "?")
        value = g.get("value", g.get("title", ""))
        display = f"{gap_id}" + (f" ({value})" if value and str(value) != gap_id else "")
        sev = g.get("severity", "?")
        score = g.get("priority_score", 0)
        factors = ", ".join(g.get("escalation_factors") or []) or "-"
        lines.append(f"| {i} | {display} | {sev} | {score} | {factors} |")
    lines.append("")

    # Details
    lines.append("## Details")
    lines.append("")
    for g in prioritized[:10]:
        gap_id = g.get("gap_id", "?")
        hint = g.get("mitigation_hint", "")
        if hint:
            lines.append(f"- **{gap_id}:** {hint}")
    lines.append("")

    return "\n".join(lines)


def render_json(coverage_map: dict) -> dict:
    """Erzeugt JSON-Gap-Report (reduziert)."""
    prioritized = coverage_map.get("prioritized_gaps") or []
    governance = coverage_map.get("governance") or {}
    return {
        "schema_version": "1.0",
        "generated_at": coverage_map.get("generated_at"),
        "source": "QA_COVERAGE_MAP.json",
        "prioritized_gaps": prioritized,
        "orphan_count": governance.get("orphan_count", 0),
        "orphan_breakdown": governance.get("orphan_breakdown", {}),
        "gap_type_counts": (coverage_map.get("summary") or {}).get("gap_types") or {},
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Phase 3 – Gap-Report aus QA_COVERAGE_MAP erzeugen"
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "json", "both"],
        default="markdown",
        help="Output-Format",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=None,
        help="Output-Pfad (default: docs/qa/PHASE3_GAP_REPORT.{md|json})",
    )
    parser.add_argument(
        "--coverage-map",
        type=Path,
        default=DEFAULT_COVERAGE_MAP,
        help="Pfad zu QA_COVERAGE_MAP.json",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Anzahl priorisierter Gaps im Markdown-Report",
    )
    args = parser.parse_args()

    try:
        coverage_map = load_coverage_map(args.coverage_map)
    except FileNotFoundError as e:
        print(f"Fehler: {e}", file=sys.stderr)
        return 1

    if args.format in ("markdown", "both"):
        md = render_markdown(coverage_map, top_n=args.top)
        out_md = args.output if (args.output and args.format == "markdown") else (ARTIFACTS_DASHBOARDS / "PHASE3_GAP_REPORT.md")
        if str(out_md) == "-":
            print(md)
        else:
            Path(out_md).parent.mkdir(parents=True, exist_ok=True)
            Path(out_md).write_text(md, encoding="utf-8")
            print(f"Gap-Report (Markdown): {out_md}", file=sys.stderr)

    if args.format in ("json", "both"):
        data = render_json(coverage_map)
        out_json = args.output if (args.output and args.format == "json") else (ARTIFACTS_JSON / "PHASE3_GAP_REPORT.json")
        if str(out_json) == "-":
            json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
        else:
            Path(out_json).parent.mkdir(parents=True, exist_ok=True)
            Path(out_json).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"Gap-Report (JSON): {out_json}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())

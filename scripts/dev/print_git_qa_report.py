#!/usr/bin/env python3
"""
QA-Bericht mit Git-Kontext, Provenance und Segment-Analyse geänderter Pfade.

Vom Repository-Root (venv aktiv):

    python3 scripts/dev/print_git_qa_report.py
    python3 scripts/dev/print_git_qa_report.py --json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _main() -> int:
    parser = argparse.ArgumentParser(description="Linux Desktop Chat — QA Report (Git + Segmente)")
    parser.add_argument(
        "--cwd",
        type=Path,
        default=None,
        help="Git-Arbeitsverzeichnis (Standard: aktuelles Verzeichnis)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="JSON auf stdout statt Textbericht",
    )
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    repo_root = here.parent.parent
    sys.path.insert(0, str(repo_root))

    from app.qa.git_context import capture_git_context
    from app.qa.git_provenance import build_qa_run_provenance
    from app.qa.git_qa_report import build_qa_report_json_dict, build_qa_report_text

    cwd = args.cwd.resolve() if args.cwd else Path.cwd().resolve()
    ctx = capture_git_context(cwd)
    prov = build_qa_run_provenance(ctx)

    if args.json:
        payload = build_qa_report_json_dict(ctx, prov=prov)
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(build_qa_report_text(ctx, prov=prov), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())

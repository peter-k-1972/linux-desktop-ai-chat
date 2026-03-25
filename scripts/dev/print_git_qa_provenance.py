#!/usr/bin/env python3
"""
Gibt Git-QA-Provenance und Soft-Gate-Status als JSON auf stdout aus.

Nutzung vom Repository-Root (mit aktivierter venv):

    python3 scripts/dev/print_git_qa_provenance.py

Optional für CI: Ausgabe in Artefakte anhängen — kein Workflow-Zwang.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path


def _main() -> int:
    parser = argparse.ArgumentParser(description="Git-QA-Provenance (JSON)")
    parser.add_argument(
        "--cwd",
        type=Path,
        default=None,
        help="Git-Arbeitsverzeichnis (Standard: aktuelles Verzeichnis)",
    )
    args = parser.parse_args()

    # Repo-Root: scripts/dev -> ../..
    here = Path(__file__).resolve().parent
    repo_root = here.parent.parent
    sys.path.insert(0, str(repo_root))

    from app.qa.git_context import capture_git_context
    from app.qa.git_governance import describe_allowed_claims_text, evaluate_soft_gates
    from app.qa.git_provenance import build_qa_run_provenance

    cwd = args.cwd.resolve() if args.cwd else Path.cwd().resolve()
    ctx = capture_git_context(cwd)
    prov = build_qa_run_provenance(ctx)
    gate = evaluate_soft_gates(ctx)

    payload = {
        "cwd": str(cwd),
        "provenance": asdict(prov),
        "soft_gate": {
            "max_formal_tier": gate.max_formal_tier.value,
            "strong_claims_allowed": gate.strong_claims_allowed,
            "warnings": list(gate.warnings),
            "rationale": list(gate.rationale),
            "summary_de": describe_allowed_claims_text(gate),
        },
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(_main())

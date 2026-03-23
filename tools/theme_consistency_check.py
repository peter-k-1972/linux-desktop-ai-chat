#!/usr/bin/env python3
"""
Optional: heuristische Prüfung auf neue Hardcoded-Farben in GUI-Python.

Exit 0 = keine Treffer in den gescannten Pfaden (oder nur Allowlist).
Nicht als harter CI-Gate gedacht — ergänzt docs/design/THEME_MIGRATION_PLAN.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN_DIRS = [
    ROOT / "app" / "gui" / "domains",
    ROOT / "app" / "gui" / "inspector",
]
# Erlaubt: reine Token-/Theme-Module und generierte Reports
SKIP_SUBSTR = (
    "app/gui/themes/canonical_token_ids.py",
    "app/gui/themes/resolved_spec_tokens.py",
    "app/gui/themes/builtin_semantic_profiles.py",
    "app/gui/themes/palette_resolve.py",
    "app/gui/themes/tokens.py",
    "app/agents/departments.py",
)
HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
QCOLOR_HEX_RE = re.compile(r'QColor\s*\(\s*["\']#')


def main() -> int:
    p = argparse.ArgumentParser(description="Theme consistency heuristic scan")
    p.add_argument("--strict", action="store_true", help="exit 1 on any hit")
    args = p.parse_args()
    hits: list[tuple[str, int, str]] = []
    for base in SCAN_DIRS:
        if not base.exists():
            continue
        for path in base.rglob("*.py"):
            rel = str(path.relative_to(ROOT))
            if any(s in rel for s in SKIP_SUBSTR):
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            for i, line in enumerate(text.splitlines(), 1):
                if HEX_RE.search(line) or QColor_HEX_RE.search(line):
                    hits.append((rel, i, line.strip()[:120]))
    for rel, ln, snippet in hits[:200]:
        print(f"{rel}:{ln}: {snippet}")
    if len(hits) > 200:
        print(f"... and {len(hits) - 200} more")
    print(f"Total heuristic hits: {len(hits)}")
    if args.strict and hits:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

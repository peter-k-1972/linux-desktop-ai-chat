#!/usr/bin/env python3
"""
Führt Icon-Usage-, SVG- und Registry-Guards aus und schreibt ICON_GUARD_REPORT.md.

Delegiert an ``icon_guard_report.py`` (eine aggregierte Implementierung).

Exit 1 bei Violations (CI / pre-push).
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Alle Icon-Guards + ICON_GUARD_REPORT.md")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--include-tests", action="store_true")
    ap.add_argument("--fail-on-orphans", action="store_true")
    args = ap.parse_args(argv)
    base = args.root.resolve()

    p = base / "tools" / "icon_guard_report.py"
    spec = importlib.util.spec_from_file_location("icon_guard_report", p)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    extra: list[str] = ["--root", str(base)]
    if args.include_tests:
        extra.append("--include-tests")
    if args.fail_on_orphans:
        extra.append("--fail-on-orphans")
    return mod.main(extra)


if __name__ == "__main__":
    raise SystemExit(main())

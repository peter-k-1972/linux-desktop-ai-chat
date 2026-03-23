#!/usr/bin/env python3
"""
Schreibt ICON_GUARD_REPORT.md und gibt Exit 1 zurück, wenn Violations vorliegen.
"""

from __future__ import annotations

import argparse
import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT_PATH = ROOT / "ICON_GUARD_REPORT.md"


def _load_tool(name: str, filename: str):
    p = ROOT / "tools" / filename
    spec = importlib.util.spec_from_file_location(name, p)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run_all(base: Path, *, include_tests: bool, fail_on_orphans: bool) -> dict:
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))

    icon_usage_guard = _load_tool("icon_usage_guard", "icon_usage_guard.py")
    icon_svg_guard = _load_tool("icon_svg_guard", "icon_svg_guard.py")
    icon_registry_guard = _load_tool("icon_registry_guard", "icon_registry_guard.py")

    usage_v = icon_usage_guard.collect_violations(base, include_tests=include_tests)
    icons_root = base / "resources" / "icons"
    svg_invalid: list[str] = []
    if icons_root.is_dir():
        svg_invalid = icon_svg_guard.validate_tree(icons_root)
    reg_viol, reg_warn, orphans = icon_registry_guard.collect_registry_issues(base)
    if fail_on_orphans and orphans:
        reg_viol = list(reg_viol) + [f"Orphan-SVGs (--fail-on-orphans): {len(orphans)}"]

    return {
        "usage_violations": usage_v,
        "svg_invalid": svg_invalid,
        "registry_violations": reg_viol,
        "registry_warnings": reg_warn,
        "orphan_svgs": orphans,
    }


def _write_report(base: Path, data: dict) -> None:
    lines = [
        "# ICON_GUARD_REPORT",
        "",
        f"Generiert: {datetime.now(timezone.utc).isoformat()}Z",
        f"Root: `{base}`",
        "",
        "## Violations",
        "",
    ]
    uv = data["usage_violations"]
    sv = data["svg_invalid"]
    rv = data["registry_violations"]
    if not uv and not sv and not rv:
        lines.append("*(keine)*")
        lines.append("")
    else:
        if uv:
            lines.append("### icon_usage_guard")
            lines.extend(f"- {x}" for x in uv)
            lines.append("")
        if sv:
            lines.append("### icon_svg_guard")
            lines.extend(f"- {x}" for x in sv)
            lines.append("")
        if rv:
            lines.append("### icon_registry_guard")
            lines.extend(f"- {x}" for x in rv)
            lines.append("")

    lines.extend(["## Warnings", ""])
    rw = data["registry_warnings"]
    if not rw:
        lines.append("*(keine)*")
        lines.append("")
    else:
        lines.extend(f"- {x}" for x in rw)
    lines.append("")

    lines.extend(["## Orphan icons (nicht in REGISTRY_TO_RESOURCE)", ""])
    op = data["orphan_svgs"]
    if not op:
        lines.append("*(keine)*")
        lines.append("")
    else:
        lines.extend(f"- `{x}`" for x in op)
    lines.append("")

    lines.extend(
        [
            "## Unused registry IDs",
            "",
            "*Nicht automatisch geprüft (Homonyme wie «run», «system»); siehe* `ICON_CANONICAL_SET.md`.",
            "",
            "## Invalid SVGs (Kurzreferenz)",
            "",
        ]
    )
    if not sv:
        lines.append("*(keine)*")
    else:
        lines.append(f"*{len(sv)} Einträge — Details unter Violations.*")
    lines.append("")

    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="ICON_GUARD_REPORT.md erzeugen")
    ap.add_argument("--root", type=Path, default=ROOT)
    ap.add_argument("--include-tests", action="store_true")
    ap.add_argument("--fail-on-orphans", action="store_true")
    args = ap.parse_args(argv)
    base = args.root.resolve()

    data = _run_all(base, include_tests=args.include_tests, fail_on_orphans=args.fail_on_orphans)
    bad = bool(data["usage_violations"] or data["svg_invalid"] or data["registry_violations"])
    if bad:
        for x in data["usage_violations"]:
            print(x, file=sys.stderr)
        for x in data["svg_invalid"]:
            print(x, file=sys.stderr)
        for x in data["registry_violations"]:
            print(x, file=sys.stderr)
    for w in data["registry_warnings"]:
        print(w, file=sys.stderr)

    _write_report(base, data)

    if bad:
        print(f"Report: {REPORT_PATH} (Violations, Exit 1)", file=sys.stderr)
        return 1
    print(f"Report: {REPORT_PATH} (ok)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

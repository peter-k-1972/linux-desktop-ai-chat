#!/usr/bin/env python3
"""
Icon Usage Guard — verhindert direktes Laden von UI-Icons außerhalb Registry/Manager.

Scannt Python-Code unter ``app/`` (und optional ``main.py`` im Projektroot).

Erkennt u. a.:
  - QIcon(… mit Literalpfad / QRC
  - QPixmap(… mit Literalpfad
  - load_icon(
  - String-Literale mit ``assets/icons/``, ``resources/icons/``, ``icons/`` (UI-Pfad)

Erlaubt in allowlisteten Dateien oder wenn dieselbe Zeile IconManager/get_icon/get_resource… nutzt.

Exit: 0 = ok, 1 = Violations, 2 = Konfigurationsfehler
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Volle Pfade relativ zum Projektroot — komplette Datei von Pfad-String-Checks ausnehmen
ALLOWLIST_FULL_PATHS: frozenset[str] = frozenset(
    {
        "app/gui/icons/manager.py",
        "app/gui/icons/icon_registry.py",
        "app/gui/icons/registry.py",
        "app/utils/paths.py",
        "tools/generate_canonical_icon_set.py",
        "tools/icon_usage_guard.py",
        "tools/icon_registry_guard.py",
        "tools/icon_svg_guard.py",
        "tools/icon_guard_report.py",
        "tools/run_icon_guards.py",
    }
)

# QIcon/QPixmap-Sonderfälle (kein Registry-UI-Icon)
ALLOWLIST_QICON_PIXMAP: frozenset[str] = frozenset(
    {
        "app/gui/icons/manager.py",
        "app/gui/workbench/canvas/canvas_tabs.py",
        "app/gui/legacy/message_widget.py",
        "app/gui/domains/operations/chat/panels/chat_message_widget.py",
    }
)

STRING_QICON = re.compile(r"QIcon\s*\(\s*(['\"])([^'\"]+)\1")
JOIN_QICON = re.compile(r"QIcon\s*\(\s*os\.path\.join", re.I)
STRING_QPIXMAP = re.compile(r"QPixmap\s*\(\s*(['\"])([^'\"]+)\1")
JOIN_QPIXMAP = re.compile(r"QPixmap\s*\(\s*os\.path\.join", re.I)
LOAD_ICON = re.compile(r"\bload_icon\s*\(")

# String-Literale mit Icon-Asset-Pfaden
RE_ASSETS_ICONS = re.compile(r"""['\"]([^'\"]*assets/icons[^'\"]*)['\"]""")
RE_RESOURCES_ICONS = re.compile(r"""['\"]([^'\"]*resources/icons[^'\"]*)['\"]""")
# z. B. "icons/foo.svg" oder '/icons/' — nur wenn .svg/.png im Literal oder "icons/" als Pfadsegment
RE_ICONS_SLASH = re.compile(r"""['\"]([^'\"]*[/\\]icons[/\\][^'\"]*)['\"]""")

ALLOWED_TOKENS_RE = re.compile(
    r"\b(IconManager|get_icon|get_icon_for_|icon_registry|get_resource_svg_path|"
    r"get_resource_icons_root|get_icons_dir|REGISTRY_TO_RESOURCE)\b"
)


def _rel_posix(path: Path, base: Path) -> str:
    return path.relative_to(base).as_posix()


def collect_violations(base: Path, *, include_tests: bool = False) -> list[str]:
    violations: list[str] = []
    app_dir = base / "app"
    if not app_dir.is_dir():
        return [f"Kein Verzeichnis: {app_dir}"]

    py_files: list[Path] = []
    for p in sorted(app_dir.rglob("*.py")):
        if "__pycache__" in p.parts:
            continue
        py_files.append(p)

    root_main = base / "main.py"
    if root_main.is_file():
        py_files.append(root_main)

    if include_tests:
        tdir = base / "tests"
        if tdir.is_dir():
            for p in sorted(tdir.rglob("*.py")):
                if "__pycache__" in p.parts:
                    continue
                py_files.append(p)

    for path in py_files:
        try:
            rel = _rel_posix(path, base)
        except ValueError:
            continue

        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            violations.append(f"{rel}: nicht lesbar")
            continue

        allow_full = rel in ALLOWLIST_FULL_PATHS
        allow_qp = rel in ALLOWLIST_QICON_PIXMAP or allow_full

        for i, line in enumerate(text.splitlines(), 1):
            if allow_full:
                continue

            # load_icon( — aktuell nicht im Projekt; künftig nur über Allowlist/Wrapper
            if LOAD_ICON.search(line) and "test_" not in rel and "tools/icon" not in rel.replace("\\", "/"):
                violations.append(f"{rel}:{i}: load_icon( — nutze IconManager / get_icon*")

            # Asset-Pfad-Strings
            if RE_ASSETS_ICONS.search(line) or RE_RESOURCES_ICONS.search(line):
                if not ALLOWED_TOKENS_RE.search(line):
                    violations.append(
                        f"{rel}:{i}: String mit assets/icons oder resources/icons — nur über paths.py / IconManager-Schicht"
                    )
            m_ic = RE_ICONS_SLASH.search(line)
            if m_ic:
                lit = m_ic.group(1).lower()
                if lit.endswith((".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp")) or "/icons/" in lit.replace(
                    "\\", "/"
                ):
                    if not ALLOWED_TOKENS_RE.search(line):
                        violations.append(f"{rel}:{i}: verdächtiger icons/-Pfad im Literal — Registry/Manager nutzen")

            if allow_qp:
                continue

            if "QIcon(" in line:
                if JOIN_QICON.search(line):
                    violations.append(f"{rel}:{i}: QIcon(os.path.join…) — IconManager/registry")
                for m in STRING_QICON.finditer(line):
                    inner = m.group(2)
                    if inner.startswith(":/"):
                        violations.append(f"{rel}:{i}: QRC in QIcon(«{inner}»)")
                    low = inner.lower()
                    if low.endswith((".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif")):
                        violations.append(f"{rel}:{i}: Dateiliteral in QIcon(«{inner}»)")

            if "QPixmap(" in line:
                if JOIN_QPIXMAP.search(line):
                    violations.append(f"{rel}:{i}: QPixmap(os.path.join…) — für UI-Icons IconManager")
                for m in STRING_QPIXMAP.finditer(line):
                    inner = m.group(2)
                    low = inner.lower()
                    if low.endswith((".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif")) or "icons" in low:
                        violations.append(f"{rel}:{i}: Dateiliteral in QPixmap(«{inner}»)")

    return violations


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Icon Usage Guard (Registry/Manager erzwingen)")
    ap.add_argument("--root", type=Path, default=ROOT, help="Projektroot")
    ap.add_argument(
        "--include-tests",
        action="store_true",
        help="Auch tests/ scannen (Standard: nein, reduziert Rauschen)",
    )
    args = ap.parse_args(argv)
    base = args.root.resolve()
    viol = collect_violations(base, include_tests=args.include_tests)
    if viol:
        for v in viol:
            print(v, file=sys.stderr)
        return 1
    scope = "app/ + main.py" + (" + tests/" if args.include_tests else "")
    print(f"OK: icon_usage_guard ({scope})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

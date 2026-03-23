#!/usr/bin/env python3
"""
Heuristische Hinweise zu QSS/Python-Doppelquellen (Control-Höhen, typische Konfliktzahlen).

Nur Analyse — keine automatischen Fixes. Siehe docs/design/QSS_PYTHON_OWNERSHIP_RULES.md.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IGNORE_DIR_PARTS = frozenset({".venv", ".venv-ci", "__pycache__", "node_modules", ".git"})

# Python: Combo-Höhe parallel zu base.qss — meist QSS-Owner
_LINE_COMBO_HEIGHT = re.compile(
    r"[Cc]ombo\w*\.set(?:Minimum|Maximum|Fixed)Height\s*\(",
)

# Bekannte Risiko-Zahlen (P2 Button, ad-hoc padding rows)
_FIXED_TALL_RE = re.compile(
    r"\.setFixedHeight\s*\(\s*4[4-9]\s*\)|\.setFixedHeight\s*\(\s*48\s*\)|"
    r"\.setMinimumHeight\s*\(\s*4[4-9]\s*\)|\.setMinimumHeight\s*\(\s*48\s*\)",
)

# Inline-Stylesheets mit Layout-Metriken
_PY_STYLE_LAYOUT_RE = re.compile(
    r"setStyleSheet\s*\(\s*[\"'][^\"']*"
    r"(min-height|max-height|min-width|max-width|padding)\s*:\s*\d",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Hint:
    path: str
    line_no: int
    line: str
    rule: str


def _skip_path(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & IGNORE_DIR_PARTS)


def scan_python_gui(root: Path) -> list[Hint]:
    hints: list[Hint] = []
    gui = root / "app" / "gui"
    if not gui.is_dir():
        return hints

    for path in sorted(gui.rglob("*.py")):
        if _skip_path(path):
            continue
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines, start=1):
            if _LINE_COMBO_HEIGHT.search(line):
                hints.append(
                    Hint(rel, i, line.strip(), "combo_height_python: QSS base.qss setzt QComboBox min-height — prüfen ob redundant")
                )
            if _FIXED_TALL_RE.search(line):
                hints.append(
                    Hint(rel, i, line.strip(), "tall_fixed_control: 44–48px — P2 Konflikt mit Standard-32 QSS?")
                )
            if _PY_STYLE_LAYOUT_RE.search(line):
                hints.append(
                    Hint(rel, i, line.strip()[:120], "inline_stylesheet_layout: Layout-Pixel in Python-QSS — Owner klären")
                )
    return hints


def scan_qss_literals(root: Path) -> list[Hint]:
    """min-height/max-height in px ohne {{token}} in Theme-base (heuristisch)."""
    hints: list[Hint] = []
    base = root / "assets" / "themes" / "base"
    if not base.is_dir():
        return hints
    for path in sorted(base.rglob("*.qss")):
        rel = path.relative_to(root).as_posix()
        try:
            lines = path.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for i, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("/*") or stripped.startswith("*"):
                continue
            if "{{" in line:
                continue
            if re.search(r"\bmin-height\s*:\s*\d+px", line, re.I):
                hints.append(
                    Hint(rel, i, stripped[:120], "qss_literal_min_height: Token/Placeholder erwägen")
                )
    return hints


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 wenn mindestens ein Hint gefunden wird.",
    )
    parser.add_argument(
        "--include-qss",
        action="store_true",
        help="Zusätzlich assets/themes/base/*.qss auf literale min-height (ohne {{) prüfen — viele Treffer möglich.",
    )
    args = parser.parse_args(argv)

    py_hints = scan_python_gui(ROOT)
    qss_hints: list[Hint] = []
    if args.include_qss:
        qss_hints = scan_qss_literals(ROOT)
    all_h = py_hints + qss_hints

    for h in all_h:
        print(f"{h.path}:{h.line_no}: [{h.rule}] {h.line}")

    if not all_h:
        print("layout_double_source_guard: keine Hinweise.")
    if args.strict and all_h:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

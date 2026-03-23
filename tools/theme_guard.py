#!/usr/bin/env python3
"""
THEME GUARD — statische Analyse: keine Hardcoded-Farben außerhalb erlaubter Theme-Pfade.

Analysiert nur (ändert keine Dateien). Optional: --suggest für Hinweise.
Exit: 0 = keine Verstöße, 1 = Verstöße (CI-tauglich).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

# Repo-Root (tools/..)
ROOT = Path(__file__).resolve().parents[1]

IGNORE_DIR_NAMES = frozenset({
    ".git",
    ".venv",
    ".venv-ci",
    "venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
})

# Python: diese Präfixe dürfen Literalfarben enthalten (Theme-Autoren, Doku, Tests).
ALLOW_PYTHON_PREFIXES = (
    "docs/",
    "tests/",
    "app/gui/themes/",
    "app/themes/",  # reserviert / zukünftige Struktur
    "example_output/",
)

# Einzeldateien (Legacy-Generator, dieses Tool, zugehörige Tests).
ALLOW_PYTHON_FILES = frozenset(
    {
        "tools/theme_guard.py",
        "tests/tools/test_theme_guard.py",
        "app/resources/styles.py",
        "tools/theme_consistency_check.py",
    }
)

# QSS: nur „Legacy“-Theme-Dateien mit Rohfarben erlaubt; base/shell/workbench müssen token-only sein.
ALLOW_QSS_PREFIXES = (
    "assets/themes/legacy/",
    "app/resources/",
)

HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b")
RGB_RE = re.compile(r"\brgb\s*\(", re.IGNORECASE)
RGBA_RE = re.compile(r"\brgba\s*\(", re.IGNORECASE)
QCOLOR_RE = re.compile(r"\bQColor\s*\(")
QT_NAMED_COLOR_RE = re.compile(
    r"\bQt\.(?:GlobalColor\.)?"
    r"(black|white|red|green|blue|gray|darkGray|lightGray|cyan|magenta|yellow)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Violation:
    path: str
    line_no: int
    line: str
    rule: str


def _norm_rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _is_under_ignored_dir(parts: tuple[str, ...]) -> bool:
    return any(p in IGNORE_DIR_NAMES for p in parts)


def _allowed_python(rel: str) -> bool:
    if rel in ALLOW_PYTHON_FILES:
        return True
    return any(rel.startswith(p) for p in ALLOW_PYTHON_PREFIXES)


def _allowed_qss(rel: str) -> bool:
    return any(rel.startswith(p) for p in ALLOW_QSS_PREFIXES)


def _suggest_for_line(line: str, rule: str) -> str:
    low = line.lower()
    if "background" in low:
        return "theme_manager.color(ThemeTokenId.BG_SURFACE) bzw. ThemeTokenId.BG_APP / BG_PANEL"
    if "border" in low and "color" in low:
        return "theme_manager.color(ThemeTokenId.BORDER_DEFAULT) oder BORDER_SUBTLE"
    if "color:" in low or "color " in low:
        return "theme_manager.color(ThemeTokenId.FG_PRIMARY) bzw. FG_SECONDARY / FG_MUTED"
    if rule == "QColor(":
        return "QColor(theme_manager.color(ThemeTokenId.<passend>))"
    if rule.startswith("Qt."):
        return "theme_manager.color(ThemeTokenId.…) statt Qt-Named-Color"
    if rule == "rgb()/rgba()":
        return "Token-Hex aus ThemeManager; keine rgb()/rgba()-Literale in UI-Code"
    if rule == "hex":
        return "ThemeTokenId + get_theme_manager().color(...) oder QSS mit {{color_*}} Platzhaltern"
    return "Siehe docs/design/THEME_TOKEN_SPEC.md — passendes ThemeTokenId wählen"


def _scan_line_py(line: str, line_no: int, rel: str) -> list[Violation]:
    out: list[Violation] = []
    stripped = line.strip()
    # Volle Zeilen-Kommentare ohne ausführbaren Code überspringen (kein Hex in Strings)
    if stripped.startswith("#") and '"' not in line and "'" not in line:
        return out

    if QCOLOR_RE.search(line):
        out.append(Violation(rel, line_no, line.rstrip(), "QColor("))
        return out

    m = QT_NAMED_COLOR_RE.search(line)
    if m:
        out.append(Violation(rel, line_no, line.rstrip(), f"Qt.{m.group(1)}"))
        return out

    if RGB_RE.search(line) or RGBA_RE.search(line):
        out.append(Violation(rel, line_no, line.rstrip(), "rgb()/rgba()"))

    has_hex = bool(HEX_RE.search(line))
    if "setStyleSheet" in line and has_hex:
        out.append(Violation(rel, line_no, line.rstrip(), "setStyleSheet+hex"))
    elif has_hex:
        out.append(Violation(rel, line_no, line.rstrip(), "hex"))

    return out


def _scan_line_qss(line: str, line_no: int, rel: str) -> list[Violation]:
    out: list[Violation] = []
    if line.strip().startswith("/*") or line.strip().startswith("*"):
        return out
    if HEX_RE.search(line):
        out.append(Violation(rel, line_no, line.rstrip(), "hex (QSS)"))
    if RGB_RE.search(line) or RGBA_RE.search(line):
        out.append(Violation(rel, line_no, line.rstrip(), "rgb()/rgba() (QSS)"))
    return out


def iter_project_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for p in root.rglob("*"):
        if not p.is_file():
            continue
        parts = p.relative_to(root).parts
        if _is_under_ignored_dir(parts):
            continue
        suf = p.suffix.lower()
        if suf == ".py" or suf == ".qss":
            files.append(p)
    files.sort()
    return files


def scan(root: Path) -> list[Violation]:
    violations: list[Violation] = []
    for path in iter_project_files(root):
        rel = _norm_rel(path, root)
        suf = path.suffix.lower()

        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        if suf == ".py":
            if _allowed_python(rel):
                continue
            for i, line in enumerate(text.splitlines(), 1):
                violations.extend(_scan_line_py(line, i, rel))
        elif suf == ".qss":
            if _allowed_qss(rel):
                continue
            for i, line in enumerate(text.splitlines(), 1):
                violations.extend(_scan_line_qss(line, i, rel))

    violations.sort(key=lambda v: (v.path, v.line_no, v.rule))
    return violations


def print_report(violations: list[Violation], suggest: bool) -> None:
    print("THEME GUARD REPORT")
    print()
    if not violations:
        print("No hardcoded color violations found.")
        return
    print("Hardcoded colors found")
    print()
    for v in violations:
        print(f"{v.path}:{v.line_no}  [{v.rule}]")
        print(f"  {v.line.strip()}")
        if suggest:
            print(f"  Suggestion: {_suggest_for_line(v.line, v.rule)}")
        print()
    print(f"Total Violations: {len(violations)}")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="THEME GUARD — Farb-Lint für Linux Desktop Chat")
    p.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Projektroot (Standard: Repository-Root)",
    )
    p.add_argument(
        "--suggest",
        action="store_true",
        help="Auto-Fix-Vorschläge (nur Text, keine Dateiänderung)",
    )
    p.add_argument(
        "--max",
        type=int,
        default=0,
        help="Max. auszugebene Verstöße (0 = alle)",
    )
    args = p.parse_args(argv)

    root = args.root.resolve()
    if not root.is_dir():
        print(f"THEME GUARD: root not a directory: {root}", file=sys.stderr)
        return 2

    violations = scan(root)
    if args.max and len(violations) > args.max:
        violations = violations[: args.max]
        print(f"(truncated to {args.max} violations)", file=sys.stderr)

    print_report(violations, suggest=args.suggest)
    return 1 if violations else 0


if __name__ == "__main__":
    raise SystemExit(main())

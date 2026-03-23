"""
Strukturprüfung für Tabellen und Hilfslogik für sichere GUI-Darstellung.

Keine inhaltliche Umschreibung — nur Stabilitäts-/Fallback-Entscheidungen.
"""

from __future__ import annotations

import re

_ASCII_FRAME = re.compile(r"\+[-=+]+\+")
_PSEUDO_ROW = re.compile(r"^\s*\|.*\|\s*$")


def table_raw_lines_unstable(raw_lines: tuple[str, ...]) -> tuple[bool, tuple[str, ...]]:
    """
    True, wenn Rohzeilen ASCII-Rahmen oder andere Nicht-GFM-Mischformen enthalten.
    """
    reasons: list[str] = []
    for ln in raw_lines:
        if _ASCII_FRAME.search(ln):
            reasons.append("ascii_frame_mix")
            break
    return (bool(reasons), tuple(reasons))


def table_rows_column_stable(rows: list[list[str]]) -> tuple[bool, tuple[str, ...]]:
    """Gleiche Spaltenanzahl in jeder Zeile."""
    if not rows:
        return False, ("empty",)
    w = len(rows[0])
    for i, r in enumerate(rows):
        if len(r) != w:
            return False, ("column_mismatch",)
    return True, ()


def evaluate_table_stability(
    rows: list[list[str]],
    *,
    saw_separator: bool,
    raw_lines: tuple[str, ...],
) -> tuple[bool, tuple[str, ...]]:
    """
    Entscheidet, ob eine GFM-Tabelle proportional/tabellarisch gerendert werden darf.

    Bei Unsicherheit: stable=False → Preformatted-Fallback (kein „Schönrechnen“).
    """
    warnings: list[str] = []

    if not saw_separator:
        warnings.append("missing_separator")

    ok_cols, col_reasons = table_rows_column_stable(rows)
    if not ok_cols:
        warnings.extend(col_reasons)

    raw_unstable, raw_reasons = table_raw_lines_unstable(raw_lines)
    if raw_unstable:
        warnings.extend(raw_reasons)

    stable = not warnings
    return stable, tuple(warnings)

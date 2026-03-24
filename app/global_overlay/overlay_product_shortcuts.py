"""
Produktreservierte Shortcuts für das Global Overlay — zentrale Governance-Quelle.

Andere Module (Workbench, QML-Bridges) sollen dieselben Sequenz-Strings nicht
doppelt definieren; Konfliktprüfungen können diese Liste nutzen.

Hinweis: ``QKeySequence``-Strings sind plattformabhängig interpretiert; die
kanonischen Produktstrings bleiben dennoch hier festgehalten.
"""

from __future__ import annotations

from typing import Final

# Kanonische QKeySequence-Strings (identisch zu bisherigem Overlay-Verhalten)
OVERLAY_TOGGLE_NORMAL_SHORTCUT: Final[str] = "Alt+Z"
OVERLAY_TOGGLE_EMERGENCY_SHORTCUT: Final[str] = "Alt+Shift+Z"

# (logischer_name, sequenz) — für Doku und Registrierungsprüfungen
RESERVED_PRODUCT_OVERLAY_SHORTCUTS: Final[tuple[tuple[str, str], ...]] = (
    ("toggle_system_overlay", OVERLAY_TOGGLE_NORMAL_SHORTCUT),
    ("toggle_emergency_overlay", OVERLAY_TOGGLE_EMERGENCY_SHORTCUT),
)


def all_reserved_overlay_sequence_strings() -> tuple[str, ...]:
    """Alle reservierten Overlay-Sequenzen (ohne Duplikat-Anforderung)."""
    return tuple(seq for _name, seq in RESERVED_PRODUCT_OVERLAY_SHORTCUTS)


def shortcut_sequences_for_host() -> tuple[str, str]:
    """Paar für GlobalOverlayHost und Tests."""
    return (OVERLAY_TOGGLE_NORMAL_SHORTCUT, OVERLAY_TOGGLE_EMERGENCY_SHORTCUT)


def assert_reserved_overlay_sequences_are_unique() -> None:
    """Prüft interne Konsistenz der Registry (Tests / Debug)."""
    seqs = all_reserved_overlay_sequence_strings()
    if len(set(seqs)) != len(seqs):
        raise ValueError("Reserved overlay shortcut sequences must be unique")

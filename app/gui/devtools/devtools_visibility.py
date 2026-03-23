"""
Sichtbarkeit interner GUI-Devtools (nicht für Endnutzer gedacht).

Steuerung über Umgebungsvariable — kein Rollenmodell im Projekt; minimal-invasiv.
"""

from __future__ import annotations

import os

_ENV = "LINUX_DESKTOP_CHAT_DEVTOOLS"


def is_theme_visualizer_available() -> bool:
    """
    Theme-Visualizer und zugehörige Einträge nur anzeigen, wenn explizit freigeschaltet.

    LINUX_DESKTOP_CHAT_DEVTOOLS=1|true|yes|on → sichtbar
    LINUX_DESKTOP_CHAT_DEVTOOLS=0|false|no|off → ausgeblendet
    Unset → ausgeblendet (sicheres Standardverhalten für Produktiv-Builds).
    """
    raw = os.environ.get(_ENV)
    if raw is None or not str(raw).strip():
        return False
    return str(raw).strip().lower() in ("1", "true", "yes", "on")

"""
Gemeinsame, workspace-übergreifende Fehler-DTOs (Qt-frei).

Kanonisch für querschnittliche Anzeige-Fehler, die früher nur über
``settings_appearance`` erreichbar waren.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SettingsErrorInfo:
    """Fehlerzustand für die Anzeige (ohne Stacktrace-Zwang)."""

    code: str
    message: str
    recoverable: bool = True
    detail: str | None = None


__all__ = ["SettingsErrorInfo"]

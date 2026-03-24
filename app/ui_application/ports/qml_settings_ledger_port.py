"""
QML Settings-Ledger — Zugriff auf :class:`AppSettings` ohne ``get_infrastructure`` im ViewModel.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.core.config.settings import AppSettings


@runtime_checkable
class QmlSettingsLedgerPort(Protocol):
    def get_settings(self) -> AppSettings:
        """Aktuelle (mutable) Einstellungen der laufenden App."""
        ...

    def reload_settings(self) -> None:
        """``AppSettings.load()`` — z. B. nach externer Änderung."""
        ...

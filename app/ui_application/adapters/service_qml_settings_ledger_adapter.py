"""Adapter: :class:`QmlSettingsLedgerPort` → Infrastruktur-``AppSettings``."""

from __future__ import annotations

from app.core.config.settings import AppSettings


class ServiceQmlSettingsLedgerAdapter:
    def get_settings(self) -> AppSettings:
        from app.services.infrastructure import get_infrastructure

        return get_infrastructure().settings

    def reload_settings(self) -> None:
        self.get_settings().load()

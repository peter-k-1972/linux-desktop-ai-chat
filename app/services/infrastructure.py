"""
Infrastructure – gemeinsame Backend-Instanzen für Services.

Zentraler Zugriff auf OllamaClient, DatabaseManager, AppSettings.
Vermeidet doppelte Instanzen und ermöglicht konsistente Konfiguration.

Dependency Inversion: Settings-Backend wird von außen injiziert (init_infrastructure).
Services kennen keine GUI; GUI-Bootstrap (run_gui_shell, run_legacy_gui) übergibt
QSettingsBackend. Ohne Aufruf von init_infrastructure: InMemoryBackend (Tests, CLI).
"""

from typing import Optional

from app.providers.ollama_client import OllamaClient
from app.core.db import DatabaseManager
from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend, SettingsBackend


_settings_backend: Optional[SettingsBackend] = None


def init_infrastructure(settings_backend: Optional[SettingsBackend] = None) -> None:
    """
    Setzt das Settings-Backend für die nächste Infrastruktur-Erstellung.

    Muss vor get_infrastructure() aufgerufen werden, wenn QSettings-Persistenz gewünscht ist.
    GUI-Bootstrap (run_gui_shell, run_legacy_gui) ruft init_infrastructure(create_qsettings_backend()) auf.
    Ohne Aufruf: InMemoryBackend (Tests, CLI).
    """
    global _settings_backend
    _settings_backend = settings_backend


_infrastructure: Optional["_ServiceInfrastructure"] = None


class _ServiceInfrastructure:
    """Gemeinsame Infrastruktur für alle Services."""

    def __init__(self):
        self._client = OllamaClient()
        self._db = DatabaseManager()
        backend = _settings_backend if _settings_backend is not None else InMemoryBackend()
        self._settings = AppSettings(backend=backend)

    @property
    def ollama_client(self) -> OllamaClient:
        return self._client

    @property
    def database(self) -> DatabaseManager:
        return self._db

    @property
    def settings(self) -> AppSettings:
        return self._settings


def get_infrastructure() -> _ServiceInfrastructure:
    """Liefert die gemeinsame Infrastruktur (Singleton)."""
    global _infrastructure
    if _infrastructure is None:
        _infrastructure = _ServiceInfrastructure()
    return _infrastructure


def set_infrastructure(infra: Optional[_ServiceInfrastructure]) -> None:
    """Setzt die Infrastruktur (für Tests)."""
    global _infrastructure
    _infrastructure = infra

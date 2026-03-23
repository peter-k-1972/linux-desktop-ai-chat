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


def _close_ollama_client_best_effort(client: Optional[OllamaClient]) -> None:
    """
    Schließt die aiohttp-Session des Clients, falls eine existiert.

    Wird beim Austausch der Infrastruktur (Tests, Teardown) aufgerufen, damit keine
    „Unclosed client session“-Warnungen am Prozessende entstehen.
    """
    if client is None:
        return
    import asyncio
    import inspect

    close_result = client.close()
    if not inspect.isawaitable(close_result):
        return

    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        try:
            asyncio.run(close_result)
        except RuntimeError:
            pass
    else:
        try:
            loop.create_task(close_result)
        except RuntimeError:
            try:
                asyncio.run(close_result)
            except RuntimeError:
                pass


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
    old = _infrastructure
    if old is not None and old is not infra:
        _close_ollama_client_best_effort(getattr(old, "_client", None))
        try:
            from app.services.provider_service import reset_provider_service

            reset_provider_service()
        except ImportError:
            pass
        try:
            from app.services.workflow_service import reset_workflow_service

            reset_workflow_service()
        except ImportError:
            pass
        try:
            from app.services.schedule_service import reset_schedule_service

            reset_schedule_service()
        except ImportError:
            pass
        try:
            from app.services.deployment_operations_service import reset_deployment_operations_service

            reset_deployment_operations_service()
        except ImportError:
            pass
        try:
            from app.services.model_orchestrator_service import reset_model_orchestrator

            reset_model_orchestrator()
        except ImportError:
            pass
    _infrastructure = infra

"""Smoke: SettingsDialog-API und Ollama-Provider-Adapter importierbar."""

from __future__ import annotations

import inspect
import sys

import pytest


def test_settings_dialog_accepts_port_kwargs() -> None:
    from app.gui.domains.settings.settings_dialog import SettingsDialog

    sig = inspect.signature(SettingsDialog.__init__)
    assert "ollama_provider_port" in sig.parameters
    assert "catalog_port" in sig.parameters
    assert "settings_operations_port" in sig.parameters


def test_ollama_provider_adapter_import() -> None:
    from app.ui_application.adapters.service_ollama_provider_settings_adapter import (
        ServiceOllamaProviderSettingsAdapter,
    )

    assert ServiceOllamaProviderSettingsAdapter.__name__ == "ServiceOllamaProviderSettingsAdapter"


def test_settings_dialog_init_without_running_asyncio_loop() -> None:
    """__init__ darf nicht create_task ohne Loop ausführen (pytest ohne Qt/async-Harness)."""
    pytest.importorskip("PySide6")

    from PySide6.QtWidgets import QApplication

    from app.core.config.settings import AppSettings
    from app.gui.domains.settings.settings_dialog import SettingsDialog
    from app.ui_contracts.workspaces.settings_ai_model_catalog import AiModelCatalogPortLoadOutcome

    app = QApplication.instance() or QApplication(sys.argv)

    class _StubCatalog:
        async def load_chat_selectable_catalog_for_settings(self):
            return AiModelCatalogPortLoadOutcome(
                status="success_empty_usable",
                entries=(),
                default_selection_id="",
                placeholder_line="(test)",
            )

        def persist_default_chat_model_id(self, _mid: str) -> None:
            pass

    class _StubProvider:
        def get_ollama_api_key_from_env(self) -> str | None:
            return None

        async def validate_cloud_api_key(self, _key: str) -> bool:
            return False

    class _StubSettingsOps:
        def persist_legacy_modal_settings(self, _settings, _commit) -> None:
            pass

    dlg = SettingsDialog(
        AppSettings(),
        catalog_port=_StubCatalog(),
        ollama_provider_port=_StubProvider(),
        settings_operations_port=_StubSettingsOps(),
    )
    try:
        assert dlg.model_combo is not None
    finally:
        dlg.close()
    app.processEvents()

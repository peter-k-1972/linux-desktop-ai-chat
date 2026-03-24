"""SettingsLegacyModalPresenter — Commit-Aufbau und Katalog-Refresh."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.ui_application.presenters.settings_legacy_modal_presenter import SettingsLegacyModalPresenter
from app.ui_contracts.workspaces.settings_modal_ollama import OllamaCloudApiKeyValidationResult
from app.ui_contracts.workspaces.settings_ai_model_catalog import AiModelCatalogPortLoadOutcome


def test_persist_from_ui_delegates_to_port() -> None:
    port = MagicMock()
    catalog_port = MagicMock()
    sink = MagicMock()
    ollama_port = MagicMock()
    pre = SettingsLegacyModalPresenter(port, catalog_port, sink, ollama_port)
    backend = InMemoryBackend()
    settings = AppSettings(backend)
    pre.persist_from_ui(
        settings,
        model_id_str="m1",
        temperature=0.3,
        max_tokens=1000,
        legacy_theme_text="dark",
        think_mode="low",
        auto_routing=False,
        cloud_escalation=True,
        cloud_via_local=False,
        overkill_mode=True,
        rag_enabled=True,
        rag_space="code",
        rag_top_k=3,
        self_improving_enabled=False,
        debug_panel_enabled=True,
        prompt_storage_is_directory=True,
        prompt_directory="/p",
        prompt_confirm_delete=False,
        ollama_api_key="k",
    )
    port.persist_legacy_modal_settings.assert_called_once()
    call_kw = port.persist_legacy_modal_settings.call_args
    assert call_kw[0][0] is settings
    commit = call_kw[0][1]
    assert commit.model_id == "m1"
    assert commit.legacy_theme == "dark"
    assert commit.prompt_storage_type == "directory"
    assert commit.ollama_api_key == "k"


@pytest.mark.asyncio
async def test_refresh_model_catalog_applies_sink() -> None:
    port = MagicMock()
    outcome = AiModelCatalogPortLoadOutcome(
        status="success_empty_usable",
        entries=(),
        default_selection_id="",
        placeholder_line="(x)",
    )
    catalog_port = MagicMock()
    catalog_port.load_chat_selectable_catalog_for_settings = AsyncMock(return_value=outcome)
    sink = MagicMock()
    ollama_port = MagicMock()
    pre = SettingsLegacyModalPresenter(port, catalog_port, sink, ollama_port)
    await pre.refresh_model_catalog("stored-model")
    sink.apply_full_catalog_state.assert_called_once()
    sink.sync_to_stored_model.assert_called_once_with("stored-model")


@pytest.mark.asyncio
async def test_validate_ollama_cloud_api_key_valid() -> None:
    port = MagicMock()
    catalog_port = MagicMock()
    catalog_sink = MagicMock()
    ollama_port = MagicMock()
    ollama_port.validate_cloud_api_key = AsyncMock(return_value=True)
    val_sink = MagicMock()
    pre = SettingsLegacyModalPresenter(port, catalog_port, catalog_sink, ollama_port)
    await pre.validate_ollama_cloud_api_key("secret", validation_sink=val_sink)
    ollama_port.validate_cloud_api_key.assert_awaited_once_with("secret")
    val_sink.apply_ollama_cloud_api_key_validation.assert_called_once()
    arg = val_sink.apply_ollama_cloud_api_key_validation.call_args[0][0]
    assert isinstance(arg, OllamaCloudApiKeyValidationResult)
    assert arg.kind == "valid"


@pytest.mark.asyncio
async def test_validate_ollama_cloud_api_key_invalid() -> None:
    ollama_port = MagicMock()
    ollama_port.validate_cloud_api_key = AsyncMock(return_value=False)
    val_sink = MagicMock()
    pre = SettingsLegacyModalPresenter(MagicMock(), MagicMock(), MagicMock(), ollama_port)
    await pre.validate_ollama_cloud_api_key("x", validation_sink=val_sink)
    arg = val_sink.apply_ollama_cloud_api_key_validation.call_args[0][0]
    assert arg.kind == "invalid"


@pytest.mark.asyncio
async def test_validate_ollama_cloud_api_key_error() -> None:
    ollama_port = MagicMock()
    ollama_port.validate_cloud_api_key = AsyncMock(side_effect=RuntimeError("boom"))
    val_sink = MagicMock()
    pre = SettingsLegacyModalPresenter(MagicMock(), MagicMock(), MagicMock(), ollama_port)
    await pre.validate_ollama_cloud_api_key("x", validation_sink=val_sink)
    arg = val_sink.apply_ollama_cloud_api_key_validation.call_args[0][0]
    assert arg.kind == "error"
    assert "boom" in arg.message

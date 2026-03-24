"""
SettingsLegacyModalPresenter — Legacy-``SettingsDialog``: Commit + Katalog (dünne Schicht).

Widget liefert Primitive; Presenter baut ``SettingsLegacyModalCommit`` und ruft Port/Sink.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

from app.core.config.settings import AppSettings
from app.ui_contracts.workspaces.settings_ai_model_catalog import AiModelCatalogState
from app.ui_contracts.workspaces.settings_legacy_modal import (
    LegacyModalThemeBucket,
    SettingsLegacyModalCommit,
)
from app.ui_contracts.workspaces.settings_modal_ollama import OllamaCloudApiKeyValidationResult
from app.ui_application.presenters.settings_ai_model_catalog_presenter import SettingsAiModelCatalogPresenter

if TYPE_CHECKING:
    from app.ui_application.ports.ai_model_catalog_port import AiModelCatalogPort
    from app.ui_application.ports.ollama_provider_settings_port import OllamaProviderSettingsPort
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort


class SettingsLegacyModalCatalogSinkPort(Protocol):
    def apply_full_catalog_state(self, state: AiModelCatalogState) -> None: ...

    def sync_to_stored_model(self, model_id: str) -> None: ...


class OllamaCloudApiKeyValidationSink(Protocol):
    def apply_ollama_cloud_api_key_validation(self, result: OllamaCloudApiKeyValidationResult) -> None:
        """Spiegelt Prüfergebnis auf Statuszeile + Button (GUI)."""
        ...


class SettingsLegacyModalPresenter:
    def __init__(
        self,
        settings_operations_port: SettingsOperationsPort,
        catalog_port: AiModelCatalogPort,
        catalog_sink: SettingsLegacyModalCatalogSinkPort,
        ollama_provider_port: OllamaProviderSettingsPort,
    ) -> None:
        self._settings_operations_port = settings_operations_port
        self._catalog_port = catalog_port
        self._catalog_sink: SettingsLegacyModalCatalogSinkPort = catalog_sink
        self._ollama_provider_port = ollama_provider_port

    def persist_from_ui(
        self,
        settings: AppSettings,
        *,
        model_id_str: str,
        temperature: float,
        max_tokens: int,
        legacy_theme_text: str,
        think_mode: str,
        auto_routing: bool,
        cloud_escalation: bool,
        cloud_via_local: bool,
        overkill_mode: bool,
        rag_enabled: bool,
        rag_space: str,
        rag_top_k: int,
        self_improving_enabled: bool,
        debug_panel_enabled: bool,
        prompt_storage_is_directory: bool,
        prompt_directory: str,
        prompt_confirm_delete: bool,
        ollama_api_key: str,
    ) -> None:
        lt_raw = legacy_theme_text if legacy_theme_text in ("light", "dark") else "light"
        lt = cast(LegacyModalThemeBucket, lt_raw)
        commit = SettingsLegacyModalCommit(
            model_id=model_id_str,
            temperature=temperature,
            max_tokens=max_tokens,
            legacy_theme=lt,
            think_mode=think_mode,
            auto_routing=auto_routing,
            cloud_escalation=cloud_escalation,
            cloud_via_local=cloud_via_local,
            overkill_mode=overkill_mode,
            rag_enabled=rag_enabled,
            rag_space=rag_space,
            rag_top_k=rag_top_k,
            self_improving_enabled=self_improving_enabled,
            debug_panel_enabled=debug_panel_enabled,
            prompt_storage_type="directory" if prompt_storage_is_directory else "database",
            prompt_directory=prompt_directory,
            prompt_confirm_delete=prompt_confirm_delete,
            ollama_api_key=ollama_api_key,
        )
        self._settings_operations_port.persist_legacy_modal_settings(settings, commit)

    async def refresh_model_catalog(self, stored_model_id: str) -> None:
        outcome = await self._catalog_port.load_chat_selectable_catalog_for_settings()
        catalog_state = SettingsAiModelCatalogPresenter._outcome_to_state(outcome)
        self._catalog_sink.apply_full_catalog_state(catalog_state)
        self._catalog_sink.sync_to_stored_model(stored_model_id)

    async def validate_ollama_cloud_api_key(
        self,
        api_key: str,
        *,
        validation_sink: OllamaCloudApiKeyValidationSink,
    ) -> None:
        try:
            ok = await self._ollama_provider_port.validate_cloud_api_key(api_key)
            if ok:
                validation_sink.apply_ollama_cloud_api_key_validation(
                    OllamaCloudApiKeyValidationResult(kind="valid", message="✓ Key gültig")
                )
            else:
                validation_sink.apply_ollama_cloud_api_key_validation(
                    OllamaCloudApiKeyValidationResult(
                        kind="invalid",
                        message="✗ Key ungültig oder abgelaufen (401)",
                    )
                )
        except Exception as e:  # noqa: BLE001 — gleiche Abdeckung wie vorher im Dialog
            msg = str(e).strip()[:60]
            validation_sink.apply_ollama_cloud_api_key_validation(
                OllamaCloudApiKeyValidationResult(kind="error", message=f"✗ Fehler: {msg}")
            )

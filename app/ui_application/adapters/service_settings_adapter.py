"""
Adapter: Infrastructure / Theme-Metadaten → :class:`SettingsOperationsPort`.

Appearance-Themes: Liste und Validierung über :func:`get_theme_manager` (eine Registry mit Built-ins + installierten JSON-Themes).

Advanced (Slice 2): reine Delegation an ``get_infrastructure().settings`` — keine neue Fachlogik.

Data (Slice 3): RAG + Prompt-Speicher — nur Delegation, Normalisierung wie bisheriges Panel (Clamp/Coerce).

AI Models (Slice 4, Teilschnitt): nur skalare Felder — Unified Model Catalog: Slice 4b
(:class:`ServiceAiModelCatalogAdapter`, eigener Port).
"""

from __future__ import annotations

from typing import cast

from app.core.config.settings import AppSettings
from app.core.models.roles import ModelRole
from app.gui.themes import get_theme_manager
from app.gui.themes.theme_id_utils import theme_id_to_legacy_light_dark
from app.services.infrastructure import get_infrastructure
from app.ui_contracts.workspaces.settings_advanced import (
    AdvancedSettingsState,
    AdvancedSettingsWritePatch,
    CHAT_CONTEXT_MODES,
    ChatContextMode,
    SettingsAdvancedPortError,
)
from app.ui_contracts.workspaces.settings_data import (
    DataSettingsState,
    DataSettingsWritePatch,
    PromptStorageType,
    RAG_SPACE_IDS,
    SettingsDataPortError,
)
from app.ui_contracts.workspaces.settings_appearance import (
    AppearanceSettingsState,
    SettingsAppearancePortError,
    ThemeListEntry,
)
from app.ui_contracts.workspaces.settings_ai_models import (
    AiModelsScalarSettingsState,
    AiModelsScalarWritePatch,
    MAX_TOKENS_MAX,
    MAX_TOKENS_MIN,
    TEMPERATURE_MAX,
    TEMPERATURE_MIN,
    THINK_MODES,
    ThinkMode,
    SettingsAiModelsPortError,
)
from app.ui_contracts.workspaces.settings_legacy_modal import (
    SettingsLegacyModalCommit,
    SettingsLegacyModalPortError,
)
from app.ui_contracts.workspaces.settings_model_routing import (
    ModelRoutingStudioState,
    ModelRoutingStudioWritePatch,
    SettingsModelRoutingPortError,
)

_RAG_TOP_K_MIN = 1
_RAG_TOP_K_MAX = 20


class ServiceSettingsAdapter:
    """Konkreter Port: ThemeManager-Registry + AppSettings (wie ThemeSelectionPanel zuvor)."""

    def __init__(self) -> None:
        pass

    def validate_theme_id(self, theme_id: str) -> bool:
        return theme_id in get_theme_manager().registry

    def load_appearance_state(self) -> AppearanceSettingsState:
        mgr = get_theme_manager()
        reg = mgr.registry
        themes = tuple(
            ThemeListEntry(theme_id=tid, display_name=name)
            for tid, name in reg.list_themes()
        )
        current = mgr.get_current_id()
        if current not in reg:
            current = themes[0].theme_id if themes else "light_default"
        return AppearanceSettingsState(
            themes=themes,
            selected_theme_id=current,
            error=None,
        )

    def persist_theme_choice(self, theme_id: str) -> None:
        if theme_id not in get_theme_manager().registry:
            raise SettingsAppearancePortError(
                "unknown_theme",
                f"Unbekanntes Theme: {theme_id!r}",
                recoverable=True,
            )
        settings = get_infrastructure().settings
        settings.theme_id = theme_id
        settings.theme = theme_id_to_legacy_light_dark(theme_id)
        try:
            settings.save()
        except OSError as exc:
            raise SettingsAppearancePortError(
                "persist_failed",
                "Theme-Einstellung konnte nicht gespeichert werden.",
                recoverable=True,
            ) from exc
        except Exception as exc:
            raise SettingsAppearancePortError(
                "persist_failed",
                "Theme-Einstellung konnte nicht gespeichert werden.",
                recoverable=True,
            ) from exc

    @staticmethod
    def _coerce_chat_context_mode(raw: object) -> ChatContextMode:
        if raw in CHAT_CONTEXT_MODES:
            return cast(ChatContextMode, raw)
        return "semantic"

    def load_advanced_settings_state(self) -> AdvancedSettingsState:
        settings = get_infrastructure().settings
        mode = self._coerce_chat_context_mode(getattr(settings, "chat_context_mode", "semantic"))
        return AdvancedSettingsState(
            debug_panel_enabled=bool(getattr(settings, "debug_panel_enabled", True)),
            context_debug_enabled=bool(getattr(settings, "context_debug_enabled", False)),
            chat_context_mode=mode,
            error=None,
        )

    def persist_advanced_settings(self, write: AdvancedSettingsWritePatch) -> None:
        if (
            write.debug_panel_enabled is None
            and write.context_debug_enabled is None
            and write.chat_context_mode is None
        ):
            return
        settings = get_infrastructure().settings
        if write.debug_panel_enabled is not None:
            settings.debug_panel_enabled = write.debug_panel_enabled
        if write.context_debug_enabled is not None:
            settings.context_debug_enabled = write.context_debug_enabled
        if write.chat_context_mode is not None:
            if write.chat_context_mode not in CHAT_CONTEXT_MODES:
                raise SettingsAdvancedPortError(
                    "invalid_context_mode",
                    f"Ungültiger Chat-Kontext-Modus: {write.chat_context_mode!r}",
                    recoverable=True,
                )
            settings.chat_context_mode = write.chat_context_mode
        try:
            settings.save()
        except OSError as exc:
            raise SettingsAdvancedPortError(
                "persist_failed",
                "Advanced-Einstellungen konnten nicht gespeichert werden.",
                recoverable=True,
            ) from exc
        except Exception as exc:
            raise SettingsAdvancedPortError(
                "persist_failed",
                "Advanced-Einstellungen konnten nicht gespeichert werden.",
                recoverable=True,
            ) from exc

    @staticmethod
    def _coerce_prompt_storage_type(raw: object) -> PromptStorageType:
        if raw == "directory":
            return "directory"
        return "database"

    def _coerce_rag_space(self, raw: object) -> str:
        s = str(raw) if raw is not None else "default"
        return s if s in RAG_SPACE_IDS else "default"

    def _coerce_rag_top_k(self, raw: object) -> int:
        try:
            v = int(raw)
        except (TypeError, ValueError):
            v = 5
        return max(_RAG_TOP_K_MIN, min(_RAG_TOP_K_MAX, v))

    def load_data_settings_state(self) -> DataSettingsState:
        settings = get_infrastructure().settings
        return DataSettingsState(
            rag_enabled=bool(getattr(settings, "rag_enabled", False)),
            rag_space=self._coerce_rag_space(getattr(settings, "rag_space", "default")),
            rag_top_k=self._coerce_rag_top_k(getattr(settings, "rag_top_k", 5)),
            self_improving_enabled=bool(getattr(settings, "self_improving_enabled", False)),
            prompt_storage_type=self._coerce_prompt_storage_type(
                getattr(settings, "prompt_storage_type", "database")
            ),
            prompt_directory=str(getattr(settings, "prompt_directory", "") or ""),
            prompt_confirm_delete=bool(getattr(settings, "prompt_confirm_delete", True)),
            error=None,
        )

    @staticmethod
    def _data_write_is_empty(write: DataSettingsWritePatch) -> bool:
        return (
            write.rag_enabled is None
            and write.rag_space is None
            and write.rag_top_k is None
            and write.self_improving_enabled is None
            and write.prompt_storage_type is None
            and not write.prompt_directory_set
            and write.prompt_confirm_delete is None
        )

    def persist_data_settings(self, write: DataSettingsWritePatch) -> None:
        if self._data_write_is_empty(write):
            return
        settings = get_infrastructure().settings
        if write.rag_enabled is not None:
            settings.rag_enabled = write.rag_enabled
        if write.rag_space is not None:
            if write.rag_space not in RAG_SPACE_IDS:
                raise SettingsDataPortError(
                    "invalid_rag_space",
                    f"Unbekannter RAG-Space: {write.rag_space!r}",
                    recoverable=True,
                )
            settings.rag_space = write.rag_space
        if write.rag_top_k is not None:
            settings.rag_top_k = self._coerce_rag_top_k(write.rag_top_k)
        if write.self_improving_enabled is not None:
            settings.self_improving_enabled = write.self_improving_enabled
        if write.prompt_storage_type is not None:
            if write.prompt_storage_type not in ("database", "directory"):
                raise SettingsDataPortError(
                    "invalid_prompt_storage",
                    f"Ungültige Prompt-Speicherart: {write.prompt_storage_type!r}",
                    recoverable=True,
                )
            settings.prompt_storage_type = write.prompt_storage_type
        if write.prompt_directory_set:
            settings.prompt_directory = write.prompt_directory if write.prompt_directory is not None else ""
        if write.prompt_confirm_delete is not None:
            settings.prompt_confirm_delete = write.prompt_confirm_delete
        try:
            settings.save()
        except OSError as exc:
            raise SettingsDataPortError(
                "persist_failed",
                "Data-Einstellungen konnten nicht gespeichert werden.",
                recoverable=True,
            ) from exc
        except Exception as exc:
            raise SettingsDataPortError(
                "persist_failed",
                "Data-Einstellungen konnten nicht gespeichert werden.",
                recoverable=True,
            ) from exc

    @staticmethod
    def _coerce_temperature(raw: object) -> float:
        try:
            v = float(raw)
        except (TypeError, ValueError):
            v = 0.7
        return max(TEMPERATURE_MIN, min(TEMPERATURE_MAX, v))

    @staticmethod
    def _coerce_max_tokens(raw: object) -> int:
        try:
            v = int(raw)
        except (TypeError, ValueError):
            v = 4096
        return max(MAX_TOKENS_MIN, min(MAX_TOKENS_MAX, v))

    @staticmethod
    def _coerce_think_mode_read(raw: object) -> ThinkMode:
        s = str(raw) if raw is not None else "auto"
        if s in THINK_MODES:
            return cast(ThinkMode, s)
        return "auto"

    @staticmethod
    def _ai_scalar_write_is_empty(write: AiModelsScalarWritePatch) -> bool:
        return (
            write.temperature is None
            and write.max_tokens is None
            and write.think_mode is None
            and write.chat_streaming_enabled is None
        )

    def load_ai_models_scalar_state(self) -> AiModelsScalarSettingsState:
        settings = get_infrastructure().settings
        return AiModelsScalarSettingsState(
            temperature=self._coerce_temperature(getattr(settings, "temperature", 0.7)),
            max_tokens=self._coerce_max_tokens(getattr(settings, "max_tokens", 4096)),
            think_mode=self._coerce_think_mode_read(getattr(settings, "think_mode", "auto")),
            chat_streaming_enabled=bool(getattr(settings, "chat_streaming_enabled", True)),
            error=None,
        )

    def persist_ai_models_scalar(self, write: AiModelsScalarWritePatch) -> None:
        if self._ai_scalar_write_is_empty(write):
            return
        settings = get_infrastructure().settings
        if write.temperature is not None:
            settings.temperature = self._coerce_temperature(write.temperature)
        if write.max_tokens is not None:
            settings.max_tokens = self._coerce_max_tokens(write.max_tokens)
        if write.think_mode is not None:
            if write.think_mode not in THINK_MODES:
                raise SettingsAiModelsPortError(
                    "invalid_think_mode",
                    f"Ungültiger Thinking-Modus: {write.think_mode!r}",
                    recoverable=True,
                )
            settings.think_mode = write.think_mode
        if write.chat_streaming_enabled is not None:
            settings.chat_streaming_enabled = write.chat_streaming_enabled
        try:
            settings.save()
        except OSError as exc:
            raise SettingsAiModelsPortError(
                "persist_failed",
                "AI-Models-Einstellungen konnten nicht gespeichert werden.",
                recoverable=True,
            ) from exc
        except Exception as exc:
            raise SettingsAiModelsPortError(
                "persist_failed",
                "AI-Models-Einstellungen konnten nicht gespeichert werden.",
                recoverable=True,
            ) from exc

    @staticmethod
    def _coerce_top_p(raw: object) -> float:
        try:
            v = float(raw)
        except (TypeError, ValueError):
            v = 1.0
        return max(0.0, min(1.0, v))

    @staticmethod
    def _coerce_llm_timeout_seconds(raw: object) -> int:
        try:
            v = int(raw)
        except (TypeError, ValueError):
            v = 0
        return max(0, min(300, v))

    @staticmethod
    def _model_routing_write_is_empty(write: ModelRoutingStudioWritePatch) -> bool:
        return (
            write.model is None
            and write.auto_routing is None
            and write.cloud_escalation is None
            and write.cloud_via_local is None
            and write.web_search is None
            and write.overkill_mode is None
            and write.default_role is None
            and write.temperature is None
            and write.top_p is None
            and write.max_tokens is None
            and write.llm_timeout_seconds is None
            and write.retry_without_thinking is None
            and write.chat_streaming_enabled is None
        )

    def load_model_routing_studio_state(self) -> ModelRoutingStudioState:
        settings = get_infrastructure().settings
        dr_raw = getattr(settings, "default_role", "DEFAULT")
        dr_str = dr_raw if isinstance(dr_raw, str) else str(dr_raw)
        if dr_str not in {r.value for r in ModelRole}:
            dr_str = ModelRole.DEFAULT.value
        return ModelRoutingStudioState(
            model=str(getattr(settings, "model", "") or ""),
            auto_routing=bool(getattr(settings, "auto_routing", True)),
            cloud_escalation=bool(getattr(settings, "cloud_escalation", False)),
            cloud_via_local=bool(getattr(settings, "cloud_via_local", False)),
            web_search=bool(getattr(settings, "web_search", False)),
            overkill_mode=bool(getattr(settings, "overkill_mode", False)),
            default_role=dr_str,
            temperature=self._coerce_temperature(getattr(settings, "temperature", 0.7)),
            top_p=self._coerce_top_p(getattr(settings, "top_p", 1.0)),
            max_tokens=self._coerce_max_tokens(getattr(settings, "max_tokens", 4096)),
            llm_timeout_seconds=self._coerce_llm_timeout_seconds(
                getattr(settings, "llm_timeout_seconds", 0),
            ),
            retry_without_thinking=bool(getattr(settings, "retry_without_thinking", True)),
            chat_streaming_enabled=bool(getattr(settings, "chat_streaming_enabled", True)),
            error=None,
        )

    def persist_model_routing_studio(self, write: ModelRoutingStudioWritePatch) -> None:
        if self._model_routing_write_is_empty(write):
            return
        settings = get_infrastructure().settings
        if write.model is not None:
            settings.model = write.model
        if write.auto_routing is not None:
            settings.auto_routing = write.auto_routing
        if write.cloud_escalation is not None:
            settings.cloud_escalation = write.cloud_escalation
        if write.cloud_via_local is not None:
            settings.cloud_via_local = write.cloud_via_local
        if write.web_search is not None and hasattr(settings, "web_search"):
            settings.web_search = write.web_search
        if write.overkill_mode is not None:
            settings.overkill_mode = write.overkill_mode
        if write.default_role is not None:
            if write.default_role not in {r.value for r in ModelRole}:
                raise SettingsModelRoutingPortError(
                    "invalid_default_role",
                    f"Unbekannte Standardrolle: {write.default_role!r}",
                    recoverable=True,
                )
            settings.default_role = write.default_role
        if write.temperature is not None:
            settings.temperature = self._coerce_temperature(write.temperature)
        if write.top_p is not None:
            settings.top_p = self._coerce_top_p(write.top_p)
        if write.max_tokens is not None:
            settings.max_tokens = self._coerce_max_tokens(write.max_tokens)
        if write.llm_timeout_seconds is not None:
            settings.llm_timeout_seconds = self._coerce_llm_timeout_seconds(write.llm_timeout_seconds)
        if write.retry_without_thinking is not None:
            settings.retry_without_thinking = write.retry_without_thinking
        if write.chat_streaming_enabled is not None:
            settings.chat_streaming_enabled = write.chat_streaming_enabled
        try:
            settings.save()
        except OSError as exc:
            raise SettingsModelRoutingPortError(
                "persist_failed",
                "Model/Routing-Einstellungen konnten nicht gespeichert werden.",
                recoverable=True,
            ) from exc
        except Exception as exc:
            raise SettingsModelRoutingPortError(
                "persist_failed",
                "Model/Routing-Einstellungen konnten nicht gespeichert werden.",
                recoverable=True,
            ) from exc

    def persist_legacy_modal_settings(self, settings: AppSettings, commit: SettingsLegacyModalCommit) -> None:
        if commit.legacy_theme not in ("light", "dark"):
            raise SettingsLegacyModalPortError(
                "invalid_theme",
                f"Ungültiges Legacy-Theme: {commit.legacy_theme!r}",
                recoverable=True,
            )
        if commit.think_mode not in THINK_MODES:
            raise SettingsLegacyModalPortError(
                "invalid_think_mode",
                f"Ungültiger Thinking-Modus: {commit.think_mode!r}",
                recoverable=True,
            )
        if commit.rag_space not in RAG_SPACE_IDS:
            raise SettingsLegacyModalPortError(
                "invalid_rag_space",
                f"Unbekannter RAG-Space: {commit.rag_space!r}",
                recoverable=True,
            )
        if commit.prompt_storage_type not in ("database", "directory"):
            raise SettingsLegacyModalPortError(
                "invalid_prompt_storage",
                f"Ungültige Prompt-Speicherart: {commit.prompt_storage_type!r}",
                recoverable=True,
            )
        settings.model = commit.model_id
        settings.temperature = self._coerce_temperature(commit.temperature)
        settings.max_tokens = self._coerce_max_tokens(commit.max_tokens)
        settings.theme = commit.legacy_theme
        settings.think_mode = commit.think_mode
        settings.auto_routing = commit.auto_routing
        settings.cloud_escalation = commit.cloud_escalation
        settings.cloud_via_local = commit.cloud_via_local
        settings.overkill_mode = commit.overkill_mode
        settings.rag_enabled = commit.rag_enabled
        settings.rag_space = commit.rag_space
        settings.rag_top_k = self._coerce_rag_top_k(commit.rag_top_k)
        settings.self_improving_enabled = commit.self_improving_enabled
        settings.debug_panel_enabled = commit.debug_panel_enabled
        settings.prompt_storage_type = commit.prompt_storage_type
        settings.prompt_directory = commit.prompt_directory.strip()
        settings.prompt_confirm_delete = commit.prompt_confirm_delete
        settings.ollama_api_key = commit.ollama_api_key.strip()
        try:
            settings.save()
        except OSError as exc:
            raise SettingsLegacyModalPortError(
                "persist_failed",
                "Einstellungen konnten nicht gespeichert werden.",
                recoverable=True,
            ) from exc
        except Exception as exc:
            raise SettingsLegacyModalPortError(
                "persist_failed",
                "Einstellungen konnten nicht gespeichert werden.",
                recoverable=True,
            ) from exc

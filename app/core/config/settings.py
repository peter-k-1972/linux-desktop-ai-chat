"""
AppSettings – Anwendungskonfiguration.

Arbeitet über injizierbares SettingsBackend. Qt-frei.
"""

from enum import Enum
from typing import Any, Optional

from app.core.config.builtin_theme_ids import BUILTIN_THEME_IDS
from app.core.config.chat_context_enums import ChatContextDetailLevel, ChatContextMode
from app.core.config.settings_backend import InMemoryBackend, SettingsBackend
from app.utils.paths import DEFAULT_LEGACY_ICONS_PATH_STR


class ChatContextProfile(str, Enum):
    """Presets für Kontext-Konfiguration. Regelbasiert, keine Heuristik."""

    STRICT_MINIMAL = "strict_minimal"
    BALANCED = "balanced"
    FULL_GUIDANCE = "full_guidance"


def _theme_id_to_legacy_light_dark(theme_id: str) -> str:
    """Legacy ``theme``-Bucket; entspricht app.gui.themes.theme_id_utils (ohne GUI-Import)."""
    if theme_id == "light_default":
        return "light"
    return "dark"


def _normalize_theme_id(raw: str, legacy_theme: str) -> str:
    """Nur Built-in-IDs; unbekannte gespeicherte IDs → light_default, leer → legacy light/dark."""
    tid = (raw or "").strip()
    if tid in BUILTIN_THEME_IDS:
        return tid
    if not tid:
        return "dark_default" if legacy_theme == "dark" else "light_default"
    return "light_default"


class AppSettings:
    """Anwendungseinstellungen. Backend wird von außen injiziert."""

    def __init__(self, backend: Optional[SettingsBackend] = None) -> None:
        self._backend = backend if backend is not None else InMemoryBackend()
        self.load()

    def _load_bool(self, key: str, default: bool) -> bool:
        v = self._backend.value(key, default)
        if v is None:
            return default
        if isinstance(v, bool):
            return v
        return str(v).lower() in ("true", "1", "yes", "on")

    def load(self) -> None:
        legacy_theme = self._backend.value("theme", "light")
        self.theme = legacy_theme if isinstance(legacy_theme, str) else "light"
        raw_theme_id = (self._backend.value("theme_id", "") or "").strip()
        self.theme_id = _normalize_theme_id(raw_theme_id, self.theme)
        self.theme = _theme_id_to_legacy_light_dark(self.theme_id)
        self.model = self._backend.value("model", "llama2")
        self.temperature = float(self._backend.value("temperature", 0.7))
        self.top_p = float(self._backend.value("top_p", 1.0))
        self.max_tokens = int(self._backend.value("max_tokens", 4096))
        self.llm_timeout_seconds = int(self._backend.value("llm_timeout_seconds", 0))
        self.icons_path = self._backend.value("icons_path", DEFAULT_LEGACY_ICONS_PATH_STR)
        self.think_mode = self._backend.value("think_mode", "auto")

        self.auto_routing = self._load_bool("auto_routing", True)
        self.cloud_escalation = self._load_bool("cloud_escalation", False)
        self.cloud_via_local = self._load_bool("cloud_via_local", False)
        self.overkill_mode = self._load_bool("overkill_mode", False)
        self.web_search = self._load_bool("web_search", False)
        self.default_role = self._backend.value("default_role", "DEFAULT")
        self.ollama_api_key = (self._backend.value("ollama_api_key", "") or "").strip()

        self.retry_without_thinking = self._load_bool("retry_without_thinking", True)
        self.strip_html = self._load_bool("strip_html", True)
        self.preserve_markdown = self._load_bool("preserve_markdown", True)
        self.max_retries = int(self._backend.value("max_retries", 1))
        self.fallback_model = (self._backend.value("fallback_model", "") or "").strip() or None
        self.fallback_role = (self._backend.value("fallback_role", "") or "").strip() or None

        self.prompt_storage_type = self._backend.value("prompt_storage_type", "database")
        self.prompt_directory = self._backend.value("prompt_directory", "")
        self.prompt_confirm_delete = self._load_bool("prompt_confirm_delete", True)

        self.rag_enabled = self._load_bool("rag_enabled", False)
        self.rag_space = self._backend.value("rag_space", "default")
        self.rag_top_k = int(self._backend.value("rag_top_k", 5))
        self.self_improving_enabled = self._load_bool("self_improving_enabled", False)
        self.chat_mode = self._backend.value("chat_mode", "auto")
        self.debug_panel_enabled = self._load_bool("debug_panel_enabled", True)
        self.context_debug_enabled = self._load_bool("context_debug_enabled", False)
        self.chat_guard_ml_enabled = self._load_bool("chat_guard_ml_enabled", False)
        # chat.streaming_enabled: Antworten während der Generierung anzeigen (Streaming ON) oder erst am Ende (OFF)
        self.chat_streaming_enabled = self._load_bool("chat_streaming_enabled", True)
        # chat_context_mode: off | neutral | semantic – steuert Kontext-Injektion im Chat
        # load: aus Backend, default="semantic"; save: in save()
        raw_mode = (self._backend.value("chat_context_mode", "semantic") or "semantic").strip().lower()
        self.chat_context_mode = raw_mode if raw_mode in ("off", "neutral", "semantic") else "semantic"
        # chat_context_detail_level: minimal | standard | full – steuert Umfang der Kontext-Injektion
        raw_detail = (self._backend.value("chat_context_detail_level", "standard") or "standard").strip().lower()
        self.chat_context_detail_level = raw_detail if raw_detail in ("minimal", "standard", "full") else "standard"
        # chat_context_include_*: welche Felder injiziert werden (ADR: project_chat = Projekt+Chat, kein Topic)
        self.chat_context_include_project = self._load_bool("chat_context_include_project", True)
        self.chat_context_include_chat = self._load_bool("chat_context_include_chat", True)
        self.chat_context_include_topic = self._load_bool("chat_context_include_topic", False)

        self.chat_context_profile_enabled = self._load_bool("chat_context_profile_enabled", False)
        self.chat_context_profile = (
            self._backend.value("chat_context_profile", "balanced") or "balanced"
        ).strip().lower()

        self.model_usage_tracking_enabled = self._load_bool("model_usage_tracking_enabled", True)

        # Kanonische gui_id (siehe app.gui_registry); Legacy-Werte werden migriert.
        _raw_pg = (self._backend.value("preferred_gui", "default_widget_gui") or "default_widget_gui").strip().lower()
        if _raw_pg in ("library_qml", "qml", "library_qml_gui"):
            self.preferred_gui = "library_qml_gui"
        elif _raw_pg in ("default", "widget", "default_widget_gui"):
            self.preferred_gui = "default_widget_gui"
        else:
            self.preferred_gui = "default_widget_gui"

    def get_chat_context_mode(self) -> ChatContextMode:
        """Liefert den validierten Kontextmodus. Ungültige Werte → SEMANTIC."""
        try:
            return ChatContextMode(self.chat_context_mode)
        except Exception:
            return ChatContextMode.SEMANTIC

    def get_chat_context_detail_level(self) -> ChatContextDetailLevel:
        """Liefert den validierten Detail-Level. Ungültige Werte → STANDARD."""
        try:
            return ChatContextDetailLevel(self.chat_context_detail_level)
        except Exception:
            return ChatContextDetailLevel.STANDARD

    def get_chat_context_profile(self) -> ChatContextProfile:
        """Liefert das validierte Kontextprofil. Ungültige Werte → BALANCED."""
        try:
            return ChatContextProfile(self.chat_context_profile)
        except Exception:
            return ChatContextProfile.BALANCED

    def save(self) -> None:
        self._backend.setValue("theme", self.theme)
        self._backend.setValue("theme_id", self.theme_id)
        self._backend.setValue("model", self.model)
        self._backend.setValue("temperature", self.temperature)
        self._backend.setValue("top_p", self.top_p)
        self._backend.setValue("max_tokens", self.max_tokens)
        self._backend.setValue("llm_timeout_seconds", self.llm_timeout_seconds)
        self._backend.setValue("icons_path", self.icons_path)
        self._backend.setValue("think_mode", self.think_mode)
        self._backend.setValue("auto_routing", self.auto_routing)
        self._backend.setValue("cloud_escalation", self.cloud_escalation)
        self._backend.setValue("cloud_via_local", self.cloud_via_local)
        self._backend.setValue("overkill_mode", self.overkill_mode)
        self._backend.setValue("web_search", self.web_search)
        self._backend.setValue("default_role", self.default_role)
        self._backend.setValue("ollama_api_key", self.ollama_api_key)
        self._backend.setValue("retry_without_thinking", self.retry_without_thinking)
        self._backend.setValue("strip_html", self.strip_html)
        self._backend.setValue("preserve_markdown", self.preserve_markdown)
        self._backend.setValue("max_retries", self.max_retries)
        self._backend.setValue("fallback_model", self.fallback_model or "")
        self._backend.setValue("fallback_role", self.fallback_role or "")
        self._backend.setValue("prompt_storage_type", self.prompt_storage_type)
        self._backend.setValue("prompt_directory", self.prompt_directory)
        self._backend.setValue("prompt_confirm_delete", self.prompt_confirm_delete)
        self._backend.setValue("rag_enabled", self.rag_enabled)
        self._backend.setValue("rag_space", self.rag_space)
        self._backend.setValue("rag_top_k", self.rag_top_k)
        self._backend.setValue("self_improving_enabled", self.self_improving_enabled)
        self._backend.setValue("chat_mode", self.chat_mode)
        self._backend.setValue("debug_panel_enabled", self.debug_panel_enabled)
        self._backend.setValue("context_debug_enabled", self.context_debug_enabled)
        self._backend.setValue("chat_guard_ml_enabled", self.chat_guard_ml_enabled)
        self._backend.setValue("chat_streaming_enabled", self.chat_streaming_enabled)
        self._backend.setValue("chat_context_mode", self.chat_context_mode)
        self._backend.setValue("chat_context_detail_level", self.chat_context_detail_level)
        self._backend.setValue("chat_context_include_project", self.chat_context_include_project)
        self._backend.setValue("chat_context_include_chat", self.chat_context_include_chat)
        self._backend.setValue("chat_context_include_topic", self.chat_context_include_topic)
        self._backend.setValue("chat_context_profile_enabled", self.chat_context_profile_enabled)
        self._backend.setValue("chat_context_profile", self.chat_context_profile)
        self._backend.setValue("model_usage_tracking_enabled", self.model_usage_tracking_enabled)
        self._backend.setValue("preferred_gui", self.preferred_gui)

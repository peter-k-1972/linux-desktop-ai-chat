"""
QML-Kontextobjekt für Settings (``settingsStudio``).

Properties: providers, appearance, policies (Kontext + Richtlinien zusammen in ``policies``)
Slots: updateSetting, saveSettings, selectSection, reloadSettings
"""

from __future__ import annotations

import logging
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.core.config.builtin_theme_ids import BUILTIN_THEME_IDS
from app.core.config.settings import AppSettings
from app.ui_application.adapters.service_qml_settings_ledger_adapter import ServiceQmlSettingsLedgerAdapter
from app.ui_application.ports.qml_settings_ledger_port import QmlSettingsLedgerPort

from python_bridge.settings.settings_models import SettingsLedgerListModel

logger = logging.getLogger(__name__)


def _as_bool_str(v: Any) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    s = str(v).lower()
    return "true" if s in ("true", "1", "yes", "on") else "false"


def _display_value(settings: AppSettings, key: str, pending: dict[str, str]) -> str:
    if key in pending:
        return pending[key]
    if not hasattr(settings, key):
        return ""
    v = getattr(settings, key)
    if isinstance(v, bool):
        return _as_bool_str(v)
    if v is None:
        return ""
    return str(v)


def _parse_and_apply(settings: AppSettings, key: str, raw: str) -> None:
    if not hasattr(settings, key):
        return
    cur = getattr(settings, key)
    t = type(cur)
    s = (raw or "").strip()
    if t is bool:
        setattr(settings, key, s.lower() in ("true", "1", "yes", "on"))
        return
    if t is int:
        try:
            setattr(settings, key, int(float(s)))
        except ValueError:
            pass
        return
    if t is float:
        try:
            setattr(settings, key, float(s))
        except ValueError:
            pass
        return
    setattr(settings, key, s)


# (key, label, kind, options pipe-separated or "", description)
_PROVIDERS_DEF: tuple[tuple[str, str, str, str, str], ...] = (
    ("model", "Standard-Modell", "string", "", "Ollama-Modellkennung für den Chat."),
    ("temperature", "Temperatur", "number", "", "0 = deterministisch, höher = variabler."),
    ("top_p", "Top-P", "number", "", "Nucleus-Sampling."),
    ("max_tokens", "Max. Tokens", "number", "", "Obergrenze pro Antwort."),
    ("default_role", "Standard-Rolle", "string", "", "Routing / Modellrolle."),
    ("think_mode", "Think-Modus", "string", "", "z. B. auto."),
    ("ollama_api_key", "Ollama API-Schlüssel", "string", "", "Für Cloud-Zugriff (lokal leer lassen)."),
    ("auto_routing", "Auto-Routing", "bool", "", "Modelle automatisch wählen."),
    ("cloud_escalation", "Cloud-Eskalation", "bool", "", "Bei Bedarf in die Cloud wechseln."),
    ("cloud_via_local", "Cloud via Local", "bool", "", "Cloud-Anfragen über lokalen Pfad."),
    ("web_search", "Websuche", "bool", "", "Externe Suche aktivieren."),
    ("llm_timeout_seconds", "LLM-Timeout (s)", "number", "", "0 = Standard / kein explizites Limit."),
)

_CONTEXT_DEF: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "chat_context_mode",
        "Kontextmodus",
        "enum",
        "off|neutral|semantic",
        "Wie Kontext in den Prompt einfließt.",
    ),
    (
        "chat_context_detail_level",
        "Detailstufe",
        "enum",
        "minimal|standard|full",
        "Umfang der Kontext-Injektion.",
    ),
    ("chat_context_include_project", "Projekt im Kontext", "bool", "", "Projektmetadaten mitsenden."),
    ("chat_context_include_chat", "Chat im Kontext", "bool", "", "Chat-Metadaten mitsenden."),
    ("chat_context_include_topic", "Thema im Kontext", "bool", "", "Thema mitsenden."),
    ("chat_context_profile_enabled", "Kontextprofil aktiv", "bool", "", "Profil-Preset nutzen."),
    (
        "chat_context_profile",
        "Kontextprofil",
        "enum",
        "strict_minimal|balanced|full_guidance",
        "Preset für Kontextumfang.",
    ),
)

_APPEARANCE_DEF: tuple[tuple[str, str, str, str, str], ...] = (
    (
        "theme_id",
        "Theme",
        "enum",
        "|".join(sorted(BUILTIN_THEME_IDS)),
        "Erscheinungsbild der Anwendung.",
    ),
    ("icons_path", "Icon-Pfad", "string", "", "Legacy-Icon-Verzeichnis."),
)

_POLICIES_DEF: tuple[tuple[str, str, str, str, str], ...] = (
    ("rag_enabled", "RAG aktiv", "bool", "", "Retrieval-Augmented Generation."),
    ("rag_space", "RAG-Space", "string", "", "Name des Wissensraums."),
    ("rag_top_k", "RAG Top-K", "number", "", "Anzahl Chunks."),
    ("prompt_storage_type", "Prompt-Speicher", "string", "", "database oder directory."),
    ("prompt_confirm_delete", "Löschen bestätigen", "bool", "", "Sicherheitsabfrage beim Löschen."),
    ("chat_streaming_enabled", "Streaming", "bool", "", "Antwort während der Generierung anzeigen."),
    ("debug_panel_enabled", "Debug-Panel", "bool", "", "Entwickler-UI-Elemente."),
    ("context_debug_enabled", "Kontext-Debug", "bool", "", "Zusätzliche Kontext-Diagnose."),
    ("chat_guard_ml_enabled", "Chat-Guard (ML)", "bool", "", "ML-basierte Absicherung."),
    ("model_usage_tracking_enabled", "Modell-Nutzung tracken", "bool", "", "Nutzungsmetriken."),
    ("overkill_mode", "Overkill-Modus", "bool", "", "Aggressivere Pipeline."),
    ("self_improving_enabled", "Self-Improving", "bool", "", "Experimentelle Selbstoptimierung."),
)


def _section_row(heading: str) -> dict[str, str]:
    return {
        "key": "",
        "label": heading,
        "value": "",
        "kind": "section",
        "options": "",
        "description": "",
    }


class SettingsViewModel(QObject):
    providersChanged = Signal()
    appearanceChanged = Signal()
    policiesChanged = Signal()
    activeSectionChanged = Signal()
    dirtyChanged = Signal()
    previewTextChanged = Signal()

    def __init__(
        self,
        port: QmlSettingsLedgerPort | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._port: QmlSettingsLedgerPort = port or ServiceQmlSettingsLedgerAdapter()
        self._providers = SettingsLedgerListModel(self)
        self._appearance = SettingsLedgerListModel(self)
        self._policies = SettingsLedgerListModel(self)
        self._pending: dict[str, str] = {}
        self._active_section = "providers"
        self._rebuild_all()

    def _settings(self) -> AppSettings:
        return self._port.get_settings()

    def _get_providers(self) -> SettingsLedgerListModel:
        return self._providers

    providers = Property(QObject, _get_providers, notify=providersChanged)

    def _get_appearance(self) -> SettingsLedgerListModel:
        return self._appearance

    appearance = Property(QObject, _get_appearance, notify=appearanceChanged)

    def _get_policies(self) -> SettingsLedgerListModel:
        return self._policies

    policies = Property(QObject, _get_policies, notify=policiesChanged)

    def _get_active(self) -> str:
        return self._active_section

    activeSection = Property(str, _get_active, notify=activeSectionChanged)

    def _get_dirty(self) -> bool:
        return bool(self._pending)

    dirty = Property(bool, _get_dirty, notify=dirtyChanged)

    def _get_preview(self) -> str:
        s = self._settings()
        tid = self._pending.get("theme_id", s.theme_id)
        ctx = self._pending.get("chat_context_mode", s.chat_context_mode)
        return f"Theme: {tid}\nKontextmodus: {ctx}\nModell: {self._pending.get('model', s.model)}"

    previewText = Property(str, _get_preview, notify=previewTextChanged)

    def _rows_for(
        self,
        defs: tuple[tuple[str, str, str, str, str], ...],
        settings: AppSettings,
    ) -> list[dict[str, str]]:
        out: list[dict[str, str]] = []
        for key, label, kind, options, desc in defs:
            out.append(
                {
                    "key": key,
                    "label": label,
                    "value": _display_value(settings, key, self._pending),
                    "kind": kind,
                    "options": options,
                    "description": desc,
                }
            )
        return out

    def _rows_policies_merged(self, settings: AppSettings) -> list[dict[str, str]]:
        rows: list[dict[str, str]] = []
        rows.append(_section_row("Kontext"))
        rows.extend(self._rows_for(_CONTEXT_DEF, settings))
        rows.append(_section_row("Hausregeln & Richtlinien"))
        rows.extend(self._rows_for(_POLICIES_DEF, settings))
        return rows

    def _rebuild_all(self) -> None:
        s = self._settings()
        self._providers.set_rows(self._rows_for(_PROVIDERS_DEF, s))
        self._appearance.set_rows(self._rows_for(_APPEARANCE_DEF, s))
        self._policies.set_rows(self._rows_policies_merged(s))
        self.providersChanged.emit()
        self.appearanceChanged.emit()
        self.policiesChanged.emit()
        self.previewTextChanged.emit()

    @Slot(str)
    def selectSection(self, section_id: str) -> None:  # noqa: N802
        sid = (section_id or "").strip().lower()
        allowed = {"providers", "context", "appearance", "policies"}
        if sid not in allowed:
            return
        if self._active_section != sid:
            self._active_section = sid
            self.activeSectionChanged.emit()

    @Slot(str, str)
    def updateSetting(self, key: str, value: str) -> None:  # noqa: N802
        k = (key or "").strip()
        if not k:
            return
        if not hasattr(self._settings(), k):
            return
        v = value if value is not None else ""
        saved = _display_value(self._settings(), k, {})
        if v == saved:
            self._pending.pop(k, None)
        else:
            self._pending[k] = v
        self.dirtyChanged.emit()
        self._rebuild_all()

    @Slot()
    def saveSettings(self) -> None:  # noqa: N802
        if not self._pending:
            return
        s = self._settings()
        try:
            for k, v in self._pending.items():
                _parse_and_apply(s, k, v)
            s.save()
            self._pending.clear()
            self.dirtyChanged.emit()
            self._rebuild_all()
            self._try_apply_theme()
        except Exception:
            logger.exception("saveSettings")

    def _try_apply_theme(self) -> None:
        try:
            from app.gui.themes import get_theme_manager

            get_theme_manager().set_theme(self._settings().theme_id)
        except Exception:
            pass

    @Slot()
    def reloadSettings(self) -> None:  # noqa: N802
        self._pending.clear()
        self._port.reload_settings()
        self.dirtyChanged.emit()
        self._rebuild_all()


def build_settings_viewmodel() -> SettingsViewModel:
    return SettingsViewModel()

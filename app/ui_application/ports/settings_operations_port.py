"""
SettingsOperationsPort — Qt-frei (Appearance, Advanced, Data, AI-Models skalar, …).

Implementierungen in ``adapters/``; ThemeManager bleibt GUI-seitig.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.core.config.settings import AppSettings
from app.ui_contracts.workspaces.settings_advanced import (
    AdvancedSettingsState,
    AdvancedSettingsWritePatch,
)
from app.ui_contracts.workspaces.settings_appearance import AppearanceSettingsState
from app.ui_contracts.workspaces.settings_data import DataSettingsState, DataSettingsWritePatch
from app.ui_contracts.workspaces.settings_ai_models import (
    AiModelsScalarSettingsState,
    AiModelsScalarWritePatch,
)
from app.ui_contracts.workspaces.settings_legacy_modal import SettingsLegacyModalCommit
from app.ui_contracts.workspaces.settings_model_routing import (
    ModelRoutingStudioState,
    ModelRoutingStudioWritePatch,
)


@runtime_checkable
class SettingsOperationsPort(Protocol):
    """Zentrale Settings-Operationen für Presenter (ohne ORM-Objekte)."""

    def load_appearance_state(self) -> AppearanceSettingsState:
        """Theme-Metadaten + aktuelle Auswahl (wie bisher ThemeManager/Settings)."""
        ...

    def validate_theme_id(self, theme_id: str) -> bool:
        """True, wenn theme_id in der Registry bekannt ist."""
        ...

    def persist_theme_choice(self, theme_id: str) -> None:
        """
        Schreibt theme_id + Legacy-theme-String in AppSettings und speichert.

        Raises:
            SettingsAppearancePortError: unbekannte ID oder Persistenzfehler.
        """
        ...

    def load_advanced_settings_state(self) -> AdvancedSettingsState:
        """Debug-Flags und chat_context_mode aus AppSettings."""
        ...

    def persist_advanced_settings(self, write: AdvancedSettingsWritePatch) -> None:
        """
        Schreibt nur gesetzte Felder und ruft ``save()`` auf.

        Raises:
            SettingsAdvancedPortError: ungültiger Modus oder Persistenzfehler.
        """
        ...

    def load_data_settings_state(self) -> DataSettingsState:
        """RAG- und Prompt-Speicher-Felder aus AppSettings."""
        ...

    def persist_data_settings(self, write: DataSettingsWritePatch) -> None:
        """
        Schreibt nur gesetzte Felder und ruft ``save()`` auf.

        Raises:
            SettingsDataPortError: Validierung (z. B. RAG-Space) oder Persistenzfehler.
        """
        ...

    def load_ai_models_scalar_state(self) -> AiModelsScalarSettingsState:
        """Temperatur, Max-Tokens, Think-Modus, Streaming (AppSettings)."""
        ...

    def persist_ai_models_scalar(self, write: AiModelsScalarWritePatch) -> None:
        """
        Schreibt nur gesetzte Felder und ruft ``save()`` auf.

        Raises:
            SettingsAiModelsPortError: Validierung oder Persistenzfehler.
        """
        ...

    def load_model_routing_studio_state(self) -> ModelRoutingStudioState:
        """Routing/Assistant/skalare Streaming-Felder für ModelSettingsPanel (Studio)."""
        ...

    def persist_model_routing_studio(self, write: ModelRoutingStudioWritePatch) -> None:
        """
        Schreibt nur gesetzte Felder; ein ``save()`` wenn das Patch nicht leer ist.

        Raises:
            SettingsModelRoutingPortError: Validierung oder Persistenzfehler.
        """
        ...

    def persist_legacy_modal_settings(self, settings: AppSettings, commit: SettingsLegacyModalCommit) -> None:
        """
        Atomarer Speichervorgang für ``SettingsDialog`` (alle Felder + ein ``save()``).

        Mutiert die übergebene ``AppSettings``-Instanz (gleiche Referenz wie im Dialog).

        Raises:
            SettingsLegacyModalPortError: Validierung oder Persistenzfehler.
        """
        ...

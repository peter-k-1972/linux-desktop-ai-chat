"""
Schnittstellen, die QWidget-/QML-Adapter implementieren.

Nur Methoden, die Contract-Daten entgegennehmen — keine Service-Aufrufe.
"""

from __future__ import annotations

from typing import Any, Protocol

from app.ui_contracts.workspaces.chat import ChatStatePatch, ChatWorkspaceState
from app.ui_contracts.workspaces.settings_advanced import (
    AdvancedSettingsPatch,
    AdvancedSettingsState,
)
from app.ui_contracts.workspaces.settings_data import DataSettingsPatch, DataSettingsState
from app.ui_contracts.workspaces.deployment_releases import DeploymentReleasesViewState
from app.ui_contracts.workspaces.agent_tasks_inspector import AgentTasksInspectorState
from app.ui_contracts.workspaces.agent_tasks_task_panel import AgentTaskPanelState
from app.ui_contracts.workspaces.prompt_studio_detail import PromptStudioDetailState
from app.ui_contracts.workspaces.prompt_studio_editor import PromptEditorSaveResultState
from app.ui_contracts.workspaces.prompt_studio_list import PromptStudioListState
from app.ui_contracts.workspaces.prompt_studio_templates import PromptTemplatesState
from app.ui_contracts.workspaces.prompt_studio_test_lab import (
    PromptTestLabModelsState,
    PromptTestLabPromptsState,
    PromptTestLabRunPatch,
    PromptTestLabVersionsState,
)
from app.ui_contracts.workspaces.agent_tasks_runtime import StartAgentTaskResultDto
from app.ui_contracts.workspaces.prompt_studio_versions import PromptVersionPanelState
from app.ui_contracts.workspaces.agent_tasks_registry import (
    AgentTasksRegistryViewState,
    AgentTasksSelectionViewState,
)
from app.ui_contracts.workspaces.deployment_rollouts import DeploymentRolloutsViewState
from app.ui_contracts.workspaces.deployment_targets import DeploymentTargetsViewState
from app.ui_contracts.workspaces.settings_ai_model_catalog import AiModelCatalogState
from app.ui_contracts.workspaces.settings_ai_models import (
    AiModelsScalarSettingsPatch,
    AiModelsScalarSettingsState,
)
from app.ui_contracts.workspaces.model_usage_sidebar import ModelUsageSidebarHintState
from app.ui_contracts.workspaces.settings_appearance import (
    AppearanceSettingsState,
    AppearanceStatePatch,
)


class ChatUiSink(Protocol):
    """Ziel für Presenter-Updates (reiner Zustand / Patches)."""

    def apply_full_state(self, state: ChatWorkspaceState) -> None:
        """Kompletter Ersatz (Initial-Ladung, harte Resets)."""
        ...

    def apply_chat_patch(self, patch: ChatStatePatch) -> None:
        """Partielles Update (inkl. Stream-Chunks)."""
        ...


class SettingsAppearanceUiSink(Protocol):
    """Ziel für Settings-Appearance-Presenter (keine Service-Aufrufe)."""

    def apply_full_state(self, state: AppearanceSettingsState) -> None:
        """Kompletter Zustand (Initial-Ladung, harte Resets)."""
        ...

    def apply_patch(self, patch: AppearanceStatePatch) -> None:
        """Teilupdate (Auswahl-Häkchen, Fehlertext)."""
        ...

    def apply_selected_theme_visual(self, theme_id: str) -> bool:
        """ThemeManager.set_theme — nur visueller Effekt; kein Persist."""
        ...


class SettingsAdvancedUiSink(Protocol):
    """Ziel für Settings-Advanced-Presenter."""

    def apply_full_state(self, state: AdvancedSettingsState) -> None:
        ...

    def apply_patch(self, patch: AdvancedSettingsPatch) -> None:
        ...


class SettingsDataUiSink(Protocol):
    """Ziel für Settings-Data-Presenter."""

    def apply_full_state(self, state: DataSettingsState) -> None:
        ...

    def apply_patch(self, patch: DataSettingsPatch) -> None:
        ...


class SettingsAiModelsUiSink(Protocol):
    """Ziel für Settings-AI-Models-Presenter (skalare Felder, ohne Modell-Combo)."""

    def apply_full_state(self, state: AiModelsScalarSettingsState) -> None:
        ...

    def apply_patch(self, patch: AiModelsScalarSettingsPatch) -> None:
        ...


class SettingsAiModelCatalogUiSink(Protocol):
    """Ziel für Settings-AI-Model-Catalog-Presenter (Modell-Combo, Slice 4b)."""

    def apply_full_catalog_state(self, state: AiModelCatalogState) -> None:
        ...


class DeploymentTargetsUiSink(Protocol):
    """Ziel für Deployment-Targets-Presenter (Slice 1)."""

    def apply_full_state(self, state: DeploymentTargetsViewState) -> None:
        ...


class DeploymentReleasesUiSink(Protocol):
    """Ziel für Deployment-Releases-Presenter (Slice 3)."""

    def apply_full_state(self, state: DeploymentReleasesViewState) -> None:
        ...


class DeploymentRolloutsUiSink(Protocol):
    """Ziel für Deployment-Rollouts-Presenter (Slice 4)."""

    def apply_full_state(self, state: DeploymentRolloutsViewState) -> None:
        ...


class AgentTasksRegistryUiSink(Protocol):
    """Ziel für Agent-Tasks-Registry-Presenter (Slice 1)."""

    def apply_full_state(
        self,
        state: AgentTasksRegistryViewState,
        agent_profiles: tuple[Any, ...] = (),
    ) -> None:
        ...


class AgentTasksSelectionUiSink(Protocol):
    """Ziel für Agent-Tasks-Selection-Presenter (Slice 2, Betrieb-Detail)."""

    def apply_selection_state(self, state: AgentTasksSelectionViewState) -> None:
        ...


class AgentTasksInspectorUiSink(Protocol):
    """Ziel für Agent-Tasks-Inspector-Presenter (Slice 3)."""

    def apply_inspector_state(self, state: AgentTasksInspectorState) -> None:
        ...


class AgentTasksTaskPanelUiSink(Protocol):
    """Ziel für Agent-Tasks-Task-Panel-Presenter (Slice 4, Read)."""

    def apply_task_panel_state(self, state: AgentTaskPanelState) -> None:
        ...


class PromptStudioListUiSink(Protocol):
    """Ziel für Prompt-Studio-Listen-Presenter (Slice 1)."""

    def apply_full_state(
        self,
        state: PromptStudioListState,
        prompt_models: tuple[Any, ...] = (),
    ) -> None:
        ...


class PromptStudioDetailUiSink(Protocol):
    """Ziel für Prompt-Studio-Detail-Presenter (Slice 2)."""

    def apply_prompt_detail_state(self, state: PromptStudioDetailState) -> None:
        ...


class PromptStudioEditorUiSink(Protocol):
    """Ziel für Prompt-Studio-Editor-Persistenz (Batch 3)."""

    def apply_save_result(self, state: PromptEditorSaveResultState) -> None:
        ...


class PromptStudioVersionsUiSink(Protocol):
    """Ziel für Prompt-Studio-Versionen-Presenter (Batch 2)."""

    def apply_version_state(self, state: PromptVersionPanelState) -> None:
        ...


class PromptStudioTemplatesUiSink(Protocol):
    """Ziel für Prompt-Studio-Templates-Presenter (Batch 2)."""

    def apply_templates_state(
        self,
        state: PromptTemplatesState,
        template_models: tuple[Any, ...] = (),
    ) -> None:
        ...


class PromptStudioTestLabUiSink(Protocol):
    """Ziel für Prompt-Studio-Test-Lab-Presenter (Batch 5 read, Batch 6 run/stream)."""

    def apply_prompts_state(self, state: PromptTestLabPromptsState) -> None:
        ...

    def apply_versions_state(self, state: PromptTestLabVersionsState) -> None:
        ...

    def apply_models_state(self, state: PromptTestLabModelsState) -> None:
        ...

    def apply_run_patch(self, patch: PromptTestLabRunPatch) -> None:
        ...


class AgentTasksRuntimeUiSink(Protocol):
    """Ziel für Agent-Tasks-Runtime-Start (Batch 6)."""

    def apply_start_task_result(self, dto: StartAgentTaskResultDto) -> None:
        ...

    def apply_start_task_cancelled(self) -> None:
        ...

    def apply_start_task_exception(self, agent_id: str, prompt: str, error: str) -> None:
        ...


class ModelUsageSidebarUiSink(Protocol):
    """Ziel für Model-Usage-Sidebar-Hinweis (Chat-Studio-Panel)."""

    def apply_full_state(self, state: ModelUsageSidebarHintState) -> None:
        ...

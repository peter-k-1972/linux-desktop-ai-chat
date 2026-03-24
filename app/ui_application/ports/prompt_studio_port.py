"""
PromptStudioPort — Prompt Studio: Listen-Lesepfad (Slice 1), Detail-Lesepfad (Slice 2).
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from app.ui_contracts.workspaces.prompt_studio_detail import PromptDetailDto
from app.ui_contracts.workspaces.prompt_studio_editor import (
    PromptEditorPersistCommand,
    PromptEditorSaveResultState,
)
from app.ui_contracts.workspaces.prompt_studio_library import PromptLibraryMutationResult
from app.ui_contracts.workspaces.prompt_studio_list import PromptStudioListState
from app.ui_contracts.workspaces.prompt_studio_templates import (
    CopyPromptTemplateCommand,
    CreatePromptTemplateCommand,
    DeletePromptTemplateCommand,
    PromptTemplateMutationResult,
    PromptTemplatesState,
    UpdatePromptTemplateCommand,
)
from app.ui_contracts.workspaces.prompt_studio_versions import PromptVersionPanelState
from app.ui_contracts.workspaces.prompt_studio_workspace import PromptStudioWorkspaceOpResult
from app.ui_contracts.workspaces.prompt_studio_test_lab import (
    LoadPromptTestLabModelsCommand,
    LoadPromptTestLabPromptsCommand,
    LoadPromptTestLabVersionsCommand,
    PromptTestLabModelsState,
    PromptTestLabPromptsState,
    PromptTestLabStreamChunkDto,
    PromptTestLabVersionsState,
    RunPromptTestLabCommand,
)


@runtime_checkable
class PromptStudioPort(Protocol):
    def load_prompt_list(
        self,
        project_id: int | None,
        filter_text: str = "",
    ) -> PromptStudioListState:
        """
        Liefert Listen-Zustand; bei Fehler ``phase=error``.

        Konkrete Adapter können ``last_prompt_list_models`` (Reihenfolge wie ``rows``) setzen —
        nicht Teil des Protocols.
        """
        ...

    def load_prompt_detail(self, prompt_id: str, project_id: str | None) -> PromptDetailDto:
        """
        Lädt Prompt-Details für den Inspector.

        Leeres ``prompt_id`` ist ungültig — Aufrufer sollen den Presenter-Pfad für „keine Auswahl“ nutzen.
        """
        ...

    def load_prompt_versions(self, prompt_id: int) -> PromptVersionPanelState:
        """Versionen für das Versions-Panel (read-only)."""
        ...

    def load_prompt_templates(
        self,
        project_id: int | None,
        filter_text: str = "",
    ) -> PromptTemplatesState:
        """Templates-Liste (read-only); Adapter kann ``last_prompt_template_models`` setzen."""
        ...

    def persist_prompt_editor(self, command: PromptEditorPersistCommand) -> PromptEditorSaveResultState:
        """Editor speichern (Version oder Metadaten-Update) — schmal, kein vollständiges CRUD."""
        ...

    def create_user_prompt_for_studio(
        self,
        title: str,
        content: str,
        *,
        scope: str,
        project_id: int | None,
    ) -> PromptStudioWorkspaceOpResult:
        """Neuer User-Prompt wie Workspace „Neuer Prompt“."""
        ...

    def open_prompt_snapshot_for_studio(self, prompt_id: int) -> PromptStudioWorkspaceOpResult:
        """Prompt per ID für Kontext-Navigation laden."""
        ...

    def load_prompt_test_lab_prompts(
        self,
        command: LoadPromptTestLabPromptsCommand,
    ) -> PromptTestLabPromptsState:
        """Test-Lab: Prompt-Auswahl (read-only, kein Run/Stream)."""
        ...

    def load_prompt_test_lab_versions(
        self,
        command: LoadPromptTestLabVersionsCommand,
    ) -> PromptTestLabVersionsState:
        """Test-Lab: Versionen zur aktuellen Prompt-ID (read-only)."""
        ...

    async def load_prompt_test_lab_models(
        self,
        command: LoadPromptTestLabModelsCommand,
    ) -> PromptTestLabModelsState:
        """Test-Lab: Modellliste (async, read-only)."""
        ...

    async def stream_prompt_test_lab_run(
        self,
        command: RunPromptTestLabCommand,
    ) -> AsyncIterator[PromptTestLabStreamChunkDto]:
        """Test-Lab: Chat-Stream; Adapter mappt Service-Chunks auf DTOs."""
        ...

    def delete_prompt_library_entry(self, prompt_id: int) -> PromptLibraryMutationResult:
        """Library: Prompt löschen (Batch 7)."""
        ...

    def create_prompt_template(self, command: CreatePromptTemplateCommand) -> PromptTemplateMutationResult:
        ...

    def update_prompt_template(self, command: UpdatePromptTemplateCommand) -> PromptTemplateMutationResult:
        ...

    def copy_template_to_user_prompt(self, command: CopyPromptTemplateCommand) -> PromptStudioWorkspaceOpResult:
        ...

    def delete_prompt_template(self, command: DeletePromptTemplateCommand) -> PromptTemplateMutationResult:
        ...

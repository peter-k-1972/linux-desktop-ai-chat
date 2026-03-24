"""
PromptStudioTemplatesPresenter — Templates lesen (Batch 2).
"""

from __future__ import annotations

from typing import Any

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.prompt_studio_port import PromptStudioPort
from app.ui_application.view_models.protocols import PromptStudioTemplatesUiSink
from app.ui_contracts.workspaces.prompt_studio_workspace import PromptStudioWorkspaceOpResult
from app.ui_contracts.workspaces.prompt_studio_templates import (
    CopyPromptTemplateCommand,
    CreatePromptTemplateCommand,
    DeletePromptTemplateCommand,
    LoadPromptTemplatesCommand,
    PromptTemplateMutationResult,
    UpdatePromptTemplateCommand,
    prompt_templates_loading_state,
)


class PromptStudioTemplatesPresenter(BasePresenter):
    def __init__(self, sink: PromptStudioTemplatesUiSink, port: PromptStudioPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_command(self, command: LoadPromptTemplatesCommand) -> None:
        self._sink.apply_templates_state(prompt_templates_loading_state(), ())
        view = self._port.load_prompt_templates(command.project_id, command.filter_text)
        models: tuple[Any, ...] = ()
        if hasattr(self._port, "last_prompt_template_models"):
            models = tuple(getattr(self._port, "last_prompt_template_models"))
        self._sink.apply_templates_state(view, models)

    def _refresh_templates(self, project_id: int | None, filter_text: str) -> None:
        self.handle_command(LoadPromptTemplatesCommand(project_id, filter_text))

    def handle_create_template(
        self,
        command: CreatePromptTemplateCommand,
        *,
        refresh_project_id: int | None,
        refresh_filter_text: str,
    ) -> PromptTemplateMutationResult:
        result = self._port.create_prompt_template(command)
        if result.ok:
            self._refresh_templates(refresh_project_id, refresh_filter_text)
        return result

    def handle_update_template(
        self,
        command: UpdatePromptTemplateCommand,
        *,
        refresh_project_id: int | None,
        refresh_filter_text: str,
    ) -> PromptTemplateMutationResult:
        result = self._port.update_prompt_template(command)
        if result.ok:
            self._refresh_templates(refresh_project_id, refresh_filter_text)
        return result

    def handle_copy_template_to_prompt(
        self,
        command: CopyPromptTemplateCommand,
    ) -> PromptStudioWorkspaceOpResult:
        return self._port.copy_template_to_user_prompt(command)

    def handle_delete_template(
        self,
        command: DeletePromptTemplateCommand,
        *,
        refresh_project_id: int | None,
        refresh_filter_text: str,
    ) -> PromptTemplateMutationResult:
        result = self._port.delete_prompt_template(command)
        if result.ok:
            self._refresh_templates(refresh_project_id, refresh_filter_text)
        return result

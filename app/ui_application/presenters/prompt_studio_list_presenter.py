"""
PromptStudioListPresenter — Prompt-Liste lesen (Slice 1).
"""

from __future__ import annotations

from typing import Any

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.prompt_studio_port import PromptStudioPort
from app.ui_application.view_models.protocols import PromptStudioListUiSink
from app.ui_contracts.workspaces.prompt_studio_library import (
    DeletePromptLibraryCommand,
    PromptLibraryMutationResult,
)
from app.ui_contracts.workspaces.prompt_studio_list import (
    LoadPromptStudioListCommand,
    prompt_studio_list_loading_state,
)


class PromptStudioListPresenter(BasePresenter):
    def __init__(self, sink: PromptStudioListUiSink, port: PromptStudioPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_command(self, command: LoadPromptStudioListCommand) -> None:
        self._sink.apply_full_state(prompt_studio_list_loading_state(), ())
        view = self._port.load_prompt_list(command.project_id, command.filter_text)
        models: tuple[Any, ...] = ()
        if hasattr(self._port, "last_prompt_list_models"):
            models = tuple(getattr(self._port, "last_prompt_list_models"))
        self._sink.apply_full_state(view, models)

    def handle_delete_library_prompt(self, command: DeletePromptLibraryCommand) -> PromptLibraryMutationResult:
        result = self._port.delete_prompt_library_entry(command.prompt_id)
        if result.ok:
            self.handle_command(LoadPromptStudioListCommand(command.project_id, command.filter_text))
        return result

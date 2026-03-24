"""
PromptStudioVersionsPresenter — Versionen lesen (Batch 2).
"""

from __future__ import annotations

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.prompt_studio_port import PromptStudioPort
from app.ui_application.view_models.protocols import PromptStudioVersionsUiSink
from app.ui_contracts.workspaces.prompt_studio_versions import (
    LoadPromptVersionsCommand,
    prompt_versions_loading_state,
)


class PromptStudioVersionsPresenter(BasePresenter):
    def __init__(self, sink: PromptStudioVersionsUiSink, port: PromptStudioPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_command(self, command: LoadPromptVersionsCommand) -> None:
        self._sink.apply_version_state(prompt_versions_loading_state(command.prompt_id))
        view = self._port.load_prompt_versions(command.prompt_id)
        self._sink.apply_version_state(view)

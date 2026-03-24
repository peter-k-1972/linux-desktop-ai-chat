"""
PromptStudioEditorPresenter — Editor-Persistenz (Batch 3).
"""

from __future__ import annotations

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.prompt_studio_port import PromptStudioPort
from app.ui_application.view_models.protocols import PromptStudioEditorUiSink
from app.ui_contracts.workspaces.prompt_studio_editor import (
    PromptEditorPersistCommand,
    prompt_editor_save_saving_state,
)


class PromptStudioEditorPresenter(BasePresenter):
    def __init__(self, sink: PromptStudioEditorUiSink, port: PromptStudioPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def persist(self, command: PromptEditorPersistCommand) -> None:
        self._sink.apply_save_result(prompt_editor_save_saving_state())
        self._sink.apply_save_result(self._port.persist_prompt_editor(command))

"""
PromptStudioDetailPresenter — Prompt-Detail lesen (Slice 2).
"""

from __future__ import annotations

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.prompt_studio_port import PromptStudioPort
from app.ui_application.view_models.protocols import PromptStudioDetailUiSink
from app.ui_contracts.workspaces.prompt_studio_detail import (
    LoadPromptDetailCommand,
    PromptStudioDetailState,
    prompt_studio_detail_loading_state,
)


class PromptStudioDetailPresenter(BasePresenter):
    def __init__(self, sink: PromptStudioDetailUiSink, port: PromptStudioPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_command(self, command: LoadPromptDetailCommand) -> None:
        self._sink.apply_prompt_detail_state(prompt_studio_detail_loading_state())
        if not (command.prompt_id or "").strip():
            self._sink.apply_prompt_detail_state(
                PromptStudioDetailState(phase="ready", detail=None, error_message=None),
            )
            return
        try:
            dto = self._port.load_prompt_detail(command.prompt_id.strip(), command.project_id)
            self._sink.apply_prompt_detail_state(
                PromptStudioDetailState(phase="ready", detail=dto, error_message=None),
            )
        except Exception as exc:
            self._sink.apply_prompt_detail_state(
                PromptStudioDetailState(phase="error", detail=None, error_message=str(exc)),
            )

"""
PromptStudioWorkspacePresenter — Neuanlage / Kontext-Öffnen (Batch 3, dünn).
"""

from __future__ import annotations

from app.ui_application.ports.prompt_studio_port import PromptStudioPort
from app.ui_contracts.workspaces.prompt_studio_workspace import PromptStudioWorkspaceOpResult


class PromptStudioWorkspacePresenter:
    def __init__(self, port: PromptStudioPort) -> None:
        self._port = port

    def create_user_prompt(
        self,
        title: str,
        content: str,
        *,
        scope: str,
        project_id: int | None,
    ) -> PromptStudioWorkspaceOpResult:
        return self._port.create_user_prompt_for_studio(
            title,
            content,
            scope=scope,
            project_id=project_id,
        )

    def open_prompt(self, prompt_id: int) -> PromptStudioWorkspaceOpResult:
        return self._port.open_prompt_snapshot_for_studio(prompt_id)

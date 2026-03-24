"""PromptStudioWorkspacePresenter — thin delegate."""

from __future__ import annotations

from unittest.mock import MagicMock

from app.ui_application.presenters.prompt_studio_workspace_presenter import PromptStudioWorkspacePresenter
from app.ui_contracts.workspaces.prompt_studio_workspace import PromptStudioWorkspaceOpResult


def test_create_delegates_to_port() -> None:
    port = MagicMock()
    port.create_user_prompt_for_studio.return_value = PromptStudioWorkspaceOpResult(ok=False, error_message="x")
    pre = PromptStudioWorkspacePresenter(port)
    r = pre.create_user_prompt("t", "c", scope="global", project_id=None)
    assert r.ok is False
    port.create_user_prompt_for_studio.assert_called_once_with("t", "c", scope="global", project_id=None)


def test_open_delegates_to_port() -> None:
    port = MagicMock()
    port.open_prompt_snapshot_for_studio.return_value = PromptStudioWorkspaceOpResult(ok=True)
    pre = PromptStudioWorkspacePresenter(port)
    pre.open_prompt(42)
    port.open_prompt_snapshot_for_studio.assert_called_once_with(42)

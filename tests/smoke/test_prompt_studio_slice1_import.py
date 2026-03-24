"""Smoke: Prompt Studio Slice 1 (Prompt list read-only)."""


def test_prompt_studio_slice1_stack() -> None:
    from app.gui.domains.operations.prompt_studio.prompt_studio_list_sink import PromptStudioListSink
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter
    from app.ui_application.ports.prompt_studio_port import PromptStudioPort
    from app.ui_application.presenters.prompt_studio_list_presenter import PromptStudioListPresenter
    from app.ui_contracts.workspaces.prompt_studio_list import (
        LoadPromptStudioListCommand,
        prompt_studio_list_loading_state,
    )

    assert LoadPromptStudioListCommand(None, "").project_id is None
    assert prompt_studio_list_loading_state().phase == "loading"
    assert PromptStudioPort.__name__ == "PromptStudioPort"
    assert ServicePromptStudioAdapter.__name__ == "ServicePromptStudioAdapter"
    assert PromptStudioListPresenter.__name__ == "PromptStudioListPresenter"
    assert PromptStudioListSink.__name__ == "PromptStudioListSink"


def test_prompt_studio_workspace_imports() -> None:
    from app.gui.domains.operations.prompt_studio.prompt_studio_workspace import PromptStudioWorkspace

    assert PromptStudioWorkspace.__name__ == "PromptStudioWorkspace"

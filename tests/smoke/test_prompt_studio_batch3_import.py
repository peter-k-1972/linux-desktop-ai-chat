"""Smoke: Prompt Studio Batch 3 (Editor persist + Workspace presenter)."""


def test_prompt_studio_batch3_stack_imports() -> None:
    from app.gui.domains.operations.prompt_studio.prompt_studio_editor_sink import PromptStudioEditorSink
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter
    from app.ui_application.ports.prompt_studio_port import PromptStudioPort
    from app.ui_application.presenters.prompt_studio_editor_presenter import PromptStudioEditorPresenter
    from app.ui_application.presenters.prompt_studio_workspace_presenter import PromptStudioWorkspacePresenter
    from app.ui_contracts.workspaces.prompt_studio_editor import SavePromptVersionEditorCommand

    a = ServicePromptStudioAdapter()
    assert hasattr(a, "persist_prompt_editor")
    assert hasattr(a, "create_user_prompt_for_studio")
    assert hasattr(a, "open_prompt_snapshot_for_studio")
    assert hasattr(PromptStudioPort, "persist_prompt_editor")
    wp = PromptStudioWorkspacePresenter(a)
    assert wp.open_prompt(1) is not None
    assert SavePromptVersionEditorCommand(1, "a", "b").prompt_id == 1
    assert PromptStudioEditorSink.__name__ == "PromptStudioEditorSink"
    assert PromptStudioEditorPresenter.__name__ == "PromptStudioEditorPresenter"

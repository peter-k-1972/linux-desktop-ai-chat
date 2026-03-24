"""Smoke: Prompt Studio Batch 2 (Library/Version/Templates read stack)."""


def test_prompt_studio_batch2_stack_imports() -> None:
    from app.gui.domains.operations.prompt_studio.prompt_studio_library_sink import PromptStudioLibrarySink
    from app.gui.domains.operations.prompt_studio.prompt_studio_templates_sink import PromptStudioTemplatesSink
    from app.gui.domains.operations.prompt_studio.prompt_studio_versions_sink import PromptStudioVersionsSink
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter
    from app.ui_application.ports.prompt_studio_port import PromptStudioPort
    from app.ui_application.presenters.prompt_studio_templates_presenter import PromptStudioTemplatesPresenter
    from app.ui_application.presenters.prompt_studio_versions_presenter import PromptStudioVersionsPresenter
    from app.ui_contracts.workspaces.prompt_studio_library import LoadPromptLibraryCommand
    from app.ui_contracts.workspaces.prompt_studio_templates import LoadPromptTemplatesCommand
    from app.ui_contracts.workspaces.prompt_studio_versions import LoadPromptVersionsCommand

    assert PromptStudioPort.__name__ == "PromptStudioPort"
    a = ServicePromptStudioAdapter()
    assert hasattr(a, "load_prompt_versions")
    assert hasattr(a, "load_prompt_templates")
    assert PromptStudioVersionsPresenter.__name__ == "PromptStudioVersionsPresenter"
    assert PromptStudioTemplatesPresenter.__name__ == "PromptStudioTemplatesPresenter"
    assert PromptStudioLibrarySink.__name__ == "PromptStudioLibrarySink"
    assert PromptStudioVersionsSink.__name__ == "PromptStudioVersionsSink"
    assert PromptStudioTemplatesSink.__name__ == "PromptStudioTemplatesSink"
    assert LoadPromptLibraryCommand(1, "").project_id == 1
    assert LoadPromptVersionsCommand(2).prompt_id == 2
    assert LoadPromptTemplatesCommand(None, "").project_id is None

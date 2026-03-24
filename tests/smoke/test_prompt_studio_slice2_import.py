"""Smoke: Prompt Studio Slice 2 (Prompt detail read path)."""


def test_prompt_studio_slice2_stack() -> None:
    from app.gui.domains.prompt_studio.prompt_detail_sink import PromptDetailSink
    from app.gui.domains.operations.prompt_studio.panels.prompt_inspector_panel import PromptInspectorPanel
    from app.ui_application.adapters.service_prompt_studio_adapter import ServicePromptStudioAdapter
    from app.ui_application.ports.prompt_studio_port import PromptStudioPort
    from app.ui_application.presenters.prompt_studio_detail_presenter import PromptStudioDetailPresenter
    from app.ui_contracts.workspaces.prompt_studio_detail import (
        LoadPromptDetailCommand,
        prompt_studio_detail_loading_state,
    )

    assert LoadPromptDetailCommand("1", None).prompt_id == "1"
    assert prompt_studio_detail_loading_state().phase == "loading"
    assert PromptStudioPort.__name__ == "PromptStudioPort"
    a = ServicePromptStudioAdapter()
    assert hasattr(a, "load_prompt_detail")
    assert PromptStudioDetailPresenter.__name__ == "PromptStudioDetailPresenter"
    assert PromptDetailSink.__name__ == "PromptDetailSink"
    assert PromptInspectorPanel.__name__ == "PromptInspectorPanel"

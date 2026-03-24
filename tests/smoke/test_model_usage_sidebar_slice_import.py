"""Smoke: Model-Usage-Sidebar-Slice importierbar."""


def test_import_stack() -> None:
    from app.ui_application.adapters.service_model_usage_gui_adapter import ServiceModelUsageGuiAdapter
    from app.ui_application.presenters.model_usage_sidebar_presenter import ModelUsageSidebarHintPresenter
    from app.gui.domains.settings.model_usage_sidebar_sink import ModelUsageSidebarSink

    assert ServiceModelUsageGuiAdapter.__name__ == "ServiceModelUsageGuiAdapter"
    assert ModelUsageSidebarHintPresenter.__name__ == "ModelUsageSidebarHintPresenter"
    assert ModelUsageSidebarSink.__name__ == "ModelUsageSidebarSink"

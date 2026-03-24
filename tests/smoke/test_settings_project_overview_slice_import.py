"""Smoke: Settings-Projektübersicht-Slice importierbar."""


def test_import_stack() -> None:
    from app.ui_application.adapters.service_settings_project_overview_adapter import (
        ServiceSettingsProjectOverviewAdapter,
    )
    from app.ui_application.presenters.settings_project_overview_presenter import (
        SettingsProjectOverviewPresenter,
    )
    from app.gui.domains.settings.settings_project_overview_sink import SettingsProjectOverviewSink

    assert ServiceSettingsProjectOverviewAdapter.__name__ == "ServiceSettingsProjectOverviewAdapter"
    assert SettingsProjectOverviewPresenter.__name__ == "SettingsProjectOverviewPresenter"
    assert SettingsProjectOverviewSink.__name__ == "SettingsProjectOverviewSink"

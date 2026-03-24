"""Smoke: Settings Slice 3 (Data) — Module importierbar."""


def test_settings_data_stack_imports() -> None:
    from app.gui.domains.settings.settings_data_sink import SettingsDataSink
    from app.gui.domains.settings.panels.data_settings_panel import DataSettingsPanel
    from app.ui_application.presenters.settings_data_presenter import SettingsDataPresenter
    from app.ui_contracts.workspaces.settings_data import DataSettingsState

    assert SettingsDataSink.__name__ == "SettingsDataSink"
    assert DataSettingsPanel.__name__ == "DataSettingsPanel"
    assert SettingsDataPresenter.__name__ == "SettingsDataPresenter"
    assert DataSettingsState.__name__ == "DataSettingsState"

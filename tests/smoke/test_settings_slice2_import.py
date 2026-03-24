"""Smoke: Settings Slice 2 (Advanced) — Module importierbar."""


def test_settings_advanced_stack_imports() -> None:
    from app.gui.domains.settings.settings_advanced_sink import SettingsAdvancedSink
    from app.gui.domains.settings.panels.advanced_settings_panel import AdvancedSettingsPanel
    from app.ui_application.presenters.settings_advanced_presenter import SettingsAdvancedPresenter
    from app.ui_contracts.workspaces.settings_advanced import AdvancedSettingsState

    assert SettingsAdvancedSink.__name__ == "SettingsAdvancedSink"
    assert AdvancedSettingsPanel.__name__ == "AdvancedSettingsPanel"
    assert SettingsAdvancedPresenter.__name__ == "SettingsAdvancedPresenter"
    assert AdvancedSettingsState.__name__ == "AdvancedSettingsState"

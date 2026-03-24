"""Smoke: Settings Slice 1 (Appearance) — Module und Stack importierbar."""


def test_settings_appearance_stack_imports() -> None:
    from app.gui.domains.settings.settings_appearance_sink import SettingsAppearanceSink
    from app.gui.domains.settings.panels.theme_selection_panel import ThemeSelectionPanel
    from app.ui_application.adapters.service_settings_adapter import ServiceSettingsAdapter
    from app.ui_application.presenters.settings_appearance_presenter import SettingsAppearancePresenter
    from app.ui_application.ports.settings_operations_port import SettingsOperationsPort
    from app.ui_contracts.workspaces.settings_appearance import AppearanceSettingsState

    assert SettingsAppearanceSink.__name__ == "SettingsAppearanceSink"
    assert ThemeSelectionPanel.__name__ == "ThemeSelectionPanel"
    assert ServiceSettingsAdapter.__name__ == "ServiceSettingsAdapter"
    assert SettingsAppearancePresenter.__name__ == "SettingsAppearancePresenter"
    assert SettingsOperationsPort.__name__ == "SettingsOperationsPort"
    assert AppearanceSettingsState.__name__ == "AppearanceSettingsState"

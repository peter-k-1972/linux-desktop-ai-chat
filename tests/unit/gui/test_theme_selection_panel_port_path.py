"""ThemeSelectionPanel — Port-Pfad vs. Legacy-Fallback."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.settings.panels.theme_selection_panel import ThemeSelectionPanel
from app.ui_contracts.workspaces.settings_appearance import (
    AppearanceSettingsState,
    LoadAppearanceSettingsCommand,
    SelectThemeCommand,
    ThemeListEntry,
)


class _FakePort:
    def __init__(self) -> None:
        self.persisted: list[str] = []
        self._state = AppearanceSettingsState(
            themes=(
                ThemeListEntry("light_default", "Light"),
                ThemeListEntry("dark_default", "Dark"),
            ),
            selected_theme_id="light_default",
            error=None,
        )

    def load_appearance_state(self) -> AppearanceSettingsState:
        return self._state

    def validate_theme_id(self, theme_id: str) -> bool:
        return theme_id in ("light_default", "dark_default")

    def persist_theme_choice(self, theme_id: str) -> None:
        self.persisted.append(theme_id)
        self._state = AppearanceSettingsState(
            themes=self._state.themes,
            selected_theme_id=theme_id,
            error=None,
        )


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


def test_legacy_panel_populates_theme_list(qapp) -> None:
    panel = ThemeSelectionPanel(appearance_port=None)
    assert panel._list.count() >= 1


def test_port_path_populates_from_load(qapp) -> None:
    port = _FakePort()
    panel = ThemeSelectionPanel(appearance_port=port)
    assert panel._list.count() == 2
    assert panel._presenter is not None


def test_port_path_select_persists(qapp) -> None:
    port = _FakePort()
    panel = ThemeSelectionPanel(appearance_port=port)
    item = panel._list.item(1)
    assert item is not None
    panel._list.itemClicked.emit(item)
    assert port.persisted == ["dark_default"]


def test_port_path_unknown_theme_shows_error(qapp) -> None:
    port = _FakePort()
    panel = ThemeSelectionPanel(appearance_port=port)
    assert panel._presenter is not None
    panel._presenter.handle_command(LoadAppearanceSettingsCommand())
    panel._presenter.handle_command(SelectThemeCommand("invalid_theme_id"))
    # Ohne Top-Level-Fenster ist isVisible() oft False; Text + isHidden reicht.
    assert not panel._error_label.isHidden()
    assert "Unbekanntes Theme" in panel._error_label.text()

"""SettingsAppearanceSink — Liste und Fehlerzeile aus Contract-State."""

from __future__ import annotations

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidget, QApplication

from app.gui.domains.settings.settings_appearance_sink import SettingsAppearanceSink
from app.ui_contracts.workspaces.settings_appearance import (
    AppearanceSettingsState,
    AppearanceStatePatch,
    SettingsErrorInfo,
    ThemeListEntry,
)


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _qapp()
    yield


def test_apply_full_state_renders_list_and_checkmark(qapp) -> None:
    lst = QListWidget()
    err = QLabel()
    sink = SettingsAppearanceSink(lst, err, {})
    state = AppearanceSettingsState(
        themes=(
            ThemeListEntry("a", "Alpha"),
            ThemeListEntry("b", "Beta"),
        ),
        selected_theme_id="b",
        error=None,
    )
    sink.apply_full_state(state)
    assert lst.count() == 2
    item1 = lst.item(1)
    assert item1 is not None
    assert item1.data(Qt.ItemDataRole.UserRole) == "b"
    assert "✓" in item1.text()


def test_apply_patch_updates_error(qapp) -> None:
    lst = QListWidget()
    err = QLabel()
    sink = SettingsAppearanceSink(lst, err, {})
    sink.apply_full_state(
        AppearanceSettingsState(
            themes=(ThemeListEntry("x", "X"),),
            selected_theme_id="x",
            error=None,
        )
    )
    sink.apply_patch(
        AppearanceStatePatch(
            error=SettingsErrorInfo(code="e", message="oops"),
            has_error_update=True,
        )
    )
    assert "oops" in err.text()
    assert err.isVisible()

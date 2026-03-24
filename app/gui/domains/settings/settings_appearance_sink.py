"""
SettingsAppearanceSink — spiegelt AppearanceSettingsState auf QListWidget + Fehlerzeile.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidget, QListWidgetItem

from app.gui.themes import get_theme_manager
from app.ui_contracts.workspaces.settings_appearance import (
    AppearanceSettingsState,
    AppearanceStatePatch,
    merge_appearance_state,
)


class SettingsAppearanceSink:
    def __init__(
        self,
        list_widget: QListWidget,
        error_label: QLabel,
        theme_descriptions: dict[str, str],
    ) -> None:
        self._list = list_widget
        self._error = error_label
        self._descriptions = theme_descriptions
        self._last: AppearanceSettingsState | None = None

    def apply_full_state(self, state: AppearanceSettingsState) -> None:
        self._last = state
        self._render_list(state)
        self._render_error(state)

    def apply_patch(self, patch: AppearanceStatePatch) -> None:
        if self._last is None:
            return
        merged = merge_appearance_state(self._last, patch)
        self._last = merged
        self._render_list(merged)
        self._render_error(merged)

    def apply_selected_theme_visual(self, theme_id: str) -> bool:
        return get_theme_manager().set_theme(theme_id)

    def _render_error(self, state: AppearanceSettingsState) -> None:
        if state.error is None:
            self._error.clear()
            self._error.hide()
        else:
            self._error.setText(state.error.message)
            self._error.show()

    def _render_list(self, state: AppearanceSettingsState) -> None:
        self._list.clear()
        current = state.selected_theme_id
        for entry in state.themes:
            tid = entry.theme_id
            name = entry.display_name
            item = QListWidgetItem(f"  {name}")
            item.setData(Qt.ItemDataRole.UserRole, tid)
            if tid == current:
                item.setText(f"  {name}  ✓")
            desc = self._descriptions.get(tid)
            if desc:
                item.setToolTip(desc)
            self._list.addItem(item)

"""
SettingsProjectOverviewSink — Body-QLabel aus SettingsProjectCategoryBodyState.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from app.ui_contracts.workspaces.settings_project_overview import SettingsProjectCategoryBodyState


class SettingsProjectOverviewSink:
    def __init__(self, body_label: QLabel) -> None:
        self._body = body_label

    def apply_body_state(self, state: SettingsProjectCategoryBodyState) -> None:
        self._body.setText(state.body_text)

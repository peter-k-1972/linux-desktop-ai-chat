"""
ModelUsageSidebarSink — spiegelt ModelUsageSidebarHintState auf QLabel.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel

from app.ui_contracts.workspaces.model_usage_sidebar import ModelUsageSidebarHintState


class ModelUsageSidebarSink:
    def __init__(self, hint_label: QLabel) -> None:
        self._label = hint_label

    def apply_full_state(self, state: ModelUsageSidebarHintState) -> None:
        self._label.setText(state.hint_text)

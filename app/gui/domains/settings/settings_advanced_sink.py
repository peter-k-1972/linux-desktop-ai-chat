"""
SettingsAdvancedSink — spiegelt AdvancedSettingsState auf Checkboxen + Combo.
"""

from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel

from app.ui_contracts.workspaces.settings_advanced import (
    AdvancedSettingsPatch,
    AdvancedSettingsState,
    merge_advanced_state,
)


class SettingsAdvancedSink:
    def __init__(
        self,
        debug_panel_check: QCheckBox,
        context_debug_check: QCheckBox,
        context_mode_combo: QComboBox,
        error_label: QLabel,
    ) -> None:
        self._debug = debug_panel_check
        self._ctx = context_debug_check
        self._mode = context_mode_combo
        self._error = error_label
        self._last: AdvancedSettingsState | None = None

    def _block(self, on: bool) -> None:
        self._debug.blockSignals(on)
        self._ctx.blockSignals(on)
        self._mode.blockSignals(on)

    def apply_full_state(self, state: AdvancedSettingsState) -> None:
        self._last = state
        self._block(True)
        try:
            self._debug.setChecked(state.debug_panel_enabled)
            self._ctx.setChecked(state.context_debug_enabled)
            idx = self._mode.findText(state.chat_context_mode)
            if idx >= 0:
                self._mode.setCurrentIndex(idx)
            else:
                self._mode.setCurrentText(state.chat_context_mode)
            self._render_error(state.error)
        finally:
            self._block(False)

    def apply_patch(self, patch: AdvancedSettingsPatch) -> None:
        if self._last is None:
            return
        merged = merge_advanced_state(self._last, patch)
        self.apply_full_state(merged)

    def _render_error(self, error) -> None:
        if error is None:
            self._error.clear()
            self._error.hide()
        else:
            self._error.setText(error.message)
            self._error.show()

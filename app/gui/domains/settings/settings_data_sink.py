"""
SettingsDataSink — spiegelt DataSettingsState auf Formular-Widgets.
"""

from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QComboBox, QLabel, QLineEdit, QSpinBox

from app.ui_contracts.workspaces.settings_data import (
    DataSettingsPatch,
    DataSettingsState,
    merge_data_state,
)


class SettingsDataSink:
    def __init__(
        self,
        rag_enabled_check: QCheckBox,
        rag_space_combo: QComboBox,
        rag_top_k_spin: QSpinBox,
        self_improving_check: QCheckBox,
        prompt_storage_combo: QComboBox,
        prompt_directory_edit: QLineEdit,
        prompt_confirm_delete_check: QCheckBox,
        error_label: QLabel,
    ) -> None:
        self._rag_en = rag_enabled_check
        self._rag_space = rag_space_combo
        self._rag_top_k = rag_top_k_spin
        self._self_imp = self_improving_check
        self._prompt_st = prompt_storage_combo
        self._prompt_dir = prompt_directory_edit
        self._prompt_del = prompt_confirm_delete_check
        self._error = error_label
        self._last: DataSettingsState | None = None

    def _block(self, on: bool) -> None:
        self._rag_en.blockSignals(on)
        self._rag_space.blockSignals(on)
        self._rag_top_k.blockSignals(on)
        self._self_imp.blockSignals(on)
        self._prompt_st.blockSignals(on)
        self._prompt_dir.blockSignals(on)
        self._prompt_del.blockSignals(on)

    def apply_full_state(self, state: DataSettingsState) -> None:
        self._last = state
        self._block(True)
        try:
            self._rag_en.setChecked(state.rag_enabled)
            self._rag_space.setCurrentText(state.rag_space)
            self._rag_top_k.setValue(state.rag_top_k)
            self._self_imp.setChecked(state.self_improving_enabled)
            self._prompt_st.setCurrentIndex(1 if state.prompt_storage_type == "directory" else 0)
            self._prompt_dir.setText(state.prompt_directory)
            self._prompt_del.setChecked(state.prompt_confirm_delete)
            self._render_error(state.error)
        finally:
            self._block(False)

    def apply_patch(self, patch: DataSettingsPatch) -> None:
        if self._last is None:
            return
        merged = merge_data_state(self._last, patch)
        self.apply_full_state(merged)

    def _render_error(self, error) -> None:
        if error is None:
            self._error.clear()
            self._error.hide()
        else:
            self._error.setText(error.message)
            self._error.show()

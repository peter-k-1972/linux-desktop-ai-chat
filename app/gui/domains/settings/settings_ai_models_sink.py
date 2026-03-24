"""
SettingsAiModelsSink — skalare AI-Model-Felder (ohne Modell-Combo).

Slice 4: Temperatur, Max-Tokens, Think-Modus, Streaming; Fehlerzeile.
"""

from __future__ import annotations

from PySide6.QtWidgets import QCheckBox, QDoubleSpinBox, QLabel, QSpinBox, QComboBox

from app.ui_contracts.workspaces.settings_ai_models import (
    AiModelsScalarSettingsPatch,
    AiModelsScalarSettingsState,
    merge_ai_models_scalar_state,
)


class SettingsAiModelsSink:
    def __init__(
        self,
        temp_spin: QDoubleSpinBox,
        tokens_spin: QSpinBox,
        think_mode_combo: QComboBox,
        stream_check: QCheckBox,
        error_label: QLabel,
    ) -> None:
        self._temp = temp_spin
        self._tokens = tokens_spin
        self._think = think_mode_combo
        self._stream = stream_check
        self._error = error_label
        self._last: AiModelsScalarSettingsState | None = None

    def _block(self, on: bool) -> None:
        self._temp.blockSignals(on)
        self._tokens.blockSignals(on)
        self._think.blockSignals(on)
        self._stream.blockSignals(on)

    def apply_full_state(self, state: AiModelsScalarSettingsState) -> None:
        self._last = state
        self._block(True)
        try:
            self._temp.setValue(state.temperature)
            self._tokens.setValue(state.max_tokens)
            idx = self._think.findText(state.think_mode)
            if idx >= 0:
                self._think.setCurrentIndex(idx)
            else:
                self._think.setCurrentIndex(0)
            self._stream.setChecked(state.chat_streaming_enabled)
            self._render_error(state.error)
        finally:
            self._block(False)

    def apply_patch(self, patch: AiModelsScalarSettingsPatch) -> None:
        if self._last is None:
            return
        merged = merge_ai_models_scalar_state(self._last, patch)
        self.apply_full_state(merged)

    def _render_error(self, error) -> None:
        if error is None:
            self._error.clear()
            self._error.hide()
        else:
            self._error.setText(error.message)
            self._error.show()

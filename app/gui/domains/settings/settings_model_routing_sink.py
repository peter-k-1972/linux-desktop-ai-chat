"""
SettingsModelRoutingSink — ModelSettingsPanel (Studio) aus :class:`ModelRoutingStudioState`.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QCheckBox, QComboBox, QDoubleSpinBox, QSpinBox

from app.core.models.roles import ModelRole
from app.ui_contracts.workspaces.settings_model_routing import ModelRoutingStudioState


class SettingsModelRoutingSink:
    def __init__(
        self,
        assistant_combo: QComboBox,
        auto_routing_check: QCheckBox,
        cloud_check: QCheckBox,
        cloud_via_local_check: QCheckBox,
        web_search_check: QCheckBox,
        overkill_check: QCheckBox,
        default_role_combo: QComboBox,
        temp_spin: QDoubleSpinBox,
        top_p_spin: QDoubleSpinBox,
        max_tokens_spin: QSpinBox,
        timeout_spin: QSpinBox,
        retry_check: QCheckBox,
        stream_check: QCheckBox,
    ) -> None:
        self._assistant_combo = assistant_combo
        self._auto_routing_check = auto_routing_check
        self._cloud_check = cloud_check
        self._cloud_via_local_check = cloud_via_local_check
        self._web_search_check = web_search_check
        self._overkill_check = overkill_check
        self._default_role_combo = default_role_combo
        self._temp_spin = temp_spin
        self._top_p_spin = top_p_spin
        self._max_tokens_spin = max_tokens_spin
        self._timeout_spin = timeout_spin
        self._retry_check = retry_check
        self._stream_check = stream_check

    def _find_model_index(self, combo: QComboBox, model_id: str) -> int:
        for i in range(combo.count()):
            if combo.itemData(i, Qt.ItemDataRole.UserRole) == model_id:
                return i
            if combo.itemText(i) == model_id:
                return i
        return -1

    def apply_full_state(self, state: ModelRoutingStudioState) -> None:
        widgets = (
            self._assistant_combo,
            self._auto_routing_check,
            self._cloud_check,
            self._cloud_via_local_check,
            self._web_search_check,
            self._overkill_check,
            self._default_role_combo,
            self._temp_spin,
            self._top_p_spin,
            self._max_tokens_spin,
            self._timeout_spin,
            self._retry_check,
            self._stream_check,
        )
        for w in widgets:
            w.blockSignals(True)
        try:
            self._auto_routing_check.setChecked(state.auto_routing)
            self._cloud_check.setChecked(state.cloud_escalation)
            self._cloud_via_local_check.setChecked(state.cloud_via_local)
            self._web_search_check.setChecked(state.web_search)
            self._overkill_check.setChecked(state.overkill_mode)
            self._temp_spin.setValue(state.temperature)
            self._top_p_spin.setValue(state.top_p)
            self._max_tokens_spin.setValue(state.max_tokens)
            self._timeout_spin.setValue(state.llm_timeout_seconds)
            self._retry_check.setChecked(state.retry_without_thinking)
            self._stream_check.setChecked(state.chat_streaming_enabled)
            try:
                role_enum = ModelRole(state.default_role)
            except ValueError:
                role_enum = ModelRole.DEFAULT
            idx = self._default_role_combo.findData(role_enum)
            if idx >= 0:
                self._default_role_combo.setCurrentIndex(idx)
            if state.model:
                mi = self._find_model_index(self._assistant_combo, state.model)
                if mi >= 0:
                    self._assistant_combo.setCurrentIndex(mi)
        finally:
            for w in widgets:
                w.blockSignals(False)

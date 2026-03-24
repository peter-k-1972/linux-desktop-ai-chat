"""
DeploymentRolloutsSink — Rollout-Tabelle und Filter-Combos aus :class:`DeploymentRolloutsViewState`.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QLabel, QTableWidget, QTableWidgetItem

from app.ui_contracts.workspaces.deployment_rollouts import DeploymentRolloutsViewState


class DeploymentRolloutsSink:
    def __init__(
        self,
        table: QTableWidget,
        target_combo: QComboBox,
        release_combo: QComboBox,
        outcome_combo: QComboBox,
        range_combo: QComboBox,
        feedback: QLabel,
    ) -> None:
        self._table = table
        self._target = target_combo
        self._release = release_combo
        self._outcome = outcome_combo
        self._range = range_combo
        self._feedback = feedback

    def apply_full_state(self, state: DeploymentRolloutsViewState) -> None:
        if state.phase == "loading":
            self._feedback.setText("Rollouts werden geladen …")
            self._feedback.show()
            self._table.setRowCount(0)
            return
        if state.phase == "error":
            msg = state.error.message if state.error else "Unbekannter Fehler."
            self._feedback.setText(msg)
            self._feedback.show()
            self._table.setRowCount(0)
            return
        self._feedback.hide()
        self._apply_combos(state)
        self._apply_table(state)

    def _apply_combos(self, state: DeploymentRolloutsViewState) -> None:
        af = state.active_filter
        for cb in (self._target, self._release, self._outcome, self._range):
            cb.blockSignals(True)
        try:
            self._target.clear()
            for opt in state.target_options:
                self._target.addItem(opt.label, opt.value_id)
            for i in range(self._target.count()):
                if self._target.itemData(i) == af.target_id:
                    self._target.setCurrentIndex(i)
                    break
            self._release.clear()
            for opt in state.release_options:
                self._release.addItem(opt.label, opt.value_id)
            for i in range(self._release.count()):
                if self._release.itemData(i) == af.release_id:
                    self._release.setCurrentIndex(i)
                    break
            for i in range(self._outcome.count()):
                if self._outcome.itemData(i) == af.outcome:
                    self._outcome.setCurrentIndex(i)
                    break
            for i in range(self._range.count()):
                if self._range.itemData(i) == af.range_preset:
                    self._range.setCurrentIndex(i)
                    break
        finally:
            for cb in (self._target, self._release, self._outcome, self._range):
                cb.blockSignals(False)

    def _apply_table(self, state: DeploymentRolloutsViewState) -> None:
        self._table.setRowCount(0)
        for row_dto in state.table_rows:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(row_dto.recorded_at))
            self._table.setItem(row, 1, QTableWidgetItem(row_dto.target_display_name))
            self._table.setItem(row, 2, QTableWidgetItem(row_dto.release_display_name))
            self._table.setItem(row, 3, QTableWidgetItem(row_dto.version_label))
            self._table.setItem(row, 4, QTableWidgetItem(row_dto.outcome))
            self._table.setItem(row, 5, QTableWidgetItem(row_dto.workflow_run_id))
            self._table.setItem(row, 6, QTableWidgetItem(row_dto.message))
            run_it = self._table.item(row, 5)
            if run_it is not None:
                run_it.setData(Qt.ItemDataRole.UserRole, row_dto.workflow_run_id)

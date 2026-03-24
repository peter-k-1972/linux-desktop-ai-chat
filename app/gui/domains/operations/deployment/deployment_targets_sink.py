"""
DeploymentTargetsSink — Tabelle + Feedbackzeile aus :class:`DeploymentTargetsViewState`.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem

from app.ui_contracts.workspaces.deployment_targets import DeploymentTargetsViewState


class DeploymentTargetsSink:
    def __init__(self, table: QTableWidget, feedback: QLabel) -> None:
        self._table = table
        self._feedback = feedback

    def apply_full_state(self, state: DeploymentTargetsViewState) -> None:
        self._table.blockSignals(True)
        try:
            if state.phase == "loading":
                self._feedback.setText("Ziele werden geladen …")
                self._feedback.show()
                self._table.setRowCount(0)
                return
            if state.phase == "error":
                msg = state.error.message if state.error else "Unbekannter Fehler."
                self._feedback.setText(msg)
                self._feedback.show()
                self._table.setRowCount(0)
                return
            if state.banner_message:
                self._feedback.setText(state.banner_message.message)
                self._feedback.show()
            else:
                self._feedback.hide()
            self._table.setRowCount(0)
            for row_dto in state.rows:
                row = self._table.rowCount()
                self._table.insertRow(row)
                self._table.setItem(row, 0, QTableWidgetItem(row_dto.name))
                self._table.setItem(row, 1, QTableWidgetItem(row_dto.kind))
                self._table.setItem(
                    row,
                    2,
                    QTableWidgetItem(
                        "" if row_dto.project_id is None else str(row_dto.project_id),
                    ),
                )
                self._table.setItem(
                    row,
                    3,
                    QTableWidgetItem(row_dto.last_rollout_recorded_at),
                )
                self._table.setItem(
                    row,
                    4,
                    QTableWidgetItem(row_dto.last_rollout_outcome),
                )
                it = self._table.item(row, 0)
                if it is not None:
                    it.setData(Qt.ItemDataRole.UserRole, row_dto.target_id)
        finally:
            self._table.blockSignals(False)

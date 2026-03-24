"""
DeploymentReleasesSink — Release-Liste, Feedback, Detail und Historie aus :class:`DeploymentReleasesViewState`.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem

from app.ui_contracts.workspaces.deployment_releases import DeploymentReleasesViewState


class DeploymentReleasesSink:
    def __init__(
        self,
        list_table: QTableWidget,
        hist_table: QTableWidget,
        detail: QLabel,
        feedback: QLabel,
    ) -> None:
        self._list = list_table
        self._hist = hist_table
        self._detail = detail
        self._feedback = feedback

    def apply_full_state(self, state: DeploymentReleasesViewState) -> None:
        self._list.blockSignals(True)
        self._hist.blockSignals(True)
        try:
            if state.phase == "loading":
                self._feedback.setText("Releases werden geladen …")
                self._feedback.show()
                self._list.setRowCount(0)
                self._detail.setText("")
                self._hist.setRowCount(0)
                return
            if state.phase == "error":
                msg = state.error.message if state.error else "Unbekannter Fehler."
                self._feedback.setText(msg)
                self._feedback.show()
                self._list.setRowCount(0)
                self._detail.setText("")
                self._hist.setRowCount(0)
                return
            if state.banner_message:
                self._feedback.setText(state.banner_message.message)
                self._feedback.show()
            else:
                self._feedback.hide()
            self._list.setRowCount(0)
            for row_dto in state.rows:
                row = self._list.rowCount()
                self._list.insertRow(row)
                self._list.setItem(row, 0, QTableWidgetItem(row_dto.display_name))
                self._list.setItem(row, 1, QTableWidgetItem(row_dto.version_label))
                self._list.setItem(row, 2, QTableWidgetItem(row_dto.lifecycle_status))
                self._list.setItem(row, 3, QTableWidgetItem(row_dto.artifact_kind))
                self._list.setItem(
                    row,
                    4,
                    QTableWidgetItem(
                        "" if row_dto.project_id is None else str(row_dto.project_id),
                    ),
                )
                it = self._list.item(row, 0)
                if it is not None:
                    it.setData(Qt.ItemDataRole.UserRole, row_dto.release_id)
            self._apply_detail_and_history(state)
        finally:
            self._hist.blockSignals(False)
            self._list.blockSignals(False)

    def _apply_detail_and_history(self, state: DeploymentReleasesViewState) -> None:
        if state.detail is None:
            self._detail.setText("")
            self._hist.setRowCount(0)
            return
        d = state.detail
        ar = d.artifact_ref if d.artifact_ref else "—"
        ak = d.artifact_kind if d.artifact_kind else "—"
        self._detail.setText(
            f"<b>{d.display_name}</b> {d.version_label}<br/>"
            f"Lifecycle: {d.lifecycle_status}<br/>"
            f"Referenz: {ar}<br/>"
            f"Art: {ak}",
        )
        self._hist.setRowCount(0)
        for hr in state.history_rows:
            row = self._hist.rowCount()
            self._hist.insertRow(row)
            self._hist.setItem(row, 0, QTableWidgetItem(hr.recorded_at))
            self._hist.setItem(row, 1, QTableWidgetItem(hr.target_display_name))
            self._hist.setItem(row, 2, QTableWidgetItem(hr.outcome))
            self._hist.setItem(row, 3, QTableWidgetItem(hr.workflow_run_id))
            self._hist.setItem(row, 4, QTableWidgetItem(hr.message))
            if hr.workflow_run_id:
                w_it = self._hist.item(row, 3)
                if w_it is not None:
                    w_it.setData(Qt.ItemDataRole.UserRole, hr.workflow_run_id)

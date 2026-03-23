"""Linke Liste der gespeicherten Workflows."""

from __future__ import annotations

from typing import Callable, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
)

from app.workflows.models.definition import WorkflowDefinition


class WorkflowListPanel(QFrame):
    """Tabelle + Aktionen für Workflow-Auswahl."""

    selection_workflow_id_changed = Signal(object)  # Optional[str]
    refresh_requested = Signal()
    new_requested = Signal()
    delete_requested = Signal()
    duplicate_requested = Signal()

    # Spalten: Name, Projekt, workflow_id, Version, Status, Aktualisiert
    _COL_WID = 2

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("workflowListPanel")
        self._table = QTableWidget(0, 6)
        self._table.setHorizontalHeaderLabels(
            ["Name", "Projekt", "workflow_id", "Version", "Status", "Aktualisiert"]
        )
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.itemSelectionChanged.connect(self._emit_selection)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        title = QLabel("Gespeicherte Workflows")
        title.setObjectName("domainNavTitle")
        layout.addWidget(title)
        self._filter_hint = QLabel("")
        self._filter_hint.setObjectName("workflowListFilterHint")
        self._filter_hint.setWordWrap(True)
        self._filter_hint.hide()
        layout.addWidget(self._filter_hint)
        self._empty_hint = QLabel(
            "Noch keine Definitionen in der Datenbank. „Neu“ legt einen Workflow "
            "mit Start- und End-Knoten an."
        )
        self._empty_hint.setObjectName("workflowListEmptyHint")
        self._empty_hint.setWordWrap(True)
        layout.addWidget(self._empty_hint)

        btn_row = QHBoxLayout()
        self._btn_new = QPushButton("Neu")
        self._btn_new.clicked.connect(self.new_requested.emit)
        self._btn_refresh = QPushButton("Aktualisieren")
        self._btn_refresh.clicked.connect(self.refresh_requested.emit)
        self._btn_dup = QPushButton("Duplizieren")
        self._btn_dup.clicked.connect(self.duplicate_requested.emit)
        self._btn_del = QPushButton("Löschen")
        self._btn_del.clicked.connect(self.delete_requested.emit)
        for b in (self._btn_new, self._btn_refresh, self._btn_dup, self._btn_del):
            btn_row.addWidget(b)
        btn_row.addStretch()
        layout.addLayout(btn_row)
        layout.addWidget(self._table, 1)

    def set_filter_hint(self, text: str) -> None:
        t = (text or "").strip()
        self._filter_hint.setText(t)
        self._filter_hint.setVisible(bool(t))

    def _emit_selection(self) -> None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            self.selection_workflow_id_changed.emit(None)
            return
        row = rows[0].row()
        item = self._table.item(row, self._COL_WID)
        wid = item.data(Qt.ItemDataRole.UserRole) if item else None
        self.selection_workflow_id_changed.emit(wid)

    def set_workflows(
        self,
        items: list[WorkflowDefinition],
        *,
        project_label: Optional[Callable[[Optional[int]], str]] = None,
        reselect_id: str | None = None,
    ) -> None:
        self._table.blockSignals(True)
        self._table.setRowCount(0)
        label_fn = project_label or (lambda _pid: "—")
        for w in items:
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setItem(r, 0, QTableWidgetItem(w.name))
            self._table.setItem(r, 1, QTableWidgetItem(label_fn(w.project_id)))
            id_item = QTableWidgetItem(w.workflow_id)
            id_item.setData(Qt.ItemDataRole.UserRole, w.workflow_id)
            self._table.setItem(r, 2, id_item)
            self._table.setItem(r, 3, QTableWidgetItem(str(w.version)))
            self._table.setItem(r, 4, QTableWidgetItem(w.status.value))
            upd = w.updated_at.isoformat() if w.updated_at else ""
            self._table.setItem(r, 5, QTableWidgetItem(upd))
        self._table.resizeColumnsToContents()
        self._table.blockSignals(False)
        self._empty_hint.setVisible(len(items) == 0)
        if reselect_id:
            self.select_workflow_id(reselect_id)

    def select_workflow_id(self, workflow_id: str) -> None:
        self._table.blockSignals(True)
        for r in range(self._table.rowCount()):
            item = self._table.item(r, self._COL_WID)
            if item and item.data(Qt.ItemDataRole.UserRole) == workflow_id:
                self._table.selectRow(r)
                self._table.blockSignals(False)
                return
        self._table.blockSignals(False)

    def current_workflow_id(self) -> str | None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            return None
        item = self._table.item(rows[0].row(), self._COL_WID)
        return item.data(Qt.ItemDataRole.UserRole) if item else None

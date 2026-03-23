"""Incidents: Liste, Detail, Status, Sprung zum Workflow-Run (R1)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.core.audit.models import IncidentRecord, IncidentStatus


class IncidentsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._selected: IncidentRecord | None = None

        self._table = QTableWidget()
        self._table.setColumnCount(7)
        self._table.setHorizontalHeaderLabels(
            ["Zuletzt", "Status", "Schwere", "Titel", "Workflow", "Run", "Anz."]
        )
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.itemSelectionChanged.connect(self._on_sel)

        self._status_filter = QComboBox()
        self._status_filter.addItem("Alle Stati", None)
        for s in (
            IncidentStatus.OPEN,
            IncidentStatus.ACKNOWLEDGED,
            IncidentStatus.RESOLVED,
            IncidentStatus.IGNORED,
        ):
            self._status_filter.addItem(s, s)

        refresh = QPushButton("Aktualisieren")
        refresh.clicked.connect(self.refresh)
        filt_bar = QHBoxLayout()
        filt_bar.addWidget(QLabel("Statusfilter:"))
        filt_bar.addWidget(self._status_filter, 1)
        filt_bar.addWidget(refresh)

        self._detail_title = QLabel("—")
        self._detail_body = QTextEdit()
        self._detail_body.setReadOnly(True)
        self._detail_body.setMaximumHeight(120)

        self._status_apply = QComboBox()
        for s in (
            IncidentStatus.OPEN,
            IncidentStatus.ACKNOWLEDGED,
            IncidentStatus.RESOLVED,
            IncidentStatus.IGNORED,
        ):
            self._status_apply.addItem(s, s)
        self._note = QLineEdit()
        self._note.setPlaceholderText("Optional: Hinweis zur Erledigung …")
        btn_apply = QPushButton("Status setzen")
        btn_apply.clicked.connect(self._apply_status)
        btn_run = QPushButton("Zum Run …")
        btn_run.clicked.connect(self._goto_run)

        form = QFormLayout()
        form.addRow("Neuer Status:", self._status_apply)
        form.addRow("Notiz:", self._note)
        actions = QHBoxLayout()
        actions.addWidget(btn_apply)
        actions.addWidget(btn_run)
        form.addRow(actions)

        detail_box = QGroupBox("Detail")
        dv = QVBoxLayout(detail_box)
        dv.addWidget(self._detail_title)
        dv.addWidget(self._detail_body)
        dv.addLayout(form)

        left = QWidget()
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.addLayout(filt_bar)
        lv.addWidget(self._table, 1)

        split = QSplitter()
        split.addWidget(left)
        split.addWidget(detail_box)
        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 1)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addWidget(split, 1)

    def refresh(self) -> None:
        from app.services.incident_service import get_incident_service

        st = self._status_filter.currentData()
        rows = get_incident_service().list_incidents(status=st, limit=800)
        self._table.setRowCount(0)
        self._selected = None
        self._clear_detail()
        for inc in rows:
            r = self._table.rowCount()
            self._table.insertRow(r)
            self._table.setItem(r, 0, QTableWidgetItem(inc.last_seen_at))
            self._table.setItem(r, 1, QTableWidgetItem(inc.status))
            self._table.setItem(r, 2, QTableWidgetItem(inc.severity))
            self._table.setItem(r, 3, QTableWidgetItem(inc.title))
            self._table.setItem(r, 4, QTableWidgetItem(inc.workflow_id))
            self._table.setItem(r, 5, QTableWidgetItem(inc.workflow_run_id))
            self._table.setItem(r, 6, QTableWidgetItem(str(inc.occurrence_count)))
            id_item = self._table.item(r, 0)
            if id_item:
                id_item.setData(Qt.ItemDataRole.UserRole, inc.id)
        self._table.resizeColumnsToContents()

    def _clear_detail(self) -> None:
        self._detail_title.setText("—")
        self._detail_body.clear()

    def _on_sel(self) -> None:
        rows = self._table.selectionModel().selectedRows()
        if not rows:
            self._selected = None
            self._clear_detail()
            return
        row = rows[0].row()
        it = self._table.item(row, 0)
        iid = it.data(Qt.ItemDataRole.UserRole) if it else None
        if iid is None:
            return
        from app.services.incident_service import get_incident_service

        inc = get_incident_service().get_incident(int(iid))
        self._selected = inc
        if not inc:
            return
        self._detail_title.setText(f"#{inc.id} — {inc.title}")
        parts = [
            inc.short_description,
            "",
            f"Fingerprint: {inc.fingerprint}",
        ]
        if inc.diagnostic_code:
            parts.append(f"Diagnosecode: {inc.diagnostic_code}")
        if inc.resolution_note:
            parts.append(f"Notiz: {inc.resolution_note}")
        self._detail_body.setPlainText("\n".join(parts))

    def _apply_status(self) -> None:
        if not self._selected:
            QMessageBox.information(self, "Incidents", "Bitte einen Eintrag wählen.")
            return
        inc_id = self._selected.id
        new_st = self._status_apply.currentData()
        note = self._note.text().strip() or None
        try:
            from app.services.incident_service import get_incident_service

            get_incident_service().set_status(inc_id, new_st, resolution_note=note)
        except Exception as e:
            QMessageBox.warning(self, "Incidents", str(e))
            return
        self.refresh()

    def _goto_run(self) -> None:
        if not self._selected:
            QMessageBox.information(self, "Incidents", "Bitte einen Eintrag wählen.")
            return
        try:
            from app.gui.domains.operations.operations_context import set_pending_context

            set_pending_context(
                {
                    "workflow_ops_run_id": self._selected.workflow_run_id,
                    "workflow_ops_workflow_id": self._selected.workflow_id,
                }
            )
        except Exception:
            pass
        host = self._find_workspace_host()
        if host:
            from app.gui.navigation.nav_areas import NavArea

            host.show_area(NavArea.OPERATIONS, "operations_workflows")

    def _find_workspace_host(self):
        p = self
        while p:
            if hasattr(p, "show_area") and hasattr(p, "_area_to_index"):
                return p
            p = p.parent() if hasattr(p, "parent") else None
        return None

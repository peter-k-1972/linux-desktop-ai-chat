"""Audit-Aktivität: Liste und Filter (R1)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.core.audit.models import AuditEventType


class AuditActivityPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._table = QTableWidget()
        self._table.setColumnCount(6)
        self._table.setHorizontalHeaderLabels(
            ["Zeit", "Typ", "Zusammenfassung", "Projekt", "Workflow", "Run"]
        )
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self._type_combo = QComboBox()
        self._type_combo.addItem("Alle Typen", None)
        for label, val in (
            ("Workflow gestartet", AuditEventType.WORKFLOW_STARTED),
            ("Workflow Re-Run", AuditEventType.WORKFLOW_RERUN_STARTED),
            ("Projekt erstellt", AuditEventType.PROJECT_CREATED),
            ("Projekt bearbeitet", AuditEventType.PROJECT_UPDATED),
            ("Projekt gelöscht", AuditEventType.PROJECT_DELETED),
            ("Incident erstellt", AuditEventType.INCIDENT_CREATED),
            ("Incident-Status", AuditEventType.INCIDENT_STATUS_CHANGED),
            ("Deployment-Ziel", AuditEventType.DEPLOYMENT_TARGET_MUTATED),
            ("Deployment-Release", AuditEventType.DEPLOYMENT_RELEASE_MUTATED),
            ("Deployment-Rollout", AuditEventType.DEPLOYMENT_ROLLOUT_RECORDED),
        ):
            self._type_combo.addItem(label, val)

        refresh = QPushButton("Aktualisieren")
        refresh.clicked.connect(self.refresh)

        bar = QHBoxLayout()
        bar.addWidget(QLabel("Ereignistyp:"))
        bar.addWidget(self._type_combo, 1)
        bar.addWidget(refresh)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addLayout(bar)
        root.addWidget(self._table, 1)

    def refresh(self) -> None:
        from app.services.audit_service import get_audit_service

        et = self._type_combo.currentData()
        events = get_audit_service().list_events(event_type=et, limit=800)
        self._table.setRowCount(0)
        for ev in events:
            row = self._table.rowCount()
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(ev.occurred_at))
            self._table.setItem(row, 1, QTableWidgetItem(ev.event_type))
            self._table.setItem(row, 2, QTableWidgetItem(ev.summary))
            self._table.setItem(
                row, 3, QTableWidgetItem("" if ev.project_id is None else str(ev.project_id))
            )
            self._table.setItem(row, 4, QTableWidgetItem(ev.workflow_id or ""))
            self._table.setItem(row, 5, QTableWidgetItem(ev.run_id or ""))
        self._table.resizeColumnsToContents()

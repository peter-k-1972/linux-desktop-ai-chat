"""
Incidents Panels – Incident List, Severity, Status, Timeline.
Nutzt QAGovernanceService für reale Daten aus docs/qa/incidents/.
"""

from __future__ import annotations

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
)
from PySide6.QtCore import Signal

from app.services.qa_governance_service import (
    get_qa_governance_service,
    IncidentEntry,
)


def _qa_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class IncidentListPanel(QFrame):
    """Incident List – reale Daten aus incidents/index.json."""

    incident_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("incidentListPanel")
        self.setMinimumHeight(200)
        self._service = get_qa_governance_service()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setStyleSheet(_qa_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Incident List")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Incident ID", "Severity", "Status", "Datum", "Failure Class"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setStyleSheet(
            "QTableWidget { background: #fafafa; border: none; gridline-color: #e2e8f0; }"
        )
        self._table.cellClicked.connect(self._on_cell_clicked)
        layout.addWidget(self._table)

    def _load_data(self):
        try:
            incidents = self._service.list_incidents()
            self._incidents = incidents
            self._table.setRowCount(len(incidents))
            for row, i in enumerate(incidents):
                self._table.setItem(row, 0, QTableWidgetItem(i.incident_id))
                self._table.setItem(row, 1, QTableWidgetItem(i.severity))
                self._table.setItem(row, 2, QTableWidgetItem(i.status))
                self._table.setItem(row, 3, QTableWidgetItem(i.detected_at[:10] if len(i.detected_at) >= 10 else i.detected_at))
                self._table.setItem(row, 4, QTableWidgetItem(i.failure_class or "—"))
            if not incidents:
                self._table.setRowCount(1)
                self._table.setItem(0, 0, QTableWidgetItem("Keine Incidents. docs/qa/incidents/index.json prüfen."))
                self._incidents = []
        except Exception as e:
            self._table.setRowCount(1)
            self._table.setItem(0, 0, QTableWidgetItem(f"Fehler beim Laden: {e}"))
            self._incidents = []

    def _on_cell_clicked(self, row: int, _col: int):
        if 0 <= row < len(getattr(self, "_incidents", [])):
            self.incident_selected.emit(self._incidents[row])


class IncidentSummaryPanel(QFrame):
    """Severity / Status – Metriken."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("incidentSummaryPanel")
        self.setMinimumHeight(100)
        self._service = get_qa_governance_service()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setStyleSheet(_qa_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Incident Summary")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._row = QHBoxLayout()
        layout.addLayout(self._row)

    def _load_data(self):
        while self._row.count():
            w = self._row.takeAt(0).widget()
            if w:
                w.deleteLater()
        try:
            summary = self._service.get_incident_summary()
            metrics = summary.get("metrics") or {}
            count = summary.get("incident_count", 0)
            open_ = metrics.get("open_incidents", 0)
            replay_def = metrics.get("replay_defined", 0)
            items = [
                ("Total", str(count), "#334155"),
                ("Offen", str(open_), "#ef4444" if open_ > 0 else "#10b981"),
                ("Replay definiert", str(replay_def), "#10b981"),
            ]
            for label, value, color in items:
                box = QFrame()
                box.setStyleSheet("background: #f8fafc; border-radius: 6px; padding: 8px;")
                bl = QVBoxLayout(box)
                bl.setContentsMargins(12, 8, 12, 8)
                lbl = QLabel(label)
                lbl.setStyleSheet("color: #64748b; font-size: 11px;")
                val = QLabel(value)
                val.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 16px;")
                bl.addWidget(lbl)
                bl.addWidget(val)
                self._row.addWidget(box)
        except Exception:
            lbl = QLabel("Keine Daten. docs/qa/incidents/index.json prüfen.")
            lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
            self._row.addWidget(lbl)


class IncidentDetailPanel(QFrame):
    """Details zum ausgewählten Incident."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("incidentDetailPanel")
        self.setMinimumHeight(100)
        self._setup_ui()
        self.set_incident(None)

    def _setup_ui(self):
        self.setStyleSheet(
            "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
            "min-height: 100px; padding: 16px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        self._title = QLabel("Incident Details")
        self._title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(self._title)
        self._content = QLabel("Wählen Sie einen Incident aus der Liste.")
        self._content.setStyleSheet("color: #64748b; font-size: 12px;")
        self._content.setWordWrap(True)
        layout.addWidget(self._content)

    def set_incident(self, incident: IncidentEntry | None) -> None:
        if not incident:
            self._content.setText("Wählen Sie einen Incident aus der Liste.")
            return
        lines = [
            f"ID: {incident.incident_id}",
            f"Titel: {incident.title}",
            f"Status: {incident.status} · Severity: {incident.severity}",
            f"Subsystem: {incident.subsystem} · Failure Class: {incident.failure_class}",
            f"Detected: {incident.detected_at}",
        ]
        if incident.replay_status:
            lines.append(f"Replay Status: {incident.replay_status}")
        self._content.setText("\n".join(lines))

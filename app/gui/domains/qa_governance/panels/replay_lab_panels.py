"""
Replay Lab Panels – Replay Cases, Status, letzte Runs.
Nutzt QAGovernanceService für reale Daten (Incidents + Coverage).
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
    ReplayEntry,
)


def _qa_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class ReplayListPanel(QFrame):
    """Replay Cases – aus Incidents und Coverage."""

    replay_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("replayListPanel")
        self.setMinimumHeight(200)
        self._service = get_qa_governance_service()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setStyleSheet(_qa_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Replay Cases / Replay-Artefakte")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Replay ID", "Incident", "Status", "Quelle"])
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
            replays = self._service.list_replays()
            self._replays = replays
            self._table.setRowCount(len(replays))
            for row, r in enumerate(replays):
                self._table.setItem(row, 0, QTableWidgetItem(r.id))
                self._table.setItem(row, 1, QTableWidgetItem(r.incident_id or "—"))
                self._table.setItem(row, 2, QTableWidgetItem(r.status or "—"))
                src = "Incident" if r.incident_id else "Coverage"
                self._table.setItem(row, 3, QTableWidgetItem(src))
            if not replays:
                self._table.setRowCount(1)
                self._table.setItem(0, 0, QTableWidgetItem("Keine Replay-Artefakte. Incidents/Coverage prüfen."))
                self._replays = []
        except Exception as e:
            self._table.setRowCount(1)
            self._table.setItem(0, 0, QTableWidgetItem(f"Fehler: {e}"))
            self._replays = []

    def _on_cell_clicked(self, row: int, _col: int):
        if 0 <= row < len(getattr(self, "_replays", [])):
            self.replay_selected.emit(self._replays[row])


class ReplaySummaryPanel(QFrame):
    """Replay Status / Anzahl."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("replaySummaryPanel")
        self.setMinimumHeight(100)
        self._service = get_qa_governance_service()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setStyleSheet(_qa_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Replay Summary")
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
            replays = self._service.list_replays()
            count = len(replays)
            from_inc = sum(1 for r in replays if r.incident_id)
            items = [
                ("Anzahl Replays", str(count), "#334155"),
                ("Verknüpft mit Incidents", str(from_inc), "#10b981"),
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
            lbl = QLabel("Keine Daten.")
            lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
            self._row.addWidget(lbl)


class ReplayDetailPanel(QFrame):
    """Details zum ausgewählten Replay."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("replayDetailPanel")
        self.setMinimumHeight(100)
        self._setup_ui()
        self.set_replay(None)

    def _setup_ui(self):
        self.setStyleSheet(
            "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
            "min-height: 100px; padding: 16px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        self._title = QLabel("Replay Details")
        self._title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(self._title)
        self._content = QLabel("Wählen Sie einen Replay aus der Liste.")
        self._content.setStyleSheet("color: #64748b; font-size: 12px;")
        self._content.setWordWrap(True)
        layout.addWidget(self._content)

    def set_replay(self, replay: ReplayEntry | None) -> None:
        if not replay:
            self._content.setText("Wählen Sie einen Replay aus der Liste.")
            return
        lines = [
            f"ID: {replay.id}",
            f"Incident: {replay.incident_id or '—'}",
            f"Status: {replay.status}",
        ]
        self._content.setText("\n".join(lines))

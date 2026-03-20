"""
Gap Analysis Panels – Gap Summary, Priorität, Review Candidates.
Nutzt QAGovernanceService für reale Daten aus PHASE3_GAP_REPORT.json.
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
    GapEntry,
)


def _qa_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class GapListPanel(QFrame):
    """Gap-Einträge – priorisierte Gaps oder Orphan-Übersicht."""

    gap_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("gapListPanel")
        self.setMinimumHeight(200)
        self._service = get_qa_governance_service()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setStyleSheet(_qa_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Gap List / Priorisierte Gaps")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["ID", "Typ", "Severity", "Subsystem", "Titel"])
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
            gaps = self._service.list_gaps()
            self._gaps = gaps
            self._table.setRowCount(len(gaps))
            for row, g in enumerate(gaps):
                self._table.setItem(row, 0, QTableWidgetItem(g.id))
                self._table.setItem(row, 1, QTableWidgetItem(g.gap_type or "—"))
                self._table.setItem(row, 2, QTableWidgetItem(g.severity or "—"))
                self._table.setItem(row, 3, QTableWidgetItem(g.subsystem or "—"))
                self._table.setItem(row, 4, QTableWidgetItem((g.title or "—")[:60]))
            if not gaps:
                self._table.setRowCount(1)
                self._table.setItem(0, 0, QTableWidgetItem("Keine priorisierten Gaps. Orphan-Backlog siehe Summary."))
                self._gaps = []
        except Exception as e:
            self._table.setRowCount(1)
            self._table.setItem(0, 0, QTableWidgetItem(f"Fehler: {e}"))
            self._gaps = []

    def _on_cell_clicked(self, row: int, _col: int):
        if 0 <= row < len(getattr(self, "_gaps", [])):
            self.gap_selected.emit(self._gaps[row])


class GapSummaryPanel(QFrame):
    """Gap Summary – Orphan Count, Priorisierte, Gap-Typen."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("gapSummaryPanel")
        self.setMinimumHeight(120)
        self._service = get_qa_governance_service()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setStyleSheet(_qa_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Gap Summary")
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
            summary = self._service.get_gap_summary()
            orphan = summary.get("orphan_count", 0)
            prio = summary.get("prioritized_count", 0)
            breakdown = summary.get("orphan_breakdown") or {}
            review = breakdown.get("review_candidates", 0)
            whitelisted = breakdown.get("whitelisted", 0)
            items = [
                ("Orphan Backlog", str(orphan), "#f59e0b" if orphan > 0 else "#10b981"),
                ("Review Candidates", str(review), "#f59e0b" if review > 0 else "#10b981"),
                ("Whitelisted", str(whitelisted), "#10b981"),
                ("Priorisierte Gaps", str(prio), "#ef4444" if prio > 0 else "#10b981"),
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
            lbl = QLabel("Keine Daten. PHASE3_GAP_REPORT.json prüfen.")
            lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
            self._row.addWidget(lbl)


class GapDetailPanel(QFrame):
    """Details zum ausgewählten Gap."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("gapDetailPanel")
        self.setMinimumHeight(100)
        self._setup_ui()
        self.set_gap(None)

    def _setup_ui(self):
        self.setStyleSheet(
            "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
            "min-height: 100px; padding: 16px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        self._title = QLabel("Gap Details")
        self._title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(self._title)
        self._content = QLabel("Wählen Sie einen Gap aus der Liste.")
        self._content.setStyleSheet("color: #64748b; font-size: 12px;")
        self._content.setWordWrap(True)
        layout.addWidget(self._content)

    def set_gap(self, gap: GapEntry | None) -> None:
        if not gap:
            self._content.setText("Wählen Sie einen Gap aus der Liste.")
            return
        lines = [
            f"ID: {gap.id}",
            f"Titel: {gap.title}",
            f"Typ: {gap.gap_type} · Severity: {gap.severity}",
            f"Subsystem: {gap.subsystem}",
        ]
        self._content.setText("\n".join(lines))

"""
Coverage Map Panels – Coverage Overview, Failure Classes, Guards, Regression.
Nutzt QAGovernanceService für reale Daten.
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
    QComboBox,
    QAbstractItemView,
)
from PySide6.QtCore import Signal

from app.services.qa_governance_service import (
    get_qa_governance_service,
    CoverageEntry,
)


def _qa_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class CoverageOverviewPanel(QFrame):
    """Coverage Overview – Failure Classes, Guards, Regression Requirements."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("coverageOverviewPanel")
        self.setMinimumHeight(120)
        self._service = get_qa_governance_service()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setStyleSheet(_qa_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Coverage Overview")
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
            summary = self._service.get_coverage_summary()
            strength = summary.get("coverage_strength") or {}
            gap_types = summary.get("gap_types") or {}
            items = []
            gap_keys = {
                "failure_class": "failure_class_uncovered",
                "guard": "guard_missing",
                "regression_requirement": "regression_requirement_unbound",
                "replay_binding": "replay_unbound",
            }
            for ax in ["failure_class", "guard", "regression_requirement", "replay_binding"]:
                s = strength.get(ax, "unknown")
                g = gap_types.get(gap_keys.get(ax, ""), 0)
                color = "#10b981" if s == "covered" else "#f59e0b" if s == "partial" else "#94a3b8"
                label = ax.replace("_", " ").title()
                items.append((label, s, str(g), color))
            for label, strength_val, gap_val, color in items:
                box = QFrame()
                box.setStyleSheet("background: #f8fafc; border-radius: 6px; padding: 8px;")
                bl = QVBoxLayout(box)
                bl.setContentsMargins(12, 8, 12, 8)
                lbl = QLabel(label)
                lbl.setStyleSheet("color: #64748b; font-size: 11px;")
                val = QLabel(f"{strength_val} · Gaps: {gap_val}")
                val.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 14px;")
                bl.addWidget(lbl)
                bl.addWidget(val)
                self._row.addWidget(box)
        except Exception:
            lbl = QLabel("Keine Daten. QA_COVERAGE_MAP.json prüfen.")
            lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
            self._row.addWidget(lbl)


class CoverageListPanel(QFrame):
    """Coverage-Einträge (Failure Class, Guard, etc.)."""

    entry_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("coverageListPanel")
        self.setMinimumHeight(200)
        self._service = get_qa_governance_service()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setStyleSheet(_qa_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Coverage Map / Mapping")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        self._axis_combo = QComboBox()
        self._axis_combo.addItems([
            "failure_class",
            "guard",
            "regression_requirement",
            "replay_binding",
        ])
        self._axis_combo.setStyleSheet(
            "padding: 6px 10px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 12px;"
        )
        self._axis_combo.currentTextChanged.connect(self._load_data)
        layout.addWidget(self._axis_combo)

        self._table = QTableWidget()
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(["Key", "Axis", "Strength", "Test Count"])
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
            axis = self._axis_combo.currentText() or ""
            entries = self._service.get_coverage_entries(axis=axis)
            self._entries = entries
            self._table.setRowCount(len(entries))
            for row, e in enumerate(entries):
                self._table.setItem(row, 0, QTableWidgetItem(e.key[:50] + "…" if len(e.key) > 50 else e.key))
                self._table.setItem(row, 1, QTableWidgetItem(e.axis))
                self._table.setItem(row, 2, QTableWidgetItem(e.strength))
                self._table.setItem(row, 3, QTableWidgetItem(str(e.test_count)))
            if not entries:
                self._table.setRowCount(1)
                self._table.setItem(0, 0, QTableWidgetItem("Keine Einträge für diese Achse."))
                self._entries = []
        except Exception as e:
            self._table.setRowCount(1)
            self._table.setItem(0, 0, QTableWidgetItem(f"Fehler: {e}"))
            self._entries = []

    def _on_cell_clicked(self, row: int, _col: int):
        if 0 <= row < len(getattr(self, "_entries", [])):
            self.entry_selected.emit(self._entries[row])


class CoverageDetailPanel(QFrame):
    """Details zum ausgewählten Coverage-Eintrag."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("coverageDetailPanel")
        self.setMinimumHeight(100)
        self._setup_ui()
        self.set_entry(None)

    def _setup_ui(self):
        self.setStyleSheet(
            "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
            "min-height: 100px; padding: 16px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        self._title = QLabel("Details")
        self._title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(self._title)
        self._content = QLabel("Wählen Sie einen Eintrag aus der Liste.")
        self._content.setStyleSheet("color: #64748b; font-size: 12px;")
        self._content.setWordWrap(True)
        layout.addWidget(self._content)

    def set_entry(self, entry: CoverageEntry | None) -> None:
        if not entry:
            self._content.setText("Wählen Sie einen Eintrag aus der Liste.")
            return
        lines = [
            f"Key: {entry.key}",
            f"Axis: {entry.axis}",
            f"Strength: {entry.strength}",
            f"Test Count: {entry.test_count}",
        ]
        if entry.test_ids:
            sample = entry.test_ids[:5]
            lines.append(f"Test IDs (Auszug): {', '.join((s[:40] + '…') if len(s) > 40 else s for s in sample)}")
        self._content.setText("\n".join(lines))

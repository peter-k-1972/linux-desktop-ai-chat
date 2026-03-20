"""
Test Inventory Panels – Test List, Kategorien, Status, Summary, Details.
Nutzt QAGovernanceService für reale Daten.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QLineEdit,
    QComboBox,
    QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal

from app.services.qa_governance_service import (
    get_qa_governance_service,
    TestEntry,
)


def _qa_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class TestListPanel(QFrame):
    """Test List / Test Browser – reale Daten aus QA_TEST_INVENTORY.json."""

    test_selected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("testListPanel")
        self.setMinimumHeight(200)
        self._service = get_qa_governance_service()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setStyleSheet(_qa_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Test List / Test Browser")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        row = QHBoxLayout()
        self._subsystem_combo = QComboBox()
        self._subsystem_combo.addItem("(alle Subsysteme)", "")
        self._subsystem_combo.setStyleSheet(
            "padding: 6px 10px; border: 1px solid #e2e8f0; border-radius: 6px; font-size: 12px;"
        )
        self._subsystem_combo.currentIndexChanged.connect(self._on_filter_changed)
        row.addWidget(self._subsystem_combo)

        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter / Suche (Testname, Pfad)...")
        self._search.setStyleSheet(
            "padding: 8px 12px; border: 1px solid #e2e8f0; border-radius: 6px; "
            "background: #fafafa; font-size: 12px;"
        )
        self._search.textChanged.connect(self._on_filter_changed)
        row.addWidget(self._search, 1)
        layout.addLayout(row)

        self._table = QTableWidget()
        self._table.setColumnCount(5)
        self._table.setHorizontalHeaderLabels(["Test ID", "Subsystem", "Test Domain", "Test Type", "Failure Classes"])
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
            summary = self._service.get_test_summary()
            subsystems = sorted((summary.get("by_subsystem") or {}).keys())
            self._subsystem_combo.clear()
            self._subsystem_combo.addItem("(alle Subsysteme)", "")
            for s in subsystems:
                if s and s != "unknown":
                    self._subsystem_combo.addItem(s, s)
            self._subsystem_combo.addItem("unknown", "unknown")

            sub_filter = self._subsystem_combo.currentData() or ""
            text_filter = self._search.text().strip()
            tests = self._service.list_tests(
                subsystem_filter=sub_filter,
                text_filter=text_filter,
                limit=300,
            )
            self._tests = tests
            self._table.setRowCount(len(tests))
            for row, t in enumerate(tests):
                self._table.setItem(row, 0, QTableWidgetItem(t.id[:60] + "…" if len(t.id) > 60 else t.id))
                self._table.setItem(row, 1, QTableWidgetItem(t.subsystem))
                self._table.setItem(row, 2, QTableWidgetItem(t.test_domain))
                self._table.setItem(row, 3, QTableWidgetItem(t.test_type))
                self._table.setItem(row, 4, QTableWidgetItem(", ".join(t.failure_classes[:3]) or "—"))
            if not tests:
                self._table.setRowCount(1)
                self._table.setItem(0, 0, QTableWidgetItem("Keine Tests gefunden. QA_TEST_INVENTORY.json prüfen."))
        except Exception as e:
            self._table.setRowCount(1)
            self._table.setItem(0, 0, QTableWidgetItem(f"Fehler beim Laden: {e}"))
            self._tests = []

    def _on_filter_changed(self):
        self._load_data()

    def _on_cell_clicked(self, row: int, _col: int):
        if 0 <= row < len(getattr(self, "_tests", [])):
            t = self._tests[row]
            self.test_selected.emit(t)


class TestSummaryPanel(QFrame):
    """Kategorien / Status / Test Summary – reale Daten."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("testSummaryPanel")
        self.setMinimumHeight(100)
        self._service = get_qa_governance_service()
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setStyleSheet(_qa_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Test Summary")
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
            summary = self._service.get_test_summary()
            total = summary.get("test_count", 0)
            by_sub = summary.get("by_subsystem") or {}
            top_subs = sorted(by_sub.items(), key=lambda x: -x[1])[:5]
            items = [(f"{k[:12]}…" if len(k) > 12 else k, str(v), "#10b981") for k, v in top_subs]
            items.append(("Total", str(total), "#334155"))
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
            lbl = QLabel("Keine Daten. QA_TEST_INVENTORY.json prüfen.")
            lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
            self._row.addWidget(lbl)


class TestDetailPanel(QFrame):
    """Detaildarstellung des ausgewählten Tests."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("testDetailPanel")
        self.setMinimumHeight(100)
        self._setup_ui()
        self.set_test(None)

    def _setup_ui(self):
        self.setStyleSheet(
            "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
            "min-height: 100px; padding: 16px;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        self._title = QLabel("Details / Metadata")
        self._title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(self._title)
        self._content = QLabel("Wählen Sie einen Test aus der Liste.")
        self._content.setStyleSheet("color: #64748b; font-size: 12px;")
        self._content.setWordWrap(True)
        layout.addWidget(self._content)

    def set_test(self, test: "TestEntry | None"):
        if not test:
            self._content.setText("Wählen Sie einen Test aus der Liste.")
            return
        lines = [
            f"ID: {test.id}",
            f"Pfad: {test.file_path}",
            f"Test: {test.test_name}",
            f"Subsystem: {test.subsystem} · Domain: {test.test_domain} · Type: {test.test_type}",
        ]
        if test.failure_classes:
            lines.append(f"Failure Classes: {', '.join(test.failure_classes)}")
        if test.guard_types:
            lines.append(f"Guard Types: {', '.join(test.guard_types)}")
        if test.replay_ids:
            lines.append(f"Replay IDs: {', '.join(test.replay_ids)}")
        if test.covers_regression:
            lines.append("Covers Regression: ja")
        self._content.setText("\n".join(lines))

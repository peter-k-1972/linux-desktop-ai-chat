"""
Data Stores Panels – SQLite, ChromaDB, File, Connection, State.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
)
from PySide6.QtCore import Qt


def _cc_panel_style() -> str:
    return (
        "background: white; border: 1px solid #e2e8f0; border-radius: 10px; "
        "padding: 12px;"
    )


class DataStoreOverviewPanel(QFrame):
    """SQLite, ChromaDB, File / Storage Overview."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dataStoreOverviewPanel")
        self.setMinimumHeight(180)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Data Stores Overview")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        demo_label = QLabel("Vorschau (Stores bei Verbindung)")
        demo_label.setStyleSheet("font-size: 11px; color: #94a3b8; margin-bottom: 4px;")
        layout.addWidget(demo_label)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Store", "Type", "Connection", "State"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setRowCount(3)
        table.setStyleSheet(
            "QTableWidget { background: #fafafa; border: none; gridline-color: #e2e8f0; }"
        )

        dummy_data = [
            ("Sessions DB", "SQLite", "local", "Connected"),
            ("Vector Store", "ChromaDB", "local", "Connected"),
            ("File Storage", "File", "local", "Available"),
        ]
        for row, (store, typ, conn, state) in enumerate(dummy_data):
            table.setItem(row, 0, QTableWidgetItem(store))
            table.setItem(row, 1, QTableWidgetItem(typ))
            table.setItem(row, 2, QTableWidgetItem(conn))
            table.setItem(row, 3, QTableWidgetItem(state))

        layout.addWidget(table)


class DataStoreHealthPanel(QFrame):
    """Connection / State Summary / Health."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("dataStoreHealthPanel")
        self.setMinimumHeight(100)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Connection / State Summary")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        row = QHBoxLayout()
        for label, value, color in [
            ("SQLite", "Healthy", "#10b981"),
            ("ChromaDB", "Healthy", "#10b981"),
            ("File", "OK", "#10b981"),
        ]:
            box = QFrame()
            box.setStyleSheet("background: #f8fafc; border-radius: 6px; padding: 8px;")
            bl = QVBoxLayout(box)
            bl.setContentsMargins(12, 8, 12, 8)
            lbl = QLabel(label)
            lbl.setStyleSheet("color: #334155; font-size: 12px; font-weight: 500;")
            val = QLabel(value)
            val.setStyleSheet(f"color: {color}; font-size: 12px;")
            bl.addWidget(lbl)
            bl.addWidget(val)
            row.addWidget(box)

        layout.addLayout(row)

"""
Tools Panels – Tool Registry, Status, Categories, Permissions.
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


class ToolRegistryPanel(QFrame):
    """Tool Registry – Steuerungsbereich für Tools."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toolRegistryPanel")
        self.setMinimumHeight(200)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Tool Registry")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        demo_label = QLabel("Vorschau (Tools bei Verbindung)")
        demo_label.setStyleSheet("font-size: 11px; color: #94a3b8; margin-bottom: 4px;")
        layout.addWidget(demo_label)

        table = QTableWidget()
        table.setColumnCount(4)
        table.setHorizontalHeaderLabels(["Tool", "Category", "Permissions", "Status"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setRowCount(5)
        table.setStyleSheet(
            "QTableWidget { background: #fafafa; border: none; gridline-color: #e2e8f0; }"
        )

        dummy_data = [
            ("web_search", "Search", "Read", "Available"),
            ("file_read", "File", "Read", "Available"),
            ("code_exec", "Code", "Execute", "Available"),
            ("vector_store_query", "RAG", "Read", "Available"),
            ("prompt_template", "Prompt", "Read", "Available"),
        ]
        for row, (tool, cat, perm, status) in enumerate(dummy_data):
            table.setItem(row, 0, QTableWidgetItem(tool))
            table.setItem(row, 1, QTableWidgetItem(cat))
            table.setItem(row, 2, QTableWidgetItem(perm))
            table.setItem(row, 3, QTableWidgetItem(status))

        layout.addWidget(table)


class ToolSummaryPanel(QFrame):
    """Tool Status / Categories / Permissions / Availability."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("toolSummaryPanel")
        self.setMinimumHeight(100)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_cc_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Categories / Capabilities")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #334155;")
        layout.addWidget(title)

        row = QHBoxLayout()
        for cat, count in [
            ("Search", "1"),
            ("File", "2"),
            ("Code", "1"),
            ("RAG", "2"),
            ("Prompt", "1"),
        ]:
            box = QFrame()
            box.setStyleSheet("background: #f8fafc; border-radius: 6px; padding: 8px;")
            bl = QVBoxLayout(box)
            bl.setContentsMargins(12, 8, 12, 8)
            lbl = QLabel(cat)
            lbl.setStyleSheet("color: #334155; font-size: 12px; font-weight: 500;")
            val = QLabel(count)
            val.setStyleSheet("color: #64748b; font-size: 12px;")
            bl.addWidget(lbl)
            bl.addWidget(val)
            row.addWidget(box)

        layout.addLayout(row)

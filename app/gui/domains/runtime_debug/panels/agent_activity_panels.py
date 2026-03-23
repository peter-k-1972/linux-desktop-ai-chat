"""
Agent Activity Panels – Agent List, Current Task, Status, Last Action, Timeline.
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

from app.gui.domains.runtime_debug.rd_surface_styles import (
    rd_panel_qss,
    rd_section_title_qss,
    rd_monospace_table_qss,
)


class AgentActivityPanel(QFrame):
    """Agent List / Current Task / Status / Last Action / Activity Timeline."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentActivityPanel")
        self.setMinimumHeight(220)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(rd_panel_qss())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Agent Activity")
        title.setStyleSheet(rd_section_title_qss())
        layout.addWidget(title)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Agent", "Current Task", "Status", "Last Action", "Time"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setRowCount(4)
        table.setStyleSheet(rd_monospace_table_qss())

        dummy_data = [
            ("Research Agent", "web_search", "Active", "tool_call", "10:32:01"),
            ("Code Agent", "—", "Idle", "task_done", "10:31:45"),
            ("General Assistant", "chat", "Active", "llm_response", "10:32:00"),
            ("—", "—", "—", "—", "—"),
        ]
        for row, (agent, task, status, action, time) in enumerate(dummy_data):
            table.setItem(row, 0, QTableWidgetItem(agent))
            table.setItem(row, 1, QTableWidgetItem(task))
            table.setItem(row, 2, QTableWidgetItem(status))
            table.setItem(row, 3, QTableWidgetItem(action))
            table.setItem(row, 4, QTableWidgetItem(time))

        layout.addWidget(table)

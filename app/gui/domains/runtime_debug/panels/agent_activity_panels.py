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


def _rd_panel_style() -> str:
    return (
        "background: #0f172a; border: 1px solid #334155; border-radius: 8px; "
        "padding: 12px;"
    )


class AgentActivityPanel(QFrame):
    """Agent List / Current Task / Status / Last Action / Activity Timeline."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentActivityPanel")
        self.setMinimumHeight(220)
        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet(_rd_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Agent Activity")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #94a3b8;")
        layout.addWidget(title)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["Agent", "Current Task", "Status", "Last Action", "Time"])
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table.setRowCount(4)
        table.setStyleSheet(
            "QTableWidget { background: #0f172a; color: #cbd5e1; border: none; "
            "gridline-color: #334155; font-family: monospace; font-size: 11px; }"
        )

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

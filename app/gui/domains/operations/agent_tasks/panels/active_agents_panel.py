"""
ActiveAgentsPanel – Laufende Agenten, Status, aktuelle Aufgabe.
"""

from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, QTimer
from app.gui.shared import BasePanel
from app.debug.debug_store import TaskInfo, get_debug_store


def _panel_style() -> str:
    return (
        "background: #ffffff; border: 1px solid #e5e7eb; border-radius: 12px; "
        "padding: 12px;"
    )


def _status_color(status: str) -> str:
    if status == "running":
        return "#8b5cf6"
    if status == "completed":
        return "#10b981"
    if status == "failed":
        return "#ef4444"
    return "#6b7280"


class ActiveAgentsPanel(BasePanel):
    """Zeigt laufende und kürzlich abgeschlossene Tasks aus DebugStore."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("activeAgentsPanel")
        self.setMinimumHeight(120)
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(1500)

    def _setup_ui(self):
        self.setStyleSheet(_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Aktive Tasks")
        title.setStyleSheet("font-weight: 600; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        self._list = QListWidget()
        self._list.setObjectName("activeAgentsList")
        self._list.setStyleSheet(
            "QListWidget { background: transparent; border: none; }"
            "QListWidget::item { padding: 6px; border-radius: 6px; }"
        )
        layout.addWidget(self._list, 1)

    def refresh(self) -> None:
        """Lädt aktive Tasks aus DebugStore."""
        self._list.clear()
        try:
            store = get_debug_store()
            tasks = store.get_active_tasks()
            # Neueste zuerst
            def _sort_key(t: TaskInfo):
                ts = t.completed_at or t.created_at
                return ts.timestamp() if ts else 0.0
            tasks = sorted(tasks, key=_sort_key, reverse=True)
            for task in tasks[:20]:
                item = QListWidgetItem()
                time_str = ""
                if task.created_at:
                    time_str = task.created_at.strftime("%H:%M:%S")
                desc = (task.description or "")[:60]
                if len((task.description or "")) > 60:
                    desc += "…"
                text = f"{task.agent_name} · {task.status}\n  {desc}  {time_str}"
                item.setText(text)
                item.setForeground(QColor(_status_color(task.status)))
                self._list.addItem(item)
            if not tasks:
                item = QListWidgetItem("Keine aktiven Tasks")
                item.setForeground(QColor("#6b7280"))
                self._list.addItem(item)
        except Exception:
            item = QListWidgetItem("DebugStore nicht verfügbar")
            self._list.addItem(item)

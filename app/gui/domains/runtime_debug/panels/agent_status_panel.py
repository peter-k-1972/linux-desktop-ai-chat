"""
AgentStatusPanel – Aktuell laufende Agenten (idle / running / finished).
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import QTimer
from PySide6.QtGui import QColor
from app.debug.debug_store import get_debug_store


def _panel_style() -> str:
    return (
        "background: #0f172a; border: 1px solid #334155; border-radius: 8px; "
        "padding: 12px;"
    )


def _status_color(status: str) -> str:
    if status == "running":
        return "#8b5cf6"
    if status in ("completed", "selected"):
        return "#10b981"
    if status == "failed":
        return "#ef4444"
    return "#64748b"


class AgentStatusPanel(QFrame):
    """Zeigt Agent-Status aus DebugStore (idle/running/finished)."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentStatusPanel")
        self.setMinimumHeight(120)
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(1500)

    def _setup_ui(self):
        self.setStyleSheet(_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Agent Status")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #94a3b8;")
        layout.addWidget(title)

        self._list = QListWidget()
        self._list.setObjectName("agentStatusList")
        self._list.setStyleSheet(
            "QListWidget { background: #0f172a; color: #cbd5e1; border: none; }"
        )
        layout.addWidget(self._list, 1)

    def refresh(self) -> None:
        """Lädt Agent-Status aus DebugStore."""
        self._list.clear()
        try:
            store = get_debug_store()
            status_map = store.get_agent_status()
            for agent_name, status in sorted(status_map.items(), key=lambda x: (x[0] or "")):
                item = QListWidgetItem(f"{agent_name}: {status}")
                item.setForeground(QColor(_status_color(status)))
                self._list.addItem(item)
            if not status_map:
                item = QListWidgetItem("Keine Agenten aktiv")
                item.setForeground(QColor("#64748b"))
                self._list.addItem(item)
        except Exception:
            item = QListWidgetItem("DebugStore nicht verfügbar")
            self._list.addItem(item)

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
from app.gui.domains.runtime_debug.rd_surface_styles import (
    rd_panel_qss,
    rd_section_title_qss,
    rd_monospace_list_qss,
    rd_status_color_for_label,
    rd_list_item_muted_qss,
)


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
        self.setStyleSheet(rd_panel_qss())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Agent Status")
        title.setStyleSheet(rd_section_title_qss())
        layout.addWidget(title)

        self._list = QListWidget()
        self._list.setObjectName("agentStatusList")
        self._list.setStyleSheet(rd_monospace_list_qss())
        layout.addWidget(self._list, 1)

    def refresh(self) -> None:
        """Lädt Agent-Status aus DebugStore."""
        self._list.clear()
        try:
            store = get_debug_store()
            status_map = store.get_agent_status()
            for agent_name, status in sorted(status_map.items(), key=lambda x: (x[0] or "")):
                item = QListWidgetItem(f"{agent_name}: {status}")
                item.setForeground(QColor(rd_status_color_for_label(status)))
                self._list.addItem(item)
            if not status_map:
                item = QListWidgetItem("Keine Agenten aktiv")
                item.setForeground(QColor(rd_list_item_muted_qss()))
                self._list.addItem(item)
        except Exception:
            item = QListWidgetItem("DebugStore nicht verfügbar")
            self._list.addItem(item)

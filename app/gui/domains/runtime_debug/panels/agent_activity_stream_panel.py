"""
AgentActivityStreamPanel – Chronologische Liste von Agentaktionen.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, QTimer
from app.debug.agent_event import AgentEvent, EventType
from app.debug.debug_store import get_debug_store


def _panel_style() -> str:
    return (
        "background: #0f172a; border: 1px solid #334155; border-radius: 8px; "
        "padding: 12px;"
    )


def _event_label(event: AgentEvent) -> str:
    ts = event.timestamp.strftime("%H:%M:%S") if event.timestamp else ""
    t = event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type)
    msg = (event.message or "")[:50]
    if len(event.message or "") > 50:
        msg += "…"
    return f"{event.agent_name} · {t} · {msg}  {ts}"


class AgentActivityStreamPanel(QFrame):
    """Chronologische Liste von Agent-Events aus DebugStore."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentActivityStreamPanel")
        self.setMinimumHeight(200)
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self.refresh)
        self._timer.start(1000)

    def _setup_ui(self):
        self.setStyleSheet(_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Activity Stream")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #94a3b8;")
        layout.addWidget(title)

        self._list = QListWidget()
        self._list.setObjectName("agentActivityStreamList")
        self._list.itemClicked.connect(self._on_item_clicked)
        self._list.setStyleSheet(
            "QListWidget { background: #0f172a; color: #cbd5e1; border: none; "
            "font-family: monospace; font-size: 11px; }"
            "QListWidget::item:selected { background: #334155; }"
        )
        layout.addWidget(self._list, 1)

    def _on_item_clicked(self, item):
        event = item.data(Qt.ItemDataRole.UserRole)
        if event and hasattr(self.parent(), "on_activity_selected"):
            self.parent().on_activity_selected(event)

    def refresh(self) -> None:
        """Lädt Events aus DebugStore."""
        self._list.clear()
        try:
            store = get_debug_store()
            events = store.get_event_history()
            for ev in events[:100]:
                item = QListWidgetItem(_event_label(ev))
                item.setData(Qt.ItemDataRole.UserRole, ev)
                self._list.addItem(item)
            if not events:
                item = QListWidgetItem("Keine Aktivität")
                self._list.addItem(item)
        except Exception:
            item = QListWidgetItem("DebugStore nicht verfügbar")
            self._list.addItem(item)

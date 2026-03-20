"""Events Monitor – kompakte Event-Ansicht für Bottom Panel."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import QTimer
from app.debug.debug_store import get_debug_store


class EventsMonitor(QWidget):
    """Kompakter Event-Monitor für Bottom Panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("eventsMonitor")
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        title = QLabel("Events")
        title.setStyleSheet("font-weight: 600; font-size: 12px; color: #64748b;")
        layout.addWidget(title)
        self._list = QListWidget()
        self._list.setMaximumHeight(120)
        self._list.setStyleSheet(
            "QListWidget { background: #f8fafc; border: 1px solid #e2e8f0; "
            "border-radius: 6px; font-size: 11px; }"
        )
        layout.addWidget(self._list)

    def _refresh(self) -> None:
        self._list.clear()
        try:
            events = get_debug_store().get_event_history()[:8]
            for ev in events:
                ts = ev.timestamp.strftime("%H:%M") if ev.timestamp else ""
                t = ev.event_type.value if hasattr(ev.event_type, "value") else str(ev.event_type)
                msg = (ev.message or "")[:40]
                if len(ev.message or "") > 40:
                    msg += "…"
                self._list.addItem(QListWidgetItem(f"{ts} {t} · {ev.agent_name or '—'}: {msg}"))
            if not events:
                self._list.addItem(QListWidgetItem("Keine Events"))
        except Exception:
            self._list.addItem(QListWidgetItem("DebugStore nicht verfügbar"))

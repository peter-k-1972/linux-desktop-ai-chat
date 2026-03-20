"""LLM Trace Monitor – kompakte LLM-Call-Ansicht für Bottom Panel."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem
from PySide6.QtCore import QTimer
from app.debug.debug_store import get_debug_store
from app.debug.agent_event import EventType


class LLMTraceMonitor(QWidget):
    """Kompakter LLM-Trace-Monitor für Bottom Panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("llmTraceMonitor")
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        title = QLabel("LLM Trace")
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
            events = [e for e in get_debug_store().get_event_history() if e.event_type == EventType.MODEL_CALL][:8]
            for ev in events:
                ts = ev.timestamp.strftime("%H:%M") if ev.timestamp else ""
                model = ev.metadata.get("model_id") or ev.message or "—"
                dur = ev.metadata.get("duration_sec")
                dur_str = f"{dur:.1f}s" if dur else "—"
                self._list.addItem(QListWidgetItem(f"{ts} {model} · {dur_str} · {ev.agent_name or '—'}"))
            if not events:
                self._list.addItem(QListWidgetItem("Keine LLM-Aufrufe"))
        except Exception:
            self._list.addItem(QListWidgetItem("DebugStore nicht verfügbar"))

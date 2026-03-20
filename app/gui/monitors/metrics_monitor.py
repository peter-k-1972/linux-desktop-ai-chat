"""Metrics Monitor – kompakte Metrik-Ansicht für Bottom Panel."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout
from PySide6.QtCore import QTimer


class MetricsMonitor(QWidget):
    """Kompakter Metrics-Monitor für Bottom Panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("metricsMonitor")
        self._labels = {}
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        title = QLabel("Metrics")
        title.setStyleSheet("font-weight: 600; font-size: 12px; color: #64748b;")
        layout.addWidget(title)
        grid = QGridLayout()
        for i, (key, label) in enumerate([
            ("chats", "Chats:"),
            ("tasks", "Tasks:"),
            ("llm", "LLM:"),
        ]):
            l = QLabel("—")
            l.setStyleSheet("font-family: monospace; font-size: 12px;")
            self._labels[key] = l
            grid.addWidget(QLabel(label), 0, i)
            grid.addWidget(l, 1, i)
        layout.addLayout(grid)

    def _refresh(self) -> None:
        try:
            from app.services.chat_service import get_chat_service
            from app.debug.debug_store import get_debug_store
            from app.debug.agent_event import EventType
            chat_count = len(get_chat_service().list_chats())
            store = get_debug_store()
            task_count = len(store.get_active_tasks())
            events = store.get_event_history()
            llm_count = sum(1 for e in events if e.event_type == EventType.MODEL_CALL)
            self._labels["chats"].setText(str(chat_count))
            self._labels["tasks"].setText(str(task_count))
            self._labels["llm"].setText(str(llm_count))
        except Exception:
            for l in self._labels.values():
                l.setText("—")

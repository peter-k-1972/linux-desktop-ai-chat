"""
Metrics Panels – Runtime-Metriken aus echten Quellen.
"""

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QLabel,
    QGridLayout,
)
from PySide6.QtCore import QTimer


def _rd_panel_style() -> str:
    return (
        "background: #0f172a; border: 1px solid #334155; border-radius: 8px; "
        "padding: 12px;"
    )


def _metric_card(title: str, value: str, unit: str = "", color: str = "#34d399"):
    """Erstellt eine Monitoring-Karte. Returns (card, value_label)."""
    card = QFrame()
    card.setStyleSheet(
        "background: #1e293b; border: 1px solid #334155; border-radius: 6px; "
        "padding: 12px;"
    )
    layout = QVBoxLayout(card)
    layout.setContentsMargins(12, 12, 12, 12)
    t = QLabel(title)
    t.setStyleSheet("color: #64748b; font-size: 11px;")
    layout.addWidget(t)
    v = QLabel(value)
    v.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 20px; font-family: monospace;")
    layout.addWidget(v)
    if unit:
        u = QLabel(unit)
        u.setStyleSheet("color: #94a3b8; font-size: 11px;")
        layout.addWidget(u)
    return card, v


class MetricsOverviewPanel(QFrame):
    """Runtime-Metriken aus ChatService, DebugStore."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("metricsOverviewPanel")
        self.setMinimumHeight(200)
        self._value_labels: list = []
        self._setup_ui()
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._refresh)
        self._timer.start(2000)

    def _setup_ui(self):
        self.setStyleSheet(_rd_panel_style())
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Metrics Overview")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #94a3b8;")
        layout.addWidget(title)

        grid = QGridLayout()
        cards = [
            ("Chats", "0", "Sessions", "#34d399"),
            ("Agent Tasks", "0", "aktiv/kürzlich", "#8b5cf6"),
            ("LLM Calls", "0", "heute", "#06b6d4"),
            ("Model Runtime", "—", "Gesamt", "#10b981"),
            ("Letzter Fehler", "—", "", "#64748b"),
            ("Agent Status", "—", "", "#94a3b8"),
        ]
        for i, (t, v, u, c) in enumerate(cards):
            card, val_label = _metric_card(t, v, u, c)
            self._value_labels.append((val_label, c))
            grid.addWidget(card, i // 3, i % 3)
        layout.addLayout(grid)

    def _refresh(self) -> None:
        chat_count = 0
        try:
            from app.services.chat_service import get_chat_service
            chat_count = len(get_chat_service().list_chats())
        except Exception:
            pass

        task_count = 0
        llm_count = 0
        last_error = "—"
        total_duration = 0.0
        agent_summary = "—"
        try:
            from app.debug.debug_store import get_debug_store
            from app.debug.agent_event import EventType
            store = get_debug_store()
            task_count = len(store.get_active_tasks())
            events = store.get_event_history()
            llm_count = sum(1 for e in events if e.event_type == EventType.MODEL_CALL)
            for e in events:
                if e.event_type == EventType.TASK_FAILED:
                    last_error = (e.message or e.metadata.get("error") or "Fehler")[:45]
                    if len(last_error) >= 45:
                        last_error += "…"
                    break
            for e in events:
                if e.event_type == EventType.MODEL_CALL:
                    total_duration += e.metadata.get("duration_sec", 0) or 0
            status = store.get_agent_status()
            running = sum(1 for s in status.values() if s == "running")
            agent_summary = f"{running} aktiv" if running > 0 else (f"{len(status)} bekannt" if status else "—")
        except Exception:
            pass

        model_runtime = "—"
        if total_duration > 0:
            model_runtime = f"{total_duration:.1f}s" if total_duration >= 1 else f"{total_duration*1000:.0f}ms"

        values = [str(chat_count), str(task_count), str(llm_count), model_runtime, last_error, agent_summary]
        colors = ["#34d399", "#8b5cf6", "#06b6d4", "#10b981", "#ef4444" if last_error != "—" else "#64748b", "#94a3b8"]
        for (label, _), val, color in zip(self._value_labels, values, colors):
            label.setText(val)
            label.setStyleSheet(f"color: {color}; font-weight: 600; font-size: 20px; font-family: monospace;")

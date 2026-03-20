"""
Event Timeline View – chronologische Liste von Ereignissen.

Beispiel:
  12:01  Planner  started
  12:02  Planner  completed
  12:02  Research started
"""

from datetime import datetime

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt

from app.debug.agent_event import AgentEvent, EventType
from app.debug.debug_store import DebugStore
from app.resources.styles import get_theme_colors


def _format_time(dt: datetime) -> str:
    """Formatiert Zeit für Timeline-Anzeige."""
    return dt.strftime("%H:%M:%S") if dt else ""


def _event_display_text(event: AgentEvent) -> str:
    """Kurzer Anzeigetext für ein Event."""
    if event.message:
        return event.message
    type_map = {
        EventType.TASK_CREATED: "Task erstellt",
        EventType.TASK_STARTED: "gestartet",
        EventType.TASK_COMPLETED: "abgeschlossen",
        EventType.TASK_FAILED: "fehlgeschlagen",
        EventType.AGENT_SELECTED: "ausgewählt",
        EventType.MODEL_CALL: "Modellaufruf",
        EventType.TOOL_EXECUTION: "Tool ausgeführt",
        EventType.RAG_RETRIEVAL_FAILED: "RAG-Abruf fehlgeschlagen",
    }
    return type_map.get(event.event_type, event.event_type.value)


class EventTimelineView(QWidget):
    """Chronologische Liste von Agenten-Events."""

    def __init__(self, store: DebugStore, theme: str = "dark", parent=None):
        super().__init__(parent)
        self._store = store
        self._theme = theme
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        title = QLabel("Event-Timeline")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setMinimumHeight(180)
        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

        self._empty_label = QLabel("Keine Events.")
        self._empty_label.setStyleSheet("color: gray; font-size: 11px;")
        self._container_layout.addWidget(self._empty_label)

        self._item_frames: list[QFrame] = []

    def _get_styles(self) -> dict:
        return get_theme_colors(self._theme)

    def refresh(self):
        """Aktualisiert die Timeline aus dem DebugStore."""
        colors = self._get_styles()
        fg = colors.get("fg", "#e8e8e8")
        muted = colors.get("muted", "#a0a0a0")

        for frame in self._item_frames:
            frame.deleteLater()
        self._item_frames.clear()

        events = self._store.get_event_history()
        self._empty_label.setVisible(len(events) == 0)

        for event in events[:100]:  # Max 100 anzeigen
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel)
            frame.setStyleSheet(
                "background: transparent; border: none; padding: 2px 0;"
            )
            fl = QVBoxLayout(frame)
            fl.setContentsMargins(4, 2, 4, 2)
            fl.setSpacing(0)

            time_str = _format_time(event.timestamp)
            agent_str = event.agent_name or "-"
            msg_str = _event_display_text(event)

            line = QLabel(f"{time_str}  {agent_str}  {msg_str}")
            line.setStyleSheet(f"font-size: 11px; font-family: monospace; color: {fg};")
            line.setWordWrap(True)
            fl.addWidget(line)

            self._container_layout.addWidget(frame)
            self._item_frames.append(frame)

    def set_theme(self, theme: str):
        """Setzt das Theme."""
        self._theme = theme


__all__ = [
    "EventTimelineView",
    "_event_display_text",
]

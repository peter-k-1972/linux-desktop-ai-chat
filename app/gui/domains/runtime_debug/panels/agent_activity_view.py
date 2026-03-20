"""
Agent Activity View – zeigt Agent | Task | Status.

Beispiel:
  Planner Agent    Task: Analyse prompt    Status: completed
  Research Agent   Task: Analyse Codebasis Status: running
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt

from app.debug.debug_store import DebugStore, TaskInfo
from app.resources.styles import get_theme_colors


class AgentActivityView(QWidget):
    """Zeigt aktive Agenten mit Task und Status."""

    def __init__(self, store: DebugStore, theme: str = "dark", parent=None):
        super().__init__(parent)
        self._store = store
        self._theme = theme
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        title = QLabel("Agenten-Aktivität")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setMinimumHeight(150)
        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

        self._empty_label = QLabel("Keine aktiven Tasks.")
        self._empty_label.setStyleSheet("color: gray; font-size: 11px;")
        self._container_layout.addWidget(self._empty_label)

        self._item_frames: list[QFrame] = []

    def _get_styles(self) -> dict:
        return get_theme_colors(self._theme)

    def refresh(self):
        """Aktualisiert die Anzeige aus dem DebugStore."""
        colors = self._get_styles()
        fg = colors.get("fg", "#e8e8e8")
        muted = colors.get("muted", "#a0a0a0")

        # Alte Frames entfernen
        for frame in self._item_frames:
            frame.deleteLater()
        self._item_frames.clear()

        tasks = self._store.get_active_tasks()
        self._empty_label.setVisible(len(tasks) == 0)

        for task in tasks:
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel)
            frame.setStyleSheet(
                f"background: rgba(255,255,255,0.05); border-radius: 6px; "
                f"padding: 8px; border: 1px solid rgba(255,255,255,0.08);"
            )
            fl = QVBoxLayout(frame)
            fl.setSpacing(4)

            agent_lbl = QLabel(f"🤖 {task.agent_name or 'Unbekannt'}")
            agent_lbl.setStyleSheet(f"font-size: 12px; font-weight: 600; color: {fg};")
            fl.addWidget(agent_lbl)

            desc = task.description[:60] + ("…" if len(task.description) > 60 else "")
            task_lbl = QLabel(f"Task: {desc}")
            task_lbl.setStyleSheet(f"font-size: 11px; color: {muted};")
            task_lbl.setWordWrap(True)
            fl.addWidget(task_lbl)

            status_color = {
                "pending": muted,
                "running": "#06b6d4",
                "completed": "#10b981",
                "failed": "#ef4444",
            }.get(task.status, muted)
            status_lbl = QLabel(f"Status: {task.status}")
            status_lbl.setStyleSheet(f"font-size: 11px; color: {status_color};")
            fl.addWidget(status_lbl)

            self._container_layout.addWidget(frame)
            self._item_frames.append(frame)

    def set_theme(self, theme: str):
        """Setzt das Theme für die Anzeige."""
        self._theme = theme

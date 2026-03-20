"""
Task Graph View – vereinfachte Darstellung des Task-Graphen.

Zeigt Tasks mit Abhängigkeiten als hierarchische Liste.
"""

from typing import Optional

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


class TaskGraphView(QWidget):
    """Vereinfachte Darstellung des Task-Graphen (Tasks + Status)."""

    def __init__(self, store: DebugStore, theme: str = "dark", parent=None):
        super().__init__(parent)
        self._store = store
        self._theme = theme
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        title = QLabel("Task-Graph")
        title.setStyleSheet("font-weight: bold; font-size: 13px;")
        layout.addWidget(title)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._scroll.setMinimumHeight(120)
        self._container = QWidget()
        self._container_layout = QVBoxLayout(self._container)
        self._container_layout.setContentsMargins(0, 0, 0, 0)
        self._scroll.setWidget(self._container)
        layout.addWidget(self._scroll)

        self._empty_label = QLabel("Kein Task-Graph.")
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

        for frame in self._item_frames:
            frame.deleteLater()
        self._item_frames.clear()

        tasks = self._store.get_active_tasks()
        self._empty_label.setVisible(len(tasks) == 0)

        # Nach Status sortieren: running zuerst, dann pending, completed, failed
        status_order = {"running": 0, "pending": 1, "completed": 2, "failed": 3}
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (status_order.get(t.status, 4), t.task_id),
        )

        for task in sorted_tasks:
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel)
            status_color = {
                "pending": muted,
                "running": "#06b6d4",
                "completed": "#10b981",
                "failed": "#ef4444",
            }.get(task.status, muted)
            frame.setStyleSheet(
                f"background: rgba(255,255,255,0.04); border-radius: 6px; "
                f"padding: 6px; border-left: 3px solid {status_color};"
            )
            fl = QVBoxLayout(frame)
            fl.setSpacing(2)

            desc = task.description[:70] + ("…" if len(task.description) > 70 else "")
            line1 = QLabel(f"• {desc}")
            line1.setStyleSheet(f"font-size: 11px; color: {fg};")
            line1.setWordWrap(True)
            fl.addWidget(line1)

            meta = f"{task.status} | Agent: {task.agent_name or '-'}"
            if task.error:
                meta += f" | {task.error[:50]}…" if len(task.error) > 50 else f" | {task.error}"
            line2 = QLabel(meta)
            line2.setStyleSheet(f"font-size: 10px; color: {muted};")
            line2.setWordWrap(True)
            fl.addWidget(line2)

            self._container_layout.addWidget(frame)
            self._item_frames.append(frame)

    def set_theme(self, theme: str):
        """Setzt das Theme."""
        self._theme = theme

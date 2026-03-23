"""
Task Graph View – vereinfachte Darstellung des Task-Graphen.

Zeigt Tasks mit Abhängigkeiten als hierarchische Liste.
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
from app.gui.domains.runtime_debug.rd_surface_styles import (
    rd_bold_title_qss,
    rd_label_line_qss,
    rd_task_status_color,
    rd_task_row_frame_qss,
)


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
        title.setStyleSheet(rd_bold_title_qss())
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
        self._empty_label.setStyleSheet(rd_label_line_qss(font_size_px=11, muted=True))
        self._container_layout.addWidget(self._empty_label)

        self._item_frames: list[QFrame] = []

    def refresh(self):
        """Aktualisiert die Anzeige aus dem DebugStore."""
        line1_style = rd_label_line_qss(font_size_px=11, muted=False)
        line2_style = rd_label_line_qss(font_size_px=10, muted=True)

        for frame in self._item_frames:
            frame.deleteLater()
        self._item_frames.clear()

        tasks = self._store.get_active_tasks()
        self._empty_label.setVisible(len(tasks) == 0)

        status_order = {"running": 0, "pending": 1, "completed": 2, "failed": 3}
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (status_order.get(t.status, 4), t.task_id),
        )

        for task in sorted_tasks:
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel)
            accent = rd_task_status_color(task.status)
            frame.setStyleSheet(rd_task_row_frame_qss(left_accent_color=accent))
            fl = QVBoxLayout(frame)
            fl.setSpacing(2)

            desc = task.description[:70] + ("…" if len(task.description) > 70 else "")
            line1 = QLabel(f"• {desc}")
            line1.setStyleSheet(line1_style)
            line1.setWordWrap(True)
            fl.addWidget(line1)

            meta = f"{task.status} | Agent: {task.agent_name or '-'}"
            if task.error:
                meta += f" | {task.error[:50]}…" if len(task.error) > 50 else f" | {task.error}"
            line2 = QLabel(meta)
            line2.setStyleSheet(line2_style)
            line2.setWordWrap(True)
            fl.addWidget(line2)

            self._container_layout.addWidget(frame)
            self._item_frames.append(frame)

    def set_theme(self, theme: str):
        """Setzt das Theme."""
        self._theme = theme

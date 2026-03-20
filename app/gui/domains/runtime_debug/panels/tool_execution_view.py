"""
Tool Execution View – zeigt ausgeführte Tools, AI Studio / ComfyUI Aufrufe, Status.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QFrame,
    QScrollArea,
)
from PySide6.QtCore import Qt

from app.debug.debug_store import DebugStore, ToolExecutionEntry
from app.resources.styles import get_theme_colors


def _format_ts(entry: ToolExecutionEntry) -> str:
    """Formatiert Zeitstempel für Anzeige."""
    if entry.timestamp:
        return entry.timestamp.strftime("%H:%M:%S")
    return ""


class ToolExecutionView(QWidget):
    """Zeigt ausgeführte Tools mit Status."""

    def __init__(self, store: DebugStore, theme: str = "dark", parent=None):
        super().__init__(parent)
        self._store = store
        self._theme = theme
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        title = QLabel("Tool-Ausführungen")
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

        self._empty_label = QLabel("Keine Tool-Ausführungen.")
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

        entries = self._store.get_tool_executions()
        self._empty_label.setVisible(len(entries) == 0)

        for entry in entries[:50]:
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel)
            frame.setStyleSheet(
                "background: rgba(255,255,255,0.04); border-radius: 6px; "
                "padding: 6px; border: 1px solid rgba(255,255,255,0.06);"
            )
            fl = QVBoxLayout(frame)
            fl.setSpacing(2)

            status_color = {
                "started": "#06b6d4",
                "completed": "#10b981",
                "failed": "#ef4444",
            }.get(entry.status, muted)

            line1 = QLabel(f"🔧 {entry.tool_name}  [{entry.status}]")
            line1.setStyleSheet(f"font-size: 11px; color: {fg};")
            fl.addWidget(line1)

            meta = []
            if entry.agent_name:
                meta.append(f"Agent: {entry.agent_name}")
            if entry.timestamp:
                meta.append(_format_ts(entry))
            if entry.error:
                meta.append(f"Fehler: {entry.error[:80]}…" if len(entry.error) > 80 else f"Fehler: {entry.error}")
            if meta:
                line2 = QLabel("  ".join(meta))
                line2.setStyleSheet(f"font-size: 10px; color: {muted};")
                line2.setWordWrap(True)
                fl.addWidget(line2)

            self._container_layout.addWidget(frame)
            self._item_frames.append(frame)

    def set_theme(self, theme: str):
        """Setzt das Theme."""
        self._theme = theme

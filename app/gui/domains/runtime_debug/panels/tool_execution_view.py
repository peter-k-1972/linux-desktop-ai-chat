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
from app.gui.domains.runtime_debug.rd_surface_styles import (
    rd_bold_title_qss,
    rd_embedded_row_frame_qss,
    rd_label_line_qss,
)


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

        self._empty_label = QLabel("Keine Tool-Ausführungen.")
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

        entries = self._store.get_tool_executions()
        self._empty_label.setVisible(len(entries) == 0)

        for entry in entries[:50]:
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel)
            frame.setStyleSheet(rd_embedded_row_frame_qss(padding_px=6))
            fl = QVBoxLayout(frame)
            fl.setSpacing(2)

            line1 = QLabel(f"🔧 {entry.tool_name}  [{entry.status}]")
            line1.setStyleSheet(line1_style)
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
                line2.setStyleSheet(line2_style)
                line2.setWordWrap(True)
                fl.addWidget(line2)

            self._container_layout.addWidget(frame)
            self._item_frames.append(frame)

    def set_theme(self, theme: str):
        """Setzt das Theme."""
        self._theme = theme

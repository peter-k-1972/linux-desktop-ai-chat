"""
RuntimeDebugView – Einstieg für Debug-/Runtime-Navigation.

Verlinkt auf bestehende Debug-Panels (im Chat-Sidepanel), dupliziert sie nicht.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
)
from PySide6.QtCore import Signal

from app.resources.styles import get_theme_colors


class RuntimeDebugView(QWidget):
    """
    Runtime/Debug-Einstieg – Navigation zum Debug-Panel.

    Das Debug-Panel (AgentActivityView, EventTimelineView, etc.) lebt im
    Chat-Sidepanel. Diese View verlinkt dorthin, ohne zu duplizieren.
    """

    back_requested = Signal()
    go_to_chat_requested = Signal()

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self._init_ui()
        self._apply_theme()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        header = QHBoxLayout()
        back_btn = QPushButton("← Zurück")
        back_btn.clicked.connect(self.back_requested.emit)
        header.addWidget(back_btn)
        header.addStretch()
        title = QLabel("Runtime / Debug")
        title.setStyleSheet("font-size: 18px; font-weight: 700;")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        group = QGroupBox("Debug-Panel")
        group.setObjectName("debugGroup")
        group_layout = QVBoxLayout(group)
        group_layout.addWidget(QLabel(
            "Das Debug-Panel (Aktivität, Timeline, Task-Graph, Tool-Execution, Model-Usage) "
            "befindet sich im Chat-Sidepanel auf der rechten Seite.\n\n"
            "Klicken Sie unten, um zum Chat zu wechseln und das Debug-Panel zu nutzen."
        ))
        go_btn = QPushButton("Zum Chat (Debug-Panel öffnen)")
        go_btn.clicked.connect(self.go_to_chat_requested.emit)
        group_layout.addWidget(go_btn)
        layout.addWidget(group)

        empty_group = QGroupBox("Live-Daten")
        empty_group.setObjectName("emptyGroup")
        empty_layout = QVBoxLayout(empty_group)
        empty_layout.addWidget(QLabel(
            "Keine Live-Debug-Daten in der Kommandozentrale.\n"
            "Events und Tasks werden im Chat-Kontext angezeigt."
        ))
        layout.addWidget(empty_group)

    def _apply_theme(self):
        colors = get_theme_colors(self.theme)
        fg = colors.get("fg", "#e8e8e8")
        muted = colors.get("muted", "#a0a0a0")
        style = f"""
            QGroupBox {{ font-weight: 600; color: {fg}; border: 1px solid {colors.get('top_bar_border', '#505050')}; border-radius: 8px; margin-top: 12px; }}
            QGroupBox::title {{ subcontrol-origin: margin; left: 10px; padding: 0 6px; color: {muted}; }}
        """
        for g in self.findChildren(QGroupBox):
            g.setStyleSheet(style)

    def refresh_theme(self, theme: str):
        self.theme = theme
        self._apply_theme()

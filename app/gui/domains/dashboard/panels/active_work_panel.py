"""
ActiveWorkPanel – Hinweis auf Arbeitsbereiche (kein globaler Task-Tracker).
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel
from app.gui.shared import BasePanel


class ActiveWorkPanel(BasePanel):
    """Panel: Orientierung, keine Live-Queue."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("Aktive Arbeit")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        detail = QLabel(
            "Laufende Chats, Agent-Tasks und Indexierungen werden in den jeweiligen "
            "Operations-Workspaces geführt (Chat, Agent Tasks, Knowledge). "
            "Diese Karte bündelt keine Live-Metriken."
        )
        detail.setObjectName("panelMeta")
        detail.setWordWrap(True)
        layout.addWidget(detail)

        layout.addStretch()

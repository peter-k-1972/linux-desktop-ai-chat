"""
ActiveWorkPanel – Aktive Arbeit für das Dashboard.

Platzhalter-UI ohne Backend-Logik.
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel
from app.gui.shared import BasePanel


class ActiveWorkPanel(BasePanel):
    """Panel für aktive Arbeit."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("Active Work")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        detail = QLabel("Laufende Chats, Agent Tasks, Verifikationen.")
        detail.setObjectName("panelMeta")
        detail.setWordWrap(True)
        layout.addWidget(detail)

        layout.addStretch()

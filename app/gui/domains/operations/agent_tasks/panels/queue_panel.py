"""AgentQueuePanel – Queue / Running Tasks."""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from app.gui.shared import BasePanel


class AgentQueuePanel(BasePanel):
    """Queue und laufende Tasks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentQueuePanel")
        self.setMinimumHeight(140)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Queue / Running Tasks")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        desc = QLabel("Laufende Tasks, Warteschlange. (Platzhalter)")
        desc.setStyleSheet("color: #6b7280; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

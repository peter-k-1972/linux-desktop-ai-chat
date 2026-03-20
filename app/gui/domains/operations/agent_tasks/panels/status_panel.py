"""AgentStatusPanel – Statusbereich für Agenten."""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from app.gui.shared import BasePanel


class AgentStatusPanel(BasePanel):
    """Statusbereich: Active Agents, Status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentStatusPanel")
        self.setMinimumHeight(120)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Active Agents")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        desc = QLabel("Status: Bereit. (Platzhalter)")
        desc.setStyleSheet("color: #22c55e; font-size: 12px;")
        layout.addWidget(desc)

        layout.addStretch()

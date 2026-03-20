"""AgentTasksOverviewPanel – Übersicht aktiver Agenten und Tasks."""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QScrollArea
from PySide6.QtCore import Qt
from app.gui.shared import BasePanel


class AgentTasksOverviewPanel(BasePanel):
    """Übersicht: Agent Task Overview."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("agentTasksOverviewPanel")
        self.setMinimumHeight(180)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Agent Task Overview")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        desc = QLabel(
            "Aktive Agenten, delegierte Tasks, Status.\n"
            "Wird bei Backend-Integration mit echten Daten befüllt."
        )
        desc.setStyleSheet("color: #6b7280; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

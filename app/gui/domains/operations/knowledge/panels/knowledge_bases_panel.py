"""KnowledgeBasesPanel – Knowledge Bases, Collections, Sources."""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from app.gui.shared import BasePanel


class KnowledgeBasesPanel(BasePanel):
    """Knowledge Bases und Collections."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("knowledgeBasesPanel")
        self.setMinimumHeight(180)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Knowledge Bases")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        desc = QLabel(
            "Collections, Sources, Dokumente.\n"
            "Wird bei RAG-Integration befüllt."
        )
        desc.setStyleSheet("color: #6b7280; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

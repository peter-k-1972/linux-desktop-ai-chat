"""PromptPreviewPanel – Prompt Test / Preview."""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from app.gui.shared import BasePanel


class PromptPreviewPanel(BasePanel):
    """Prompt-Test und Vorschau."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("promptPreviewPanel")
        self.setMinimumHeight(140)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Prompt Test / Preview")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        desc = QLabel("Vorschau, Test-Ausführung. (Platzhalter)")
        desc.setStyleSheet("color: #6b7280; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

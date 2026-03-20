"""RetrievalStatusPanel – Retrieval Status."""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from app.gui.shared import BasePanel


class RetrievalStatusPanel(BasePanel):
    """Retrieval-Status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("retrievalStatusPanel")
        self.setMinimumHeight(120)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Retrieval Status")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        desc = QLabel("Bereit. (Platzhalter)")
        desc.setStyleSheet("color: #22c55e; font-size: 12px;")
        layout.addWidget(desc)

        layout.addStretch()

"""IndexOverviewPanel – Index Overview."""

from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel
from app.gui.shared import BasePanel


class IndexOverviewPanel(BasePanel):
    """Index-Übersicht."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("indexOverviewPanel")
        self.setMinimumHeight(140)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        title = QLabel("Index Overview")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        layout.addWidget(title)

        desc = QLabel("Embeddings, Chunks, Status. (Platzhalter)")
        desc.setStyleSheet("color: #6b7280; font-size: 12px;")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        layout.addStretch()

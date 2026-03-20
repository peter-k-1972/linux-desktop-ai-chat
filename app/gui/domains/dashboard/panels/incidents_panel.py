"""
IncidentsPanel – Incidents für das Dashboard.

Platzhalter-UI ohne Backend-Logik.
"""

from PySide6.QtWidgets import QVBoxLayout, QLabel
from app.gui.shared import BasePanel


class IncidentsPanel(BasePanel):
    """Panel für Incidents."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title = QLabel("Incidents")
        title.setObjectName("panelTitle")
        layout.addWidget(title)

        detail = QLabel("Offene Incidents, Bindings, Replay-Status.")
        detail.setObjectName("panelMeta")
        detail.setWordWrap(True)
        layout.addWidget(detail)

        layout.addStretch()

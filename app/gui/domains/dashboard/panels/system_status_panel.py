"""
SystemStatusPanel – System-Status-Karte für das Dashboard.

Platzhalter-UI ohne Backend-Logik.
"""

from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QLabel, QWidget
from PySide6.QtCore import Qt
from app.gui.shared import BasePanel
from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry


class SystemStatusPanel(BasePanel):
    """Panel für System-Status."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(140)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        title_row = QWidget()
        title_row_layout = QHBoxLayout(title_row)
        title_row_layout.setContentsMargins(0, 0, 0, 0)
        title_row_layout.setSpacing(8)
        icon_label = QLabel()
        icon_label.setPixmap(IconManager.get(IconRegistry.CONTROL, size=18).pixmap(18, 18))
        title_row_layout.addWidget(icon_label)
        title = QLabel("System Status")
        title.setObjectName("panelTitle")
        title_row_layout.addWidget(title)
        title_row_layout.addStretch()
        layout.addWidget(title_row)

        status = QLabel("Bereit")
        status.setObjectName("panelStatus")
        layout.addWidget(status)

        detail = QLabel("Ollama, RAG, Agents – Status wird geladen.")
        detail.setObjectName("panelMeta")
        detail.setWordWrap(True)
        layout.addWidget(detail)

        layout.addStretch()

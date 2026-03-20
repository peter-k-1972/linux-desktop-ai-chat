"""
ToolInspector – Inspector-Inhalt für Tool-Details.

Kategorie, Berechtigungen, Verfügbarkeit.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class ToolInspector(QWidget):
    """Inspector für Tool-Kontext im Control Center."""

    def __init__(
        self,
        tool: str = "(keine)",
        category: str = "—",
        permissions: str = "—",
        availability: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("toolInspector")
        self._tool = tool
        self._category = category
        self._permissions = permissions
        self._availability = availability
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Tool", self._tool),
            ("Kategorie", self._category),
            ("Berechtigungen", self._permissions),
            ("Verfügbarkeit", self._availability),
        ]:
            group = QGroupBox(title)
            group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
            gl = QVBoxLayout(group)
            label = QLabel(text)
            label.setStyleSheet("color: #6b7280; font-size: 12px;")
            label.setWordWrap(True)
            gl.addWidget(label)
            layout.addWidget(group)

        layout.addStretch()

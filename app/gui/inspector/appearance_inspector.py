"""
AppearanceInspector – Inspector für Theme-Details.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class AppearanceInspector(QWidget):
    """Inspector für Appearance/Theme-Kontext."""

    def __init__(self, theme_id: str = "(keine)", parent=None):
        super().__init__(parent)
        self.setObjectName("appearanceInspector")
        self._theme_id = theme_id
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Theme", self._theme_id),
            ("Details", "Design-Tokens, Farben, Typografie."),
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

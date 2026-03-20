"""ModelsSettingsInspector – Inspector für Model-Detail."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class ModelsSettingsInspector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        for title, text in [
            ("Model Detail", "Default Model, Token Limits."),
        ]:
            g = QGroupBox(title)
            g.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
            gl = QVBoxLayout(g)
            l = QLabel(text)
            l.setStyleSheet("color: #6b7280; font-size: 12px;")
            gl.addWidget(l)
            layout.addWidget(g)
        layout.addStretch()

"""AdvancedSettingsInspector – Inspector für Feature Description."""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class AdvancedSettingsInspector(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        for title, text in [
            ("Feature Description", "Debug, Experimental, Developer."),
        ]:
            g = QGroupBox(title)
            g.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
            gl = QVBoxLayout(g)
            l = QLabel(text)
            l.setStyleSheet("color: #6b7280; font-size: 12px;")
            gl.addWidget(l)
            layout.addWidget(g)
        layout.addStretch()

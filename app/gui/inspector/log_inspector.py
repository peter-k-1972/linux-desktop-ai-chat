"""
LogInspector – Inspector-Inhalt für vollständigen Logeintrag.

Timestamp, Level, Module, Message.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class LogInspector(QWidget):
    """Inspector für Log-Kontext im Runtime-/Debug-Bereich."""

    def __init__(
        self,
        timestamp: str = "—",
        level: str = "—",
        module: str = "—",
        message: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("logInspector")
        self._timestamp = timestamp
        self._level = level
        self._module = module
        self._message = message
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Timestamp", self._timestamp),
            ("Level", self._level),
            ("Module", self._module),
            ("Message", self._message),
        ]:
            group = QGroupBox(title)
            group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
            gl = QVBoxLayout(group)
            label = QLabel(text)
            label.setStyleSheet("color: #6b7280; font-size: 12px; font-family: monospace;")
            label.setWordWrap(True)
            gl.addWidget(label)
            layout.addWidget(group)

        layout.addStretch()

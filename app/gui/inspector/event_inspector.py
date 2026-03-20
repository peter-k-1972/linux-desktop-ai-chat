"""
EventInspector – Inspector-Inhalt für Event-Details.

Event Type, Timestamp, Source, Payload.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class EventInspector(QWidget):
    """Inspector für Event-Kontext im Runtime-/Debug-Bereich."""

    def __init__(
        self,
        event_type: str = "(keine)",
        timestamp: str = "—",
        source: str = "—",
        payload: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("eventInspector")
        self._event_type = event_type
        self._timestamp = timestamp
        self._source = source
        self._payload = payload
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Event Type", self._event_type),
            ("Timestamp", self._timestamp),
            ("Source", self._source),
            ("Payload", self._payload),
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

"""
ProviderInspector – Inspector-Inhalt für Provider-Details.

Endpoint, Verfügbarkeit, Fehlerstatus.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class ProviderInspector(QWidget):
    """Inspector für Provider-Kontext im Control Center."""

    def __init__(
        self,
        provider: str = "(keine)",
        endpoint: str = "—",
        availability: str = "—",
        error_status: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("providerInspector")
        self._provider = provider
        self._endpoint = endpoint
        self._availability = availability
        self._error_status = error_status
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Provider", self._provider),
            ("Endpoint", self._endpoint),
            ("Verfügbarkeit", self._availability),
            ("Fehlerstatus", self._error_status),
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

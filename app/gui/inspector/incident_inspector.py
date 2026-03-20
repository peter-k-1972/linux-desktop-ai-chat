"""
IncidentInspector – Inspector-Inhalt für Incident-Details.

Incident-ID, Severity, Status, letzte Aktivität.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox


class IncidentInspector(QWidget):
    """Inspector für Incident-Kontext im QA-&-Governance-Bereich."""

    def __init__(
        self,
        incident_id: str = "(keine)",
        severity: str = "—",
        status: str = "—",
        last_activity: str = "—",
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("incidentInspector")
        self._incident_id = incident_id
        self._severity = severity
        self._status = status
        self._last_activity = last_activity
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        for title, text in [
            ("Incident-ID", self._incident_id),
            ("Severity", self._severity),
            ("Status", self._status),
            ("Letzte Aktivität", self._last_activity),
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

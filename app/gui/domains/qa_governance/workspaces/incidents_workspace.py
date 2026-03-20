"""
IncidentsWorkspace – Incident List, Severity, Status, Timeline.
Nutzt QAGovernanceService für reale Daten.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from app.gui.domains.qa_governance.workspaces.base_analysis_workspace import BaseAnalysisWorkspace
from app.gui.domains.qa_governance.panels.incidents_panels import (
    IncidentListPanel,
    IncidentSummaryPanel,
    IncidentDetailPanel,
)


class IncidentsWorkspace(BaseAnalysisWorkspace):
    """Workspace für Incidents."""

    def __init__(self, parent=None):
        super().__init__("qa_incidents", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(IncidentSummaryPanel(self))

        self._list_panel = IncidentListPanel(self)
        self._list_panel.incident_selected.connect(self._on_incident_selected)
        content_layout.addWidget(self._list_panel)

        self._detail_panel = IncidentDetailPanel(self)
        content_layout.addWidget(self._detail_panel)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")
        layout.addWidget(scroll)

    def _on_incident_selected(self, incident):
        self._detail_panel.set_incident(incident)
        if self._inspector_host:
            from app.gui.inspector.incident_inspector import IncidentInspector
            content = IncidentInspector(
                incident_id=incident.incident_id,
                severity=incident.severity,
                status=incident.status,
                last_activity=incident.detected_at,
            )
            self._inspector_host.set_content(content)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Incident-spezifischen Inspector. D9: content_token optional."""
        super().setup_inspector(inspector_host, content_token=content_token)
        from app.gui.inspector.incident_inspector import IncidentInspector
        content = IncidentInspector(
            incident_id="(keine)",
            severity="—",
            status="—",
            last_activity="—",
        )
        inspector_host.set_content(content, content_token=content_token)

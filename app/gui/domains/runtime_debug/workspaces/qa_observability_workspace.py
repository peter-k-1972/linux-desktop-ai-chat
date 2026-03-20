"""
QA Observability Workspace – Host für das QA Observability Panel.

Zeigt QA-Health-Metriken aus docs/qa/artifacts/json/ im Runtime/Debug-Bereich.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from app.gui.domains.runtime_debug.workspaces.base_monitoring_workspace import BaseMonitoringWorkspace
from app.gui.domains.runtime_debug.panels.qa_observability_panel import QAObservabilityPanel


class QAObservabilityWorkspace(BaseMonitoringWorkspace):
    """Workspace für QA Observability – Coverage, Risk, Incidents, Tests, Stability."""

    def __init__(self, parent=None):
        super().__init__("rd_qa_observability", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._panel = QAObservabilityPanel(self)
        layout.addWidget(self._panel)

"""
QA Cockpit Workspace – Host für das QA Cockpit Panel.

Zeigt QA-Health aus docs/qa/artifacts/json/ im Runtime/Debug-Bereich.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout
from app.gui.domains.runtime_debug.workspaces.base_monitoring_workspace import BaseMonitoringWorkspace
from app.debug.qa_cockpit_panel import QACockpitPanel


class QACockpitWorkspace(BaseMonitoringWorkspace):
    """Workspace für QA Cockpit – Test Inventory, Coverage, Risk, Gaps, Incidents, Stability."""

    def __init__(self, parent=None):
        super().__init__("rd_qa_cockpit", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self._panel = QACockpitPanel(self)
        layout.addWidget(self._panel)

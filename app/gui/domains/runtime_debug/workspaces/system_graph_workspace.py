"""
SystemGraphWorkspace – Systemübersicht, Komponenten, strukturierte Darstellung.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame, QLabel
from app.gui.domains.runtime_debug.workspaces.base_monitoring_workspace import BaseMonitoringWorkspace
from app.gui.domains.runtime_debug.panels.system_graph_panels import SystemGraphPanel
from app.gui.domains.runtime_debug.rd_surface_styles import rd_scroll_area_qss


class SystemGraphWorkspace(BaseMonitoringWorkspace):
    """Workspace für System Graph."""

    def __init__(self, parent=None):
        super().__init__("rd_system_graph", parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(SystemGraphPanel(self))

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(rd_scroll_area_qss())
        layout.addWidget(scroll)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt System-Node-spezifischen Inspector. D9: content_token optional."""
        self._inspector_host = inspector_host
        from app.gui.inspector.system_node_inspector import SystemNodeInspector
        content = SystemNodeInspector(
            node="Chat",
            status="Active",
            connections="Agents, Models",
        )
        inspector_host.set_content(content, content_token=content_token)

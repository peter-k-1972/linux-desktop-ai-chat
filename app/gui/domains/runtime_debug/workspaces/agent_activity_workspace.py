"""
AgentActivityWorkspace – Systemmonitor für Agentenaktivität.

AgentActivityStream, AgentStatusPanel, ActivityDetailPanel.
Vollständig an DebugStore und EventBus angebunden.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QScrollArea, QFrame
from app.gui.domains.runtime_debug.workspaces.base_monitoring_workspace import BaseMonitoringWorkspace
from app.gui.domains.runtime_debug.panels.agent_activity_stream_panel import AgentActivityStreamPanel
from app.gui.domains.runtime_debug.panels.agent_status_panel import AgentStatusPanel
from app.gui.domains.runtime_debug.panels.activity_detail_panel import ActivityDetailPanel
from app.gui.domains.runtime_debug.rd_surface_styles import rd_page_title_qss


class AgentActivityWorkspace(BaseMonitoringWorkspace):
    """Workspace für Agent Activity – chronologischer Stream, Status, Details."""

    def __init__(self, parent=None):
        super().__init__("rd_agent_activity", parent)
        self._inspector_host = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Agent Activity")
        title.setStyleSheet(rd_page_title_qss())
        layout.addWidget(title)

        grid = QGridLayout()
        grid.setSpacing(16)

        self._stream = AgentActivityStreamPanel(self)
        self._status = AgentStatusPanel(self)
        self._detail = ActivityDetailPanel(self)

        grid.addWidget(self._stream, 0, 0, 1, 2)
        grid.addWidget(self._status, 1, 0)
        grid.addWidget(self._detail, 1, 1)

        layout.addLayout(grid)

    def on_activity_selected(self, event) -> None:
        """Wird von AgentActivityStreamPanel aufgerufen bei Klick."""
        self._detail.set_event(event)
        self._refresh_inspector(event)

    def _refresh_inspector(self, event, content_token: int | None = None) -> None:
        """Aktualisiert den Inspector mit ausgewählter Aktivität."""
        if not self._inspector_host:
            return
        from app.gui.inspector.runtime_agent_inspector import RuntimeAgentInspector
        if event:
            content = RuntimeAgentInspector(
                agent=event.agent_name or "—",
                current_task=event.message or "—",
                status=event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type),
                last_action=event.message or "—",
            )
        else:
            content = RuntimeAgentInspector()
        self._inspector_host.set_content(content, content_token=content_token)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Agent-spezifischen Inspector (Runtime-Ansicht). D9: content_token optional."""
        self._inspector_host = inspector_host
        self._refresh_inspector(None, content_token=content_token)

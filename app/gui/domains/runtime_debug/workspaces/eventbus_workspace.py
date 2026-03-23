"""
EventBusWorkspace – Event Stream aus DebugStore.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from app.gui.domains.runtime_debug.workspaces.base_monitoring_workspace import BaseMonitoringWorkspace
from app.gui.domains.runtime_debug.panels.eventbus_panels import EventStreamPanel, EventDetailPanel
from app.gui.domains.runtime_debug.rd_surface_styles import rd_scroll_area_qss
from app.debug.agent_event import AgentEvent


class EventBusWorkspace(BaseMonitoringWorkspace):
    """Workspace für EventBus – echte Events aus DebugStore."""

    def __init__(self, parent=None):
        super().__init__("rd_eventbus", parent)
        self._inspector_host = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self._stream = EventStreamPanel(self)
        self._detail = EventDetailPanel(self)
        content_layout.addWidget(self._stream)
        content_layout.addWidget(self._detail)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet(rd_scroll_area_qss())
        layout.addWidget(scroll)

    def on_event_selected(self, event: AgentEvent | None) -> None:
        self._detail.set_event(event)
        self._refresh_inspector(event)

    def _refresh_inspector(self, event, content_token: int | None = None) -> None:
        if not self._inspector_host:
            return
        from app.gui.inspector.event_inspector import EventInspector
        if event:
            t = event.event_type.value if hasattr(event.event_type, "value") else str(event.event_type)
            ts = event.timestamp.strftime("%H:%M:%S") if event.timestamp else ""
            import json
            payload = json.dumps(event.metadata or {}, ensure_ascii=False)[:100]
            content = EventInspector(
                event_type=t,
                timestamp=ts,
                source=event.agent_name or "—",
                payload=payload,
            )
        else:
            content = EventInspector(event_type="—", timestamp="—", source="—", payload="Event auswählen…")
        self._inspector_host.set_content(content, content_token=content_token)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """D9: content_token optional."""
        self._inspector_host = inspector_host
        self._refresh_inspector(None, content_token=content_token)

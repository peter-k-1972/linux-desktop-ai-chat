"""
MetricsWorkspace – Runtime-Metriken aus echten Quellen.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from app.gui.domains.runtime_debug.workspaces.base_monitoring_workspace import BaseMonitoringWorkspace
from app.gui.domains.runtime_debug.panels.metrics_panels import MetricsOverviewPanel


class MetricsWorkspace(BaseMonitoringWorkspace):
    """Workspace für Metrics – Chats, Agent Tasks, LLM Calls, Runtime."""

    def __init__(self, parent=None):
        super().__init__("rd_metrics", parent)
        self._inspector_host = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        content_layout.addWidget(MetricsOverviewPanel(self))

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #0f172a; border: none; }")
        layout.addWidget(scroll)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt Metrics-spezifischen Inspector mit Live-Daten. D9: content_token optional."""
        self._inspector_host = inspector_host
        self._refresh_inspector(content_token=content_token)

    def _refresh_inspector(self, content_token: int | None = None) -> None:
        if not self._inspector_host:
            return
        from app.gui.inspector.metrics_inspector import MetricsInspector
        chat_count = "—"
        llm_count = "—"
        model_runtime = "—"
        try:
            from app.services.chat_service import get_chat_service
            from app.debug.debug_store import get_debug_store
            from app.debug.agent_event import EventType
            chat_count = str(len(get_chat_service().list_chats()))
            events = get_debug_store().get_event_history()
            llm_count = str(sum(1 for e in events if e.event_type == EventType.MODEL_CALL))
            total = sum(e.metadata.get("duration_sec", 0) or 0 for e in events if e.event_type == EventType.MODEL_CALL)
            model_runtime = f"{total:.1f}s" if total > 0 else "—"
        except Exception:
            pass
        content = MetricsInspector(
            cpu="—",
            model_runtime=model_runtime,
            request_count=llm_count,
        )
        self._inspector_host.set_content(content, content_token=content_token)

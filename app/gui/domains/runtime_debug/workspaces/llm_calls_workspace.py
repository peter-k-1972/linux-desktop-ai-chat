"""
LLMCallsWorkspace – LLM Call History und Detail mit echten Daten.
"""

from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QFrame
from app.gui.domains.runtime_debug.workspaces.base_monitoring_workspace import BaseMonitoringWorkspace
from app.gui.domains.runtime_debug.panels.llm_calls_panels import LLMCallHistoryPanel, LLMCallDetailPanel
from app.debug.agent_event import AgentEvent


class LLMCallsWorkspace(BaseMonitoringWorkspace):
    """Workspace für LLM Calls – echte Modellaufrufe aus DebugStore."""

    def __init__(self, parent=None):
        super().__init__("rd_llm_calls", parent)
        self._inspector_host = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 0, 0, 0)

        self._history = LLMCallHistoryPanel(self)
        self._detail = LLMCallDetailPanel(self)
        content_layout.addWidget(self._history)
        content_layout.addWidget(self._detail)

        scroll = QScrollArea()
        scroll.setWidget(content)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: #0f172a; border: none; }")
        layout.addWidget(scroll)

    def on_llm_call_selected(self, event: AgentEvent | None) -> None:
        self._detail.set_event(event)
        self._refresh_inspector(event)

    def _refresh_inspector(self, event, content_token: int | None = None) -> None:
        if not self._inspector_host:
            return
        from app.gui.inspector.llm_call_inspector import LLMCallInspector
        if event:
            model = event.metadata.get("model_id") or event.message or "—"
            dur = event.metadata.get("duration_sec")
            dur_str = f"{dur:.1f}s" if dur is not None else "—"
            content = LLMCallInspector(
                model=model,
                tokens="—",
                duration=dur_str,
                status="OK",
                prompt_preview=(event.message or "")[:100],
            )
        else:
            content = LLMCallInspector(model="—", tokens="—", duration="—", status="—", prompt_preview="Aufruf auswählen…")
        self._inspector_host.set_content(content, content_token=content_token)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """D9: content_token optional."""
        self._inspector_host = inspector_host
        self._refresh_inspector(None, content_token=content_token)

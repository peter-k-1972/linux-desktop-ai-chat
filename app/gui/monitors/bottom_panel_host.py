"""
BottomPanelHost – Host für Bottom-Monitor-Panels.

QTabWidget mit Logs, Events, Metrics, Agent Activity, LLM Trace – alle mit echten Daten.
"""

from PySide6.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from app.gui.monitors.logs_monitor import LogsMonitor
from app.gui.monitors.events_monitor import EventsMonitor
from app.gui.monitors.metrics_monitor import MetricsMonitor
from app.gui.monitors.agent_activity_monitor import AgentActivityMonitor
from app.gui.monitors.llm_trace_monitor import LLMTraceMonitor


class BottomPanelHost(QWidget):
    """Bottom-Panel mit Tabs für Monitore."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("bottomPanelHost")
        self._setup_ui()

    def _setup_ui(self):
        self._tabs = QTabWidget()
        self._tabs.setObjectName("bottomPanelTabs")
        self._tabs.addTab(LogsMonitor(self), "Logs")
        self._tabs.addTab(EventsMonitor(self), "Events")
        self._tabs.addTab(MetricsMonitor(self), "Metriken")
        self._tabs.addTab(AgentActivityMonitor(self), "Agent-Aktivität")
        self._tabs.addTab(LLMTraceMonitor(self), "LLM-Trace")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._tabs)

"""Dashboard-Panels."""

from app.gui.domains.dashboard.panels.system_status_panel import SystemStatusPanel
from app.gui.domains.dashboard.panels.active_work_panel import ActiveWorkPanel
from app.gui.domains.dashboard.panels.qa_status_panel import QAStatusPanel
from app.gui.domains.dashboard.panels.incidents_panel import IncidentsPanel

__all__ = [
    "SystemStatusPanel",
    "ActiveWorkPanel",
    "QAStatusPanel",
    "IncidentsPanel",
]

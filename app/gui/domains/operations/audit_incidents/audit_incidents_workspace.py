"""
Operations-Workspace: Audit-Aktivität, Incidents (R1), Plattform (R2).

Keine Fachlogik — nur Anbindung an Services / Panels.
"""

from PySide6.QtWidgets import QTabWidget, QVBoxLayout

from app.gui.domains.operations.audit_incidents.panels.audit_activity_panel import AuditActivityPanel
from app.gui.domains.operations.audit_incidents.panels.incidents_panel import IncidentsPanel
from app.gui.domains.operations.audit_incidents.panels.platform_health_panel import PlatformHealthPanel
from app.gui.shared.base_operations_workspace import BaseOperationsWorkspace


class AuditIncidentsWorkspace(BaseOperationsWorkspace):
    def __init__(self, parent=None):
        super().__init__("audit_incidents", parent)
        self._tabs = QTabWidget()
        self._activity = AuditActivityPanel(self)
        self._incidents = IncidentsPanel(self)
        self._platform = PlatformHealthPanel(self)
        self._tabs.addTab(self._activity, "Aktivität")
        self._tabs.addTab(self._incidents, "Störungen")
        self._tabs.addTab(self._platform, "Plattform")
        self._tabs.currentChanged.connect(self._on_tab)
        root = QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)
        root.addWidget(self._tabs, 1)
        self._activity.refresh()

    def open_with_context(self, ctx: dict) -> None:
        """R2: Tab per ``audit_incidents_tab`` steuern."""
        if not ctx:
            return
        tab = (ctx.get("audit_incidents_tab") or "").strip().lower()
        if tab == "platform":
            self._tabs.setCurrentIndex(2)
            self._platform.refresh()
        elif tab == "incidents":
            self._tabs.setCurrentIndex(1)
            self._incidents.refresh()
        elif tab == "activity":
            self._tabs.setCurrentIndex(0)
            self._activity.refresh()

    def _on_tab(self, index: int) -> None:
        if index == 0:
            self._activity.refresh()
        elif index == 1:
            self._incidents.refresh()
        elif index == 2:
            self._platform.refresh()

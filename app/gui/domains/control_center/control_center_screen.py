"""
ControlCenterScreen – Koordinator für Control-Center-Workspaces.

Systemübersicht auf Konfigurationsebene.
Verwaltung zentraler Systembausteine: Models, Providers, Agents, Tools, Data Stores.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from app.gui.shared import BaseScreen
from app.gui.navigation.nav_areas import NavArea
from app.gui.domains.control_center.control_center_nav import ControlCenterNav
from app.gui.domains.control_center.workspaces import (
    ModelsWorkspace,
    ProvidersWorkspace,
    AgentsWorkspace,
    ToolsWorkspace,
    DataStoresWorkspace,
)


class ControlCenterScreen(BaseScreen):
    """Control-Center-Container: Nav + Workspace-Stack."""

    def __init__(self, parent=None):
        super().__init__(NavArea.CONTROL_CENTER, parent)
        self._stack_indices: dict[str, int] = {}
        self._inspector_host = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._nav = ControlCenterNav(self)
        layout.addWidget(self._nav)

        self._stack = QStackedWidget()
        self._stack.setObjectName("controlCenterWorkspaceHost")

        workspaces = [
            ("cc_models", ModelsWorkspace),
            ("cc_providers", ProvidersWorkspace),
            ("cc_agents", AgentsWorkspace),
            ("cc_tools", ToolsWorkspace),
            ("cc_data_stores", DataStoresWorkspace),
        ]

        for area_id, workspace_class in workspaces:
            w = workspace_class(self)
            idx = self._stack.addWidget(w)
            self._stack_indices[area_id] = idx

        layout.addWidget(self._stack, 1)

        self._stack.currentChanged.connect(self._on_workspace_changed)
        self._nav.set_current("cc_models")

    def _connect_signals(self):
        self._nav.workspace_selected.connect(self._on_nav_selected)

    def _on_nav_selected(self, workspace_id: str):
        if workspace_id in self._stack_indices:
            self._stack.setCurrentIndex(self._stack_indices[workspace_id])
            self._nav.set_current(workspace_id)
            try:
                from app.gui.breadcrumbs import get_breadcrumb_manager
                mgr = get_breadcrumb_manager()
                if mgr:
                    mgr.set_workspace(self.area_id, workspace_id)
            except Exception:
                pass

    def show_workspace(self, workspace_id: str) -> None:
        """Zeigt einen Workspace (z.B. cc_agents). Für Command Palette."""
        self._on_nav_selected(workspace_id)

    def get_current_workspace(self) -> str | None:
        """Aktueller Workspace für Breadcrumbs."""
        idx = self._stack.currentIndex()
        for ws_id, i in self._stack_indices.items():
            if i == idx:
                return ws_id
        return None

    def _on_workspace_changed(self, index: int):
        """Aktualisiert den Inspector bei Workspace-Wechsel. D9: Token verhindert stale Updates."""
        if not self._inspector_host:
            return
        content_token = self._inspector_host.prepare_for_setup()
        widget = self._stack.widget(index)
        if widget and hasattr(widget, "setup_inspector"):
            widget.setup_inspector(self._inspector_host, content_token=content_token)
        else:
            self._inspector_host.clear_content()

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Wird von WorkspaceHost aufgerufen. Delegiert an aktuellen Workspace. D9: content_token optional."""
        self._inspector_host = inspector_host
        token = content_token if content_token is not None else inspector_host.prepare_for_setup()
        widget = self._stack.widget(self._stack.currentIndex())
        if widget and hasattr(widget, "setup_inspector"):
            widget.setup_inspector(inspector_host, content_token=token)
        else:
            inspector_host.clear_content()

"""
OperationsScreen – Koordinator für Operations-Unterworkspaces.

OperationsNav + OperationsWorkspaceHost. Keine God-Class.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from PySide6.QtCore import Qt
from app.gui.shared import BaseScreen
from app.gui.navigation.nav_areas import NavArea
from app.gui.domains.operations.operations_nav import OperationsNav
from app.gui.domains.operations.projects import ProjectsWorkspace
from app.gui.domains.operations.chat import ChatWorkspace
from app.gui.domains.operations.agent_tasks import AgentTasksWorkspace
from app.gui.domains.operations.knowledge import KnowledgeWorkspace


class OperationsScreen(BaseScreen):
    """Operations-Container: Nav + Workspace-Stack."""

    def __init__(self, parent=None):
        super().__init__(NavArea.OPERATIONS, parent)
        self._stack_indices: dict[str, int] = {}
        self._inspector_host = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._nav = OperationsNav(self)
        layout.addWidget(self._nav)

        self._stack = QStackedWidget()
        self._stack.setObjectName("operationsWorkspaceHost")

        from app.gui.domains.operations.prompt_studio import PromptStudioWorkspace

        workspaces = [
            ("operations_projects", ProjectsWorkspace),
            ("operations_chat", ChatWorkspace),
            ("operations_agent_tasks", AgentTasksWorkspace),
            ("operations_knowledge", KnowledgeWorkspace),
            ("operations_prompt_studio", PromptStudioWorkspace),
        ]

        for area_id, workspace_class in workspaces:
            w = workspace_class(self)
            idx = self._stack.addWidget(w)
            self._stack_indices[area_id] = idx

        layout.addWidget(self._stack, 1)

        self._stack.currentChanged.connect(self._on_workspace_changed)
        self._nav.set_current("operations_projects")

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
        """Zeigt einen Workspace (z.B. operations_chat). Für Command Palette und Project Hub."""
        self._on_nav_selected(workspace_id)
        try:
            from app.gui.domains.operations.operations_context import consume_pending_context
            ctx = consume_pending_context()
            if ctx and workspace_id in self._stack_indices:
                widget = self._stack.widget(self._stack_indices[workspace_id])
                if widget and hasattr(widget, "open_with_context"):
                    widget.open_with_context(ctx)
        except Exception:
            pass

    def get_current_workspace(self) -> str | None:
        """Aktueller Workspace für Breadcrumbs."""
        idx = self._stack.currentIndex()
        for ws_id, i in self._stack_indices.items():
            if i == idx:
                return ws_id
        return None

    def _on_workspace_changed(self, index: int):
        """Aktualisiert den Inspector bei Workspace-Wechsel. Clear vor Setup verhindert stale Content."""
        if not self._inspector_host:
            return
        widget = self._stack.widget(index)
        if widget and hasattr(widget, "setup_inspector"):
            content_token = self._inspector_host.prepare_for_setup()
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

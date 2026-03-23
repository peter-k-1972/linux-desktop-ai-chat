"""
RuntimeDebugScreen – Koordinator für Runtime-/Debug-Workspaces.

Systemzustände, Event-Streams, Laufzeitmetriken, LLM-Aufrufe, Agent-Aktivitäten.
"""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QStackedWidget
from app.gui.shared import BaseScreen
from app.gui.navigation.nav_areas import NavArea
from app.gui.domains.runtime_debug.runtime_debug_nav import RuntimeDebugNav
from app.gui.devtools.markdown_demo_panel import MarkdownDemoWorkspace
from app.gui.domains.runtime_debug.workspaces import (
    EventBusWorkspace,
    LogsWorkspace,
    MetricsWorkspace,
    LLMCallsWorkspace,
    AgentActivityWorkspace,
    SystemGraphWorkspace,
    IntrospectionWorkspace,
    QAObservabilityWorkspace,
    QACockpitWorkspace,
)


class RuntimeDebugScreen(BaseScreen):
    """Runtime-/Debug-Container: Nav + Workspace-Stack."""

    def __init__(self, parent=None):
        super().__init__(NavArea.RUNTIME_DEBUG, parent)
        self._stack_indices: dict[str, int] = {}
        self._inspector_host = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._nav = RuntimeDebugNav(self)
        layout.addWidget(self._nav)

        self._stack = QStackedWidget()
        self._stack.setObjectName("runtimeDebugWorkspaceHost")

        workspaces: list[tuple[str, type]] = [
            ("rd_introspection", IntrospectionWorkspace),
            ("rd_qa_cockpit", QACockpitWorkspace),
            ("rd_qa_observability", QAObservabilityWorkspace),
            ("rd_markdown_demo", MarkdownDemoWorkspace),
            ("rd_eventbus", EventBusWorkspace),
            ("rd_logs", LogsWorkspace),
            ("rd_metrics", MetricsWorkspace),
            ("rd_llm_calls", LLMCallsWorkspace),
            ("rd_agent_activity", AgentActivityWorkspace),
            ("rd_system_graph", SystemGraphWorkspace),
        ]
        from app.gui.devtools.devtools_visibility import is_theme_visualizer_available

        if is_theme_visualizer_available():
            from app.gui.devtools.theme_visualizer_workspace import ThemeVisualizerEntryWorkspace

            ins = next(i for i, w in enumerate(workspaces) if w[0] == "rd_markdown_demo")
            workspaces.insert(ins + 1, ("rd_theme_visualizer", ThemeVisualizerEntryWorkspace))

        for area_id, workspace_class in workspaces:
            w = workspace_class(self)
            idx = self._stack.addWidget(w)
            self._stack_indices[area_id] = idx

        layout.addWidget(self._stack, 1)

        self._stack.currentChanged.connect(self._on_workspace_changed)
        self._nav.set_current("rd_introspection")
        self._stack.setCurrentIndex(self._stack_indices["rd_introspection"])

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
        """Zeigt einen Workspace (z.B. rd_metrics). Für Command Palette."""
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

"""
Wires explorer → canvas router, canvas selection → inspector, and optional console hooks.
"""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject

from app.gui.workbench.canvas.canvas_base import CanvasKind, WorkbenchCanvasBase
from app.gui.workbench.canvas.canvas_router import CanvasRouter
from app.gui.workbench.explorer.explorer_items import ExplorerItemRef, ExplorerNodeKind
from app.gui.workbench.inspector.inspector_router import InspectorRouter


class WorkbenchController(QObject):
    def __init__(self, window: "MainWorkbench") -> None:
        super().__init__(window)
        self._window = window
        self._canvas_router = CanvasRouter(window.canvas_tabs, parent=window.canvas_tabs)
        self._inspector_router = InspectorRouter()
        self._ai_inspector_unsub: Callable[[], None] | None = None

        ex = window.explorer_panel
        ex.explorer_item_activated.connect(self._on_explorer_item)

        window.canvas_tabs.tab_canvas_changed.connect(self._on_tab_canvas_changed)
        self._on_tab_canvas_changed(window.canvas_tabs.current_canvas())

        window.console_panel.log_output(
            "Workbench ready — use Explorer (Library → Workflows) or Ctrl+Shift+P. "
            "Focus follows the active tab; contextual actions sit above the canvas."
        )

    @property
    def canvas_router(self) -> CanvasRouter:
        return self._canvas_router

    def _on_explorer_item(self, ref: object) -> None:
        if not isinstance(ref, ExplorerItemRef):
            return
        if ref.kind == ExplorerNodeKind.FOLDER:
            return
        self._window.explorer_panel.record_activation(ref)
        if ref.kind == ExplorerNodeKind.WF_TEST_AGENT and ref.payload:
            self._canvas_router.open_agent_test(ref.payload)
            return
        if ref.kind == ExplorerNodeKind.WF_KNOWLEDGE_BASE and ref.payload:
            self._canvas_router.open_knowledge_base_workflow(
                kb_id=str(ref.payload),
                display_name=str(ref.payload).replace("-", " ").title(),
            )
            return
        if ref.kind == ExplorerNodeKind.WF_BUILD_WORKFLOW and ref.payload:
            self._canvas_router.open_workflow_builder(str(ref.payload))
            return
        if ref.kind == ExplorerNodeKind.WF_PROMPT_DEV and ref.payload:
            self._canvas_router.open_prompt_development(str(ref.payload))
            return
        if ref.kind == ExplorerNodeKind.WF_MODEL_COMPARE and ref.payload:
            self._canvas_router.open_model_compare(str(ref.payload))
            return
        if ref.kind == ExplorerNodeKind.PROJECT_WORKFLOWS and ref.payload:
            self._canvas_router.open_workflow_builder(str(ref.payload).replace("/", "-")[:32] or "draft")
            return
        if ref.kind == ExplorerNodeKind.PROJECT_AGENTS and ref.payload:
            self._canvas_router.open_agent_test("demo-agent")
            return
        if ref.kind == ExplorerNodeKind.LIB_PROMPTS and ref.payload:
            self._canvas_router.open_prompt_development()
            return
        if ref.kind == ExplorerNodeKind.LIB_MODELS and ref.payload:
            self._canvas_router.open_model_compare()
            return
        if ref.kind == ExplorerNodeKind.AGENT and ref.payload:
            self._canvas_router.open_agent_test(ref.payload)
            return
        if ref.kind == ExplorerNodeKind.WORKFLOW and ref.payload:
            self._canvas_router.open_workflow(ref.payload)
            return
        if ref.kind == ExplorerNodeKind.FILE and ref.payload:
            self._canvas_router.open_file(ref.payload)
            return
        if ref.kind == ExplorerNodeKind.CHAT and ref.payload:
            self._canvas_router.open_chat(ref.payload)
            return
        if ref.kind == ExplorerNodeKind.LIB_KNOWLEDGE:
            self._canvas_router.open_knowledge_base_workflow(display_name="Knowledge base")
            return
        if ref.kind == ExplorerNodeKind.RT_LOGS:
            self._window.focus_console()
            return
        if ref.payload:
            title = ref.path_labels[-1] if ref.path_labels else ref.payload
            self._canvas_router.open_feature_page(ref.payload, title)

    def _on_tab_canvas_changed(self, canvas: WorkbenchCanvasBase | None) -> None:
        self._window.focus_controller.set_active_from_canvas(canvas)

        if self._ai_inspector_unsub is not None:
            self._ai_inspector_unsub()
            self._ai_inspector_unsub = None

        self._apply_inspector(canvas)

        if canvas is None:
            return

        from app.gui.workbench.ai_canvas.ai_canvas_widget import AiFlowEditorCanvas
        from app.gui.workbench.workflows.workflow_builder_canvas import WorkflowBuilderCanvas

        graph_canvas = None
        if isinstance(canvas, AiFlowEditorCanvas):
            graph_canvas = canvas
        elif isinstance(canvas, WorkflowBuilderCanvas):
            graph_canvas = canvas

        if graph_canvas is not None:
            sc = graph_canvas.graphics_scene()

            def _on_sel() -> None:
                self._apply_inspector(canvas)

            sc.selectionChanged.connect(_on_sel)
            self._ai_inspector_unsub = lambda: sc.selectionChanged.disconnect(_on_sel)

    def _apply_inspector(self, canvas: WorkbenchCanvasBase | None) -> None:
        insp = self._inspector_router.inspector_for_canvas(canvas, parent=self._window.inspector_panel)
        self._window.inspector_panel.set_inspector(insp)

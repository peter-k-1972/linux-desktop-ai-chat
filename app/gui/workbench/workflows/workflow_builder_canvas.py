"""
Task canvas: workflow design on the AI graph surface with builder-specific header actions.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from app.gui.workbench.ai_canvas.ai_canvas_widget import AiCanvasWidget
from app.gui.workbench.canvas.canvas_base import CanvasKind, WorkbenchCanvasBase
from app.gui.workbench.workflows.workflow_header import WorkflowCanvasHeader


class WorkflowBuilderCanvas(WorkbenchCanvasBase):
    """Same graph engine as AI Canvas; distinct tab key and Run/Validate/Export/Duplicate header."""

    def __init__(self, workflow_key: str = "draft", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.workflow_key = workflow_key

        def _log(msg: str) -> None:
            win = self.window()
            if hasattr(win, "console_panel"):
                win.console_panel.log_output(f"[Workflow {workflow_key}] {msg}")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(
            WorkflowCanvasHeader(
                "Build workflow",
                "Add nodes, connect them, validate, then run. Execution/debug strip below.",
                [
                    ("Run", lambda: _log("Run (hook)")),
                    ("Validate", lambda: _log("Validate (hook)")),
                    ("Export", lambda: _log("Export (hook)")),
                    ("Duplicate", lambda: _log("Duplicate (hook)")),
                ],
                parent=self,
            )
        )

        self._body = AiCanvasWidget(self)
        outer.addWidget(self._body, 1)

        strip = QFrame(self)
        strip.setObjectName("workbenchAiStatusStrip")
        sl = QHBoxLayout(strip)
        sl.setContentsMargins(12, 8, 12, 8)
        self._status = QLabel(self)
        self._status.setObjectName("workbenchAiStatusText")
        sl.addWidget(self._status)
        outer.addWidget(strip)

        self._body.status_changed.connect(self._status.setText)
        self._body.update_status_display()

    def graph_view_inner(self) -> AiCanvasWidget:
        return self._body

    def graphics_scene(self):
        return self._body.graphics_scene()

    def graph_document(self):
        return self._body.graph_document()

    def selected_node_id(self) -> str | None:
        return self._body.selected_node_id()

    @property
    def canvas_kind(self) -> CanvasKind:
        return CanvasKind.WF_WORKFLOW_BUILDER

    @property
    def tab_key(self) -> str:
        return f"wf:workflow-builder:{self.workflow_key}"

    @property
    def tab_title(self) -> str:
        return "Build workflow"

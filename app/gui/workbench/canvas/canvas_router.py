"""
Maps explorer / shell events to concrete canvas tabs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QWidget

from app.gui.workbench.canvas.canvas_base import (
    AgentEditorCanvas,
    ChatCanvas,
    FileViewerCanvas,
    StubFeatureCanvas,
    WorkflowEditorCanvas,
)
from app.gui.workbench.workflows.agent_test_canvas import AgentTestCanvas
from app.gui.workbench.workflows.knowledge_base_canvas import KnowledgeBaseWorkflowCanvas
from app.gui.workbench.workflows.model_compare_canvas import ModelCompareCanvas
from app.gui.workbench.workflows.prompt_dev_canvas import PromptDevelopmentCanvas
from app.gui.workbench.workflows.workflow_builder_canvas import WorkflowBuilderCanvas

if TYPE_CHECKING:
    from app.gui.workbench.canvas.canvas_tabs import CanvasTabs


class CanvasRouter:
    """Opens or focuses the appropriate :class:`WorkbenchCanvasBase` subclass."""

    def __init__(self, canvas_tabs: CanvasTabs, parent: QWidget | None = None) -> None:
        self._tabs = canvas_tabs
        self._parent = parent

    def open_agent(self, agent_id: str) -> None:
        self._tabs.open_canvas(AgentEditorCanvas(agent_id, self._parent))

    def open_agent_test(self, agent_id: str = "demo-agent") -> None:
        """Task workflow: chat/test + inspector sections."""
        self._tabs.open_canvas(AgentTestCanvas(agent_id, self._parent))

    def open_workflow(self, workflow_id: str) -> None:
        self._tabs.open_canvas(WorkflowEditorCanvas(workflow_id, self._parent))

    def open_file(self, file_path: str) -> None:
        self._tabs.open_canvas(FileViewerCanvas(file_path, self._parent))

    def open_chat(self, session_key: str = "default") -> None:
        self._tabs.open_canvas(ChatCanvas(session_key, self._parent))

    def open_feature_page(self, feature_key: str, title: str) -> None:
        self._tabs.open_canvas(StubFeatureCanvas(feature_key, title, self._parent))

    def open_ai_flow_editor(self) -> None:
        from app.gui.workbench.ai_canvas.ai_canvas_widget import AiFlowEditorCanvas

        self._tabs.open_canvas(AiFlowEditorCanvas(self._parent))

    def open_knowledge_base_workflow(self, kb_id: str = "new-kb", display_name: str | None = None) -> None:
        self._tabs.open_canvas(KnowledgeBaseWorkflowCanvas(kb_id, display_name, self._parent))

    def open_workflow_builder(self, workflow_key: str = "draft") -> None:
        self._tabs.open_canvas(WorkflowBuilderCanvas(workflow_key, self._parent))

    def open_prompt_development(self, prompt_id: str = "draft") -> None:
        self._tabs.open_canvas(PromptDevelopmentCanvas(prompt_id, self._parent))

    def open_model_compare(self, compare_id: str = "session-1") -> None:
        self._tabs.open_canvas(ModelCompareCanvas(compare_id, self._parent))

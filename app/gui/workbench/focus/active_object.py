"""
Global focus descriptor: which domain object the workbench is editing or running.

Derived from the active canvas tab; drives inspector chrome, contextual toolbar, and palette gating.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.gui.workbench.ai_canvas.ai_canvas_widget import AiFlowEditorCanvas
from app.gui.workbench.canvas.canvas_base import (
    AgentEditorCanvas,
    CanvasKind,
    WorkbenchCanvasBase,
    WorkflowEditorCanvas,
)
from app.gui.workbench.focus.object_status import ObjectStatus
from app.gui.workbench.workflows.agent_test_canvas import AgentTestCanvas
from app.gui.workbench.workflows.knowledge_base_canvas import KnowledgeBaseWorkflowCanvas
from app.gui.workbench.workflows.model_compare_canvas import ModelCompareCanvas
from app.gui.workbench.workflows.prompt_dev_canvas import PromptDevelopmentCanvas
from app.gui.workbench.workflows.workflow_builder_canvas import WorkflowBuilderCanvas


# Stable type ids for actions, palette predicates, and telemetry.
OBJECT_NONE = "none"
OBJECT_AGENT = "agent"
OBJECT_WORKFLOW = "workflow"
OBJECT_PROMPT = "prompt"
OBJECT_KNOWLEDGE_BASE = "knowledge_base"
OBJECT_MODEL_COMPARE = "model_compare"
OBJECT_AI_CANVAS = "ai_canvas"
OBJECT_CHAT = "chat"
OBJECT_FILE = "file"
OBJECT_FEATURE = "feature"


@dataclass(slots=True)
class ActiveObject:
    """What the user is focused on in the central workspace."""

    object_type: str
    object_id: str | None
    tab_key: str | None
    status: ObjectStatus

    @staticmethod
    def none() -> ActiveObject:
        return ActiveObject(OBJECT_NONE, None, None, ObjectStatus.READY)

    def is_empty(self) -> bool:
        return self.object_type == OBJECT_NONE


def active_object_from_canvas(canvas: WorkbenchCanvasBase | None) -> ActiveObject:
    """Map concrete canvas widgets to a focus descriptor (minimal, extensible)."""
    if canvas is None:
        return ActiveObject.none()

    k = canvas.canvas_kind
    tab_key = canvas.tab_key

    if isinstance(canvas, AgentTestCanvas):
        return ActiveObject(OBJECT_AGENT, canvas.agent_id, tab_key, ObjectStatus.READY)
    if isinstance(canvas, AgentEditorCanvas):
        return ActiveObject(OBJECT_AGENT, canvas.agent_id, tab_key, ObjectStatus.READY)
    if isinstance(canvas, WorkflowBuilderCanvas):
        return ActiveObject(OBJECT_WORKFLOW, canvas.workflow_key, tab_key, ObjectStatus.READY)
    if isinstance(canvas, WorkflowEditorCanvas):
        return ActiveObject(OBJECT_WORKFLOW, canvas.workflow_id, tab_key, ObjectStatus.READY)
    if isinstance(canvas, PromptDevelopmentCanvas):
        return ActiveObject(OBJECT_PROMPT, canvas.prompt_id, tab_key, ObjectStatus.READY)
    if isinstance(canvas, KnowledgeBaseWorkflowCanvas):
        return ActiveObject(OBJECT_KNOWLEDGE_BASE, canvas.kb_id, tab_key, ObjectStatus.READY)
    if isinstance(canvas, ModelCompareCanvas):
        return ActiveObject(OBJECT_MODEL_COMPARE, canvas.compare_id, tab_key, ObjectStatus.READY)
    if isinstance(canvas, AiFlowEditorCanvas):
        return ActiveObject(OBJECT_AI_CANVAS, None, tab_key, ObjectStatus.READY)

    if k == CanvasKind.CHAT:
        return ActiveObject(OBJECT_CHAT, canvas.session_key, tab_key, ObjectStatus.READY)
    if k == CanvasKind.FILE:
        return ActiveObject(OBJECT_FILE, canvas.file_path, tab_key, ObjectStatus.READY)
    if k == CanvasKind.FEATURE:
        return ActiveObject(OBJECT_FEATURE, canvas.feature_key, tab_key, ObjectStatus.READY)

    return ActiveObject(k.name.lower(), None, tab_key, ObjectStatus.READY)

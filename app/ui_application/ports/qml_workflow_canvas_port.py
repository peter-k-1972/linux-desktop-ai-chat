"""
QML Workflow-Canvas — CRUD/Run über einen Port (kein direkter WorkflowService im ViewModel).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.workflows.models.definition import WorkflowDefinition
from app.workflows.models.run_summary import WorkflowRunSummary
from app.workflows.validation.graph_validator import ValidationResult


@runtime_checkable
class QmlWorkflowCanvasPort(Protocol):
    def list_workflows(self, *, project_scope_id: int | None, include_global: bool) -> list[WorkflowDefinition]:
        ...

    def list_run_summaries(self, workflow_id: str) -> list[WorkflowRunSummary]:
        ...

    def load_workflow(self, workflow_id: str) -> WorkflowDefinition:
        """Wirft :class:`WorkflowNotFoundError` bei unbekannter ID."""
        ...

    def save_workflow(self, definition: WorkflowDefinition) -> ValidationResult:
        ...

    def start_run(self, workflow_id: str, params: dict) -> None:
        ...

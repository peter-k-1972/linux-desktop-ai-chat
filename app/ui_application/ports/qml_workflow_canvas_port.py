"""
QML Workflow-Canvas — CRUD/Run über einen Port (kein direkter WorkflowService im ViewModel).
"""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from app.workflows.models.definition import WorkflowDefinition
from app.workflows.models.run import WorkflowRun
from app.workflows.models.run_summary import WorkflowRunSummary
from app.workflows.validation.graph_validator import ValidationResult


@runtime_checkable
class QmlWorkflowCanvasPort(Protocol):
    def get_active_project_id(self) -> int | None:
        """Product-wide active project (ProjectContextManager), for navigation hints."""
        ...

    def list_workflows(self, *, project_scope_id: int | None, include_global: bool) -> list[WorkflowDefinition]:
        ...

    def list_run_summaries(
        self,
        *,
        workflow_id: Optional[str] = None,
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[WorkflowRunSummary]:
        """Gleiche Semantik wie :meth:`WorkflowService.list_run_summaries`."""

    def load_workflow(self, workflow_id: str) -> WorkflowDefinition:
        """Wirft :class:`WorkflowNotFoundError` bei unbekannter ID."""
        ...

    def save_workflow(self, definition: WorkflowDefinition) -> ValidationResult:
        ...

    def validate_workflow(self, definition: WorkflowDefinition) -> ValidationResult:
        """Wie :meth:`WorkflowService.validate_workflow` (ohne Persistenz)."""

    def start_run(self, workflow_id: str, params: dict) -> str:
        """Startet einen Lauf; liefert ``run_id`` (:meth:`WorkflowService.start_run`)."""
        ...

    def get_run(self, run_id: str) -> WorkflowRun:
        """Wirft :class:`RunNotFoundError` bei unbekannter ID."""

    def start_run_from_previous(
        self,
        run_id: str,
        initial_input_override: Optional[dict] = None,
    ) -> WorkflowRun:
        """Neuer Lauf mit Produkt-Re-Run-Semantik (:meth:`WorkflowService.start_run_from_previous`)."""

"""Adapter: :class:`QmlWorkflowCanvasPort` → :class:`app.services.workflow_service.WorkflowService`."""

from __future__ import annotations

from app.services.workflow_service import get_workflow_service
from app.workflows.models.definition import WorkflowDefinition
from app.workflows.models.run_summary import WorkflowRunSummary
from app.workflows.validation.graph_validator import ValidationResult


class ServiceQmlWorkflowCanvasAdapter:
    def list_workflows(
        self,
        *,
        project_scope_id: int | None,
        include_global: bool,
    ) -> list[WorkflowDefinition]:
        return get_workflow_service().list_workflows(
            project_scope_id=project_scope_id,
            include_global=include_global,
        )

    def list_run_summaries(self, workflow_id: str) -> list[WorkflowRunSummary]:
        return get_workflow_service().list_run_summaries(workflow_id=workflow_id)

    def load_workflow(self, workflow_id: str) -> WorkflowDefinition:
        return get_workflow_service().load_workflow(workflow_id)

    def save_workflow(self, definition: WorkflowDefinition) -> ValidationResult:
        return get_workflow_service().save_workflow(definition)

    def start_run(self, workflow_id: str, params: dict) -> None:
        get_workflow_service().start_run(workflow_id, params)

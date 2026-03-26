"""Adapter: :class:`QmlWorkflowCanvasPort` → :class:`app.services.workflow_service.WorkflowService`."""

from __future__ import annotations

from typing import Optional

from app.services.workflow_service import get_workflow_service
from app.workflows.models.definition import WorkflowDefinition
from app.workflows.models.run import WorkflowRun
from app.workflows.models.run_summary import WorkflowRunSummary
from app.workflows.validation.graph_validator import ValidationResult


class ServiceQmlWorkflowCanvasAdapter:
    def get_active_project_id(self) -> int | None:
        try:
            from app.services.project_service import get_project_service

            return get_project_service().get_active_project_id()
        except Exception:
            return None

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

    def list_run_summaries(
        self,
        *,
        workflow_id: Optional[str] = None,
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[WorkflowRunSummary]:
        return get_workflow_service().list_run_summaries(
            workflow_id=workflow_id,
            project_id=project_id,
            status=status,
            limit=limit,
        )

    def load_workflow(self, workflow_id: str) -> WorkflowDefinition:
        return get_workflow_service().load_workflow(workflow_id)

    def save_workflow(self, definition: WorkflowDefinition) -> ValidationResult:
        return get_workflow_service().save_workflow(definition)

    def validate_workflow(self, definition: WorkflowDefinition) -> ValidationResult:
        return get_workflow_service().validate_workflow(definition)

    def start_run(self, workflow_id: str, params: dict) -> str:
        run = get_workflow_service().start_run(workflow_id, params)
        return run.run_id

    def get_run(self, run_id: str) -> WorkflowRun:
        return get_workflow_service().get_run(run_id)

    def start_run_from_previous(
        self,
        run_id: str,
        initial_input_override: Optional[dict] = None,
    ) -> WorkflowRun:
        return get_workflow_service().start_run_from_previous(
            run_id,
            initial_input_override,
        )

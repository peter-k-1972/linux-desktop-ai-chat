"""
AgentTasksSelectionSink — :class:`AgentOperationsDetailPanel` aus Contract-Zustand (Slice 2).
"""

from __future__ import annotations

from app.gui.domains.operations.agent_tasks.panels.agent_operations_detail_panel import (
    AgentOperationsDetailPanel,
)
from app.qa.operations_models import AgentOperationsIssue, AgentOperationsSummary
from app.ui_contracts.workspaces.agent_tasks_registry import (
    AgentTasksOperationsSummaryDto,
    AgentTasksSelectionViewState,
)


def _dto_to_summary(dto: AgentTasksOperationsSummaryDto) -> AgentOperationsSummary:
    issues = [
        AgentOperationsIssue(code=i.code, severity=i.severity, message=i.message)
        for i in dto.issues
    ]
    return AgentOperationsSummary(
        agent_id=dto.agent_id,
        slug=dto.slug,
        display_name=dto.display_name,
        status=dto.status,
        assigned_model=dto.assigned_model,
        model_role=dto.model_role,
        cloud_allowed=dto.cloud_allowed,
        last_activity_at=dto.last_activity_at,
        last_activity_source=dto.last_activity_source,
        issues=issues,
        workflow_definition_ids=list(dto.workflow_definition_ids),
    )


class AgentTasksSelectionSink:
    def __init__(self, detail_panel: AgentOperationsDetailPanel) -> None:
        self._detail = detail_panel

    def apply_selection_state(self, state: AgentTasksSelectionViewState) -> None:
        if state.phase == "idle":
            self._detail.set_read_error(None)
            self._detail.set_summary(None)
            return
        if state.phase == "error":
            self._detail.set_summary(None)
            msg = state.error.message if state.error else "Unbekannter Fehler."
            self._detail.set_read_error(msg)
            return
        self._detail.set_read_error(None)
        if state.summary is None:
            self._detail.set_summary(None)
        else:
            self._detail.set_summary(_dto_to_summary(state.summary))

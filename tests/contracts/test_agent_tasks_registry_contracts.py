"""Agent Tasks Registry (Slice 1) — Contracts."""

from __future__ import annotations

from dataclasses import asdict

from app.ui_contracts.workspaces.agent_tasks_registry import (
    AgentRegistryRowDto,
    AgentTasksOperationsIssueDto,
    AgentTasksOperationsSummaryDto,
    AgentTasksRegistryViewState,
    AgentTasksSelectionViewState,
    LoadAgentTaskSelectionCommand,
    LoadAgentTasksRegistryCommand,
    agent_tasks_registry_loading_state,
    agent_tasks_selection_idle_state,
)
from app.ui_contracts.common.errors import SettingsErrorInfo


def test_row_dto() -> None:
    r = AgentRegistryRowDto(agent_id="a1", list_item_text="Name\n  Status: x")
    assert asdict(r)["agent_id"] == "a1"


def test_view_state_ready() -> None:
    r = AgentRegistryRowDto(agent_id="x", list_item_text="t")
    st = AgentTasksRegistryViewState(phase="ready", rows=(r,))
    assert len(st.rows) == 1


def test_view_state_error() -> None:
    err = SettingsErrorInfo(code="c", message="m")
    st = AgentTasksRegistryViewState(phase="error", error=err)
    assert st.error == err


def test_loading_helper() -> None:
    assert agent_tasks_registry_loading_state().phase == "loading"


def test_load_command() -> None:
    assert LoadAgentTasksRegistryCommand(3).project_id == 3


def test_selection_command() -> None:
    c = LoadAgentTaskSelectionCommand("a1", 2)
    assert c.agent_id == "a1"
    assert c.project_id == 2


def test_selection_idle_helper() -> None:
    assert agent_tasks_selection_idle_state().phase == "idle"


def test_operations_summary_dto_serializable_fields() -> None:
    issue = AgentTasksOperationsIssueDto(code="X", severity="warning", message="m")
    dto = AgentTasksOperationsSummaryDto(
        agent_id="a",
        slug="s",
        display_name="d",
        status="active",
        assigned_model="m",
        model_role="chat",
        cloud_allowed=False,
        last_activity_at=None,
        last_activity_source="none",
        issues=(issue,),
        workflow_definition_ids=("w1",),
    )
    assert dto.issues[0].code == "X"
    st = AgentTasksSelectionViewState(phase="ready", summary=dto)
    assert st.summary is not None
    assert st.summary.workflow_definition_ids == ("w1",)


def test_selection_error_state() -> None:
    err = SettingsErrorInfo(code="e", message="fail")
    st = AgentTasksSelectionViewState(phase="error", error=err)
    assert st.phase == "error"

"""AgentTasksSelectionPresenter — Slice 2."""

from __future__ import annotations

from typing import Any

from app.ui_application.presenters.agent_tasks_selection_presenter import AgentTasksSelectionPresenter
from app.ui_contracts.workspaces.agent_tasks_inspector import AgentTasksInspectorReadDto
from app.ui_contracts.workspaces.agent_tasks_registry import (
    AgentTasksOperationsSummaryDto,
    AgentTasksSelectionViewState,
    LoadAgentTaskSelectionCommand,
    agent_tasks_selection_idle_state,
)
from app.ui_contracts.workspaces.agent_tasks_task_panel import AgentTaskPanelDto, LoadAgentTaskPanelCommand


class _FakeSink:
    def __init__(self) -> None:
        self.states: list[AgentTasksSelectionViewState] = []

    def apply_selection_state(self, state: AgentTasksSelectionViewState) -> None:
        self.states.append(state)


class _FakePort:
    def __init__(self, out: AgentTasksSelectionViewState) -> None:
        self._out = out
        self.commands: list[LoadAgentTaskSelectionCommand] = []

    def load_registry_view(self, project_id: int | None) -> Any:  # pragma: no cover
        del project_id
        raise NotImplementedError

    def load_agent_task_selection_detail(
        self,
        command: LoadAgentTaskSelectionCommand,
    ) -> AgentTasksSelectionViewState:
        self.commands.append(command)
        return self._out

    def load_agent_tasks_inspector_state(self, agent_id: str, project_id: int | None) -> AgentTasksInspectorReadDto:
        del agent_id, project_id
        return AgentTasksInspectorReadDto()

    def load_agent_task_panel(self, command: LoadAgentTaskPanelCommand) -> AgentTaskPanelDto:
        del command
        return AgentTaskPanelDto(agent_id="", task_count=0, recent_tasks=())


def test_presenter_forwards_port_to_sink() -> None:
    dto = AgentTasksOperationsSummaryDto(
        agent_id="a",
        slug="",
        display_name="",
        status="",
        assigned_model="",
        model_role="",
        cloud_allowed=False,
        last_activity_at=None,
        last_activity_source="none",
    )
    expected = AgentTasksSelectionViewState(phase="ready", summary=dto)
    sink = _FakeSink()
    port = _FakePort(expected)
    pres = AgentTasksSelectionPresenter(sink, port)
    pres.handle_command(LoadAgentTaskSelectionCommand("a", 1))
    assert sink.states == [expected]
    assert port.commands[0].agent_id == "a"


def test_presenter_idle_path() -> None:
    sink = _FakeSink()
    port = _FakePort(agent_tasks_selection_idle_state())
    AgentTasksSelectionPresenter(sink, port).handle_command(LoadAgentTaskSelectionCommand("", 1))
    assert sink.states[0].phase == "idle"

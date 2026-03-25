"""AgentTasksInspectorPresenter — Slice 3."""

from __future__ import annotations

from app.ui_application.presenters.agent_tasks_inspector_presenter import AgentTasksInspectorPresenter
from app.ui_contracts.workspaces.agent_tasks_inspector import (
    AgentTasksInspectorReadDto,
    AgentTasksInspectorState,
    LoadAgentTasksInspectorCommand,
)
from app.ui_contracts.workspaces.agent_tasks_task_panel import AgentTaskPanelDto, LoadAgentTaskPanelCommand
from app.ui_contracts.common.errors import SettingsErrorInfo


class _Sink:
    def __init__(self) -> None:
        self.states: list[AgentTasksInspectorState] = []

    def apply_inspector_state(self, state: AgentTasksInspectorState) -> None:
        self.states.append(state)


class _Port:
    def __init__(self, dto: AgentTasksInspectorReadDto) -> None:
        self._dto = dto
        self.calls: list[tuple[str, int | None]] = []

    def load_registry_view(self, project_id: int | None) -> object:  # pragma: no cover
        del project_id
        raise NotImplementedError

    def load_agent_task_selection_detail(self, command) -> object:  # pragma: no cover
        del command
        raise NotImplementedError

    def load_agent_tasks_inspector_state(self, agent_id: str, project_id: int | None) -> AgentTasksInspectorReadDto:
        self.calls.append((agent_id, project_id))
        return self._dto

    def load_agent_task_panel(self, command: LoadAgentTaskPanelCommand) -> AgentTaskPanelDto:
        del command
        return AgentTaskPanelDto(agent_id="", task_count=0, recent_tasks=())


def test_presenter_error_phase() -> None:
    err = SettingsErrorInfo(code="e", message="fail")
    dto = AgentTasksInspectorReadDto(load_error=err)
    sink = _Sink()
    AgentTasksInspectorPresenter(sink, _Port(dto)).handle_command(
        LoadAgentTasksInspectorCommand("a", 1, False),
    )
    assert sink.states[0].phase == "error"
    assert sink.states[0].last_result_text == "fail"


def test_presenter_ready_merges_sections() -> None:
    dto = AgentTasksInspectorReadDto(
        operations_agent_status="Ops1",
        operations_task_context="Ops2",
        operations_tool_model="Ops3",
    )
    sink = _Sink()
    AgentTasksInspectorPresenter(sink, _Port(dto)).handle_command(
        LoadAgentTasksInspectorCommand(
            "id",
            2,
            True,
            task_section_1="T1",
            task_section_2="T2",
            task_section_3="T3",
        ),
    )
    assert sink.states[0].phase == "ready"
    assert sink.states[0].sending is True
    assert "Ops1" in sink.states[0].last_result_text
    assert "T1" in sink.states[0].last_result_text

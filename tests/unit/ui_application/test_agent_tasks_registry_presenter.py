"""AgentTasksRegistryPresenter — Slice 1."""

from __future__ import annotations

from typing import Any

from app.ui_application.adapters.service_agent_tasks_registry_adapter import AgentTasksRegistrySnapshot
from app.ui_application.presenters.agent_tasks_registry_presenter import AgentTasksRegistryPresenter
from app.ui_contracts.workspaces.agent_tasks_inspector import AgentTasksInspectorReadDto
from app.ui_contracts.workspaces.agent_tasks_registry import (
    AgentRegistryRowDto,
    AgentTasksRegistryViewState,
    LoadAgentTasksRegistryCommand,
    agent_tasks_selection_idle_state,
)
from app.ui_contracts.workspaces.agent_tasks_task_panel import (
    AgentTaskPanelDto,
    LoadAgentTaskPanelCommand,
)
from app.ui_contracts.common.errors import SettingsErrorInfo


class _Sink:
    def __init__(self) -> None:
        self.calls: list[tuple[AgentTasksRegistryViewState, tuple[Any, ...]]] = []

    def apply_full_state(
        self,
        state: AgentTasksRegistryViewState,
        agent_profiles: tuple[Any, ...] = (),
    ) -> None:
        self.calls.append((state, agent_profiles))


class _FakePort:
    def __init__(self, view: AgentTasksRegistryViewState) -> None:
        self._view = view
        self.loads = 0
        self.last_registry_snapshot: AgentTasksRegistrySnapshot | None = None

    def load_registry_view(self, project_id: int | None) -> AgentTasksRegistryViewState:
        self.loads += 1
        del project_id
        return self._view

    def load_agent_task_selection_detail(self, command) -> object:  # noqa: ANN001
        del command
        return agent_tasks_selection_idle_state()

    def load_agent_tasks_inspector_state(self, agent_id: str, project_id: int | None) -> AgentTasksInspectorReadDto:
        del agent_id, project_id
        return AgentTasksInspectorReadDto()

    def load_agent_task_panel(self, command: LoadAgentTaskPanelCommand) -> AgentTaskPanelDto:
        del command
        return AgentTaskPanelDto(agent_id="", task_count=0, recent_tasks=())


def test_presenter_load_loading_then_ready() -> None:
    row = AgentRegistryRowDto(agent_id="a", list_item_text="L")
    ready = AgentTasksRegistryViewState(phase="ready", rows=(row,))
    sink = _Sink()
    port = _FakePort(ready)
    port.last_registry_snapshot = AgentTasksRegistrySnapshot(
        agents=["p"],
        profiles_by_id={},
        summaries_by_id={},
    )
    pres = AgentTasksRegistryPresenter(sink, port)
    pres.handle_command(LoadAgentTasksRegistryCommand(1))
    assert len(sink.calls) == 2
    assert sink.calls[0][0].phase == "loading"
    assert sink.calls[1][0].phase == "ready"
    assert sink.calls[1][1] == ("p",)
    assert port.loads == 1


def test_presenter_error() -> None:
    err = AgentTasksRegistryViewState(
        phase="error",
        error=SettingsErrorInfo(code="e", message="fail"),
    )
    sink = _Sink()
    pres = AgentTasksRegistryPresenter(sink, _FakePort(err))
    pres.handle_command(LoadAgentTasksRegistryCommand(1))
    assert sink.calls[-1][0].phase == "error"

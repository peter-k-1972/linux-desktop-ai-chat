"""AgentTasksTaskPanelPresenter — Slice 4."""

from __future__ import annotations

from app.ui_application.presenters.agent_tasks_task_panel_presenter import AgentTasksTaskPanelPresenter
from app.ui_contracts.workspaces.agent_tasks_task_panel import (
    AgentTaskPanelDto,
    AgentTaskPanelState,
    LoadAgentTaskPanelCommand,
    agent_task_panel_loading_state,
)


def test_presenter_loading_ready() -> None:
    states: list[AgentTaskPanelState] = []
    dto = AgentTaskPanelDto("a", 1, ("t",))

    class _Sink:
        def apply_task_panel_state(self, state: AgentTaskPanelState) -> None:
            states.append(state)

    class _Port:
        def load_agent_task_panel(self, command: LoadAgentTaskPanelCommand) -> AgentTaskPanelDto:
            assert command.agent_id == "a"
            return dto

    p = AgentTasksTaskPanelPresenter(_Sink(), _Port())
    p.handle_command(LoadAgentTaskPanelCommand("a", 1))
    assert len(states) == 2
    assert states[0].phase == agent_task_panel_loading_state().phase
    assert states[1].panel == dto


def test_presenter_error() -> None:
    states: list[AgentTaskPanelState] = []

    class _Sink:
        def apply_task_panel_state(self, state: AgentTaskPanelState) -> None:
            states.append(state)

    class _Port:
        def load_agent_task_panel(self, command: LoadAgentTaskPanelCommand) -> AgentTaskPanelDto:
            raise RuntimeError("x")

    AgentTasksTaskPanelPresenter(_Sink(), _Port()).handle_command(LoadAgentTaskPanelCommand("a", None))
    assert states[-1].phase == "error"

"""Smoke: Agent Tasks Slice 2 (Selection-/Operations-Detail read path)."""


def test_agent_tasks_slice2_stack() -> None:
    from app.gui.domains.operations.agent_tasks.agent_tasks_selection_sink import AgentTasksSelectionSink
    from app.ui_application.presenters.agent_tasks_selection_presenter import AgentTasksSelectionPresenter
    from app.ui_contracts.workspaces.agent_tasks_registry import (
        LoadAgentTaskSelectionCommand,
        agent_tasks_selection_idle_state,
    )

    assert LoadAgentTaskSelectionCommand("a", None).project_id is None
    assert agent_tasks_selection_idle_state().phase == "idle"
    assert AgentTasksSelectionPresenter.__name__ == "AgentTasksSelectionPresenter"
    assert AgentTasksSelectionSink.__name__ == "AgentTasksSelectionSink"

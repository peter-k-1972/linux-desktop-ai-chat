"""Smoke: Agent Tasks Slice 3 (Inspector read path)."""


def test_agent_tasks_slice3_stack() -> None:
    from app.gui.domains.operations.agent_tasks.agent_tasks_inspector_sink import AgentTasksInspectorSink
    from app.ui_application.presenters.agent_tasks_inspector_presenter import AgentTasksInspectorPresenter
    from app.ui_contracts.workspaces.agent_tasks_inspector import (
        LoadAgentTasksInspectorCommand,
        agent_tasks_inspector_idle_state,
    )

    assert LoadAgentTasksInspectorCommand("x", None, False).project_id is None
    assert agent_tasks_inspector_idle_state().phase == "idle"
    assert AgentTasksInspectorPresenter.__name__ == "AgentTasksInspectorPresenter"
    assert AgentTasksInspectorSink.__name__ == "AgentTasksInspectorSink"

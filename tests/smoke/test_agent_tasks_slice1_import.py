"""Smoke: Agent Tasks Slice 1 (Registry read-only)."""


def test_agent_tasks_slice1_stack() -> None:
    from app.gui.domains.operations.agent_tasks.agent_tasks_registry_sink import AgentTasksRegistrySink
    from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter
    from app.ui_application.ports.agent_tasks_registry_port import AgentTasksRegistryPort
    from app.ui_application.presenters.agent_tasks_registry_presenter import AgentTasksRegistryPresenter
    from app.ui_contracts.workspaces.agent_tasks_registry import (
        LoadAgentTasksRegistryCommand,
        agent_tasks_registry_loading_state,
    )

    assert LoadAgentTasksRegistryCommand(None).project_id is None
    assert agent_tasks_registry_loading_state().phase == "loading"
    assert AgentTasksRegistryPort.__name__ == "AgentTasksRegistryPort"
    assert ServiceAgentTasksRegistryAdapter.__name__ == "ServiceAgentTasksRegistryAdapter"
    assert AgentTasksRegistryPresenter.__name__ == "AgentTasksRegistryPresenter"
    assert AgentTasksRegistrySink.__name__ == "AgentTasksRegistrySink"


def test_agent_tasks_workspace_imports() -> None:
    from app.gui.domains.operations.agent_tasks.agent_tasks_workspace import AgentTasksWorkspace

    assert AgentTasksWorkspace.__name__ == "AgentTasksWorkspace"

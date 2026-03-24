"""Smoke: Batch 6 — Test-Lab-Run + Agent-Tasks-Runtime."""

from __future__ import annotations


def test_batch6_modules_import() -> None:
    from app.ui_application.ports.agent_tasks_runtime_port import AgentTasksRuntimePort
    from app.ui_application.ports.prompt_studio_port import PromptStudioPort
    from app.ui_application.presenters.agent_tasks_runtime_presenter import AgentTasksRuntimePresenter
    from app.ui_contracts.workspaces.agent_tasks_runtime import StartAgentTaskCommand
    from app.ui_contracts.workspaces.prompt_studio_test_lab import RunPromptTestLabCommand

    assert hasattr(PromptStudioPort, "stream_prompt_test_lab_run")
    assert AgentTasksRuntimePort.__name__ == "AgentTasksRuntimePort"
    assert AgentTasksRuntimePresenter.__name__ == "AgentTasksRuntimePresenter"
    assert isinstance(StartAgentTaskCommand("a", "p"), StartAgentTaskCommand)
    assert RunPromptTestLabCommand("m", "s", "u", 0.1, 1).max_tokens == 1

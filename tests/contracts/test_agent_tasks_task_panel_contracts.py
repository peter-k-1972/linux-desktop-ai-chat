"""Agent Tasks Task Panel (Slice 4) — Contracts."""

from __future__ import annotations

from app.ui_contracts.workspaces.agent_tasks_task_panel import (
    AgentTaskPanelDto,
    AgentTaskPanelState,
    LoadAgentTaskPanelCommand,
    agent_task_panel_loading_state,
)


def test_dto() -> None:
    d = AgentTaskPanelDto(agent_id="a", task_count=2, recent_tasks=("x",))
    assert d.task_count == 2


def test_command() -> None:
    c = LoadAgentTaskPanelCommand("aid", 5)
    assert c.project_id == 5


def test_loading() -> None:
    assert agent_task_panel_loading_state().phase == "loading"

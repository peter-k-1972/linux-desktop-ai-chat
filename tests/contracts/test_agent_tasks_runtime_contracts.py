"""Agent Tasks Runtime (Batch 6) — Contracts."""

from __future__ import annotations

from app.ui_contracts.workspaces.agent_tasks_runtime import (
    StartAgentTaskCommand,
    StartAgentTaskResultDto,
)


def test_start_command() -> None:
    c = StartAgentTaskCommand(agent_id="a1", prompt="hi")
    assert c.agent_id == "a1"


def test_result_dto() -> None:
    d = StartAgentTaskResultDto(
        task_id="t1",
        agent_id="a",
        agent_name="N",
        prompt="p",
        response="r",
        model="m",
        success=True,
        duration_sec=1.5,
    )
    assert d.success and d.duration_sec == 1.5

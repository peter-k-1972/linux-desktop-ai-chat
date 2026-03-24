"""AgentTasksRuntimePresenter (Batch 6)."""

from __future__ import annotations

import asyncio

import pytest

from app.ui_application.presenters.agent_tasks_runtime_presenter import AgentTasksRuntimePresenter
from app.ui_contracts.workspaces.agent_tasks_runtime import (
    StartAgentTaskCommand,
    StartAgentTaskResultDto,
)


class _Sink:
    def __init__(self) -> None:
        self.result: StartAgentTaskResultDto | None = None
        self.cancelled = False
        self.exc: tuple[str, str, str] | None = None

    def apply_start_task_result(self, dto: StartAgentTaskResultDto) -> None:
        self.result = dto

    def apply_start_task_cancelled(self) -> None:
        self.cancelled = True

    def apply_start_task_exception(self, agent_id: str, prompt: str, error: str) -> None:
        self.exc = (agent_id, prompt, error)


class _Port:
    def __init__(self, dto: StartAgentTaskResultDto | None = None, *, boom: bool = False) -> None:
        self._dto = dto
        self._boom = boom

    async def start_agent_task_runtime(self, command: StartAgentTaskCommand) -> StartAgentTaskResultDto:
        if self._boom:
            raise RuntimeError("x")
        assert self._dto is not None
        return self._dto


async def test_presenter_applies_result() -> None:
    dto = StartAgentTaskResultDto(
        task_id="1",
        agent_id="a",
        agent_name="n",
        prompt="p",
        response="r",
        model="m",
        success=True,
    )
    sink = _Sink()
    pr = AgentTasksRuntimePresenter(sink, _Port(dto))  # type: ignore[arg-type]
    await pr.handle_start_task_async(StartAgentTaskCommand("a", "p"))
    assert sink.result == dto


async def test_presenter_exception_maps_to_sink() -> None:
    sink = _Sink()
    pr = AgentTasksRuntimePresenter(sink, _Port(boom=True))  # type: ignore[arg-type]
    await pr.handle_start_task_async(StartAgentTaskCommand("a", "p"))
    assert sink.exc == ("a", "p", "x")


async def test_presenter_cancel_propagates() -> None:
    class _PCancel:
        async def start_agent_task_runtime(self, command: StartAgentTaskCommand) -> StartAgentTaskResultDto:
            raise asyncio.CancelledError

    sink = _Sink()
    pr = AgentTasksRuntimePresenter(sink, _PCancel())  # type: ignore[arg-type]
    with pytest.raises(asyncio.CancelledError):
        await pr.handle_start_task_async(StartAgentTaskCommand("a", "p"))
    assert sink.cancelled is True

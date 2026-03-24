"""AgentTasksWorkspace — Runtime-Start über Presenter (Batch 6)."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest
from PySide6.QtWidgets import QApplication

from app.ui_contracts.workspaces.agent_tasks_runtime import StartAgentTaskCommand


@pytest.fixture
def qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


async def test_run_task_delegates_to_runtime_presenter(qapp: QApplication) -> None:
    from app.gui.domains.operations.agent_tasks.agent_tasks_workspace import AgentTasksWorkspace

    ws = AgentTasksWorkspace()
    ws._runtime_presenter.handle_start_task_async = AsyncMock()  # type: ignore[method-assign]
    ws._sending = False
    await ws._run_task("ag1", "do it")
    ws._runtime_presenter.handle_start_task_async.assert_awaited_once()
    c = ws._runtime_presenter.handle_start_task_async.call_args[0][0]
    assert isinstance(c, StartAgentTaskCommand)
    assert c.agent_id == "ag1" and c.prompt == "do it"


async def test_run_task_legacy_calls_service(qapp: QApplication, monkeypatch) -> None:
    from app.agents.agent_task_runner import AgentTaskResult
    from app.gui.domains.operations.agent_tasks.agent_tasks_workspace import AgentTasksWorkspace

    calls: list[tuple[str, str]] = []

    class _S:
        async def start_agent_task(self, aid: str, pr: str) -> AgentTaskResult:
            calls.append((aid, pr))
            return AgentTaskResult(
                task_id="1",
                agent_id=aid,
                agent_name="X",
                prompt=pr,
                response="y",
                model="m",
                success=True,
            )

    monkeypatch.setattr("app.services.agent_service.get_agent_service", lambda: _S())
    ws = AgentTasksWorkspace()
    ws._runtime_presenter = None
    ws._sending = False
    await ws._run_task("a", "p")
    assert calls == [("a", "p")]

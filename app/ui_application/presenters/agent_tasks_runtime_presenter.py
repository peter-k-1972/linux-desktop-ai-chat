"""
AgentTasksRuntimePresenter — Start-Task async (Batch 6).
"""

from __future__ import annotations

import asyncio

from app.ui_application.ports.agent_tasks_runtime_port import AgentTasksRuntimePort
from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.view_models.protocols import AgentTasksRuntimeUiSink
from app.ui_contracts.workspaces.agent_tasks_runtime import StartAgentTaskCommand


class AgentTasksRuntimePresenter(BasePresenter):
    def __init__(self, sink: AgentTasksRuntimeUiSink, port: AgentTasksRuntimePort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    async def handle_start_task_async(self, command: StartAgentTaskCommand) -> None:
        try:
            dto = await self._port.start_agent_task_runtime(command)
            self._sink.apply_start_task_result(dto)
        except asyncio.CancelledError:
            self._sink.apply_start_task_cancelled()
            raise
        except Exception as exc:
            self._sink.apply_start_task_exception(command.agent_id, command.prompt, str(exc))

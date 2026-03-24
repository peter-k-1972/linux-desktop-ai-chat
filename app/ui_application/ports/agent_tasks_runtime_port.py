"""
AgentTasksRuntimePort — nur async Start-Task (Batch 6).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.ui_contracts.workspaces.agent_tasks_runtime import (
    StartAgentTaskCommand,
    StartAgentTaskResultDto,
)


@runtime_checkable
class AgentTasksRuntimePort(Protocol):
    async def start_agent_task_runtime(
        self,
        command: StartAgentTaskCommand,
    ) -> StartAgentTaskResultDto:
        """Delegiert an Agent-Service; Mapping im Adapter."""
        ...

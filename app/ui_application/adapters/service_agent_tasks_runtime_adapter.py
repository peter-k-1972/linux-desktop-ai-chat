"""
Adapter: Agent-Service Start-Task → Runtime-DTO (Batch 6).
"""

from __future__ import annotations

from app.ui_contracts.workspaces.agent_tasks_runtime import (
    StartAgentTaskCommand,
    StartAgentTaskResultDto,
)


class ServiceAgentTasksRuntimeAdapter:
    async def start_agent_task_runtime(
        self,
        command: StartAgentTaskCommand,
    ) -> StartAgentTaskResultDto:
        from app.services.agent_service import get_agent_service

        r = await get_agent_service().start_agent_task(command.agent_id, command.prompt)
        return StartAgentTaskResultDto(
            task_id=str(r.task_id or ""),
            agent_id=str(r.agent_id or ""),
            agent_name=str(r.agent_name or ""),
            prompt=str(r.prompt or ""),
            response=str(r.response or ""),
            model=str(r.model or ""),
            success=bool(r.success),
            error=(str(r.error) if r.error else None),
            duration_sec=float(r.duration_sec or 0.0),
        )

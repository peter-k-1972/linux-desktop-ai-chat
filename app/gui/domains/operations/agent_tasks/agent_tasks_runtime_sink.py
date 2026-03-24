"""
AgentTasksRuntimeSink — Task-Ergebnis auf Result-Panel spiegeln (Batch 6).
"""

from __future__ import annotations

from app.agents.agent_task_runner import AgentTaskResult
from app.gui.domains.operations.agent_tasks.panels.result_panel import AgentResultPanel
from app.ui_contracts.workspaces.agent_tasks_runtime import StartAgentTaskResultDto


def _dto_to_result(dto: StartAgentTaskResultDto) -> AgentTaskResult:
    return AgentTaskResult(
        task_id=dto.task_id,
        agent_id=dto.agent_id,
        agent_name=dto.agent_name,
        prompt=dto.prompt,
        response=dto.response,
        model=dto.model,
        success=dto.success,
        error=dto.error,
        duration_sec=dto.duration_sec,
    )


class AgentTasksRuntimeSink:
    def __init__(self, result_panel: AgentResultPanel) -> None:
        self._result_panel = result_panel

    def apply_start_task_result(self, dto: StartAgentTaskResultDto) -> None:
        self._result_panel.set_result(_dto_to_result(dto))

    def apply_start_task_cancelled(self) -> None:
        self._result_panel.set_result(None)

    def apply_start_task_exception(self, agent_id: str, prompt: str, error: str) -> None:
        self._result_panel.set_result(
            AgentTaskResult(
                task_id="",
                agent_id=agent_id,
                agent_name="",
                prompt=prompt,
                response="",
                model="",
                success=False,
                error=error,
            ),
        )

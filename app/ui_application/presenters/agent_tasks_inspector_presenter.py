"""
AgentTasksInspectorPresenter — Inspector Read-Pfad (Slice 3).
"""

from __future__ import annotations

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.agent_tasks_registry_port import AgentTasksRegistryPort
from app.ui_application.view_models.protocols import AgentTasksInspectorUiSink
from app.ui_contracts.workspaces.agent_tasks_inspector import (
    INSPECTOR_SECTION_SEP,
    AgentTasksInspectorState,
    LoadAgentTasksInspectorCommand,
)


def _merge_section(ops: str, task: str) -> str:
    o, t = (ops or "").strip(), (task or "").strip()
    if o and t:
        return f"{o}\n\n{t}"
    return o or t or "—"


class AgentTasksInspectorPresenter(BasePresenter):
    def __init__(self, sink: AgentTasksInspectorUiSink, port: AgentTasksRegistryPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_command(self, command: LoadAgentTasksInspectorCommand) -> None:
        dto = self._port.load_agent_tasks_inspector_state(command.agent_id, command.project_id)
        if dto.load_error is not None:
            self._sink.apply_inspector_state(
                AgentTasksInspectorState(
                    phase="error",
                    agent_id=command.agent_id,
                    sending=command.sending,
                    last_result_text=dto.load_error.message,
                ),
            )
            return
        sec1 = _merge_section(dto.operations_agent_status, command.task_section_1)
        sec2 = _merge_section(dto.operations_task_context, command.task_section_2)
        sec3 = _merge_section(dto.operations_tool_model, command.task_section_3)
        body = INSPECTOR_SECTION_SEP.join([sec1, sec2, sec3])
        self._sink.apply_inspector_state(
            AgentTasksInspectorState(
                phase="ready",
                agent_id=command.agent_id,
                sending=command.sending,
                last_result_text=body,
            ),
        )

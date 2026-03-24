"""
AgentTasksTaskPanelPresenter — Task-Panel Lesepfad (Slice 4).
"""

from __future__ import annotations

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.agent_tasks_registry_port import AgentTasksRegistryPort
from app.ui_application.view_models.protocols import AgentTasksTaskPanelUiSink
from app.ui_contracts.workspaces.agent_tasks_task_panel import (
    AgentTaskPanelState,
    LoadAgentTaskPanelCommand,
    agent_task_panel_loading_state,
)


class AgentTasksTaskPanelPresenter(BasePresenter):
    def __init__(self, sink: AgentTasksTaskPanelUiSink, port: AgentTasksRegistryPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_command(self, command: LoadAgentTaskPanelCommand) -> None:
        self._sink.apply_task_panel_state(agent_task_panel_loading_state())
        try:
            dto = self._port.load_agent_task_panel(command)
            self._sink.apply_task_panel_state(
                AgentTaskPanelState(phase="ready", panel=dto, error_message=None),
            )
        except Exception as exc:
            self._sink.apply_task_panel_state(
                AgentTaskPanelState(phase="error", panel=None, error_message=str(exc)),
            )

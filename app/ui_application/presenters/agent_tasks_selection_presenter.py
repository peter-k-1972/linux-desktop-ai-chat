"""
AgentTasksSelectionPresenter — Betrieb-Tab: Operations-Detail nach Auswahl (Slice 2).
"""

from __future__ import annotations

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.agent_tasks_registry_port import AgentTasksRegistryPort
from app.ui_application.view_models.protocols import AgentTasksSelectionUiSink
from app.ui_contracts.workspaces.agent_tasks_registry import LoadAgentTaskSelectionCommand


class AgentTasksSelectionPresenter(BasePresenter):
    def __init__(self, sink: AgentTasksSelectionUiSink, port: AgentTasksRegistryPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_command(self, command: LoadAgentTaskSelectionCommand) -> None:
        state = self._port.load_agent_task_selection_detail(command)
        self._sink.apply_selection_state(state)

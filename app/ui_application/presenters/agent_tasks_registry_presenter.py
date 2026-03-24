"""
AgentTasksRegistryPresenter — Betrieb-Tab: Agentenliste lesen (Slice 1).
"""

from __future__ import annotations

from typing import Any

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.agent_tasks_registry_port import AgentTasksRegistryPort
from app.ui_application.view_models.protocols import AgentTasksRegistryUiSink
from app.ui_contracts.workspaces.agent_tasks_registry import (
    LoadAgentTasksRegistryCommand,
    agent_tasks_registry_loading_state,
)


class AgentTasksRegistryPresenter(BasePresenter):
    def __init__(self, sink: AgentTasksRegistryUiSink, port: AgentTasksRegistryPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_command(self, command: LoadAgentTasksRegistryCommand) -> None:
        self._sink.apply_full_state(agent_tasks_registry_loading_state(), ())
        view = self._port.load_registry_view(command.project_id)
        profiles: tuple[Any, ...] = ()
        snap = getattr(self._port, "last_registry_snapshot", None)
        if snap is not None:
            profiles = tuple(snap.agents)
        self._sink.apply_full_state(view, profiles)

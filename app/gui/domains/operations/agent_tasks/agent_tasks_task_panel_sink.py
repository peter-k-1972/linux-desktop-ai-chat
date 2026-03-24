"""
AgentTasksTaskPanelSink — :class:`AgentTaskPanelState` → :class:`AgentTaskPanel`.
"""

from __future__ import annotations

from typing import Any

from app.ui_contracts.workspaces.agent_tasks_task_panel import AgentTaskPanelState


class AgentTasksTaskPanelSink:
    def __init__(self, panel: Any) -> None:
        self._panel = panel

    def apply_task_panel_state(self, state: AgentTaskPanelState) -> None:
        self._panel.apply_task_panel_state(state)

"""
AgentTasksInspectorSink — Inspector aus :class:`AgentTasksInspectorState` (Slice 3).
"""

from __future__ import annotations

from typing import Any

from app.gui.inspector.agent_tasks_inspector import AgentTasksInspector
from app.ui_contracts.workspaces.agent_tasks_inspector import (
    INSPECTOR_SECTION_SEP,
    AgentTasksInspectorState,
)


class AgentTasksInspectorSink:
    def __init__(self, inspector_host: Any, *, content_token: int | None = None) -> None:
        self._inspector_host = inspector_host
        self._content_token = content_token

    def apply_inspector_state(self, state: AgentTasksInspectorState) -> None:
        if not self._inspector_host:
            return
        if state.phase == "error":
            content = AgentTasksInspector(
                port_driven_body=f"{state.last_result_text}{INSPECTOR_SECTION_SEP}{INSPECTOR_SECTION_SEP}",
                is_error=True,
            )
        else:
            content = AgentTasksInspector(port_driven_body=state.last_result_text)
        self._inspector_host.set_content(content, content_token=self._content_token)

"""
AgentTasksRegistryPort — Betrieb-Tab: Registry (Slice 1) + Selection (Slice 2) + Inspector-Read (Slice 3).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.ui_contracts.workspaces.agent_tasks_inspector import AgentTasksInspectorReadDto
from app.ui_contracts.workspaces.agent_tasks_registry import (
    AgentTasksRegistryViewState,
    AgentTasksSelectionViewState,
    LoadAgentTaskSelectionCommand,
)
from app.ui_contracts.workspaces.agent_tasks_task_panel import (
    AgentTaskPanelDto,
    LoadAgentTaskPanelCommand,
)


@runtime_checkable
class AgentTasksRegistryPort(Protocol):
    def load_registry_view(self, project_id: int | None) -> AgentTasksRegistryViewState:
        """
        Liefert Registry-Zustand; bei Fehler ``phase=error``.

        Konkrete Adapter können nach dem Aufruf ``last_registry_snapshot`` setzen — nicht Teil
        des Protocols.
        """
        ...

    def load_agent_task_selection_detail(
        self,
        command: LoadAgentTaskSelectionCommand,
    ) -> AgentTasksSelectionViewState:
        """
        Liefert Operations-Summary für die Detailspalte.

        Nutzt nach Möglichkeit ``last_registry_snapshot.summaries_by_id`` (gleicher Registry-Ladevorgang),
        sonst ``get_summary`` — ohne neue Fachlogik.
        """
        ...

    def load_agent_tasks_inspector_state(
        self,
        agent_id: str,
        project_id: int | None,
    ) -> AgentTasksInspectorReadDto:
        """Operations-Kontext für den Inspector (Read-Service nur im Adapter)."""
        ...

    def load_agent_task_panel(self, command: LoadAgentTaskPanelCommand) -> AgentTaskPanelDto:
        """DebugStore-Tasks für das Task-Panel (Read-only, Slice 4)."""
        ...

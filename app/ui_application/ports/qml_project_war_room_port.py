"""
QML Projects War-Room — ein Port für Projektliste, Inspector und eingebettete Spalten.

Kapselt Project-, Workflow- und Agent-Zugriffe für eine ViewModel-Schicht ohne Service-Imports.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from app.agents.agent_profile import AgentProfile
from app.workflows.models.definition import WorkflowDefinition


@runtime_checkable
class QmlProjectWarRoomPort(Protocol):
    def list_projects(self, filter_text: str) -> list[dict[str, Any]]:
        """Rohzeilen wie ``ProjectService.list_projects``."""
        ...

    def get_project_monitoring_snapshot(self, project_id: int) -> dict[str, Any]:
        ...

    def get_project(self, project_id: int) -> dict[str, Any] | None:
        ...

    def get_recent_chats_of_project(self, project_id: int, limit: int) -> list[dict[str, Any]]:
        ...

    def list_workflows_for_project(self, project_id: int, *, limit: int) -> list[WorkflowDefinition]:
        ...

    def list_active_agents_for_project(self, project_id: int) -> list[AgentProfile]:
        """Nur für die UI-Liste relevante aktive Profile."""
        ...

    def list_files_of_project(self, project_id: int, limit: int) -> list[dict[str, Any]]:
        ...

    def set_active_project(self, project_id: int) -> None:
        ...

    def create_project(self, name: str, description: str) -> int:
        ...

    def delete_project(self, project_id: int) -> None:
        ...

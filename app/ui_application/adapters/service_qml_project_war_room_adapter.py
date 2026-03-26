"""Adapter: :class:`QmlProjectWarRoomPort` → Project-, Workflow- und Agent-Services."""

from __future__ import annotations

from typing import Any

from app.agents.agent_profile import AgentProfile
from app.services.agent_service import get_agent_service
from app.services.project_service import get_project_service
from app.services.workflow_service import get_workflow_service
from app.workflows.models.definition import WorkflowDefinition


class ServiceQmlProjectWarRoomAdapter:
    def list_projects(self, filter_text: str) -> list[dict[str, Any]]:
        return get_project_service().list_projects(filter_text or "")

    def get_project_monitoring_snapshot(self, project_id: int) -> dict[str, Any]:
        try:
            return get_project_service().get_project_monitoring_snapshot(int(project_id))
        except Exception:
            return {}

    def get_project(self, project_id: int) -> dict[str, Any] | None:
        try:
            return get_project_service().get_project(int(project_id))
        except Exception:
            return None

    def get_recent_chats_of_project(self, project_id: int, limit: int) -> list[dict[str, Any]]:
        try:
            return get_project_service().get_recent_chats_of_project(int(project_id), int(limit))
        except Exception:
            return []

    def list_workflows_for_project(self, project_id: int, *, limit: int) -> list[WorkflowDefinition]:
        try:
            defs = get_workflow_service().list_workflows(
                project_scope_id=int(project_id),
                include_global=False,
            )
            return list(defs[: int(limit)])
        except Exception:
            return []

    def list_active_agents_for_project(self, project_id: int) -> list[AgentProfile]:
        try:
            profiles = get_agent_service().list_agents_for_project(
                project_id=int(project_id),
                filter_text="",
            )
            return [a for a in profiles if (a.status or "").lower() == "active"]
        except Exception:
            return []

    def list_files_of_project(self, project_id: int, limit: int) -> list[dict[str, Any]]:
        try:
            return get_project_service().list_files_of_project(int(project_id), limit=int(limit))
        except Exception:
            return []

    def set_active_project(self, project_id: int) -> None:
        get_project_service().set_active_project(project_id=int(project_id))

    def clear_active_project(self) -> None:
        get_project_service().clear_active_project()

    def get_active_project_id(self) -> int | None:
        return get_project_service().get_active_project_id()

    def create_project(self, name: str, description: str) -> int:
        return int(get_project_service().create_project(name, description or ""))

    def delete_project(self, project_id: int) -> None:
        get_project_service().delete_project(int(project_id))

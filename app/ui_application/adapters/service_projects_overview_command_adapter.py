"""
Adapter: bestehende Services / Host-Kontext → ProjectsOverviewCommandPort.

Slice 1: nur minimale Commands, keine neue Fachlogik.
"""

from __future__ import annotations

from app.services.project_service import get_project_service
from app.ui_contracts.workspaces.projects_overview import CommandResult


class ServiceProjectsOverviewCommandAdapter:
    def select_project(self, project_id: int | None) -> None:
        """Lokale Auswahl bleibt in Slice 1 presenter-/workspace-seitig; Adapter ist bewusst No-Op."""
        del project_id

    def set_active_project(self, project_id: int | None) -> CommandResult:
        try:
            svc = get_project_service()
            if project_id is None:
                svc.clear_active_project()
            else:
                svc.set_active_project(int(project_id))
            return CommandResult(ok=True, message=None)
        except Exception as exc:
            return CommandResult(ok=False, message=str(exc))

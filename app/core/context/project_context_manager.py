"""
ProjectContextManager – central project context system.

Tracks the active project, loads it from SQLite, and notifies listeners
when the project changes via EventBus (project_context_changed).
"""

from typing import Any, Dict, Optional

from app.gui.events.project_events import emit_project_context_changed


class ProjectContextManager:
    """
    Manages the active project context.

    - Tracks active project in memory
    - Loads project from SQLite via ProjectService
    - Notifies listeners via EventBus when project changes
    """

    def __init__(self) -> None:
        self._active_project_id: Optional[int] = None
        self._active_project: Optional[Dict[str, Any]] = None

    def set_active_project(self, project_id: Optional[int]) -> None:
        """
        Set the active project by ID.

        Loads the project from the database. If project_id is None,
        clears the active project. Emits project_context_changed.
        Syncs to ActiveProjectContext so Breadcrumbs and Projects workspace stay consistent.
        """
        if project_id is None:
            self._active_project_id = None
            self._active_project = None
            emit_project_context_changed(None)
            self._sync_to_active_project_context(None, None)
            return

        project = self._load_project(project_id)
        self._active_project_id = project_id
        self._active_project = project
        emit_project_context_changed(project_id)
        self._sync_to_active_project_context(project_id, project)

    def _sync_to_active_project_context(
        self, project_id: Optional[int], project: Optional[Dict[str, Any]]
    ) -> None:
        """Keep ActiveProjectContext in sync (Breadcrumbs, Projects workspace)."""
        try:
            from app.core.context.active_project import get_active_project_context
            ctx = get_active_project_context()
            if project_id is None and project is None:
                ctx.set_none()
            else:
                ctx.set_active(project_id=project_id, project=project)
        except Exception:
            pass

    def get_active_project(self) -> Optional[Dict[str, Any]]:
        """Return the full active project dict, or None if none is active."""
        return self._active_project

    def get_active_project_id(self) -> Optional[int]:
        """Return the active project ID, or None if none is active."""
        return self._active_project_id

    def _load_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Load project from SQLite via ProjectService."""
        try:
            from app.services.project_service import get_project_service
            return get_project_service().get_project(project_id)
        except Exception:
            return None


_manager: Optional[ProjectContextManager] = None


def get_project_context_manager() -> ProjectContextManager:
    """Return the global ProjectContextManager singleton."""
    global _manager
    if _manager is None:
        _manager = ProjectContextManager()
    return _manager

"""
ProjectContextManager – autoritativer aktiver Projektkontext.

Setzt das aktive Projekt ausschließlich hier (set_active_project). Lädt aus der
DB, feuert project_context_changed und spiegelt nach ActiveProjectContext.
"""

from typing import Any, Callable, Dict, Optional

from app.core.context.project_context_events import emit_project_context_changed

ProjectLoader = Callable[[int], Optional[Dict[str, Any]]]

_project_loader: Optional[ProjectLoader] = None


class ProjectContextManager:
    """
    Manages the active project context.

    - Tracks active project in memory
    - Loads project from SQLite via ProjectService
    - Notifies listeners via EventBus when project changes
    """

    def __init__(self, project_loader: Optional[ProjectLoader] = None) -> None:
        self._active_project_id: Optional[int] = None
        self._active_project: Optional[Dict[str, Any]] = None
        self._project_loader: Optional[ProjectLoader] = project_loader

    def set_active_project(self, project_id: Optional[int]) -> None:
        """
        Einzige unterstützte Schreib-API für das aktive Projekt (App-weit).

        Loads the project from the database. If project_id is None,
        clears the active project. Emits project_context_changed.
        Syncs to ActiveProjectContext (Listener/Breadcrumbs/Projects-Workspace).
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
        """Load project via injected neutral project loader."""
        try:
            if self._project_loader is None:
                return None
            return self._project_loader(project_id)
        except Exception:
            return None

    def set_project_loader(self, project_loader: Optional[ProjectLoader]) -> None:
        """Setzt den neutralen Projekt-Loader (v. a. Produktverdrahtung/Tests)."""
        self._project_loader = project_loader


_manager: Optional[ProjectContextManager] = None


def get_project_context_manager() -> ProjectContextManager:
    """Return the global ProjectContextManager singleton."""
    global _manager
    if _manager is None:
        _manager = ProjectContextManager(project_loader=_project_loader)
    return _manager


def set_project_context_manager(manager: Optional[ProjectContextManager]) -> None:
    """Setzt den globalen Manager (v. a. für Tests)."""
    global _manager
    if manager is not None:
        manager.set_project_loader(_project_loader)
    _manager = manager


def set_project_context_project_loader(project_loader: Optional[ProjectLoader]) -> None:
    """Setzt den globalen neutralen Projekt-Loader fuer neue und bestehende PCM-Instanzen."""
    global _project_loader
    _project_loader = project_loader
    if _manager is not None:
        _manager.set_project_loader(project_loader)

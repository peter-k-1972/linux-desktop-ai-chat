"""
ActiveProjectContext – gespiegelter aktiver Projektkontext.

Zustand wird app-weit geteilt; Benachrichtigung via Callback-System (Qt-frei).

Schreibzugriff (set_active / set_none): nur durch ProjectContextManager nach
einem set_active_project(...), damit eine einzige autoritative Quelle gilt.
Anwendungscode setzt das aktive Projekt ausschließlich über
get_project_context_manager().set_active_project(project_id).
"""

from typing import Any, Callable, Dict, List, Optional


class ActiveProjectContext:
    """
    Gespiegelter globaler Kontext (Schreiben nur aus ProjectContextManager).

    Lesen: active_project_id, active_project.
    UI-Callbacks: subscribe / unsubscribe (werden nach PCM-Sync ausgelöst).
    """

    def __init__(self) -> None:
        self._project_id: Optional[int] = None
        self._project: Optional[Dict[str, Any]] = None
        self._listeners: List[Callable[[Optional[int], Optional[Dict[str, Any]]], None]] = []

    def subscribe(self, callback: Callable[[Optional[int], Optional[Dict[str, Any]]], None]) -> None:
        """Registriert einen Listener für Projektwechsel."""
        if callback not in self._listeners:
            self._listeners.append(callback)

    def unsubscribe(self, callback: Callable[[Optional[int], Optional[Dict[str, Any]]], None]) -> None:
        """Entfernt einen Listener."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify(self) -> None:
        """Benachrichtigt alle Listener über den aktuellen Zustand."""
        for cb in list(self._listeners):
            try:
                cb(self._project_id, self._project)
            except Exception:
                pass

    @property
    def active_project_id(self) -> Optional[int]:
        """Aktuelle Projekt-ID oder None."""
        return self._project_id

    @property
    def active_project(self) -> Optional[Dict[str, Any]]:
        """Aktuelles Projekt oder None."""
        return self._project

    def set_active(self, project_id: Optional[int] = None, project: Optional[Dict[str, Any]] = None) -> None:
        """
        Intern: Spiegelung nach Außen (wird vom ProjectContextManager aufgerufen).

        - project_id: ID des Projekts
        - project: Projektdict oder None (z. B. wenn DB-Laden fehlgeschlagen ist)
        """
        if project_id is None and project is None:
            self.set_none()
            return
        if project_id is not None:
            self._project_id = project_id
            self._project = project  # None wenn Aufrufer keine Daten liefert
        elif project is not None:
            self._project_id = project.get("project_id")
            self._project = project
        else:
            self.set_none()
            return
        self._notify()

    def set_none(self) -> None:
        """Intern: leert den Spiegel (vom ProjectContextManager)."""
        self._project_id = None
        self._project = None
        self._notify()

    def clear(self) -> None:
        """Alias für set_none."""
        self.set_none()


_context: Optional[ActiveProjectContext] = None


def get_active_project_context() -> ActiveProjectContext:
    """Liefert den globalen ActiveProjectContext."""
    global _context
    if _context is None:
        _context = ActiveProjectContext()
    return _context


def set_active_project_context(ctx: Optional[ActiveProjectContext]) -> None:
    """Setzt den globalen ActiveProjectContext (für Tests)."""
    global _context
    _context = ctx

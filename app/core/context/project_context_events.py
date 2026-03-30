"""
Qt-freie Projektkontext-Events.

Kleiner neutraler Callback-Kanal fuer Wechsel des aktiven Projekts. GUI-spezifische
Adapter duerfen darauf aufbauen, aber core importiert keine GUI-Module.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional

EVENT_PROJECT_CONTEXT_CHANGED = "project_context_changed"

ProjectContextEventListener = Callable[[Dict[str, Any]], None]

_project_context_listeners: List[ProjectContextEventListener] = []


def subscribe_project_context_events(listener: ProjectContextEventListener) -> None:
    """Registriert einen Listener fuer Projektkontext-Wechsel."""
    if listener not in _project_context_listeners:
        _project_context_listeners.append(listener)


def unsubscribe_project_context_events(listener: ProjectContextEventListener) -> None:
    """Entfernt einen Listener fuer Projektkontext-Wechsel."""
    if listener in _project_context_listeners:
        _project_context_listeners.remove(listener)


def emit_project_context_changed(project_id: Optional[int]) -> None:
    """Benachrichtigt alle Listener ueber eine neue aktive Projekt-ID."""
    payload: Dict[str, Any] = {"project_id": project_id}
    for listener in list(_project_context_listeners):
        try:
            listener(payload)
        except Exception:
            pass

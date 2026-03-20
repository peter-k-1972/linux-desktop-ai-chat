"""
Project events – Event definitions and emission for project context changes.

When the active project changes, project_context_changed is emitted via EventBus.
"""

from typing import Any, Callable, Dict, List, Optional

# Event name for project context changes
EVENT_PROJECT_CONTEXT_CHANGED = "project_context_changed"

# Listener type: (payload: dict) -> None
ProjectEventListener = Callable[[Dict[str, Any]], None]

# Singleton event bus for project events
_project_listeners: List[ProjectEventListener] = []


def subscribe_project_events(listener: ProjectEventListener) -> None:
    """Register a listener for project events."""
    if listener not in _project_listeners:
        _project_listeners.append(listener)


def unsubscribe_project_events(listener: ProjectEventListener) -> None:
    """Remove a listener from project events."""
    if listener in _project_listeners:
        _project_listeners.remove(listener)


def emit_project_context_changed(project_id: Optional[int]) -> None:
    """
    Emit project_context_changed event to all listeners.

    Payload: {"project_id": ...}
    """
    payload: Dict[str, Any] = {"project_id": project_id}
    for listener in list(_project_listeners):
        try:
            listener(payload)
        except Exception:
            pass  # Don't let listener errors break emission

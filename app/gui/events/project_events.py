"""
Project events – GUI-kompatibler Adapter fuer Projektkontext-Wechsel.

Die neutrale Quelle lebt unter ``app.core.context.project_context_events``.
Dieses Modul behaelt nur den etablierten GUI-Importpfad.
"""

from app.core.context.project_context_events import (
    EVENT_PROJECT_CONTEXT_CHANGED,
    ProjectContextEventListener as ProjectEventListener,
    emit_project_context_changed,
    subscribe_project_context_events,
    unsubscribe_project_context_events,
)


def subscribe_project_events(listener: ProjectEventListener) -> None:
    """Register a listener for project events."""
    subscribe_project_context_events(listener)


def unsubscribe_project_events(listener: ProjectEventListener) -> None:
    """Remove a listener from project events."""
    unsubscribe_project_context_events(listener)

"""Core context: ActiveProjectContext, ProjectContextManager."""

from app.core.context.active_project import (
    ActiveProjectContext,
    get_active_project_context,
    set_active_project_context,
)
from app.core.context.project_context_events import (
    EVENT_PROJECT_CONTEXT_CHANGED,
    ProjectContextEventListener,
    emit_project_context_changed,
    subscribe_project_context_events,
    unsubscribe_project_context_events,
)
from app.core.context.project_context_manager import (
    ProjectContextManager,
    get_project_context_manager,
    set_project_context_project_loader,
    set_project_context_manager,
)

__all__ = [
    "ActiveProjectContext",
    "get_active_project_context",
    "set_active_project_context",
    "EVENT_PROJECT_CONTEXT_CHANGED",
    "ProjectContextEventListener",
    "subscribe_project_context_events",
    "unsubscribe_project_context_events",
    "emit_project_context_changed",
    "ProjectContextManager",
    "get_project_context_manager",
    "set_project_context_project_loader",
    "set_project_context_manager",
]

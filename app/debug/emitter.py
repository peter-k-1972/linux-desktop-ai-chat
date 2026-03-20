"""
Emitter – Hilfsfunktionen zum Senden von Debug-Events.

Agenten und Engines rufen emit_event() auf, um Aktivitäten zu melden.
Bei Fehlern (z.B. Debug-Modul nicht geladen) wird still ignoriert.
"""

from typing import Any, Dict, Optional

from app.debug.agent_event import AgentEvent, EventType
from app.debug.event_bus import get_event_bus


def emit_event(
    event_type: EventType,
    agent_name: str = "",
    task_id: Optional[str] = None,
    message: str = "",
    metadata: Optional[Dict[str, Any]] = None,
) -> None:
    """
    Sendet ein Event an den EventBus.

    Wird von Agenten, Engines und Chat-Integration aufgerufen.
    Fehler werden still ignoriert (kein Einfluss auf Hauptfunktion).
    """
    try:
        event = AgentEvent(
            agent_name=agent_name,
            task_id=task_id,
            event_type=event_type,
            message=message,
            metadata=metadata or {},
        )
        get_event_bus().emit(event)
    except Exception:
        pass  # Debug-Events dürfen die Hauptfunktion nicht beeinträchtigen

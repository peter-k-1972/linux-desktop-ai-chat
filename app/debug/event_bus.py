"""
EventBus – zentraler Event-Bus für Agentenaktivitäten.

Agenten und Engines senden Events via emit().
Listener (z.B. DebugStore) abonnieren via subscribe().
"""

import logging
from typing import Callable, List

from app.debug.agent_event import AgentEvent

logger = logging.getLogger(__name__)

# Typ für Listener: (event: AgentEvent) -> None
EventListener = Callable[[AgentEvent], None]

# Singleton EventBus
_event_bus: "EventBus | None" = None


def get_event_bus() -> "EventBus":
    """Liefert den globalen EventBus (Singleton)."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def reset_event_bus() -> None:
    """Setzt den EventBus zurück (für Tests)."""
    global _event_bus
    _event_bus = None


class EventBus:
    """
    Zentraler Event-Bus für Agenten-Events.

    - emit(event): Sendet ein Event an alle Subscriber
    - subscribe(listener): Registriert einen Listener
    - unsubscribe(listener): Entfernt einen Listener
    """

    def __init__(self):
        self._listeners: List[EventListener] = []

    def emit(self, event: AgentEvent) -> None:
        """
        Sendet ein Event an alle registrierten Listener.

        Fehler in Listenern werden geloggt, brechen die Verarbeitung aber nicht ab.
        """
        for listener in list(self._listeners):
            try:
                listener(event)
            except Exception as e:
                logger.warning("EventBus listener error: %s", e, exc_info=True)

    def subscribe(self, listener: EventListener) -> None:
        """Registriert einen Listener für alle Events."""
        if listener not in self._listeners:
            self._listeners.append(listener)

    def unsubscribe(self, listener: EventListener) -> None:
        """Entfernt einen Listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

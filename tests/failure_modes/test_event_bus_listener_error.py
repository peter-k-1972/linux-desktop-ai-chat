"""
Failure Injection: EventBus Listener-Fehler.

Simuliert: Ein Listener wirft Exception – andere Listener müssen weiterlaufen.
"""

import pytest

from app.debug.agent_event import AgentEvent, EventType
from app.debug.event_bus import EventBus


@pytest.mark.failure_mode
@pytest.mark.integration
def test_event_bus_listener_exception_does_not_break_others():
    """Fehlerhafter Listener bricht andere Listener nicht ab."""
    bus = EventBus()
    results = []

    def good_listener(event):
        results.append(("good", event.message))

    def bad_listener(event):
        raise ValueError("Listener fehlgeschlagen")

    bus.subscribe(good_listener)
    bus.subscribe(bad_listener)

    bus.emit(AgentEvent(agent_name="Test", event_type=EventType.TASK_COMPLETED, message="done"))

    # Guter Listener muss aufgerufen worden sein (trotz Exception im bad_listener)
    assert len(results) == 1
    assert results[0][1] == "done"

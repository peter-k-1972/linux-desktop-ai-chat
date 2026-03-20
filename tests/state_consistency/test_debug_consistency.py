"""
State-Consistency: Taskstatus im Backend -> Debug Panel.

Event gesendet -> DebugStore enthält Event -> get_event_history liefert konsistente Daten.
"""

import pytest

from app.debug.agent_event import AgentEvent, EventType
from app.debug.event_bus import get_event_bus, reset_event_bus
from app.debug.debug_store import DebugStore
from app.debug.emitter import emit_event


@pytest.fixture(autouse=True)
def reset_bus():
    reset_event_bus()
    yield
    reset_event_bus()


def test_debug_event_store_consistency():
    """
    Event über emit_event gesendet -> DebugStore.event_history enthält es ->
    get_event_history() liefert dieselben Daten.
    """
    bus = get_event_bus()
    store = DebugStore(bus=bus)

    emit_event(
        EventType.TASK_COMPLETED,
        agent_name="Consistency-Agent",
        task_id="task-99",
        message="Konsistenz-Test abgeschlossen",
    )

    # event_history und get_event_history müssen übereinstimmen
    history = store.get_event_history()
    assert len(history) >= 1
    evt = history[0]
    assert evt.agent_name == "Consistency-Agent"
    assert evt.task_id == "task-99"
    assert evt.event_type == EventType.TASK_COMPLETED

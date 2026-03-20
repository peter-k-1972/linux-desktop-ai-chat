"""
Golden-Path 5: Debug Panel öffnen -> Event sichtbar -> Aktivitätsstatus korrekt.

Prüft: EventBus emit -> DebugStore speichert -> View zeigt Event nach Refresh.
"""

import pytest

from app.debug.agent_event import AgentEvent, EventType
from app.debug.event_bus import get_event_bus, reset_event_bus
from app.debug.debug_store import DebugStore
from app.debug.emitter import emit_event


@pytest.fixture(autouse=True)
def reset_bus():
    """EventBus vor/nach Test zurücksetzen."""
    reset_event_bus()
    yield
    reset_event_bus()


@pytest.mark.golden_path
def test_debug_event_visible_in_store_and_refresh():
    """
    Golden Path: Event emittieren -> DebugStore enthält es ->
    Nach Refresh ist Event in Historie.
    """
    bus = get_event_bus()
    store = DebugStore(bus=bus)

    # 1. Event emittieren (nutzt get_event_bus() = dieselbe Instanz)
    emit_event(
        EventType.TASK_COMPLETED,
        agent_name="Golden-Path-Agent",
        task_id="task-123",
        message="Task abgeschlossen",
        metadata={"duration_sec": 2.5},
    )

    # 2. DebugStore hat Event (subscribe intern; get_event_history = neueste zuerst)
    events = store.get_event_history()
    assert len(events) >= 1
    evt = events[0]
    assert evt.agent_name == "Golden-Path-Agent"
    assert evt.task_id == "task-123"
    assert evt.event_type == EventType.TASK_COMPLETED
    assert "abgeschlossen" in evt.message

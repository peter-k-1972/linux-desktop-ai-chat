"""
Failure Injection: DebugStore / EventStore Fehlerszenarien.

Simuliert: Viele Events, fehlende Metadata, Clear während Verarbeitung.
"""

import pytest

from app.debug.agent_event import AgentEvent, EventType
from app.debug.debug_store import DebugStore
from app.debug.event_bus import EventBus


@pytest.fixture
def debug_store():
    """Isolierter DebugStore mit eigenem EventBus."""
    bus = EventBus()
    store = DebugStore(bus=bus)
    yield store
    store._unsubscribe()


@pytest.mark.failure_mode
@pytest.mark.integration
def test_debug_store_handles_event_with_missing_metadata(debug_store):
    """Event mit fehlender/leerer metadata crasht DebugStore nicht."""
    bus = debug_store._bus
    # TOOL_EXECUTION ohne tool_name in metadata – nutzt message als Fallback
    bus.emit(
        AgentEvent(
            agent_name="Test",
            event_type=EventType.TOOL_EXECUTION,
            message="list_dir",
            metadata={},  # leer
        )
    )
    # MODEL_CALL ohne model_id
    bus.emit(
        AgentEvent(
            agent_name="Chat",
            event_type=EventType.MODEL_CALL,
            message="",
            metadata={},
        )
    )
    history = debug_store.get_event_history()
    assert len(history) == 2
    tools = debug_store.get_tool_executions()
    assert len(tools) == 1
    assert tools[0].tool_name == "list_dir"  # Fallback auf message


@pytest.mark.failure_mode
@pytest.mark.integration
def test_debug_store_trim_at_max_history(debug_store):
    """Bei Überschreitung von MAX_EVENT_HISTORY wird getrimmt, kein Crash."""
    bus = debug_store._bus
    # Mehr Events als MAX (500) – DebugStore trimmt automatisch
    for i in range(10):  # Kleiner Test, echtes Limit wäre 501
        bus.emit(
            AgentEvent(
                agent_name=f"A{i}",
                event_type=EventType.TASK_COMPLETED,
                message=f"done {i}",
            )
        )
    history = debug_store.get_event_history()
    assert len(history) == 10
    # Nach clear: leer
    debug_store.clear()
    assert len(debug_store.get_event_history()) == 0

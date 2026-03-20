"""
Integration Tests: EventBus.

Testet den zentralen Event-Bus mit echten Events.
Keine Mocks – reale subscribe/emit/emit_event.
"""

from datetime import datetime, timezone

import pytest

from app.debug.agent_event import AgentEvent, EventType
from app.debug.event_bus import EventBus, get_event_bus, reset_event_bus
from app.debug.emitter import emit_event


@pytest.mark.integration
class TestEventBusIntegration:
    """Echte EventBus-Integration."""

    @pytest.fixture(autouse=True)
    def reset_bus(self):
        """EventBus vor und nach jedem Test zurücksetzen."""
        reset_event_bus()
        yield
        reset_event_bus()

    def test_emit_reaches_subscriber(self):
        """Emitted Events erreichen alle Subscriber."""
        received = []

        def listener(event: AgentEvent):
            received.append(event)

        bus = get_event_bus()
        bus.subscribe(listener)

        evt = AgentEvent(
            agent_name="Test-Agent",
            event_type=EventType.TASK_COMPLETED,
            message="Fertig",
        )
        bus.emit(evt)

        assert len(received) == 1
        assert received[0].agent_name == "Test-Agent"
        assert received[0].event_type == EventType.TASK_COMPLETED

    def test_multiple_subscribers(self):
        """Mehrere Subscriber erhalten alle Events."""
        a_events = []
        b_events = []

        def listener_a(e: AgentEvent):
            a_events.append(e)

        def listener_b(e: AgentEvent):
            b_events.append(e)

        bus = get_event_bus()
        bus.subscribe(listener_a)
        bus.subscribe(listener_b)

        emit_event(
            EventType.TASK_STARTED,
            agent_name="Agent1",
            task_id="t-1",
            message="Start",
        )

        assert len(a_events) == 1
        assert len(b_events) == 1
        assert a_events[0].task_id == "t-1"
        assert b_events[0].event_type == EventType.TASK_STARTED

    def test_unsubscribe_stops_receiving(self):
        """Nach unsubscribe werden keine Events mehr empfangen."""
        received = []

        def listener(e: AgentEvent):
            received.append(e)

        bus = get_event_bus()
        bus.subscribe(listener)
        bus.emit(AgentEvent(agent_name="A", event_type=EventType.TASK_CREATED))
        assert len(received) == 1

        bus.unsubscribe(listener)
        bus.emit(AgentEvent(agent_name="B", event_type=EventType.TASK_CREATED))
        assert len(received) == 1

    def test_emit_event_via_emitter(self):
        """emit_event() sendet an EventBus."""
        received = []

        def listener(e: AgentEvent):
            received.append(e)

        bus = get_event_bus()
        bus.subscribe(listener)

        emit_event(
            EventType.MODEL_CALL,
            agent_name="",
            message="llama3:latest",
            metadata={"duration_sec": 1.5},
        )

        assert len(received) == 1
        assert received[0].event_type == EventType.MODEL_CALL
        assert received[0].metadata.get("duration_sec") == 1.5

    def test_listener_exception_does_not_break_others(self):
        """Fehler in einem Listener brechen andere nicht ab."""
        good_received = []

        def bad_listener(_e: AgentEvent):
            raise ValueError("Intentional")

        def good_listener(e: AgentEvent):
            good_received.append(e)

        bus = get_event_bus()
        bus.subscribe(bad_listener)
        bus.subscribe(good_listener)

        bus.emit(AgentEvent(agent_name="X", event_type=EventType.TASK_COMPLETED))

        assert len(good_received) == 1

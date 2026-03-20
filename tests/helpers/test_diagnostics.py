"""
Test: Diagnostik-Helpers funktionieren.
"""

import pytest

from tests.helpers.diagnostics import (
    dump_chat_state,
    dump_debug_store,
    dump_recent_events,
    dump_agent_context,
    dump_prompt_context,
    dump_streaming_state,
)

from app.debug.debug_store import DebugStore
from app.debug.event_bus import EventBus
from app.debug.agent_event import AgentEvent, EventType


def test_dump_chat_state_none():
    """dump_chat_state mit None."""
    assert "None" in dump_chat_state(None)


def test_dump_debug_store_none():
    """dump_debug_store mit None."""
    assert "None" in dump_debug_store(None)


def test_dump_debug_store_with_events():
    """dump_debug_store mit Events."""
    bus = EventBus()
    store = DebugStore(bus=bus)
    bus.emit(AgentEvent(agent_name="Test", event_type=EventType.TASK_COMPLETED, message="done"))
    out = dump_debug_store(store)
    assert "1 events" in out
    assert "task_completed" in out
    store._unsubscribe()


def test_dump_recent_events():
    """dump_recent_events."""
    bus = EventBus()
    store = DebugStore(bus=bus)
    bus.emit(AgentEvent(agent_name="A", event_type=EventType.MODEL_CALL, message="llama"))
    out = dump_recent_events(store, n=3)
    assert "MODEL_CALL" in out or "model_call" in out
    store._unsubscribe()


def test_dump_agent_context(test_agent):
    """dump_agent_context mit AgentProfile."""
    out = dump_agent_context(test_agent)
    assert test_agent.name in out


def test_dump_prompt_context(test_prompt):
    """dump_prompt_context mit Prompt."""
    out = dump_prompt_context(test_prompt)
    assert test_prompt.title in out


def test_dump_streaming_state_none():
    """dump_streaming_state mit None."""
    assert "None" in dump_streaming_state(None)


def test_dump_streaming_state_with_widget():
    """dump_streaming_state mit Objekt das _streaming hat."""
    from unittest.mock import MagicMock

    w = MagicMock()
    w._streaming = True
    w._streaming_message_widget = None
    w.current_full_response = "test"
    out = dump_streaming_state(w)
    assert "_streaming" in out
    assert "True" in out

"""
Contract Tests: Debug Event Payload.

Sichert den Vertrag zwischen AgentEvent und allen Konsumenten
(EventBus, DebugStore, EventTimelineView, MetricsCollector).
"""

from datetime import datetime, timezone

import pytest

from app.debug.agent_event import AgentEvent, EventType


REQUIRED_AGENT_EVENT_FIELDS = [
    "timestamp",
    "agent_name",
    "task_id",
    "event_type",
    "message",
    "metadata",
]


@pytest.mark.contract
def test_agent_event_to_dict_contains_required_fields(test_event):
    """AgentEvent.to_dict() liefert alle Pflichtfelder für Debug-UI."""
    d = test_event.to_dict()
    for field in REQUIRED_AGENT_EVENT_FIELDS:
        assert field in d, f"Pflichtfeld '{field}' fehlt in to_dict()"


@pytest.mark.contract
def test_agent_event_event_type_serializes_as_string(test_event):
    """event_type wird als String-Wert serialisiert (nicht Enum-Name)."""
    d = test_event.to_dict()
    assert d["event_type"] == "task_completed"
    assert isinstance(d["event_type"], str)


@pytest.mark.contract
def test_agent_event_timestamp_serializes_as_iso():
    """timestamp wird als ISO-String serialisiert."""
    ts = datetime(2025, 3, 15, 12, 0, 0, tzinfo=timezone.utc)
    event = AgentEvent(
        timestamp=ts,
        agent_name="Test",
        event_type=EventType.MODEL_CALL,
        message="",
    )
    d = event.to_dict()
    assert "2025-03-15" in d["timestamp"]
    assert "T" in d["timestamp"]


@pytest.mark.contract
def test_agent_event_metadata_is_dict(test_event):
    """metadata ist immer ein Dict (serialisierbar)."""
    d = test_event.to_dict()
    assert isinstance(d["metadata"], dict)


@pytest.mark.contract
def test_event_type_values_are_stable():
    """EventType-Enum-Werte sind stabil für Debug-Store und UI."""
    from tests.contracts.event_type_registry import EVENT_TYPE_CONTRACT

    for et, expected_value in EVENT_TYPE_CONTRACT.items():
        assert et.value == expected_value, f"EventType {et}: erwartet {expected_value}, got {et.value}"

"""
Tests für das Performance-Tracking-Metrics-System.
"""

import tempfile
import os

import pytest

from app.debug.agent_event import AgentEvent, EventType
from app.debug.event_bus import EventBus, reset_event_bus
from app.metrics.agent_metrics import (
    AgentMetricEvent,
    MetricEventType,
    TimeRange,
)
from app.metrics.metrics_collector import MetricsCollector
from app.metrics.metrics_store import MetricsStore, get_metrics_store
from app.metrics.metrics_service import MetricsService, get_metrics_service


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def store(temp_db):
    return MetricsStore(db_path=temp_db)


@pytest.fixture
def bus():
    reset_event_bus()
    return EventBus()


@pytest.fixture
def collector(bus, store):
    c = MetricsCollector(bus=bus, store=store)
    c.start()
    yield c
    c.stop()


def test_metrics_store_insert_and_query(store):
    """MetricsStore speichert und liefert Events."""
    from datetime import datetime, timezone

    ev = AgentMetricEvent(
        timestamp=datetime.now(timezone.utc),
        agent_id="agent-1",
        event_type=MetricEventType.TASK_COMPLETED,
        duration_sec=2.5,
    )
    store.insert_event(ev)
    events = store.get_events("agent-1", TimeRange.ALL)
    assert len(events) == 1
    assert events[0].agent_id == "agent-1"
    assert events[0].event_type == MetricEventType.TASK_COMPLETED
    assert events[0].duration_sec == 2.5


def test_metrics_collector_task_completed(bus, store, collector):
    """MetricsCollector sammelt TASK_COMPLETED mit agent_id."""
    from datetime import datetime, timezone

    bus.emit(
        AgentEvent(
            timestamp=datetime.now(timezone.utc),
            agent_name="Test Agent",
            event_type=EventType.TASK_COMPLETED,
            task_id="t1",
            metadata={"agent_id": "agent-123"},
        )
    )
    events = store.get_events("agent-123", TimeRange.ALL)
    assert len(events) == 1
    assert events[0].event_type == MetricEventType.TASK_COMPLETED


def test_metrics_collector_task_failed(bus, store, collector):
    """MetricsCollector sammelt TASK_FAILED."""
    from datetime import datetime, timezone

    bus.emit(
        AgentEvent(
            timestamp=datetime.now(timezone.utc),
            agent_name="Agent X",
            event_type=EventType.TASK_FAILED,
            task_id="t2",
            metadata={"agent_id": "agent-x", "error": "Fehler"},
        )
    )
    events = store.get_events("agent-x", TimeRange.ALL)
    assert len(events) == 1
    assert events[0].event_type == MetricEventType.TASK_FAILED


def test_metrics_collector_model_call(bus, store, collector):
    """MetricsCollector sammelt MODEL_CALL."""
    from datetime import datetime, timezone

    bus.emit(
        AgentEvent(
            timestamp=datetime.now(timezone.utc),
            agent_name="Chat",
            event_type=EventType.MODEL_CALL,
            message="llama3",
            metadata={
                "agent_id": "agent-chat",
                "model_id": "llama3",
                "duration_sec": 1.2,
            },
        )
    )
    events = store.get_events("agent-chat", TimeRange.ALL)
    assert len(events) == 1
    assert events[0].event_type == MetricEventType.MODEL_CALL
    assert events[0].model_id == "llama3"
    assert events[0].duration_sec == 1.2


def test_metrics_collector_fallback_agent_name(bus, store, collector):
    """Ohne agent_id wird agent_name als Fallback verwendet."""
    from datetime import datetime, timezone

    bus.emit(
        AgentEvent(
            timestamp=datetime.now(timezone.utc),
            agent_name="FallbackAgent",
            event_type=EventType.TASK_COMPLETED,
            metadata={},
        )
    )
    events = store.get_events("FallbackAgent", TimeRange.ALL)
    assert len(events) == 1


def test_metrics_service_statistics(store):
    """MetricsService liefert korrekte Statistiken."""
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    store.insert_event(
        AgentMetricEvent(now, "a1", MetricEventType.TASK_COMPLETED, duration_sec=3.0)
    )
    store.insert_event(
        AgentMetricEvent(now, "a1", MetricEventType.TASK_COMPLETED, duration_sec=5.0)
    )
    store.insert_event(AgentMetricEvent(now, "a1", MetricEventType.TASK_FAILED))
    store.insert_event(
        AgentMetricEvent(
            now, "a1", MetricEventType.MODEL_CALL, model_id="llama", token_count=100
        )
    )

    svc = MetricsService(store=store)
    stats = svc.get_agent_statistics("a1", TimeRange.ALL)
    assert stats.total_tasks == 3
    assert stats.tasks_completed == 2
    assert stats.tasks_failed == 1
    assert abs(stats.success_rate - 2 / 3) < 0.01
    assert stats.avg_runtime == 4.0
    assert stats.total_model_calls == 1
    assert stats.most_used_model == "llama"

"""
Metrics unter Failure Conditions: Fehlerpfade verfälschen keine Metriken.

Fehlerklasse: failure path corrupts or falsifies metrics.

Prüft:
- fehlgeschlagener Chat/Task erhöht nicht completed
- failed wird korrekt erhöht
- Runtime bleibt plausibel
- Model Calls / Token Usage bleiben konsistent
- keine Success-Metrics trotz Failure-State
"""

import tempfile
import os
from datetime import datetime, timezone

import pytest

from app.debug.agent_event import AgentEvent, EventType
from app.debug.event_bus import EventBus, reset_event_bus
from app.metrics.agent_metrics import MetricEventType, TimeRange
from app.metrics.metrics_collector import MetricsCollector
from app.metrics.metrics_store import MetricsStore
from app.metrics.metrics_service import MetricsService
from tests.helpers.diagnostics import dump_metrics_state


@pytest.fixture
def metrics_store_temp():
    """Isolierter MetricsStore mit temporärer DB."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    store = MetricsStore(db_path=path)
    yield store
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def collector_with_store(metrics_store_temp):
    """MetricsCollector mit isoliertem EventBus und Store."""
    bus = EventBus()
    collector = MetricsCollector(bus=bus, store=metrics_store_temp)
    collector.start()
    yield bus, metrics_store_temp, collector
    collector.stop()


@pytest.mark.failure_mode
def test_task_failed_increases_failed_not_completed(collector_with_store):
    """
    TASK_FAILED → tasks_failed erhöht sich, tasks_completed nicht.

    Verhindert: Failure wird fälschlich als Success gezählt.
    """
    bus, store, collector = collector_with_store
    agent_id = "metrics-fail-agent"

    bus.emit(AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name=agent_id,
        task_id="task-fail-1",
        event_type=EventType.TASK_FAILED,
        message="Simulated failure",
        metadata={"agent_id": agent_id, "error": "Test error"},
    ))

    bus.emit(AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name=agent_id,
        task_id="task-fail-2",
        event_type=EventType.TASK_FAILED,
        message="Simulated failure 2",
        metadata={"agent_id": agent_id},
    ))

    collector.stop()

    events = store.get_events(agent_id, TimeRange.ALL)
    failed_events = [e for e in events if e.event_type == MetricEventType.TASK_FAILED]
    completed_events = [e for e in events if e.event_type == MetricEventType.TASK_COMPLETED]

    assert len(failed_events) == 2, dump_metrics_state(store, failed=True, agent_id=agent_id)
    assert len(completed_events) == 0, (
        "Bei Failure darf TASK_COMPLETED nicht erhöht werden. "
        + dump_metrics_state(store, failed=True, agent_id=agent_id)
    )

    service = MetricsService(store=store)
    stats = service.get_agent_statistics(agent_id, TimeRange.ALL)
    assert stats.tasks_failed == 2
    assert stats.tasks_completed == 0
    assert stats.success_rate == 0.0


@pytest.mark.failure_mode
def test_mixed_failures_and_completions_metrics_correct(collector_with_store):
    """
    Gemischte Events: completed und failed werden korrekt getrennt.

    Verhindert: Vermischung oder falsche Aggregation.
    """
    bus, store, collector = collector_with_store
    agent_id = "metrics-mixed-agent"

    bus.emit(AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name=agent_id,
        task_id="t1",
        event_type=EventType.TASK_COMPLETED,
        metadata={"agent_id": agent_id, "duration_sec": 2.0},
    ))
    bus.emit(AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name=agent_id,
        task_id="t2",
        event_type=EventType.TASK_FAILED,
        message="Failed",
        metadata={"agent_id": agent_id},
    ))
    bus.emit(AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name=agent_id,
        task_id="t3",
        event_type=EventType.TASK_COMPLETED,
        metadata={"agent_id": agent_id, "duration_sec": 1.5},
    ))

    collector.stop()

    service = MetricsService(store=store)
    stats = service.get_agent_statistics(agent_id, TimeRange.ALL)

    assert stats.tasks_completed == 2
    assert stats.tasks_failed == 1
    assert stats.total_tasks == 3
    assert abs(stats.success_rate - 2 / 3) < 0.01
    assert stats.avg_runtime > 0


@pytest.mark.failure_mode
def test_model_call_on_failure_does_not_increase_completed(collector_with_store):
    """
    MODEL_CALL mit error in metadata: zählt als Model-Call, nicht als Task-Completed.

    Verhindert: Fehlgeschlagener Chat wird fälschlich als Success-Task gezählt.
    """
    bus, store, collector = collector_with_store
    agent_id = "metrics-chat-fail"

    # MODEL_CALL (z.B. von Chat bei Exception) – hat error in metadata
    bus.emit(AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name="Chat",
        event_type=EventType.MODEL_CALL,
        message="llama3",
        metadata={
            "agent_id": agent_id,
            "model_id": "llama3",
            "duration_sec": 0.5,
            "error": "Connection timeout",
        },
    ))

    collector.stop()

    events = store.get_events(agent_id, TimeRange.ALL)
    model_calls = [e for e in events if e.event_type == MetricEventType.MODEL_CALL]
    completed = [e for e in events if e.event_type == MetricEventType.TASK_COMPLETED]

    assert len(model_calls) == 1
    assert len(completed) == 0, (
        "MODEL_CALL mit error darf nicht als TASK_COMPLETED zählen. "
        + dump_metrics_state(store, failed=True, agent_id=agent_id)
    )

    service = MetricsService(store=store)
    stats = service.get_agent_statistics(agent_id, TimeRange.ALL)
    assert stats.tasks_completed == 0
    assert stats.tasks_failed == 0
    assert stats.total_model_calls == 1


@pytest.mark.failure_mode
def test_runtime_plausible_on_failure(collector_with_store):
    """
    Bei TASK_FAILED: duration_sec wird nicht fälschlich für avg_runtime genutzt.

    avg_runtime basiert nur auf TASK_COMPLETED mit duration_sec > 0.
    """
    bus, store, collector = collector_with_store
    agent_id = "metrics-runtime-agent"

    bus.emit(AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name=agent_id,
        task_id="t1",
        event_type=EventType.TASK_FAILED,
        metadata={"agent_id": agent_id, "duration_sec": 999.0},  # Sollte ignoriert werden
    ))

    bus.emit(AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name=agent_id,
        task_id="t2",
        event_type=EventType.TASK_COMPLETED,
        metadata={"agent_id": agent_id, "duration_sec": 2.0},
    ))

    collector.stop()

    service = MetricsService(store=store)
    stats = service.get_agent_statistics(agent_id, TimeRange.ALL)

    # avg_runtime sollte nur aus TASK_COMPLETED kommen
    assert stats.avg_runtime == 2.0
    assert stats.avg_runtime != 999.0

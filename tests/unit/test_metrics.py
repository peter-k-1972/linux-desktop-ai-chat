"""
Unit Tests: Metrics System.

Testet MetricsCollector, MetricsStore, MetricsService.
"""

import sqlite3
from datetime import datetime, timezone, timedelta

import pytest

from app.utils.datetime_utils import to_iso_datetime

from app.metrics.agent_metrics import (
    AgentMetric,
    AgentMetricEvent,
    AgentStatistics,
    MetricEventType,
    TimeRange,
)
from app.metrics.metrics_store import MetricsStore
from app.metrics.metrics_service import MetricsService
from app.metrics.metrics_collector import MetricsCollector
from app.debug.agent_event import AgentEvent, EventType
from app.debug.event_bus import EventBus, reset_event_bus


# --- AgentMetric / AgentMetricEvent ---

def test_agent_metric_total_tasks():
    """AgentMetric.total_tasks = completed + failed."""
    m = AgentMetric(
        timestamp=datetime.now(timezone.utc),
        agent_id="a1",
        tasks_completed=5,
        tasks_failed=2,
    )
    assert m.total_tasks == 7


def test_agent_metric_success_rate():
    """AgentMetric.success_rate berechnet korrekt."""
    m = AgentMetric(
        timestamp=datetime.now(timezone.utc),
        agent_id="a1",
        tasks_completed=8,
        tasks_failed=2,
    )
    assert abs(m.success_rate - 0.8) < 0.01


def test_agent_metric_event_to_dict(test_metric_event):
    """AgentMetricEvent.to_dict() serialisiert."""
    d = test_metric_event.to_dict()
    assert d["agent_id"] == "agent-001"
    assert d["event_type"] == "task_completed"
    assert "timestamp" in d


# --- MetricsStore ---

def test_metrics_store_insert_and_get(temp_db_path, test_metric_event):
    """MetricsStore speichert und lädt Events."""
    store = MetricsStore(db_path=temp_db_path)
    store.insert_event(test_metric_event)
    events = store.get_events("agent-001", TimeRange.ALL)
    assert len(events) == 1
    assert events[0].event_type == MetricEventType.TASK_COMPLETED


def test_metrics_store_time_range(temp_db_path, test_metric_event):
    """MetricsStore filtert nach Zeitbereich."""
    store = MetricsStore(db_path=temp_db_path)
    store.insert_event(test_metric_event)
    events = store.get_events("agent-001", TimeRange.LAST_HOUR)
    assert len(events) <= 1


def test_metrics_store_aggregated(temp_db_path, test_metric_event):
    """get_aggregated_metrics aggregiert korrekt."""
    store = MetricsStore(db_path=temp_db_path)
    for _ in range(3):
        store.insert_event(test_metric_event)
    metrics = store.get_aggregated_metrics("agent-001", TimeRange.ALL)
    assert len(metrics) >= 1
    total = sum(m.tasks_completed for m in metrics)
    assert total >= 3


def test_metrics_store_get_latest_event_timestamp_max_not_asc_limit_window(temp_db_path):
    """
    get_latest_event_timestamp nutzt MAX(timestamp), nicht get_events(ASC LIMIT n).

    Bei >10k Events liefert get_events nur die ältesten 10000 Zeilen; das Maximum darunter
    wäre fachlich falsch für „letzte Aktivität“.
    """
    store = MetricsStore(db_path=temp_db_path)
    agent_id = "heavy-agent"
    t0 = datetime(2020, 1, 1, tzinfo=timezone.utc)
    bulk = []
    for i in range(10000):
        ts = to_iso_datetime(t0 + timedelta(seconds=i)) or ""
        bulk.append(
            (
                ts,
                agent_id,
                MetricEventType.TASK_COMPLETED.value,
                f"t{i}",
                0.1,
                None,
                0,
                None,
                None,
            )
        )
    newest = datetime(2025, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
    newest_s = to_iso_datetime(newest) or ""
    with sqlite3.connect(temp_db_path) as conn:
        conn.executemany(
            """
            INSERT INTO agent_metric_events
            (timestamp, agent_id, event_type, task_id, duration_sec, model_id, token_count, critic_score, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            bulk,
        )
        conn.execute(
            """
            INSERT INTO agent_metric_events
            (timestamp, agent_id, event_type, task_id, duration_sec, model_id, token_count, critic_score, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                newest_s,
                agent_id,
                MetricEventType.TASK_COMPLETED.value,
                "t_newest",
                1.0,
                None,
                0,
                None,
                None,
            ),
        )
        conn.commit()
    batch = store.get_events(agent_id, TimeRange.ALL, limit=10000)
    assert len(batch) == 10000
    misleading_max = max(e.timestamp for e in batch)
    latest = store.get_latest_event_timestamp(agent_id)
    assert latest == newest
    assert misleading_max < newest


def test_metrics_store_model_distribution(temp_db_path):
    """get_model_usage_distribution zählt Modellaufrufe."""
    store = MetricsStore(db_path=temp_db_path)
    ev = AgentMetricEvent(
        timestamp=datetime.now(timezone.utc),
        agent_id="a1",
        event_type=MetricEventType.MODEL_CALL,
        model_id="llama3",
    )
    store.insert_event(ev)
    store.insert_event(ev)
    dist = store.get_model_usage_distribution("a1", TimeRange.ALL)
    assert dist.get("llama3") == 2


# --- MetricsService ---

def test_metrics_service_get_agent_metrics(temp_db_path, test_metric_event):
    """MetricsService.get_agent_metrics liefert Metriken."""
    store = MetricsStore(db_path=temp_db_path)
    store.insert_event(test_metric_event)
    service = MetricsService(store=store)
    metrics = service.get_agent_metrics("agent-001", TimeRange.ALL)
    assert isinstance(metrics, list)


def test_metrics_service_get_agent_statistics(temp_db_path, test_metric_event):
    """MetricsService.get_agent_statistics liefert Zusammenfassung."""
    store = MetricsStore(db_path=temp_db_path)
    store.insert_event(test_metric_event)
    service = MetricsService(store=store)
    stats = service.get_agent_statistics("agent-001", TimeRange.ALL)
    assert isinstance(stats, AgentStatistics)
    assert stats.agent_id == "agent-001"
    assert stats.total_tasks >= 1
    assert 0 <= stats.success_rate <= 1.0


def test_metrics_service_empty_agent(temp_db_path):
    """Leerer Agent hat success_rate 1.0."""
    service = MetricsService(store=MetricsStore(db_path=temp_db_path))
    stats = service.get_agent_statistics("unknown-agent", TimeRange.ALL)
    assert stats.success_rate == 1.0
    assert stats.total_tasks == 0


# --- MetricsCollector ---

def test_metrics_collector_handles_task_completed(temp_db_path):
    """MetricsCollector verarbeitet TASK_COMPLETED."""
    bus = EventBus()
    store = MetricsStore(db_path=temp_db_path)
    collector = MetricsCollector(bus=bus, store=store)
    collector.start()
    event = AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name="Test",
        task_id="t1",
        event_type=EventType.TASK_COMPLETED,
        metadata={"agent_id": "a1", "duration_sec": 1.0},
    )
    bus.emit(event)
    collector.stop()
    events = store.get_events("a1", TimeRange.ALL)
    assert len(events) == 1
    assert events[0].event_type == MetricEventType.TASK_COMPLETED


def test_metrics_collector_handles_task_failed(temp_db_path):
    """MetricsCollector verarbeitet TASK_FAILED."""
    bus = EventBus()
    store = MetricsStore(db_path=temp_db_path)
    collector = MetricsCollector(bus=bus, store=store)
    collector.start()
    event = AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name="Test",
        task_id="t1",
        event_type=EventType.TASK_FAILED,
        metadata={"agent_id": "a1"},
    )
    bus.emit(event)
    collector.stop()
    events = store.get_events("a1", TimeRange.ALL)
    assert len(events) == 1
    assert events[0].event_type == MetricEventType.TASK_FAILED


def test_metrics_collector_handles_model_call(temp_db_path):
    """MetricsCollector verarbeitet MODEL_CALL."""
    bus = EventBus()
    store = MetricsStore(db_path=temp_db_path)
    collector = MetricsCollector(bus=bus, store=store)
    collector.start()
    event = AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name="Test",
        event_type=EventType.MODEL_CALL,
        message="llama3",
        metadata={"agent_id": "a1", "model_id": "llama3", "token_count": 100},
    )
    bus.emit(event)
    collector.stop()
    events = store.get_events("a1", TimeRange.ALL)
    assert len(events) == 1
    assert events[0].event_type == MetricEventType.MODEL_CALL
    assert events[0].model_id == "llama3"

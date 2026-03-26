"""
MetricsService – API für Agenten-Performance-Metriken.

Bietet get_agent_metrics, get_metrics_range, get_agent_statistics.
"""

from typing import List, Optional

from app.metrics.agent_metrics import (
    AgentMetric,
    AgentStatistics,
    MetricEventType,
    TimeRange,
)
from app.metrics.metrics_store import MetricsStore, get_metrics_store


class MetricsService:
    """Service-Layer für Metrik-Abfragen."""

    def __init__(self, store: Optional[MetricsStore] = None):
        self._store = store or get_metrics_store()

    def get_agent_metrics(
        self,
        agent_id: str,
        time_range: TimeRange = TimeRange.ALL,
        bucket_hours: int = 1,
    ) -> List[AgentMetric]:
        """
        Liefert aggregierte Metriken für einen Agenten.

        Args:
            agent_id: Agent-ID
            time_range: Zeitbereich (Letzte Stunde, Tag, Woche, Gesamt)
            bucket_hours: Bucket-Größe in Stunden für Zeitreihen

        Returns:
            Liste von AgentMetric, sortiert nach Zeit
        """
        return self._store.get_aggregated_metrics(
            agent_id=agent_id,
            time_range=time_range,
            bucket_hours=bucket_hours,
        )

    def get_metrics_range(
        self,
        agent_id: str,
        time_range: TimeRange,
    ) -> List[AgentMetric]:
        """
        Liefert Metriken für einen Zeitbereich.

        Nutzt sinnvolle Bucket-Größen je nach Range:
        - 1h: 15-Minuten-Buckets
        - 1d: 1-Stunden-Buckets
        - 7d: 6-Stunden-Buckets
        - all: 24-Stunden-Buckets
        """
        bucket_map = {
            TimeRange.LAST_HOUR: 0,  # 0 = feinere Aggregation
            TimeRange.LAST_DAY: 1,
            TimeRange.LAST_WEEK: 6,
            TimeRange.ALL: 24,
        }
        bucket = bucket_map.get(time_range, 1)
        if bucket == 0:
            bucket = 1  # Mindestens 1h für LAST_HOUR
        return self.get_agent_metrics(agent_id, time_range, bucket_hours=bucket)

    def get_agent_statistics(
        self,
        agent_id: str,
        time_range: TimeRange = TimeRange.ALL,
    ) -> AgentStatistics:
        """
        Liefert Zusammenfassung der Agenten-Performance.

        Enthält: Total Tasks, Success Rate, Avg Runtime, Most Used Model, etc.
        """
        events = self._store.get_events(agent_id, time_range)
        completed = sum(1 for e in events if e.event_type == MetricEventType.TASK_COMPLETED)
        failed = sum(1 for e in events if e.event_type == MetricEventType.TASK_FAILED)
        total = completed + failed
        success_rate = completed / total if total > 0 else 1.0

        runtimes = [
            e.duration_sec
            for e in events
            if e.event_type == MetricEventType.TASK_COMPLETED and e.duration_sec > 0
        ]
        avg_runtime = sum(runtimes) / len(runtimes) if runtimes else 0.0

        model_calls = sum(1 for e in events if e.event_type == MetricEventType.MODEL_CALL)
        token_usage = sum(e.token_count for e in events)

        dist = self._store.get_model_usage_distribution(agent_id, time_range)
        most_used = max(dist, key=dist.get) if dist else None

        return AgentStatistics(
            agent_id=agent_id,
            total_tasks=total,
            tasks_completed=completed,
            tasks_failed=failed,
            success_rate=success_rate,
            avg_runtime=avg_runtime,
            total_model_calls=model_calls,
            total_token_usage=token_usage,
            most_used_model=most_used,
            model_usage_distribution=dist,
        )


# Singleton
_service: Optional[MetricsService] = None


def get_metrics_service(store: Optional[MetricsStore] = None) -> MetricsService:
    """Liefert den globalen MetricsService."""
    global _service
    if _service is None:
        _service = MetricsService(store=store)
    return _service

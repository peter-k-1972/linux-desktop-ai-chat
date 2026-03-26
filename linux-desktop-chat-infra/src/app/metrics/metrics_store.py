"""
MetricsStore – SQLite-Persistenz für Agenten-Metriken.

Speichert Metrik-Events und ermöglicht Abfragen nach Agent und Zeitbereich.
"""

import json
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from app.metrics.agent_metrics import (
    AgentMetric,
    AgentMetricEvent,
    MetricEventType,
    TimeRange,
)
from app.utils.datetime_utils import parse_datetime, to_iso_datetime


class MetricsStore:
    """
    SQLite-basierter Store für Agenten-Metriken.

    Nutzt dieselbe DB wie die App (chat_history.db).
    """

    def __init__(self, db_path: str = "chat_history.db"):
        self.db_path = db_path
        self._init_tables()

    def _init_tables(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_metric_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL,
                    agent_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    task_id TEXT,
                    duration_sec REAL DEFAULT 0,
                    model_id TEXT,
                    token_count INTEGER DEFAULT 0,
                    critic_score REAL,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metric_events_agent
                ON agent_metric_events(agent_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metric_events_timestamp
                ON agent_metric_events(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_metric_events_agent_time
                ON agent_metric_events(agent_id, timestamp)
            """)
            conn.commit()

    def insert_event(self, event: AgentMetricEvent) -> None:
        """Speichert ein Metrik-Event."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO agent_metric_events
                (timestamp, agent_id, event_type, task_id, duration_sec, model_id, token_count, critic_score, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    to_iso_datetime(event.timestamp) or "",
                    event.agent_id,
                    event.event_type.value,
                    event.task_id,
                    event.duration_sec,
                    event.model_id,
                    event.token_count,
                    event.critic_score,
                    json.dumps(event.metadata) if event.metadata else None,
                ),
            )
            conn.commit()

    def _time_range_to_interval(self, time_range: TimeRange) -> Optional[timedelta]:
        """Konvertiert TimeRange in timedelta."""
        if time_range == TimeRange.ALL:
            return None
        if time_range == TimeRange.LAST_HOUR:
            return timedelta(hours=1)
        if time_range == TimeRange.LAST_DAY:
            return timedelta(days=1)
        if time_range == TimeRange.LAST_WEEK:
            return timedelta(weeks=1)
        return None

    def get_events(
        self,
        agent_id: str,
        time_range: TimeRange = TimeRange.ALL,
        limit: int = 10000,
    ) -> List[AgentMetricEvent]:
        """Lädt Metrik-Events für einen Agenten im Zeitbereich."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            params: list = [agent_id]
            where = "agent_id = ?"
            delta = self._time_range_to_interval(time_range)
            if delta:
                since = datetime.now(timezone.utc) - delta
                where += " AND timestamp >= ?"
                params.append(to_iso_datetime(since) or "")
            sql = f"SELECT * FROM agent_metric_events WHERE {where} ORDER BY timestamp ASC LIMIT ?"
            params.append(limit)
            rows = conn.execute(sql, params).fetchall()
            return [self._row_to_event(dict(r)) for r in rows]

    def get_latest_event_timestamp(
        self,
        agent_id: str,
        time_range: TimeRange = TimeRange.ALL,
    ) -> Optional[datetime]:
        """
        Zeitstempel des neuesten Events für den Agenten (MAX(timestamp)), ohne LIMIT-Fenster.

        Unabhängig von get_events(ORDER BY ASC LIMIT n) – für belastbare „letzte Aktivität“.
        """
        with sqlite3.connect(self.db_path) as conn:
            params: list = [agent_id]
            where = "agent_id = ?"
            delta = self._time_range_to_interval(time_range)
            if delta:
                since = datetime.now(timezone.utc) - delta
                where += " AND timestamp >= ?"
                params.append(to_iso_datetime(since) or "")
            row = conn.execute(
                f"SELECT MAX(timestamp) FROM agent_metric_events WHERE {where}",
                params,
            ).fetchone()
        if not row or row[0] is None:
            return None
        return parse_datetime(row[0])

    def _row_to_event(self, row: dict) -> AgentMetricEvent:
        meta = row.get("metadata")
        if meta:
            try:
                meta = json.loads(meta) if isinstance(meta, str) else meta
            except json.JSONDecodeError:
                meta = {}
        else:
            meta = {}
        return AgentMetricEvent(
            timestamp=parse_datetime(row["timestamp"]) or datetime.now(timezone.utc),
            agent_id=row["agent_id"],
            event_type=MetricEventType(row["event_type"]),
            task_id=row.get("task_id"),
            duration_sec=float(row.get("duration_sec") or 0),
            model_id=row.get("model_id"),
            token_count=int(row.get("token_count") or 0),
            critic_score=float(row["critic_score"]) if row.get("critic_score") is not None else None,
            metadata=meta,
        )

    def get_aggregated_metrics(
        self,
        agent_id: str,
        time_range: TimeRange = TimeRange.ALL,
        bucket_hours: int = 1,
    ) -> List[AgentMetric]:
        """
        Liefert aggregierte Metriken pro Zeit-Bucket.

        bucket_hours: Größe eines Buckets in Stunden (1 = stündlich, 24 = täglich).
        """
        events = self.get_events(agent_id, time_range)
        if not events:
            return []

        buckets: dict = {}
        runtime_counts: dict = {}  # key -> (total_sec, count) für avg
        for ev in events:
            ts = ev.timestamp
            bucket_key = ts.replace(minute=0, second=0, microsecond=0)
            if bucket_hours > 1:
                hour = bucket_key.hour
                bucket_key = bucket_key.replace(
                    hour=(hour // bucket_hours) * bucket_hours
                )
            key = to_iso_datetime(bucket_key) or ""
            if key not in buckets:
                buckets[key] = AgentMetric(timestamp=bucket_key, agent_id=agent_id)
                runtime_counts[key] = (0.0, 0)

            m = buckets[key]
            total_sec, rt_count = runtime_counts[key]
            if ev.event_type == MetricEventType.TASK_COMPLETED:
                m.tasks_completed += 1
                if ev.duration_sec > 0:
                    total_sec += ev.duration_sec
                    rt_count += 1
                    m.avg_runtime = total_sec / rt_count
                runtime_counts[key] = (total_sec, rt_count)
            elif ev.event_type == MetricEventType.TASK_FAILED:
                m.tasks_failed += 1
            elif ev.event_type == MetricEventType.MODEL_CALL:
                m.model_calls += 1
                m.token_usage += ev.token_count
            if ev.critic_score is not None:
                m.critic_score = ev.critic_score

        return sorted(buckets.values(), key=lambda x: x.timestamp)

    def get_model_usage_distribution(
        self,
        agent_id: str,
        time_range: TimeRange = TimeRange.ALL,
    ) -> Dict[str, int]:
        """Liefert Modellnutzung pro Modell (Anzahl Aufrufe)."""
        events = self.get_events(agent_id, time_range)
        dist: Dict[str, int] = {}
        for ev in events:
            if ev.event_type == MetricEventType.MODEL_CALL and ev.model_id:
                dist[ev.model_id] = dist.get(ev.model_id, 0) + 1
        return dist


# Singleton
_metrics_store: Optional[MetricsStore] = None


def get_metrics_store(db_path: str = "chat_history.db") -> MetricsStore:
    """Liefert den globalen MetricsStore."""
    global _metrics_store
    if _metrics_store is None:
        _metrics_store = MetricsStore(db_path)
    return _metrics_store

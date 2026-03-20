"""
AgentMetric – Datenstrukturen für Agenten-Performance-Metriken.

Definiert AgentMetric (aggregiert) und AgentMetricEvent (Rohdaten).
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class MetricEventType(str, Enum):
    """Typen von Metrik-Events."""

    TASK_COMPLETED = "task_completed"
    TASK_FAILED = "task_failed"
    MODEL_CALL = "model_call"


class TimeRange(str, Enum):
    """Zeitbereiche für Metrik-Abfragen."""

    LAST_HOUR = "1h"
    LAST_DAY = "1d"
    LAST_WEEK = "7d"
    ALL = "all"


@dataclass
class AgentMetricEvent:
    """
    Einzelnes Metrik-Event (Rohdaten).

    Wird vom MetricsCollector aus AgentEvent erzeugt und im Store gespeichert.
    """

    timestamp: datetime
    agent_id: str
    event_type: MetricEventType
    task_id: Optional[str] = None
    duration_sec: float = 0.0
    model_id: Optional[str] = None
    token_count: int = 0
    critic_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialisiert für Persistenz."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "agent_id": self.agent_id,
            "event_type": self.event_type.value,
            "task_id": self.task_id,
            "duration_sec": self.duration_sec,
            "model_id": self.model_id,
            "token_count": self.token_count,
            "critic_score": self.critic_score,
            "metadata": dict(self.metadata),
        }


@dataclass
class AgentMetric:
    """
    Aggregierte Metriken für einen Agenten in einem Zeitintervall.

    Wird aus AgentMetricEvents berechnet.
    """

    timestamp: datetime
    agent_id: str
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_runtime: float = 0.0
    model_calls: int = 0
    token_usage: int = 0
    critic_score: Optional[float] = None

    @property
    def total_tasks(self) -> int:
        """Gesamtzahl Tasks (erfolgreich + fehlgeschlagen)."""
        return self.tasks_completed + self.tasks_failed

    @property
    def success_rate(self) -> float:
        """Erfolgsquote (0.0–1.0)."""
        total = self.total_tasks
        if total == 0:
            return 1.0
        return self.tasks_completed / total

    @property
    def failure_rate(self) -> float:
        """Fehlerquote (0.0–1.0)."""
        return 1.0 - self.success_rate


@dataclass
class AgentStatistics:
    """
    Zusammenfassende Statistiken für einen Agenten.
    """

    agent_id: str
    total_tasks: int = 0
    tasks_completed: int = 0
    tasks_failed: int = 0
    success_rate: float = 1.0
    avg_runtime: float = 0.0
    total_model_calls: int = 0
    total_token_usage: int = 0
    most_used_model: Optional[str] = None
    model_usage_distribution: Dict[str, int] = field(default_factory=dict)

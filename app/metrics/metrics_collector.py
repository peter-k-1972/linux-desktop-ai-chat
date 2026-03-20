"""
MetricsCollector – sammelt Events vom Event-Bus und speichert sie.

Abonniert TASK_COMPLETED, TASK_FAILED, MODEL_CALL und wandelt sie
in AgentMetricEvents um.
"""

import logging
from typing import Optional

from app.debug.agent_event import AgentEvent, EventType
from app.debug.event_bus import EventBus, get_event_bus
from app.metrics.agent_metrics import AgentMetricEvent, MetricEventType
from app.metrics.metrics_store import MetricsStore, get_metrics_store

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Sammelt relevante Events vom Event-Bus und speichert sie im MetricsStore.

    Relevante Events:
    - TASK_COMPLETED
    - TASK_FAILED
    - MODEL_CALL
    """

    def __init__(
        self,
        bus: Optional[EventBus] = None,
        store: Optional[MetricsStore] = None,
    ):
        self._bus = bus or get_event_bus()
        self._store = store or get_metrics_store()
        self._subscribed = False

    def start(self) -> None:
        """Registriert sich beim Event-Bus."""
        if not self._subscribed:
            self._bus.subscribe(self._on_event)
            self._subscribed = True
            logger.debug("MetricsCollector gestartet")

    def stop(self) -> None:
        """Entfernt sich vom Event-Bus."""
        if self._subscribed:
            self._bus.unsubscribe(self._on_event)
            self._subscribed = False

    def _on_event(self, event: AgentEvent) -> None:
        """Verarbeitet eingehende Events."""
        try:
            if event.event_type == EventType.TASK_COMPLETED:
                self._handle_task_completed(event)
            elif event.event_type == EventType.TASK_FAILED:
                self._handle_task_failed(event)
            elif event.event_type == EventType.MODEL_CALL:
                self._handle_model_call(event)
        except Exception as e:
            logger.warning("MetricsCollector Fehler bei Event %s: %s", event.event_type, e)

    def _resolve_agent_id(self, event: AgentEvent) -> str:
        """
        Ermittelt die Agent-ID aus dem Event.

        Bevorzugt agent_id aus metadata, sonst agent_name als Fallback.
        """
        agent_id = event.metadata.get("agent_id") if event.metadata else None
        if agent_id:
            return str(agent_id)
        return event.agent_name or "unknown"

    def _handle_task_completed(self, event: AgentEvent) -> None:
        agent_id = self._resolve_agent_id(event)
        duration = event.metadata.get("duration_sec", 0.0) if event.metadata else 0.0
        metric = AgentMetricEvent(
            timestamp=event.timestamp,
            agent_id=agent_id,
            event_type=MetricEventType.TASK_COMPLETED,
            task_id=event.task_id,
            duration_sec=float(duration),
            critic_score=event.metadata.get("critic_score") if event.metadata else None,
            metadata=dict(event.metadata or {}),
        )
        self._store.insert_event(metric)

    def _handle_task_failed(self, event: AgentEvent) -> None:
        agent_id = self._resolve_agent_id(event)
        metric = AgentMetricEvent(
            timestamp=event.timestamp,
            agent_id=agent_id,
            event_type=MetricEventType.TASK_FAILED,
            task_id=event.task_id,
            metadata=dict(event.metadata or {}),
        )
        self._store.insert_event(metric)

    def _handle_model_call(self, event: AgentEvent) -> None:
        agent_id = self._resolve_agent_id(event)
        model_id = event.metadata.get("model_id") or event.message or "unknown"
        duration = event.metadata.get("duration_sec", 0.0) if event.metadata else 0.0
        token_count = event.metadata.get("token_count", 0) if event.metadata else 0
        metric = AgentMetricEvent(
            timestamp=event.timestamp,
            agent_id=agent_id,
            event_type=MetricEventType.MODEL_CALL,
            duration_sec=float(duration),
            model_id=model_id,
            token_count=int(token_count),
            metadata=dict(event.metadata or {}),
        )
        self._store.insert_event(metric)


# Singleton
_collector: Optional[MetricsCollector] = None


def get_metrics_collector(
    bus: Optional[EventBus] = None,
    store: Optional[MetricsStore] = None,
) -> MetricsCollector:
    """Liefert den globalen MetricsCollector und startet ihn."""
    global _collector
    if _collector is None:
        _collector = MetricsCollector(bus=bus, store=store)
        _collector.start()
    return _collector

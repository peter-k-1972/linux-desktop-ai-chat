"""
DebugStore – speichert Agenten-Events und aggregierte Debug-Daten.

Abonniert den EventBus automatisch und pflegt:
- active_tasks: Laufende und kürzlich abgeschlossene Tasks
- agent_status: Status pro Agent
- event_history: Chronologische Event-Timeline
- model_usage: Modellaufrufe mit Anzahl und Dauer
- tool_executions: Ausgeführte Tools mit Status
"""

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

from app.debug.agent_event import AgentEvent, EventType
from app.debug.event_bus import EventBus, get_event_bus

# Maximale Anzahl gespeicherter Events (Performance)
MAX_EVENT_HISTORY = 500
MAX_ACTIVE_TASKS = 100


@dataclass
class TaskInfo:
    """Kompakte Task-Info für den Debug Store."""

    task_id: str
    description: str
    agent_name: str
    status: str  # pending, running, completed, failed
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


@dataclass
class ModelUsageEntry:
    """Eintrag für Modellnutzung."""

    model_id: str
    call_count: int = 0
    total_duration_sec: float = 0.0
    last_call_at: Optional[datetime] = None


@dataclass
class ToolExecutionEntry:
    """Eintrag für Tool-Ausführung."""

    tool_name: str
    status: str  # started, completed, failed
    agent_name: str = ""
    task_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    error: Optional[str] = None


# Singleton DebugStore
_debug_store: "DebugStore | None" = None
_store_lock = threading.Lock()


def get_debug_store(bus: Optional[EventBus] = None) -> "DebugStore":
    """Liefert den globalen DebugStore (Singleton)."""
    global _debug_store
    with _store_lock:
        if _debug_store is None:
            _debug_store = DebugStore(bus or get_event_bus())
        return _debug_store


def reset_debug_store() -> None:
    """Setzt den DebugStore zurück (für Tests)."""
    global _debug_store
    with _store_lock:
        if _debug_store:
            _debug_store.clear()
            _debug_store._unsubscribe()
        _debug_store = None


class DebugStore:
    """
    Speichert und aggregiert Agenten-Events.

    Wird automatisch als Listener beim EventBus registriert.
    """

    def __init__(self, bus: EventBus):
        self._bus = bus
        self._bus.subscribe(self._on_event)
        self._lock = threading.RLock()

        self.active_tasks: Dict[str, TaskInfo] = {}
        self.agent_status: Dict[str, str] = {}  # agent_name -> status
        self.event_history: List[AgentEvent] = []
        self.model_usage: Dict[str, ModelUsageEntry] = {}
        self.tool_executions: List[ToolExecutionEntry] = []

    def _unsubscribe(self) -> None:
        """Entfernt sich vom EventBus."""
        self._bus.unsubscribe(self._on_event)

    def _on_event(self, event: AgentEvent) -> None:
        """Verarbeitet eingehende Events vom EventBus."""
        with self._lock:
            self._process_event(event)

    def _process_event(self, event: AgentEvent) -> None:
        """Verarbeitet ein einzelnes Event."""
        # Event History
        self.event_history.append(event)
        if len(self.event_history) > MAX_EVENT_HISTORY:
            self.event_history = self.event_history[-MAX_EVENT_HISTORY:]

        # Nach Event-Typ verarbeiten
        if event.event_type == EventType.TASK_CREATED:
            self._handle_task_created(event)
        elif event.event_type == EventType.TASK_STARTED:
            self._handle_task_started(event)
        elif event.event_type == EventType.TASK_COMPLETED:
            self._handle_task_completed(event)
        elif event.event_type == EventType.TASK_FAILED:
            self._handle_task_failed(event)
        elif event.event_type == EventType.AGENT_SELECTED:
            self._handle_agent_selected(event)
        elif event.event_type == EventType.MODEL_CALL:
            self._handle_model_call(event)
        elif event.event_type == EventType.TOOL_EXECUTION:
            self._handle_tool_execution(event)

    def _handle_task_created(self, event: AgentEvent) -> None:
        task_id = event.task_id or event.metadata.get("task_id", "")
        if not task_id:
            return
        desc = event.metadata.get("description") or event.message or ""
        self.active_tasks[task_id] = TaskInfo(
            task_id=task_id,
            description=desc,
            agent_name=event.agent_name or "",
            status="pending",
            created_at=event.timestamp,
        )
        self._trim_active_tasks()

    def _handle_task_started(self, event: AgentEvent) -> None:
        task_id = event.task_id or event.metadata.get("task_id", "")
        if task_id and task_id in self.active_tasks:
            self.active_tasks[task_id].status = "running"
            self.active_tasks[task_id].agent_name = event.agent_name or self.active_tasks[
                task_id
            ].agent_name
        self.agent_status[event.agent_name] = "running"

    def _handle_task_completed(self, event: AgentEvent) -> None:
        task_id = event.task_id or event.metadata.get("task_id", "")
        if task_id and task_id in self.active_tasks:
            self.active_tasks[task_id].status = "completed"
            self.active_tasks[task_id].completed_at = event.timestamp
        if event.agent_name:
            self.agent_status[event.agent_name] = "completed"

    def _handle_task_failed(self, event: AgentEvent) -> None:
        task_id = event.task_id or event.metadata.get("task_id", "")
        error = event.message or event.metadata.get("error", "")
        if task_id and task_id in self.active_tasks:
            self.active_tasks[task_id].status = "failed"
            self.active_tasks[task_id].error = error
            self.active_tasks[task_id].completed_at = event.timestamp
        if event.agent_name:
            self.agent_status[event.agent_name] = "failed"

    def _handle_agent_selected(self, event: AgentEvent) -> None:
        self.agent_status[event.agent_name] = "selected"

    def _handle_model_call(self, event: AgentEvent) -> None:
        model_id = event.metadata.get("model_id") or event.message or "unknown"
        if model_id not in self.model_usage:
            self.model_usage[model_id] = ModelUsageEntry(model_id=model_id)
        entry = self.model_usage[model_id]
        entry.call_count += 1
        duration = event.metadata.get("duration_sec", 0.0)
        entry.total_duration_sec += duration
        entry.last_call_at = event.timestamp

    def _handle_tool_execution(self, event: AgentEvent) -> None:
        tool_name = event.metadata.get("tool_name") or event.message or "unknown"
        status = event.metadata.get("status", "started")
        entry = ToolExecutionEntry(
            tool_name=tool_name,
            status=status,
            agent_name=event.agent_name,
            task_id=event.task_id,
            timestamp=event.timestamp,
            error=event.metadata.get("error"),
        )
        self.tool_executions.append(entry)
        if len(self.tool_executions) > MAX_EVENT_HISTORY:
            self.tool_executions = self.tool_executions[-MAX_EVENT_HISTORY:]

    def _trim_active_tasks(self) -> None:
        if len(self.active_tasks) <= MAX_ACTIVE_TASKS:
            return
        # Älteste completed/failed Tasks entfernen
        by_time = sorted(
            self.active_tasks.items(),
            key=lambda x: (x[1].completed_at or x[1].created_at or datetime.min)
            if x[1]
            else datetime.min,
        )
        to_remove = len(by_time) - MAX_ACTIVE_TASKS
        for i in range(to_remove):
            tid = by_time[i][0]
            if self.active_tasks[tid].status in ("completed", "failed"):
                del self.active_tasks[tid]

    def clear(self) -> None:
        """Löscht alle gespeicherten Daten."""
        with self._lock:
            self.active_tasks.clear()
            self.agent_status.clear()
            self.event_history.clear()
            self.model_usage.clear()
            self.tool_executions.clear()

    def get_event_history(self) -> List[AgentEvent]:
        """Liefert eine Kopie der Event-Historie (neueste zuerst)."""
        with self._lock:
            return list(reversed(self.event_history))

    def get_active_tasks(self) -> List[TaskInfo]:
        """Liefert eine Kopie der aktiven Tasks."""
        with self._lock:
            return list(self.active_tasks.values())

    def get_agent_status(self) -> Dict[str, str]:
        """Liefert eine Kopie des Agent-Status."""
        with self._lock:
            return dict(self.agent_status)

    def get_model_usage(self) -> List[ModelUsageEntry]:
        """Liefert Modellnutzung sortiert nach Aufrufen."""
        with self._lock:
            entries = [e for e in self.model_usage.values() if e.model_id]
            return sorted(entries, key=lambda e: -e.call_count)

    def get_tool_executions(self) -> List[ToolExecutionEntry]:
        """Liefert die letzten Tool-Ausführungen (neueste zuerst)."""
        with self._lock:
            return list(reversed(self.tool_executions))

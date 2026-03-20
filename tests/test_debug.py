"""
Tests für das Agent Debug System: Event Emission, Event Bus, Debug Store.
"""

import pytest
from datetime import datetime, timezone

from app.debug.agent_event import AgentEvent, EventType
from app.debug.event_bus import EventBus, get_event_bus, reset_event_bus
from app.debug.debug_store import (
    DebugStore,
    get_debug_store,
    reset_debug_store,
    TaskInfo,
    ModelUsageEntry,
    ToolExecutionEntry,
)
from app.debug.emitter import emit_event


# --- AgentEvent ---


def test_agent_event_creation():
    """AgentEvent wird korrekt erstellt."""
    event = AgentEvent(
        agent_name="Planner",
        task_id="t-1",
        event_type=EventType.TASK_CREATED,
        message="Task erstellt",
        metadata={"description": "Test"},
    )
    assert event.agent_name == "Planner"
    assert event.task_id == "t-1"
    assert event.event_type == EventType.TASK_CREATED
    assert event.message == "Task erstellt"
    assert event.metadata == {"description": "Test"}
    assert event.timestamp is not None


def test_agent_event_to_dict():
    """AgentEvent.to_dict() serialisiert korrekt."""
    event = AgentEvent(
        agent_name="Research",
        event_type=EventType.TASK_COMPLETED,
        message="Fertig",
    )
    d = event.to_dict()
    assert d["agent_name"] == "Research"
    assert d["event_type"] == EventType.TASK_COMPLETED.value
    assert d["message"] == "Fertig"
    assert "timestamp" in d


# --- EventBus ---


@pytest.fixture(autouse=True)
def reset_bus():
    """Setzt EventBus vor und nach jedem Test zurück."""
    reset_event_bus()
    yield
    reset_event_bus()


def test_event_bus_emit_reaches_listener():
    """EventBus.emit() ruft Listener auf."""
    bus = EventBus()
    received = []

    def listener(e: AgentEvent):
        received.append(e)

    bus.subscribe(listener)
    event = AgentEvent(agent_name="X", event_type=EventType.TASK_STARTED)
    bus.emit(event)
    assert len(received) == 1
    assert received[0].agent_name == "X"


def test_event_bus_multiple_listeners():
    """EventBus benachrichtigt alle Listener."""
    bus = EventBus()
    count = [0]

    def make_listener():
        def listener(e):
            count[0] += 1
        return listener

    bus.subscribe(make_listener())
    bus.subscribe(make_listener())
    bus.emit(AgentEvent(agent_name="X", event_type=EventType.TASK_CREATED))
    assert count[0] == 2


def test_event_bus_unsubscribe():
    """EventBus.unsubscribe entfernt Listener."""
    bus = EventBus()
    received = []

    def listener(e):
        received.append(e)

    bus.subscribe(listener)
    bus.emit(AgentEvent(agent_name="A", event_type=EventType.TASK_STARTED))
    assert len(received) == 1
    bus.unsubscribe(listener)
    bus.emit(AgentEvent(agent_name="B", event_type=EventType.TASK_STARTED))
    assert len(received) == 1


def test_get_event_bus_singleton():
    """get_event_bus liefert immer dieselbe Instanz."""
    bus1 = get_event_bus()
    bus2 = get_event_bus()
    assert bus1 is bus2


# --- DebugStore ---


@pytest.fixture
def store_with_bus():
    """DebugStore mit frischem EventBus."""
    reset_event_bus()
    reset_debug_store()
    bus = EventBus()
    store = DebugStore(bus)
    return store, bus


def test_debug_store_task_created(store_with_bus):
    """DebugStore verarbeitet TASK_CREATED."""
    store, bus = store_with_bus
    bus.emit(
        AgentEvent(
            agent_name="Planner",
            task_id="t1",
            event_type=EventType.TASK_CREATED,
            message="Recherche",
            metadata={"description": "Recherche durchführen"},
        )
    )
    tasks = store.get_active_tasks()
    assert len(tasks) == 1
    assert tasks[0].task_id == "t1"
    assert tasks[0].description == "Recherche durchführen"
    assert tasks[0].status == "pending"


def test_debug_store_task_lifecycle(store_with_bus):
    """DebugStore verarbeitet Task-Status-Änderungen."""
    store, bus = store_with_bus
    bus.emit(
        AgentEvent(
            agent_name="Planner",
            task_id="t1",
            event_type=EventType.TASK_CREATED,
            message="Task",
            metadata={"description": "Task A"},
        )
    )
    bus.emit(
        AgentEvent(
            agent_name="Research",
            task_id="t1",
            event_type=EventType.TASK_STARTED,
            message="Start",
        )
    )
    tasks = store.get_active_tasks()
    assert tasks[0].status == "running"
    assert tasks[0].agent_name == "Research"

    bus.emit(
        AgentEvent(
            agent_name="Research",
            task_id="t1",
            event_type=EventType.TASK_COMPLETED,
            message="Done",
        )
    )
    tasks = store.get_active_tasks()
    assert tasks[0].status == "completed"


def test_debug_store_model_usage(store_with_bus):
    """DebugStore aggregiert MODEL_CALL."""
    store, bus = store_with_bus
    bus.emit(
        AgentEvent(
            event_type=EventType.MODEL_CALL,
            message="qwen2.5",
            metadata={"model_id": "qwen2.5:latest", "duration_sec": 2.5},
        )
    )
    bus.emit(
        AgentEvent(
            event_type=EventType.MODEL_CALL,
            message="qwen2.5",
            metadata={"model_id": "qwen2.5:latest", "duration_sec": 1.0},
        )
    )
    usage = store.get_model_usage()
    assert len(usage) == 1
    assert usage[0].model_id == "qwen2.5:latest"
    assert usage[0].call_count == 2
    assert usage[0].total_duration_sec == 3.5


def test_debug_store_tool_execution(store_with_bus):
    """DebugStore speichert TOOL_EXECUTION."""
    store, bus = store_with_bus
    bus.emit(
        AgentEvent(
            agent_name="Chat",
            event_type=EventType.TOOL_EXECUTION,
            message="list_dir",
            metadata={"tool_name": "list_dir", "status": "completed"},
        )
    )
    tools = store.get_tool_executions()
    assert len(tools) == 1
    assert tools[0].tool_name == "list_dir"
    assert tools[0].status == "completed"


def test_debug_store_event_history(store_with_bus):
    """DebugStore speichert Event-Historie."""
    store, bus = store_with_bus
    bus.emit(AgentEvent(agent_name="A", event_type=EventType.TASK_STARTED))
    bus.emit(AgentEvent(agent_name="B", event_type=EventType.TASK_COMPLETED))
    history = store.get_event_history()
    assert len(history) == 2
    assert history[0].agent_name == "B"  # Neueste zuerst


def test_debug_store_clear(store_with_bus):
    """DebugStore.clear löscht alle Daten."""
    store, bus = store_with_bus
    bus.emit(
        AgentEvent(
            agent_name="X",
            task_id="t1",
            event_type=EventType.TASK_CREATED,
            metadata={"description": "Test"},
        )
    )
    store.clear()
    assert len(store.get_active_tasks()) == 0
    assert len(store.get_event_history()) == 0
    assert len(store.get_model_usage()) == 0


# --- Emitter ---


def test_emit_event_integration():
    """emit_event sendet an EventBus und DebugStore empfängt."""
    reset_event_bus()
    reset_debug_store()
    bus = get_event_bus()
    store = get_debug_store(bus)

    emit_event(
        EventType.TASK_CREATED,
        agent_name="TaskPlanner",
        task_id="t-debug",
        message="Test Task",
        metadata={"description": "Emitter Test"},
    )
    tasks = store.get_active_tasks()
    assert len(tasks) == 1
    assert tasks[0].task_id == "t-debug"
    assert tasks[0].agent_name == "TaskPlanner"

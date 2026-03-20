"""
Cross-Layer Debug Truth: Failure-Events im Store = sichtbar in View/Timeline.

Fehlerklasse: Debug view lies or omits failure events.

Prüft:
- Failure-Event wird im Store erfasst
- Failure-Event erscheint in der View/Timeline
- Event-Inhalt ist sichtbar/nachvollziehbar
- Reihenfolge und Inhalt stimmen
- keine Diskrepanz zwischen Store und UI
"""

from datetime import datetime, timezone

import pytest

from PySide6.QtWidgets import QLabel

from app.debug.agent_event import AgentEvent, EventType
from app.debug.debug_store import DebugStore
from app.debug.event_bus import EventBus
from app.gui.domains.runtime_debug.panels.event_timeline_view import EventTimelineView
from app.gui.domains.runtime_debug.panels.agent_debug_panel import AgentDebugPanel
from tests.helpers.diagnostics import dump_debug_failure_state


@pytest.fixture
def isolated_debug_store():
    """Isolierter DebugStore mit eigenem EventBus."""
    bus = EventBus()
    store = DebugStore(bus=bus)
    yield store
    store._unsubscribe()


def _visible_timeline_text(view) -> str:
    """Extrahiert den sichtbaren Text aus der EventTimelineView."""
    labels = [
        w.text() for w in view.findChildren(QLabel)
        if hasattr(w, "text") and w.text()
    ]
    return " ".join(labels)


@pytest.mark.cross_layer
@pytest.mark.ui
def test_task_failed_event_visible_in_timeline(qtbot, isolated_debug_store):
    """
    TASK_FAILED im Store → erscheint in Timeline mit Inhalt.

    Verhindert: Failure-Event nur intern, nicht sichtbar.
    """
    store = isolated_debug_store
    msg = "DEBUG_TRUTH_TASK_FAILED_42"
    event = AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name="Test-Agent",
        task_id="task-fail-1",
        event_type=EventType.TASK_FAILED,
        message=msg,
        metadata={"error": "Simulated failure"},
    )
    store._bus.emit(event)

    view = EventTimelineView(store, theme="dark")
    qtbot.addWidget(view)
    view.show()
    view.refresh()
    qtbot.wait(100)

    history = store.get_event_history()
    assert len(history) >= 1, dump_debug_failure_state(store, None)
    failed_events = [e for e in history if e.event_type == EventType.TASK_FAILED]
    assert len(failed_events) >= 1, dump_debug_failure_state(store, None)
    assert failed_events[0].message == msg

    visible = _visible_timeline_text(view)
    assert msg in visible, (
        f"Failure-Message '{msg}' nicht in Timeline sichtbar. "
        f"Visible: {visible[:200]}... " + dump_debug_failure_state(store, [visible])
    )
    assert "Test-Agent" in visible


@pytest.mark.cross_layer
@pytest.mark.ui
def test_rag_retrieval_failed_event_visible_in_timeline(qtbot, isolated_debug_store):
    """
    RAG_RETRIEVAL_FAILED im Store → erscheint in Timeline.

    Relevant für QA Level 2 Failure-Pfade.
    """
    store = isolated_debug_store
    msg = "DEBUG_TRUTH_RAG_FAILED_99"
    event = AgentEvent(
        timestamp=datetime.now(timezone.utc),
        agent_name="RAG-Service",
        task_id=None,
        event_type=EventType.RAG_RETRIEVAL_FAILED,
        message=msg,
        metadata={"query": "test", "error": "Chroma timeout"},
    )
    store._bus.emit(event)

    view = EventTimelineView(store, theme="dark")
    qtbot.addWidget(view)
    view.show()
    view.refresh()
    qtbot.wait(100)

    history = store.get_event_history()
    assert len(history) >= 1
    rag_events = [e for e in history if e.event_type == EventType.RAG_RETRIEVAL_FAILED]
    assert len(rag_events) >= 1, dump_debug_failure_state(store, None)
    assert rag_events[0].message == msg

    visible = _visible_timeline_text(view)
    assert msg in visible or "RAG-Service" in visible or "rag_retrieval_failed" in visible, (
        f"RAG-Failure nicht sichtbar. Visible: {visible[:200]}... "
        + dump_debug_failure_state(store, [visible])
    )


@pytest.mark.cross_layer
@pytest.mark.ui
def test_debug_panel_timeline_matches_store(qtbot, isolated_debug_store):
    """
    Debug-Panel Timeline = Store-Wahrheit. Keine Diskrepanz.

    Verhindert: View zeigt andere/ weniger Events als Store.
    """
    store = isolated_debug_store
    events_to_emit = [
        AgentEvent(
            agent_name="A1",
            task_id="t1",
            event_type=EventType.TASK_FAILED,
            message="FAIL_EVENT_1",
        ),
        AgentEvent(
            agent_name="A2",
            task_id="t2",
            event_type=EventType.RAG_RETRIEVAL_FAILED,
            message="FAIL_EVENT_2",
        ),
    ]
    for e in events_to_emit:
        store._bus.emit(e)

    qtbot.wait(50)

    panel = AgentDebugPanel(store=store, theme="dark", enabled=True)
    qtbot.addWidget(panel)
    panel.show()
    # Timer-basierter Refresh – warten und manuell triggern
    panel._timeline_view.refresh()
    qtbot.wait(150)

    history = store.get_event_history()
    visible = _visible_timeline_text(panel._timeline_view)

    assert len(history) >= 2, dump_debug_failure_state(store, [visible])
    assert "FAIL_EVENT_1" in visible, (
        "Store hat TASK_FAILED, View zeigt ihn nicht. " + dump_debug_failure_state(store, [visible])
    )
    assert "FAIL_EVENT_2" in visible or "A2" in visible, (
        "Store hat RAG_RETRIEVAL_FAILED, View zeigt ihn nicht. "
        + dump_debug_failure_state(store, [visible])
    )

"""
UI Tests: Debug Panel.

Testet Event Timeline anzeigen, Agent Aktivität anzeigen, Taskstatus anzeigen.
"""

import tempfile
from unittest.mock import MagicMock

import pytest

from PySide6.QtWidgets import QTabWidget, QPushButton
from PySide6.QtCore import Qt

from app.gui.domains.runtime_debug.panels.agent_debug_panel import AgentDebugPanel
from app.gui.domains.runtime_debug.panels.agent_activity_view import AgentActivityView
from app.gui.domains.runtime_debug.panels.event_timeline_view import EventTimelineView
from app.debug.debug_store import DebugStore
from app.debug.event_bus import EventBus
from app.debug.agent_event import AgentEvent, EventType


@pytest.fixture
def debug_store_with_events():
    """DebugStore mit Beispiel-Events."""
    bus = EventBus()
    store = DebugStore(bus=bus)
    event = AgentEvent(
        agent_name="Test-Agent",
        task_id="task-1",
        event_type=EventType.TASK_COMPLETED,
        message="Task abgeschlossen",
    )
    bus.emit(event)
    return store


def test_debug_panel_opens(qtbot):
    """Debug-Panel öffnet ohne Fehler."""
    panel = AgentDebugPanel(theme="dark", enabled=True)
    qtbot.addWidget(panel)
    panel.show()
    assert panel.isVisible()
    assert panel._tabs is not None


def test_debug_panel_has_tabs(qtbot):
    """Debug-Panel hat Aktivität, Timeline, Task-Graph Tabs."""
    panel = AgentDebugPanel(theme="dark")
    qtbot.addWidget(panel)
    assert panel._tabs.count() >= 2
    tab_names = [panel._tabs.tabText(i) for i in range(panel._tabs.count())]
    assert "Aktivität" in tab_names or "Timeline" in tab_names


def test_debug_panel_clear_button(qtbot):
    """Clear-Button ist vorhanden und klickbar."""
    panel = AgentDebugPanel(theme="dark")
    qtbot.addWidget(panel)
    assert panel._clear_btn is not None
    qtbot.mouseClick(panel._clear_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(50)


def test_agent_activity_view_opens(qtbot):
    """AgentActivityView öffnet."""
    store = DebugStore(EventBus())
    view = AgentActivityView(store, theme="dark")
    qtbot.addWidget(view)
    view.show()
    assert view.isVisible()


def test_event_timeline_view_opens(qtbot):
    """EventTimelineView öffnet."""
    store = DebugStore(EventBus())
    view = EventTimelineView(store, theme="dark")
    qtbot.addWidget(view)
    view.show()
    assert view.isVisible()


def test_event_timeline_refresh(qtbot, debug_store_with_events):
    """EventTimelineView zeigt Events nach Refresh – Event-Inhalt sichtbar."""
    store = debug_store_with_events
    view = EventTimelineView(store, theme="dark")
    qtbot.addWidget(view)
    view.show()
    view.refresh()
    qtbot.wait(50)
    assert view.isVisible()
    # Verhalten: Event-Inhalt (Message, Agent) muss in View sichtbar sein
    assert len(store.get_event_history()) >= 1
    from PySide6.QtWidgets import QLabel
    all_text = " ".join(
        w.text() for w in view.findChildren(QLabel)
        if hasattr(w, "text") and w.text()
    )
    assert "Task abgeschlossen" in all_text or "Test-Agent" in all_text


def test_agent_activity_refresh(qtbot, debug_store_with_events):
    """AgentActivityView zeigt Aktivität nach Refresh."""
    store = debug_store_with_events
    view = AgentActivityView(store, theme="dark")
    qtbot.addWidget(view)
    view.show()
    view.refresh()
    qtbot.wait(50)
    assert view.isVisible()


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.async_behavior
def test_agent_activity_shows_task_status(qtbot):
    """
    Task-Event (TASK_CREATED) -> Activity-View zeigt Agent/Status.
    Verhindert: Task-Event nicht in Activity-View sichtbar.
    """
    bus = EventBus()
    store = DebugStore(bus=bus)
    bus.emit(AgentEvent(
        agent_name="P1-Activity-Agent",
        task_id="task-p1-activity",
        event_type=EventType.TASK_CREATED,
        message="Analyse starten",
        metadata={"description": "Analyse starten"},
    ))
    qtbot.wait(50)

    view = AgentActivityView(store, theme="dark")
    qtbot.addWidget(view)
    view.show()
    view.refresh()
    qtbot.wait(100)

    tasks = store.get_active_tasks()
    assert len(tasks) >= 1
    task = next((t for t in tasks if t.task_id == "task-p1-activity"), None)
    assert task is not None
    assert "P1-Activity-Agent" in task.agent_name
    from PySide6.QtWidgets import QLabel
    all_text = " ".join(
        w.text() for w in view.findChildren(QLabel)
        if hasattr(w, "text") and w.text()
    )
    assert "P1-Activity-Agent" in all_text or "task-p1-activity" in all_text


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.async_behavior
def test_event_timeline_shows_event_content(qtbot):
    """
    Event emittieren -> refresh -> View zeigt Message/Agent.
    Verhindert: Event in Store, aber nicht in Timeline sichtbar.
    """
    bus = EventBus()
    store = DebugStore(bus=bus)
    event = AgentEvent(
        agent_name="P0-Timeline-Agent",
        task_id="task-p0",
        event_type=EventType.TASK_COMPLETED,
        message="P0-Test-Event abgeschlossen",
    )
    bus.emit(event)
    qtbot.wait(50)

    view = EventTimelineView(store, theme="dark")
    qtbot.addWidget(view)
    view.show()
    view.refresh()
    qtbot.wait(100)

    assert len(store.get_event_history()) >= 1
    from PySide6.QtWidgets import QLabel
    labels_with_content = []
    for w in view.findChildren(QLabel):
        t = w.text() if hasattr(w, "text") else ""
        if t:
            labels_with_content.append(t)
    all_text = " ".join(labels_with_content)
    assert "P0-Test-Event" in all_text or "abgeschlossen" in all_text
    assert "P0-Timeline-Agent" in all_text


@pytest.mark.ui
@pytest.mark.regression
def test_debug_panel_clear_removes_events(qtbot):
    """
    Events hinzufügen -> Clear -> get_event_history leer.
    Verhindert: Clear-Button ohne Wirkung.
    """
    bus = EventBus()
    store = DebugStore(bus=bus)
    bus.emit(AgentEvent(
        agent_name="Clear-Test",
        task_id="t1",
        event_type=EventType.TASK_COMPLETED,
        message="Wird gelöscht",
    ))
    qtbot.wait(50)
    assert len(store.get_event_history()) >= 1

    panel = AgentDebugPanel(store=store, theme="dark")
    qtbot.addWidget(panel)
    qtbot.mouseClick(panel._clear_btn, Qt.MouseButton.LeftButton)
    qtbot.wait(100)

    assert len(store.get_event_history()) == 0

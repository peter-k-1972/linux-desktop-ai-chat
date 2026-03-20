"""
Async Test: Debug Clear während Refresh.

Verhindert: Crash oder inkonsistenter State wenn Clear während
der periodischen Refresh der Timeline/Views ausgeführt wird.
"""

import pytest
from PySide6.QtCore import Qt

from app.debug.agent_event import AgentEvent, EventType
from app.debug.debug_store import DebugStore
from app.debug.event_bus import EventBus


@pytest.fixture
def debug_store():
    """Isolierter DebugStore mit eigenem EventBus."""
    bus = EventBus()
    store = DebugStore(bus=bus)
    yield store
    store._unsubscribe()


@pytest.mark.async_behavior
@pytest.mark.integration
def test_debug_clear_during_refresh_no_crash(debug_store, qtbot):
    """
    Clear und Refresh in schneller Folge führen nicht zu Crash.
    Simuliert: User klickt Clear während Timer-Refresh läuft.
    """
    from app.gui.domains.runtime_debug.panels.event_timeline_view import EventTimelineView

    # Events emittieren
    bus = debug_store._bus
    for i in range(5):
        bus.emit(
            AgentEvent(
                agent_name=f"Agent{i}",
                event_type=EventType.TASK_COMPLETED,
                message=f"Task {i} done",
            )
        )

    view = EventTimelineView(debug_store, theme="dark")
    view.show()
    qtbot.addWidget(view)

    # Refresh → Clear → Refresh in schneller Folge (simuliert Race)
    view.refresh()
    debug_store.clear()
    view.refresh()
    debug_store.clear()
    view.refresh()

    # Kein Crash, View zeigt leer
    assert len(debug_store.get_event_history()) == 0


@pytest.mark.async_behavior
@pytest.mark.integration
def test_debug_panel_clear_button_during_refresh(debug_store, qtbot):
    """
    Clear-Button des Debug-Panels während Refresh-Timer.
    """
    from app.gui.domains.runtime_debug.panels.agent_debug_panel import AgentDebugPanel

    bus = debug_store._bus
    bus.emit(
        AgentEvent(
            agent_name="Test",
            event_type=EventType.MODEL_CALL,
            message="model",
            metadata={"model_id": "llama"},
        )
    )

    panel = AgentDebugPanel(store=debug_store, theme="dark", enabled=True)
    panel.show()
    qtbot.addWidget(panel)

    # Mehrfach Clear klicken (kann mit Timer kollidieren)
    qtbot.mouseClick(panel._clear_btn, Qt.MouseButton.LeftButton)
    qtbot.mouseClick(panel._clear_btn, Qt.MouseButton.LeftButton)

    assert len(debug_store.get_event_history()) == 0

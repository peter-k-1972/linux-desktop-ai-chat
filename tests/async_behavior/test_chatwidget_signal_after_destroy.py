"""
Async Test: Spätes Signal auf echtes ChatWidget.update_chat_signal.

Verhindert: late signal / use-after-destroy / async UI race.
Szenario: Echtes ChatWidget, Signal verbunden, Widget zerstört, spätes Emit.
"""

import asyncio
from unittest.mock import MagicMock

import pytest

from PySide6.QtCore import QObject, Signal
from PySide6.QtWidgets import QWidget

from app.gui.legacy import ChatWidget
from app.core.config.settings import AppSettings


class LateSignalEmitter(QObject):
    """Externer Emitter – überlebt das ChatWidget."""
    update_signal = Signal(str, bool)


class ChatWidgetLoadModelsOnly(ChatWidget):
    """ChatWidget mit echtem on_update_chat, nur load_models überschrieben."""

    def load_models(self):
        pass


@pytest.fixture
def chat_widget_settings():
    s = AppSettings()
    s.model = "test:latest"
    s.theme = "dark"
    s.icons_path = ""
    s.save = lambda: None
    s.think_mode = "auto"
    s.rag_enabled = False
    s.auto_routing = True
    s.cloud_escalation = False
    s.overkill_mode = False
    s.web_search = False
    return s


@pytest.fixture
def fake_db():
    class FakeDB:
        def __init__(self):
            self._messages = {}
            self._next_id = 1

        def create_chat(self, title=""):
            cid = self._next_id
            self._next_id += 1
            self._messages[cid] = []
            return cid

        def save_message(self, cid, role, content):
            self._messages.setdefault(cid, []).append((role, content, "ts"))

        def load_chat(self, cid):
            return list(self._messages.get(cid, []))

        def list_workspace_roots_for_chat(self, cid):
            return []

    return FakeDB()


@pytest.mark.async_behavior
@pytest.mark.ui
def test_chatwidget_late_signal_no_crash(qtbot, chat_widget_settings, fake_db):
    """
    Spätes Signal auf ChatWidget-Slot nach Zerstörung führt zu keinem Crash.
    Externer Emitter verbunden mit _on_update_chat_slot, Widget zerstört, dann Emit.
    """
    from unittest.mock import AsyncMock

    client = MagicMock()
    client.get_models = AsyncMock(return_value=[])

    widget = ChatWidgetLoadModelsOnly(client, chat_widget_settings, fake_db)
    qtbot.addWidget(widget)
    widget.chat_id = fake_db.create_chat()

    emitter = LateSignalEmitter()
    emitter.update_signal.connect(widget._on_update_chat_slot)

    widget.deleteLater()
    qtbot.wait(150)

    emitter.update_signal.emit("Late stream update", True)

    qtbot.wait(50)


@pytest.mark.async_behavior
@pytest.mark.asyncio
@pytest.mark.ui
async def test_chatwidget_signal_during_destroy_no_crash(qtbot, chat_widget_settings, fake_db):
    """
    run_chat läuft, Widget wird zerstört – kein Crash.
    Simuliert: User schließt Fenster während Stream noch läuft.
    """
    from PySide6.QtWidgets import QWidget
    from tests.async_behavior.conftest import SlowStreamFakeClient

    container = QWidget()
    qtbot.addWidget(container)

    client = SlowStreamFakeClient()
    widget = ChatWidgetLoadModelsOnly(client, chat_widget_settings, fake_db, parent=container)
    widget.show()
    widget.chat_id = fake_db.create_chat()

    task = asyncio.create_task(widget.run_chat("Test"))
    for _ in range(30):
        if getattr(widget, "_streaming", False):
            break
        await asyncio.sleep(0.01)

    widget.deleteLater()
    qtbot.wait(100)

    try:
        await asyncio.wait_for(task, timeout=2.0)
    except (asyncio.CancelledError, asyncio.TimeoutError):
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    qtbot.wait(50)

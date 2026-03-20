"""
Integration: Chat Streaming-Verhalten.

Prüft: Senden während Streaming blockiert/serialisiert.
"""

import asyncio
from typing import Dict, List
from unittest.mock import MagicMock, AsyncMock

import pytest

from app.gui.legacy import ChatWidget
from app.core.config.settings import AppSettings


class SlowFakeClient:
    """Fake-Client mit langsamem Stream – für Race-Condition-Tests."""

    def __init__(self):
        self.call_count = 0
        self.last_messages = None

    async def get_models(self):
        return []

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs):
        self.call_count += 1
        self.last_messages = list(messages)

        async def _gen():
            yield {"message": {"content": "Teil1", "thinking": ""}, "done": False}
            await asyncio.sleep(0.2)
            yield {"message": {"content": "Teil2", "thinking": ""}, "done": True}

        return _gen()


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


class MinimalChatWidget(ChatWidget):
    def load_models(self):
        pass

    def on_update_chat(self, text, is_final):
        pass


@pytest.fixture
def settings():
    s = AppSettings()
    s.model = "test:latest"
    return s


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.async_behavior
@pytest.mark.regression
async def test_send_while_streaming_is_blocked_or_serialized(settings):
    """
    Senden während Stream blockiert oder serialisiert.
    Verhindert: Doppelte Sends, Race Conditions, korrupte Antworten.
    """
    client = SlowFakeClient()
    db = FakeDB()
    chat_id = db.create_chat()
    widget = MinimalChatWidget(client, settings, db)
    widget.chat_id = chat_id

    async def first_send():
        await widget.run_chat("Erste Nachricht")

    task = asyncio.create_task(first_send())
    # Warten bis Streaming gestartet (statt fixem Sleep – deterministischer)
    for _ in range(50):
        if widget._streaming:
            break
        await asyncio.sleep(0.01)
    assert widget._streaming is True, "Streaming muss vor zweitem Send gestartet sein"

    await widget.run_chat("Zweite Nachricht während Stream")

    await task

    assert client.call_count == 1, "Während Streaming darf kein zweiter API-Call erfolgen"
    assert "Erste Nachricht" in (client.last_messages[-1].get("content", "") if client.last_messages else "")

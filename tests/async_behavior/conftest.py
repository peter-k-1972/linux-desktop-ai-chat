"""
Fixtures für Async Behavior Tests.

Nutzt qt_event_loop und MinimalChatWidget-Pattern.
"""

import asyncio
from typing import Dict, List
from unittest.mock import MagicMock

import pytest

from app.gui.legacy import ChatWidget
from app.core.config.settings import AppSettings


class SlowStreamFakeClient:
    """Fake-Client mit langsamem Stream für Race-Condition-Tests."""

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
            await asyncio.sleep(0.15)
            yield {"message": {"content": "Teil2", "thinking": ""}, "done": True}

        return _gen()


class FakeDB:
    """Minimale DB für Chat-Tests."""

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
    """ChatWidget ohne Modell-Load für schnelle Tests."""

    def load_models(self):
        pass

    def on_update_chat(self, text, is_final):
        pass


@pytest.fixture
def async_settings():
    """AppSettings für Async-Tests."""
    s = AppSettings()
    s.model = "test:latest"
    return s


@pytest.fixture
def async_client():
    """Slow-Stream-Client für Race-Tests."""
    return SlowStreamFakeClient()


@pytest.fixture
def async_db():
    """Fake-DB für Async-Tests."""
    return FakeDB()

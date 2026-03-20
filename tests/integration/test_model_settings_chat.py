"""
Integration: Modell-Einstellung wirkt auf Chat.

P1: Modell wechseln -> anderes Modell in API.
"""

from typing import Dict, List
from unittest.mock import MagicMock, AsyncMock

import pytest

from app.gui.legacy import ChatWidget
from app.core.config.settings import AppSettings


class RecordingFakeClient:
    """Fake-Client, der verwendetes Modell protokolliert."""

    def __init__(self):
        self.models_used = []
        self.call_count = 0

    async def get_models(self):
        return [{"name": "model-a", "model": "model-a"}, {"name": "model-b", "model": "model-b"}]

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs):
        self.models_used.append(model)
        self.call_count += 1
        async def _gen():
            yield {"message": {"content": "Antwort", "thinking": ""}, "done": True}
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
    s.model = "model-a"
    return s


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.regression
async def test_model_settings_change_affects_chat(qtbot, settings):
    """
    Modell wechseln -> anderes Modell in API.
    Verhindert: Modell-Wechsel hat keine Wirkung.
    """
    client = RecordingFakeClient()
    db = FakeDB()
    chat_id = db.create_chat()
    widget = MinimalChatWidget(client, settings, db)
    qtbot.addWidget(widget)
    widget.chat_id = chat_id

    await widget.run_chat("Erste Nachricht")
    assert client.call_count == 1
    assert client.models_used[-1] == "model-a"

    settings.model = "model-b"
    widget.set_current_model("model-b")
    await widget.run_chat("Zweite Nachricht")

    assert client.call_count == 2
    assert client.models_used[-1] == "model-b"

"""
Golden-Path 1: Chat starten -> Nachricht senden -> Antwort erscheint korrekt.

Prüft den vollständigen Flow: User-Input -> DB -> LLM (Fake) -> UI-Update -> Persistenz.
"""

import asyncio
from typing import Any, Dict, List

import pytest

from app.gui.legacy import ChatWidget
from app.core.config.settings import AppSettings


class FakeOllamaClient:
    """Minimaler Fake – liefert vorbereitete Antwort."""

    def __init__(self, response: str = "Golden-Path-Antwort"):
        self._response = response
        self.last_messages = None

    async def get_models(self):
        return []

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs):
        self.last_messages = list(messages)

        async def _gen():
            yield {"message": {"content": self._response, "thinking": ""}, "done": True}

        return _gen()


class FakeDB:
    """In-Memory-DB für Chat-Historie."""

    def __init__(self):
        self._messages = {}
        self._next_chat_id = 1

    def create_chat(self, title: str = "Test") -> int:
        cid = self._next_chat_id
        self._next_chat_id += 1
        self._messages[cid] = []
        return cid

    def save_message(self, chat_id, role, content):
        self._messages.setdefault(chat_id, []).append((role, content, "ts"))

    def load_chat(self, chat_id):
        return list(self._messages.get(chat_id, []))

    def list_workspace_roots_for_chat(self, chat_id):
        return []


class CapturingChatWidget(ChatWidget):
    """Sammelt UI-Updates statt zu rendern."""

    def __init__(self, client, settings, db):
        super().__init__(client, settings, db)
        self.updates = []

    def load_models(self):
        pass

    def on_update_chat(self, text, is_final):
        self.updates.append((text, is_final))


@pytest.fixture
def settings():
    s = AppSettings()
    s.model = "test:latest"
    s.temperature = 0.3
    s.max_tokens = 128
    return s


@pytest.mark.golden_path
@pytest.mark.asyncio
async def test_chat_send_message_receive_response_displayed_and_persisted(settings):
    """
    Golden Path: Nachricht senden -> Antwort erscheint korrekt in UI und DB.

    Prüft:
    - User-Nachricht in DB
    - Antwort-Text in current_full_response
    - Antwort in DB gespeichert
    - UI-Updates enthalten finale Antwort
    """
    client = FakeOllamaClient("Antwort-123")
    db = FakeDB()
    chat_id = db.create_chat("Golden-Path-Chat")

    widget = CapturingChatWidget(client, settings, db)
    widget.chat_id = chat_id

    await widget.run_chat("Hallo, antworte mit Antwort-123")

    # Antwort korrekt verarbeitet
    assert widget.current_full_response == "Antwort-123"

    # In DB persistiert
    history = db.load_chat(chat_id)
    user_msgs = [m for m in history if m[0] == "user"]
    asst_msgs = [m for m in history if m[0] == "assistant"]
    assert user_msgs[-1][1] == "Hallo, antworte mit Antwort-123"
    assert asst_msgs[-1][1] == "Antwort-123"

    # UI hat finale Antwort erhalten
    assert widget.updates
    last_text, is_final = widget.updates[-1]
    assert is_final is True
    assert "Antwort-123" in last_text

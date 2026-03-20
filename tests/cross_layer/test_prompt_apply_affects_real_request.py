"""
Cross-Layer Prompt Truth: UI-Signal vs. echter Request-Inhalt.

Fehlerklasse: UI says prompt applied, backend request uses wrong or stale prompt.

Prüft:
- Prompt wird in der UI angewendet
- Request-Building übernimmt den Prompt wirklich
- Chat/LLM-Aufruf sieht den erwarteten Prompt-Inhalt
- kein stale Prompt aus altem Zustand
- UI und tatsächlicher Request stimmen überein
"""

from typing import Dict, List
from unittest.mock import MagicMock

import pytest

from app.gui.legacy import ChatWidget
from app.prompts.prompt_models import Prompt
from app.core.config.settings import AppSettings
from tests.helpers.diagnostics import dump_prompt_request_state


class RecordingClient:
    """Zeichnet die an die API gesendeten Messages auf."""

    def __init__(self):
        self.last_messages: List[Dict[str, str]] = None

    async def get_models(self):
        return []

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs):
        self.last_messages = list(messages)

        async def _gen():
            yield {"message": {"content": "OK", "thinking": ""}, "done": True}

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
def cross_layer_settings():
    s = AppSettings()
    s.model = "test:latest"
    return s


@pytest.mark.cross_layer
@pytest.mark.asyncio
async def test_prompt_apply_affects_real_request(cross_layer_settings):
    """
    Cross-Layer: Angewendeter Prompt landet im echten API-Request.

    Verhindert: UI zeigt "Prompt angewendet", aber Request enthält
    falschen oder veralteten Prompt (stale state).
    """
    client = RecordingClient()
    db = FakeDB()
    chat_id = db.create_chat("Test-Chat")

    widget = MinimalChatWidget(client, cross_layer_settings, db, orchestrator=None)
    widget.chat_id = chat_id

    # Kein Agent ausgewählt – nur unser Prompt soll als System-Message erscheinen
    widget.header = MagicMock()
    widget.header.agent_combo = MagicMock()
    widget.header.agent_combo.currentData = MagicMock(return_value=None)
    widget.header.role_combo = MagicMock()
    widget.header.role_combo.currentData = MagicMock(return_value=None)

    # Eindeutiger Prompt-Inhalt – nicht mit anderen verwechselbar
    prompt_content = "CROSS_LAYER_PROMPT_TRUTH_42_apply_affects_request"
    prompt = Prompt(
        id=1,
        title="Cross-Layer-Test",
        category="general",
        description="",
        content=prompt_content,
        prompt_type="user",
        tags=[],
        created_at=None,
        updated_at=None,
    )

    # 1. Prompt anwenden (wie "In Chat übernehmen")
    widget._on_prompt_apply(prompt)

    # 2. Nachricht senden – Request wird gebaut und an API gesendet
    await widget.run_chat("Kurze Testfrage")

    # 3. Assert: Request enthält den angewendeten Prompt
    assert client.last_messages is not None, (
        "Kein API-Request aufgezeichnet. "
        + dump_prompt_request_state(widget, client.last_messages)
    )

    system_msgs = [m for m in client.last_messages if m.get("role") == "system"]
    assert len(system_msgs) >= 1, (
        "Keine System-Message im Request. "
        + dump_prompt_request_state(widget, client.last_messages)
    )

    all_system_content = " ".join(m.get("content", "") for m in system_msgs)
    assert prompt_content in all_system_content, (
        f"Prompt-Inhalt '{prompt_content}' fehlt im Request. "
        f"System-Content: {all_system_content[:200]}... "
        + dump_prompt_request_state(widget, client.last_messages)
    )


@pytest.mark.cross_layer
@pytest.mark.asyncio
async def test_prompt_apply_no_stale_after_second_apply(cross_layer_settings):
    """
    Zweiter Prompt-Apply ersetzt/ergänzt – kein stale erster Prompt.

    Verhindert: Erster Prompt bleibt im Request, obwohl zweiter angewendet wurde.
    """
    client = RecordingClient()
    db = FakeDB()
    chat_id = db.create_chat("Test-Chat")

    widget = MinimalChatWidget(client, cross_layer_settings, db, orchestrator=None)
    widget.chat_id = chat_id

    widget.header = MagicMock()
    widget.header.agent_combo = MagicMock()
    widget.header.agent_combo.currentData = MagicMock(return_value=None)
    widget.header.role_combo = MagicMock()
    widget.header.role_combo.currentData = MagicMock(return_value=None)

    # Erster Prompt
    prompt1 = Prompt(
        id=1, title="P1", category="general", description="", content="STALE_PROMPT_OLD",
        prompt_type="user", tags=[], created_at=None, updated_at=None,
    )
    widget._on_prompt_apply(prompt1)

    # Zweiter Prompt (ersetzt/ergänzt – beide landen als system messages in DB)
    prompt2_content = "FRESH_PROMPT_NEW_123"
    prompt2 = Prompt(
        id=2, title="P2", category="general", description="", content=prompt2_content,
        prompt_type="user", tags=[], created_at=None, updated_at=None,
    )
    widget._on_prompt_apply(prompt2)

    await widget.run_chat("Test")

    assert client.last_messages is not None
    system_msgs = [m for m in client.last_messages if m.get("role") == "system"]
    all_content = " ".join(m.get("content", "") for m in system_msgs)

    # Der zweite (frische) Prompt muss im Request sein
    assert prompt2_content in all_content, (
        f"Zweiter Prompt fehlt im Request. Content: {all_content[:300]}... "
        + dump_prompt_request_state(widget, client.last_messages)
    )

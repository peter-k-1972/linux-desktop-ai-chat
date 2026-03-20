"""
Golden-Path: RAG aktiviert -> Kontext in Antwort.

Prüft: settings.rag_enabled=True -> augment_if_enabled aufgerufen ->
Antwort enthält RAG-Kontext.
"""

from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.gui.legacy import ChatWidget


class FakeOllamaClient:
    """Fake – prüft ob RAG-Kontext in Messages, gibt dann Kontext in Antwort."""

    def __init__(self):
        self.last_messages = None

    async def get_models(self):
        return []

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs):
        self.last_messages = list(messages)
        user_content = ""
        for m in reversed(messages):
            if m.get("role") == "user":
                user_content = m.get("content", "")
                break
        if "GOLDEN_RAG_TOKEN" in user_content:
            response = "Antwort mit RAG-Kontext GOLDEN_RAG_TOKEN"
        else:
            response = "Antwort ohne RAG"
        async def _gen():
            yield {"message": {"content": response, "thinking": ""}, "done": True}
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


class CapturingChatWidget(ChatWidget):
    def load_models(self):
        pass

    def on_update_chat(self, text, is_final):
        pass

    def _apply_routing_settings(self):
        """RAG-Signale blockieren, damit Test-settings.rag_enabled erhalten bleibt."""
        self.header.rag_check.blockSignals(True)
        self.header.self_improving_check.blockSignals(True)
        super()._apply_routing_settings()
        self.header.rag_check.setChecked(bool(getattr(self.settings, "rag_enabled", False)))
        self.header.self_improving_check.setChecked(bool(getattr(self.settings, "self_improving_enabled", False)))
        self.header.rag_check.blockSignals(False)
        self.header.self_improving_check.blockSignals(False)


@pytest.fixture
def settings():
    from app.core.config.settings import AppSettings
    s = AppSettings()
    s.model = "test:latest"
    s.rag_enabled = True
    s.rag_space = "default"
    s.rag_top_k = 5
    return s


@pytest.mark.golden_path
@pytest.mark.asyncio
@pytest.mark.async_behavior
@pytest.mark.regression
async def test_rag_toggle_enabled_context_in_response(settings):
    """
    RAG an -> augment_if_enabled liefert Kontext -> Antwort enthält Kontext.
    Verhindert: RAG aktiviert, aber Kontext nicht in Antwort.
    """
    client = FakeOllamaClient()
    db = FakeDB()
    chat_id = db.create_chat()
    rag_service = MagicMock()
    rag_service.augment_if_enabled = AsyncMock(
        return_value=(
            "User-Frage\n\n[Kontext aus Dokumenten: GOLDEN_RAG_TOKEN]",
            True,
        )
    )

    widget = CapturingChatWidget(client, settings, db, rag_service=rag_service)
    widget.chat_id = chat_id

    await widget.run_chat("Was ist Python?")

    assert rag_service.augment_if_enabled.called
    call_kwargs = rag_service.augment_if_enabled.call_args
    assert call_kwargs[1].get("enabled") is True

    assert "GOLDEN_RAG_TOKEN" in widget.current_full_response

"""
Integration: RAG + Chat.

P0: RAG aktiviert -> augment_if_enabled aufgerufen.
P0: RAG scheitert -> Chat läuft weiter, transparente Degradation.
"""

from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.gui.legacy import ChatWidget
from app.core.config.settings import AppSettings


class FakeOllamaClient:
    def __init__(self, response: str = "Antwort"):
        self._response = response
        self.call_count = 0

    async def get_models(self):
        return []

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs):
        self.call_count += 1
        async def _gen():
            yield {"message": {"content": self._response, "thinking": ""}, "done": True}
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
    """ChatWidget für Tests – blockiert RAG-Signal während Init, damit rag_enabled erhalten bleibt."""

    def load_models(self):
        pass

    def on_update_chat(self, text, is_final):
        pass

    def _apply_routing_settings(self):
        """Überschreiben: RAG-Checkbox-Signale blockieren, damit Test-settings.rag_enabled nicht überschrieben wird."""
        self.header.rag_check.blockSignals(True)
        self.header.self_improving_check.blockSignals(True)
        super()._apply_routing_settings()
        self.header.rag_check.setChecked(bool(getattr(self.settings, "rag_enabled", False)))
        self.header.self_improving_check.setChecked(bool(getattr(self.settings, "self_improving_enabled", False)))
        self.header.rag_check.blockSignals(False)
        self.header.self_improving_check.blockSignals(False)


@pytest.fixture
def settings():
    s = AppSettings()
    s.model = "test:latest"
    s.rag_enabled = True
    s.rag_space = "default"
    s.rag_top_k = 5
    return s


class RecordingRAGService:
    """RAG-Service der Aufrufe protokolliert."""

    def __init__(self):
        self.augment_calls = []

    async def augment_if_enabled(self, query, enabled=True, space=None, top_k=5):
        self.augment_calls.append({"query": query, "enabled": enabled})
        return (query, False)


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.async_behavior
@pytest.mark.regression
async def test_rag_enabled_augments_query_in_chat(qtbot):
    """
    RAG an, run_chat -> augment_if_enabled aufgerufen.
    Verhindert: RAG aktiviert, aber augment nicht aufgerufen.
    """
    from types import SimpleNamespace
    settings = SimpleNamespace(
        model="test:latest",
        theme="dark",
        temperature=0.7,
        max_tokens=4096,
        rag_enabled=True,
        rag_space="default",
        rag_top_k=5,
        auto_routing=True,
        cloud_escalation=False,
        overkill_mode=False,
        web_search=False,
        think_mode="auto",
        icons_path="",
    )
    settings.save = lambda: None

    client = FakeOllamaClient("Antwort")
    db = FakeDB()
    chat_id = db.create_chat()
    rag_service = RecordingRAGService()

    widget = MinimalChatWidget(client, settings, db, rag_service=rag_service)
    qtbot.addWidget(widget)
    widget.chat_id = chat_id

    await widget.run_chat("Was ist Python?")

    assert len(rag_service.augment_calls) >= 1
    assert rag_service.augment_calls[0]["query"] == "Was ist Python?"
    assert rag_service.augment_calls[0]["enabled"] is True


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.async_behavior
@pytest.mark.regression
async def test_rag_failure_degrades_transparently(qtbot, settings):
    """
    RAG scheitert (return query, False) -> Chat läuft weiter mit Original-Query.
    Verhindert: RAG-Fehler bricht Chat ab; keine transparente Degradation.
    """
    settings.rag_enabled = True
    client = FakeOllamaClient("Antwort ohne RAG")
    db = FakeDB()
    chat_id = db.create_chat()
    rag_service = RecordingRAGService()

    widget = MinimalChatWidget(client, settings, db, rag_service=rag_service)
    qtbot.addWidget(widget)
    widget.chat_id = chat_id

    await widget.run_chat("Was ist Python?")

    assert client.call_count == 1
    assert "Antwort" in widget.current_full_response
    assert len(rag_service.augment_calls) >= 1

"""
Failure Injection: ChromaDB RAG Retrieval Exception.

Simuliert: ChromaDB/Retriever wirft Exception.
Erwartetes Verhalten: Chat läuft weiter, keine Exception propagiert,
Debug/EventStore enthält RAG-Failure-Event, Antwort ohne Kontext.
"""

from typing import Dict, List
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.debug.agent_event import AgentEvent, EventType
from app.debug.debug_store import DebugStore
from app.debug.event_bus import EventBus
from app.rag.service import RAGService


class FailingRetriever:
    """Retriever der bei retrieve() eine ChromaDB-ähnliche Exception wirft."""

    async def retrieve(self, query, top_k=None, where=None):
        raise ConnectionError("ChromaDB nicht erreichbar")


class FailingRAGPipeline:
    """Pipeline mit failing Retriever."""

    def __init__(self):
        self.retriever = FailingRetriever()
        from app.rag.context_builder import ContextBuilder
        self.context_builder = ContextBuilder()

    async def augment_prompt(self, user_prompt, top_k=None):
        context = await self.retriever.retrieve(user_prompt, top_k=top_k)
        ctx_str = self.context_builder.build(context) if context else ""
        if not ctx_str:
            return user_prompt, False
        return f"Kontext: {ctx_str}\n\nFrage: {user_prompt}", True


@pytest.fixture
def event_bus_and_store():
    """Isolierter EventBus + DebugStore für Event-Erfassung."""
    bus = EventBus()
    store = DebugStore(bus=bus)
    yield bus, store
    store._unsubscribe()


@pytest.mark.failure_mode
@pytest.mark.asyncio
@pytest.mark.integration
async def test_rag_service_handles_retrieval_exception(event_bus_and_store):
    """
    RAGService.augment_if_enabled: Bei Retriever-Exception wird (query, False) zurückgegeben.
    Keine Exception propagiert.
    """
    bus, store = event_bus_and_store

    # RAGService mit Pipeline die wirft
    service = RAGService()
    service.get_pipeline = lambda **kw: FailingRAGPipeline()

    query = "Was steht in den Dokumenten?"
    result_text, rag_used = await service.augment_if_enabled(
        query, enabled=True, space="default", top_k=5
    )

    assert result_text == query
    assert rag_used is False


@pytest.mark.failure_mode
@pytest.mark.asyncio
@pytest.mark.integration
async def test_rag_failure_emits_event(event_bus_and_store):
    """
    Bei RAG-Exception wird RAG_RETRIEVAL_FAILED Event emittiert.
    DebugStore enthält das Event.
    """
    bus, store = event_bus_and_store

    from unittest.mock import patch

    with patch("app.debug.emitter.get_event_bus", return_value=bus):
        service = RAGService()
        service.get_pipeline = lambda **kw: FailingRAGPipeline()

        await service.augment_if_enabled("Test", enabled=True, space="default", top_k=5)

    history = store.get_event_history()
    rag_events = [e for e in history if e.event_type == EventType.RAG_RETRIEVAL_FAILED]
    assert len(rag_events) >= 1
    assert "ChromaDB" in rag_events[0].message or "nicht erreichbar" in rag_events[0].message


@pytest.mark.failure_mode
@pytest.mark.asyncio
@pytest.mark.integration
async def test_chat_continues_when_rag_fails(qtbot):
    """
    Chat mit RAG aktiviert: Bei RAG-Exception läuft Chat weiter, Antwort wird erzeugt.
    """
    from tests.integration.test_rag_chat_integration import (
        MinimalChatWidget,
        FakeDB,
        FakeOllamaClient,
    )

    class FailingRAGService:
        """RAG-Service der bei augment_if_enabled eine Exception wirft."""

        async def augment_if_enabled(self, query, enabled=True, space=None, top_k=5):
            raise ConnectionError("ChromaDB nicht erreichbar")

    # RAGService fängt ab – aber unser FailingRAGService wirft direkt.
    # Der echte RAGService würde fangen. Wir brauchen einen Service der
    # intern wirft und fängt – das ist der echte RAGService mit FailingPipeline.
    # Stattdessen: Nutze echten RAGService mit gepatchtem get_pipeline.
    from app.core.config.settings import AppSettings

    settings = AppSettings()
    settings.model = "test:latest"
    settings.rag_enabled = True
    settings.rag_space = "default"
    settings.rag_top_k = 5

    client = FakeOllamaClient("Antwort ohne RAG-Kontext")
    db = FakeDB()
    chat_id = db.create_chat()

    # Echter RAGService mit Failing-Pipeline (fängt intern ab)
    rag_service = RAGService()
    rag_service.get_pipeline = lambda **kw: FailingRAGPipeline()

    widget = MinimalChatWidget(client, settings, db, rag_service=rag_service)
    qtbot.addWidget(widget)
    widget.chat_id = chat_id

    await widget.run_chat("Was ist Python?")

    assert client.call_count == 1
    assert "Antwort" in widget.current_full_response

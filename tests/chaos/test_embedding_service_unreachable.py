"""
Chaos: Embedding-Service / RAG-Komponente nicht erreichbar.

Szenario: RAG/Embedding-Service nicht erreichbar.
Erwartung: Chat läuft weiter, RAG-Failure sichtbar, kein stilles Scheitern.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.debug.agent_event import EventType
from app.debug.debug_store import DebugStore
from app.debug.event_bus import EventBus
from app.rag.embedding_service import EmbeddingService
from app.rag.retriever import Retriever
from app.rag.service import RAGService
from app.core.config.settings import AppSettings
from tests.integration.test_rag_chat_integration import (
    MinimalChatWidget,
    FakeDB,
    FakeOllamaClient,
)
from tests.failure_modes.test_rag_retrieval_failure import FailingRAGPipeline


@pytest.fixture
def event_bus_and_store():
    bus = EventBus()
    store = DebugStore(bus=bus)
    yield bus, store
    store._unsubscribe()


@pytest.mark.chaos
@pytest.mark.asyncio
@pytest.mark.integration
async def test_chat_with_rag_unreachable_continues_and_shows_response(qtbot):
    """
    Chat mit RAG aktiviert, RAG nicht erreichbar → Chat läuft weiter,
    Antwort wird erzeugt, RAG-Failure nicht still.
    """
    settings = AppSettings()
    settings.model = "test:latest"
    settings.rag_enabled = True
    settings.rag_space = "default"
    settings.rag_top_k = 5

    client = FakeOllamaClient("Antwort ohne RAG")
    db = FakeDB()
    rag_service = RAGService()
    rag_service.get_pipeline = lambda **kw: FailingRAGPipeline()

    widget = MinimalChatWidget(client, settings, db, rag_service=rag_service)
    qtbot.addWidget(widget)
    widget.chat_id = db.create_chat()
    widget._apply_routing_settings()

    await widget.run_chat("Was ist Python?")

    assert client.call_count == 1
    assert "Antwort" in widget.current_full_response


@pytest.mark.chaos
@pytest.mark.asyncio
async def test_rag_unreachable_emits_event(event_bus_and_store):
    """
    RAG nicht erreichbar → RAG_RETRIEVAL_FAILED Event emittiert.
    Kein stilles Scheitern.
    """
    bus, store = event_bus_and_store

    with patch("app.debug.emitter.get_event_bus", return_value=bus):
        service = RAGService()
        service.get_pipeline = lambda **kw: FailingRAGPipeline()

        await service.augment_if_enabled("Test", enabled=True, space="default", top_k=5)

    history = store.get_event_history()
    rag_events = [e for e in history if e.event_type == EventType.RAG_RETRIEVAL_FAILED]
    assert len(rag_events) >= 1

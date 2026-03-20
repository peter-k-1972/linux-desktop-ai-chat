"""
Failure Injection: ChromaDB Netzwerkfehler / nicht erreichbar.

Simuliert: ChromaDB Client wirft ConnectionError (Netzwerk, Server down).
Erwartung: Retriever gibt [] zurück, RAG degradiert, Chat bleibt funktionsfähig,
Debug/EventBus erhält RAG_RETRIEVAL_FAILED.
"""

from unittest.mock import AsyncMock, patch

import pytest

from app.debug.agent_event import EventType
from app.debug.debug_store import DebugStore
from app.debug.event_bus import EventBus
from app.rag.embedding_service import EmbeddingService
from app.rag.retriever import Retriever
from app.rag.service import RAGService


class UnreachableVectorStore:
    """VectorStore-Mock: query() wirft ConnectionError (ChromaDB nicht erreichbar)."""

    def query(self, query_embedding, n_results=5, where=None):
        raise ConnectionError("ChromaDB nicht erreichbar: Connection refused")


@pytest.fixture
def event_bus_and_store():
    """Isolierter EventBus + DebugStore."""
    bus = EventBus()
    store = DebugStore(bus=bus)
    yield bus, store
    store._unsubscribe()


@pytest.mark.failure_mode
@pytest.mark.asyncio
async def test_retriever_returns_empty_on_chroma_connection_error():
    """
    Retriever.retrieve: Bei ConnectionError von VectorStore wird [] zurückgegeben.
    Keine Exception propagiert.
    """
    embed_service = EmbeddingService()
    embed_service.embed = AsyncMock(return_value=[0.1] * 384)

    retriever = Retriever(
        vector_store=UnreachableVectorStore(),
        embedding_service=embed_service,
        top_k=5,
    )

    chunks = await retriever.retrieve("test query")
    assert chunks == []


@pytest.mark.failure_mode
@pytest.mark.asyncio
async def test_rag_service_handles_chroma_unreachable():
    """
    RAGService.augment_if_enabled: Bei ChromaDB-Netzwerkfehler wird (query, False) zurückgegeben.
    Chat bleibt funktionsfähig.
    """
    from app.rag.knowledge_space import KnowledgeSpaceManager
    from app.rag.rag_pipeline import RAGPipeline

    class ManagerWithUnreachableStore:
        def get_retriever(self, space, top_k=5):
            embed = EmbeddingService()
            embed.embed = AsyncMock(return_value=[0.1] * 384)
            return Retriever(
                vector_store=UnreachableVectorStore(),
                embedding_service=embed,
                top_k=top_k,
            )

    from app.rag.context_builder import ContextBuilder

    manager = ManagerWithUnreachableStore()
    retriever = manager.get_retriever("default", top_k=5)
    pipeline = RAGPipeline(retriever=retriever, context_builder=ContextBuilder())

    service = RAGService()
    service.get_pipeline = lambda **kw: pipeline

    query = "Was steht in den Dokumenten?"
    result_text, rag_used = await service.augment_if_enabled(
        query, enabled=True, space="default", top_k=5
    )

    assert result_text == query
    assert rag_used is False


@pytest.mark.failure_mode
@pytest.mark.asyncio
async def test_chroma_unreachable_emits_rag_retrieval_failed_event(event_bus_and_store):
    """
    Bei ChromaDB-Netzwerkfehler wird RAG_RETRIEVAL_FAILED Event emittiert.
    """
    bus, store = event_bus_and_store

    with patch("app.debug.emitter.get_event_bus", return_value=bus):
        embed = EmbeddingService()
        embed.embed = AsyncMock(return_value=[0.1] * 384)
        retriever = Retriever(
            vector_store=UnreachableVectorStore(),
            embedding_service=embed,
            top_k=5,
        )

        await retriever.retrieve("test query")

    history = store.get_event_history()
    rag_events = [e for e in history if e.event_type == EventType.RAG_RETRIEVAL_FAILED]
    assert len(rag_events) >= 1
    assert "ChromaDB" in rag_events[0].message or "nicht erreichbar" in rag_events[0].message

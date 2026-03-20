"""
Contract Tests: RAG Retrieval Result Struktur.

Sichert den Vertrag zwischen RAG-Subsystem und ChatWidget/LLM-Pipeline.
"""

import pytest

from app.rag.models import Chunk
from app.rag.context_builder import ContextBuilder


REQUIRED_CHUNK_FIELDS = ["id", "document_id", "content", "metadata", "position"]


@pytest.mark.contract
def test_chunk_has_required_fields(test_chunk):
    """Chunk hat alle Felder, die Retriever und ContextBuilder erwarten."""
    for field in REQUIRED_CHUNK_FIELDS:
        assert hasattr(test_chunk, field), f"Chunk fehlt Feld '{field}'"


@pytest.mark.contract
def test_chunk_content_is_string(test_chunk):
    """Chunk.content ist String (für Context-Builder)."""
    assert isinstance(test_chunk.content, str)


@pytest.mark.contract
def test_chunk_metadata_is_dict(test_chunk):
    """Chunk.metadata ist Dict (für Metadaten-Filter)."""
    assert isinstance(test_chunk.metadata, dict)


@pytest.mark.contract
def test_context_builder_accepts_chunk_list(test_chunk):
    """ContextBuilder.build() akzeptiert Liste von Chunks."""
    builder = ContextBuilder()
    context = builder.build([test_chunk])
    assert isinstance(context, str)
    assert test_chunk.content in context


@pytest.mark.contract
def test_context_builder_handles_empty_chunks():
    """ContextBuilder.build() mit leerer Liste liefert leeren String."""
    builder = ContextBuilder()
    context = builder.build([])
    assert context == ""


@pytest.mark.contract
@pytest.mark.asyncio
async def test_rag_augment_return_format():
    """
    RAG augment_prompt liefert (str, bool) – (augmentierter_text, rag_was_used).
    Vertrag für ChatWidget und LLM-Pipeline.
    """
    from app.rag.rag_pipeline import RAGPipeline

    class FakeRetriever:
        async def retrieve(self, query, top_k=None):
            return []

    retriever = FakeRetriever()
    pipeline = RAGPipeline(retriever=retriever)
    text, rag_used = await pipeline.augment_prompt("test query")
    assert isinstance(text, str)
    assert isinstance(rag_used, bool)
    assert text == "test query"
    assert rag_used is False

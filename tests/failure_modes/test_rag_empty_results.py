"""
Failure Injection: Leere Chroma-Treffer.

Simuliert: RAG-Retrieval liefert keine Treffer.
"""

import pytest

from app.rag.rag_pipeline import RAGPipeline
from app.rag.context_builder import ContextBuilder


class EmptyRetriever:
    """Retriever der immer leere Liste liefert."""

    async def retrieve(self, query, top_k=None):
        return []


@pytest.mark.failure_mode
@pytest.mark.asyncio
@pytest.mark.integration
async def test_rag_empty_results_returns_original_query():
    """Leere Chroma-Treffer: augment_prompt liefert Original-Query, rag_was_used=False."""
    retriever = EmptyRetriever()
    pipeline = RAGPipeline(retriever=retriever)
    query = "Was steht in den Dokumenten?"
    text, rag_used = await pipeline.augment_prompt(query)
    assert text == query
    assert rag_used is False


@pytest.mark.failure_mode
@pytest.mark.asyncio
@pytest.mark.integration
async def test_rag_empty_results_context_builder_safe():
    """ContextBuilder mit leerer Chunk-Liste crasht nicht."""
    builder = ContextBuilder()
    result = builder.build([])
    assert result == ""

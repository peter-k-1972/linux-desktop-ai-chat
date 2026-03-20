"""
Failure Injection: ChromaDB Import-Fehler / RAG-Degradation.

Simuliert: chromadb nicht installiert oder VectorStore wirft.
Erwartung: App/Chat bleibt benutzbar, RAG wird sauber deaktiviert.
"""

from unittest.mock import patch

import pytest

from app.rag.vector_store import VectorStore, VectorStoreError


import builtins

_orig_import = builtins.__import__


def _fake_import(name, *args, **kwargs):
    """Simuliert fehlgeschlagenen chromadb-Import."""
    if name == "chromadb" or (isinstance(name, str) and name.startswith("chromadb.")):
        raise ImportError("No module named 'chromadb'")
    return _orig_import(name, *args, **kwargs)


@pytest.mark.failure_mode
def test_vector_store_raises_vector_store_error_on_import_error(tmp_path):
    """
    VectorStore._ensure_client: Bei ImportError wird VectorStoreError geworfen.
    Kein roher ImportError nach außen.
    """
    store = VectorStore(persist_directory=str(tmp_path))

    with patch.object(builtins, "__import__", side_effect=_fake_import):
        with pytest.raises(VectorStoreError) as exc_info:
            store.query(query_embedding=[0.1] * 384, n_results=1)
        msg = str(exc_info.value).lower()
        assert "chromadb" in msg or "install" in msg


@pytest.mark.failure_mode
@pytest.mark.asyncio
async def test_retriever_returns_empty_on_vector_store_error():
    """
    Retriever.retrieve: Bei VectorStoreError (z.B. Chroma nicht installiert)
    wird [] zurückgegeben, keine Exception propagiert.
    """
    from app.rag.retriever import Retriever
    from app.rag.embedding_service import EmbeddingService
    from app.rag.vector_store import VectorStore, VectorStoreError

    class FailingVectorStore:
        def query(self, **kwargs):
            raise VectorStoreError("chromadb nicht installiert")

    embed_service = EmbeddingService()
    retriever = Retriever(
        vector_store=FailingVectorStore(),
        embedding_service=embed_service,
        top_k=5,
    )

    chunks = await retriever.retrieve("test query")
    assert chunks == []


@pytest.mark.failure_mode
@pytest.mark.asyncio
async def test_rag_service_degrades_when_chroma_unavailable():
    """
    RAGService.augment_if_enabled: Bei Chroma/Retrieval-Fehler wird (query, False) zurückgegeben.
    Chat bleibt benutzbar.
    """
    from app.rag.service import RAGService

    # RAGService mit Manager der bei get_retriever einen Store liefert, der bei query wirft
    service = RAGService()

    class FailingVectorStore:
        def query(self, **kwargs):
            from app.rag.vector_store import VectorStoreError
            raise VectorStoreError("chromadb nicht installiert")

    class FailingRetriever:
        async def retrieve(self, query, top_k=None, where=None):
            raise Exception("Chroma nicht verfügbar")

    class FailingPipeline:
        async def augment_prompt(self, user_prompt, top_k=None):
            raise ImportError("No module named 'chromadb'")

    service.get_pipeline = lambda **kw: FailingPipeline()

    query = "Was steht in den Dokumenten?"
    result_text, rag_used = await service.augment_if_enabled(
        query, enabled=True, space="default", top_k=5
    )

    assert result_text == query
    assert rag_used is False


@pytest.mark.failure_mode
def test_vector_store_error_message_mentions_chromadb(tmp_path):
    """VectorStoreError bei ImportError enthält hilfreichen Hinweis."""
    store = VectorStore(persist_directory=str(tmp_path))

    with patch.object(builtins, "__import__", side_effect=_fake_import):
        with pytest.raises(VectorStoreError) as exc_info:
            store._ensure_client()
        msg = str(exc_info.value).lower()
        assert "chromadb" in msg or "install" in msg

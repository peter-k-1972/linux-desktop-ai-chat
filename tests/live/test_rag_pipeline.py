"""
Live Tests: RAG Pipeline.

Testet echte RAG-Pipeline mit ChromaDB und Ollama Embeddings.
Indexierung → Retrieval → Augmentierung.
"""

import pytest

from app.rag.service import RAGService
from app.rag.knowledge_space import KnowledgeSpaceManager
from app.rag.embedding_service import EmbeddingService


@pytest.fixture
def temp_rag_path(tmp_path):
    """Isoliertes RAG-Verzeichnis."""
    return str(tmp_path / "rag_live")


@pytest.fixture
def rag_service(temp_rag_path):
    """RAGService mit echtem ChromaDB und Embedding."""
    return RAGService(base_path=temp_rag_path)


def _ollama_embedding_available() -> bool:
    """Prüft, ob Ollama Embedding erreichbar ist."""
    import asyncio
    svc = EmbeddingService()
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        emb = loop.run_until_complete(svc.embed("test"))
        loop.close()
        return len(emb) > 0
    except Exception:
        return False


@pytest.fixture(scope="module")
def embedding_available():
    if not _ollama_embedding_available():
        pytest.skip("Ollama Embedding (nomic-embed-text) nicht verfügbar")


@pytest.mark.live
@pytest.mark.slow
class TestRAGPipelineLive:
    """Echte RAG-Pipeline mit ChromaDB und Ollama."""

    @pytest.mark.asyncio
    async def test_index_and_retrieve(
        self, rag_service, temp_rag_path, embedding_available, tmp_path
    ):
        """Dokument indexieren und per Query abrufen."""
        # Testdatei erstellen
        doc_path = tmp_path / "sample.md"
        doc_path.write_text(
            "# RAG Live Test\n\n"
            "Dieses Dokument enthält Informationen über Python und Machine Learning. "
            "Python ist eine beliebte Programmiersprache für KI-Projekte.",
            encoding="utf-8",
        )

        manager = rag_service.get_manager()
        count = await manager.index_document("default", str(doc_path))
        assert count > 0

        context = await rag_service.get_context("Was ist Python?", top_k=3)
        assert "Python" in context or "python" in context.lower()

    @pytest.mark.asyncio
    async def test_augment_if_enabled(self, rag_service, temp_rag_path, embedding_available, tmp_path):
        """RAG-Augmentierung erweitert Prompt mit Kontext."""
        doc_path = tmp_path / "augment_test.md"
        doc_path.write_text(
            "Spezielle Test-Information: Der Schlüssel XYZ123 ist wichtig für die Konfiguration.",
            encoding="utf-8",
        )

        manager = rag_service.get_manager()
        await manager.index_document("default", str(doc_path))

        augmented, used = await rag_service.augment_if_enabled(
            "Was steht über XYZ123?",
            enabled=True,
            top_k=2,
        )
        assert used is True
        assert "XYZ123" in augmented or "Kontext" in augmented or "Schlüssel" in augmented

    @pytest.mark.asyncio
    async def test_augment_disabled_returns_original(self, rag_service):
        """Bei RAG deaktiviert wird Original-Prompt zurückgegeben."""
        query = "Einfache Frage ohne RAG"
        augmented, used = await rag_service.augment_if_enabled(query, enabled=False)
        assert used is False
        assert augmented == query

"""
Integration Tests: ChromaDB Vector Store.

Testet echte ChromaDB-Operationen: Add, Query, Delete.
Keine Mocks – reale Vektor-Suche.
"""

import pytest

from app.rag.vector_store import VectorStore
from app.rag.embedding_service import EmbeddingService


@pytest.mark.integration
@pytest.mark.slow
class TestChromaIntegration:
    """Echte ChromaDB-Integration – benötigt Embedding-Service (Ollama)."""

    @pytest.fixture
    def temp_chroma_path(self, tmp_path):
        """Isoliertes Chroma-Verzeichnis pro Test."""
        return str(tmp_path / "chroma_integration")

    @pytest.fixture
    def vector_store(self, temp_chroma_path):
        """VectorStore mit echtem ChromaDB."""
        return VectorStore(
            persist_directory=temp_chroma_path,
            collection_name="test_integration",
        )

    @pytest.fixture
    def embedding_service(self):
        """Echter Embedding-Service (Ollama nomic-embed-text)."""
        return EmbeddingService()

    @pytest.mark.asyncio
    async def test_add_and_query_chunks(self, vector_store, embedding_service):
        """Chunks hinzufügen und per Similarity Search abrufen."""
        texts = [
            "Python ist eine Programmiersprache.",
            "Java wird für Enterprise-Anwendungen genutzt.",
            "JavaScript läuft im Browser.",
        ]
        chunk_ids = [f"chunk-{i}" for i in range(len(texts))]
        metadatas = [
            {"document_id": "doc-1", "chunk_index": i, "filename": "test.txt"}
            for i in range(len(texts))
        ]

        try:
            embeddings = await embedding_service.embed_batch(texts)
            query_embedding = await embedding_service.embed("Programmiersprache Python")
        except Exception as e:
            pytest.skip(f"Ollama Embedding nicht verfügbar: {e}")

        vector_store.add_chunks(chunk_ids, embeddings, texts, metadatas)
        assert vector_store.count() == 3

        ids, metas, distances, documents = vector_store.query(
            query_embedding=query_embedding,
            n_results=2,
        )
        assert len(ids) == 2
        assert len(documents) == 2
        assert "Python" in documents[0] or "Python" in " ".join(documents)

    @pytest.mark.asyncio
    async def test_delete_by_ids(self, vector_store, embedding_service):
        """Chunks per ID löschen."""
        text = "Test-Inhalt für Delete."
        try:
            emb = await embedding_service.embed(text)
        except Exception as e:
            pytest.skip(f"Ollama Embedding nicht verfügbar: {e}")

        vector_store.add_chunks(
            ["del-1", "del-2"],
            [emb, emb],
            [text, text],
            [{"document_id": "d1"}, {"document_id": "d2"}],
        )
        assert vector_store.count() == 2

        vector_store.delete(ids=["del-1"])
        assert vector_store.count() == 1

        ids, _, _, _ = vector_store.query(emb, n_results=5)
        assert "del-1" not in ids
        assert "del-2" in ids


@pytest.mark.integration
class TestChromaWithoutEmbedding:
    """ChromaDB ohne externen Embedding-Service (nur Vector-Store-Logik)."""

    @pytest.fixture
    def vector_store(self, tmp_path):
        return VectorStore(
            persist_directory=str(tmp_path / "chroma_no_emb"),
            collection_name="test_no_emb",
        )

    def test_add_with_precomputed_embeddings(self, vector_store):
        """Chunks mit vordefinierten Embeddings hinzufügen (ohne Ollama)."""
        # nomic-embed-text hat 768 Dimensionen
        dummy_emb = [0.1] * 768
        vector_store.add_chunks(
            ["pre-1", "pre-2"],
            [dummy_emb, dummy_emb],
            ["Text A", "Text B"],
            [{"doc": "1"}, {"doc": "2"}],
        )
        assert vector_store.count() == 2

        ids, _, _, docs = vector_store.query(dummy_emb, n_results=2)
        assert len(ids) == 2
        assert "Text A" in docs or "Text B" in docs

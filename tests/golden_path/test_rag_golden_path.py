"""
Golden-Path 4: RAG aktivieren -> Dokument indexieren -> Retrieval -> Antwort mit Kontext.

Prüft: Dokument indexieren -> Query -> Kontext enthält erwarteten Inhalt.
Verwendet ChromaDB mit vordefinierten Embeddings (ohne Ollama).
"""

import pytest

from app.rag.document_loader import load_document
from app.rag.chunker import Chunker
from app.rag.vector_store import VectorStore
from app.rag.embedding_service import EmbeddingService
from app.rag.context_builder import ContextBuilder
from app.rag.retriever import Retriever


@pytest.mark.golden_path
@pytest.mark.asyncio
async def test_rag_index_retrieve_context(temp_chroma_dir, tmp_path):
    """
    Golden Path: Dokument indexieren -> Retrieval liefert relevante Chunks ->
    ContextBuilder erzeugt Kontext mit Dokumentinhalt.
    """
    # 1. Testdokument erstellen
    doc_path = tmp_path / "rag_golden.md"
    doc_path.write_text(
        "# RAG Golden Path\n\n"
        "Dieses Dokument enthält den Schlüsselbegriff GOLDEN_RAG_TOKEN für den Test.",
        encoding="utf-8",
    )

    # 2. Dokument laden und chunken
    doc = load_document(str(doc_path))
    assert "GOLDEN_RAG_TOKEN" in doc.content

    chunker = Chunker(chunk_size_tokens=200, overlap_tokens=10)
    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 1

    # 3. VectorStore befüllen (vordefinierte Embeddings, kein Ollama)
    store = VectorStore(persist_directory=temp_chroma_dir)
    dummy_emb = [0.01] * 768  # nomic-embed-text Dimension
    chunk_ids = [c.id for c in chunks]
    embeddings = [dummy_emb] * len(chunks)
    documents = [c.content for c in chunks]
    metadatas = [
        {"document_id": c.document_id, "chunk_index": i}
        for i, c in enumerate(chunks)
    ]
    store.add_chunks(chunk_ids, embeddings, documents, metadatas)

    # 4. Retriever mit Mock-Embedding (gleicher Vektor = ähnlichster Treffer)
    from unittest.mock import MagicMock, AsyncMock
    mock_emb = MagicMock()
    mock_emb.embed = AsyncMock(return_value=dummy_emb)

    retriever = Retriever(store, mock_emb)
    result = await retriever.retrieve("GOLDEN_RAG_TOKEN")

    # 5. Retrieval liefert Chunks mit Inhalt
    assert len(result) >= 1
    assert any("GOLDEN_RAG_TOKEN" in c.content for c in result)

    # 6. ContextBuilder erzeugt nutzbaren Kontext
    builder = ContextBuilder()
    context = builder.build(result)
    assert "GOLDEN_RAG_TOKEN" in context

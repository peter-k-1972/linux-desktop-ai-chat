"""
Unit Tests: RAG System.

Testet DocumentLoader, Chunker, EmbeddingService (gemockt), VectorStore,
Retriever, ContextBuilder.
"""

import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.rag.models import Document, Chunk
from app.rag.document_loader import (
    load_document,
    load_documents_from_directory,
    DocumentLoadError,
    SUPPORTED_EXTENSIONS,
)
from app.rag.chunker import Chunker
from app.rag.context_builder import ContextBuilder
from app.rag.embedding_service import EmbeddingService, EmbeddingError
from app.rag.vector_store import VectorStore, VectorStoreError
from app.rag.retriever import Retriever


# --- Document Loader ---

def test_load_document_markdown(test_document_file):
    """Markdown-Dokument laden."""
    doc = load_document(test_document_file)
    assert doc.id
    assert "Beispiel" in doc.content
    assert doc.metadata.get("extension") == ".md"
    assert doc.source_type == "file"


def test_load_document_txt(tmp_path):
    """Text-Dokument laden."""
    txt = tmp_path / "readme.txt"
    txt.write_text("Einfacher Text.", encoding="utf-8")
    doc = load_document(str(txt))
    assert "Einfacher" in doc.content


def test_load_document_json(tmp_path):
    """JSON-Dokument laden."""
    js = tmp_path / "data.json"
    js.write_text('{"key": "value"}', encoding="utf-8")
    doc = load_document(str(js))
    assert "key" in doc.content


def test_load_document_missing():
    """Fehlende Datei wirft DocumentLoadError."""
    with pytest.raises(DocumentLoadError):
        load_document("/nonexistent/path/file.md")


def test_load_document_unsupported_format(tmp_path):
    """Nicht unterstütztes Format wirft DocumentLoadError."""
    x = tmp_path / "file.xyz"
    x.write_text("content", encoding="utf-8")
    with pytest.raises(DocumentLoadError):
        load_document(str(x))


def test_load_documents_from_directory(tmp_path):
    """Verzeichnis mit mehreren Dateien laden."""
    (tmp_path / "a.md").write_text("# A", encoding="utf-8")
    (tmp_path / "b.txt").write_text("B", encoding="utf-8")
    (tmp_path / "skip.log").write_text("log", encoding="utf-8")
    docs = load_documents_from_directory(str(tmp_path), recursive=False)
    assert len(docs) == 2


# --- Chunker ---

def test_chunker_basic(test_document):
    """Chunker erzeugt Chunks mit korrekter Struktur."""
    chunker = Chunker(chunk_size_tokens=100, overlap_tokens=10)
    chunks = chunker.chunk_document(test_document)
    assert len(chunks) >= 1
    for c in chunks:
        assert c.document_id == test_document.id
        assert c.content
        assert c.id
        assert c.position >= 0
        assert "chunk_index" in c.metadata


def test_chunker_small_doc():
    """Kleines Dokument ergibt einen Chunk."""
    doc = Document(id="d", path="/x", content="Kurz.", metadata={})
    chunker = Chunker(chunk_size_tokens=500, overlap_tokens=50)
    chunks = chunker.chunk_document(doc)
    assert len(chunks) == 1
    assert chunks[0].content == "Kurz."


def test_chunker_respects_overlap():
    """Overlap wird zwischen Chunks berücksichtigt."""
    long_text = "Satz eins. Satz zwei. Satz drei. " * 30
    doc = Document(id="d", path="/x", content=long_text, metadata={})
    chunker = Chunker(chunk_size_tokens=50, overlap_tokens=10)
    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 2


# --- Context Builder ---

def test_context_builder_empty():
    """Leere Chunk-Liste ergibt leeren Kontext."""
    cb = ContextBuilder()
    assert cb.build([]) == ""


def test_context_builder_single_chunk(test_chunk):
    """Ein Chunk wird korrekt formatiert."""
    cb = ContextBuilder()
    ctx = cb.build([test_chunk])
    assert "Chunk-Inhalt" in ctx


def test_context_builder_multiple_chunks():
    """Mehrere Chunks werden mit Separator verbunden."""
    cb = ContextBuilder(separator=" | ")
    chunks = [
        Chunk(id="c1", document_id="d1", content="A", metadata={}, position=0),
        Chunk(id="c2", document_id="d1", content="B", metadata={}, position=1),
    ]
    ctx = cb.build(chunks)
    assert "A" in ctx and "B" in ctx
    assert " | " in ctx


def test_context_builder_include_metadata(test_chunk):
    """include_metadata fügt Quellenangabe hinzu."""
    cb = ContextBuilder(include_metadata=True)
    ctx = cb.build([test_chunk])
    assert "[Quelle:" in ctx or "test.md" in ctx


# --- Embedding Service (gemockt) ---

@pytest.mark.asyncio
async def test_embedding_service_embed_empty_raises():
    """Leerer Text wirft EmbeddingError."""
    service = EmbeddingService()
    with pytest.raises(EmbeddingError):
        await service.embed("")


@pytest.mark.asyncio
async def test_embedding_service_embed_mocked():
    """Embed() mit gemockter API."""
    mock_embedding = [0.1] * 768
    with patch.object(
        EmbeddingService, "_call_api", new_callable=AsyncMock, return_value=mock_embedding
    ):
        service = EmbeddingService()
        result = await service.embed("Test-Text")
        assert len(result) == 768
        assert result[0] == 0.1


# --- Vector Store ---

def test_vector_store_add_and_query(temp_chroma_dir):
    """VectorStore speichert und findet Chunks."""
    store = VectorStore(persist_directory=temp_chroma_dir)
    chunk_ids = ["c1", "c2"]
    embeddings = [[0.1] * 768, [0.2] * 768]
    documents = ["Inhalt 1", "Inhalt 2"]
    metadatas = [
        {"document_id": "d1", "chunk_index": 0},
        {"document_id": "d1", "chunk_index": 1},
    ]
    store.add_chunks(chunk_ids, embeddings, documents, metadatas)
    ids, metas, distances, docs = store.query([0.1] * 768, n_results=2)
    assert len(ids) == 2
    assert "Inhalt 1" in docs or "Inhalt 2" in docs


def test_vector_store_count(temp_chroma_dir):
    """VectorStore.count() liefert Anzahl."""
    store = VectorStore(persist_directory=temp_chroma_dir)
    store.add_chunks(
        ["c1"],
        [[0.1] * 768],
        ["Text"],
        [{"document_id": "d1"}],
    )
    assert store.count() == 1


def test_vector_store_delete(temp_chroma_dir):
    """VectorStore.delete() entfernt Einträge."""
    store = VectorStore(persist_directory=temp_chroma_dir)
    store.add_chunks(
        ["c1"],
        [[0.1] * 768],
        ["T"],
        [{"document_id": "d1", "chunk_index": 0}],
    )
    store.delete(ids=["c1"])
    assert store.count() == 0


# --- Retriever (gemockt) ---

@pytest.mark.asyncio
async def test_retriever_empty_query():
    """Retriever gibt bei leerer Query leere Liste zurück."""
    mock_store = MagicMock()
    mock_embedding = AsyncMock(return_value=[0.1] * 768)
    retriever = Retriever(mock_store, MagicMock(embed=mock_embedding))
    result = await retriever.retrieve("")
    assert result == []


@pytest.mark.asyncio
async def test_retriever_returns_chunks():
    """Retriever liefert Chunks aus VectorStore."""
    mock_store = MagicMock()
    mock_store.query.return_value = (
        ["id1"],
        [{"document_id": "d1", "chunk_index": 0}],
        [0.1],
        ["Chunk-Inhalt"],
    )
    mock_embedding = AsyncMock(return_value=[0.1] * 768)
    retriever = Retriever(mock_store, MagicMock(embed=mock_embedding))
    chunks = await retriever.retrieve("Suchanfrage")
    assert len(chunks) == 1
    assert chunks[0].content == "Chunk-Inhalt"
    assert chunks[0].document_id == "d1"

"""
Tests für das RAG-Subsystem.

Unit-Tests für Document Loader, Chunker, Context Builder.
Embedding- und Vector-Store-Tests erfordern Ollama/Chroma (optional).
"""

import tempfile
from pathlib import Path

import pytest

from app.rag.models import Document, Chunk
from app.rag.document_loader import load_document, load_documents_from_directory, DocumentLoadError
from app.rag.chunker import Chunker
from app.rag.context_builder import ContextBuilder


# --- Document Loader ---

def test_load_document_markdown(tmp_path):
    """Markdown-Dokument laden."""
    md = tmp_path / "test.md"
    md.write_text("# Titel\n\nAbsatz mit **Text**.", encoding="utf-8")
    doc = load_document(str(md))
    assert doc.id
    assert doc.path == str(md.resolve())
    assert "Titel" in doc.content
    assert doc.source_type == "file"
    assert doc.metadata.get("extension") == ".md"


def test_load_document_txt(tmp_path):
    """Text-Dokument laden."""
    txt = tmp_path / "readme.txt"
    txt.write_text("Einfacher Text.", encoding="utf-8")
    doc = load_document(str(txt))
    assert "Einfacher" in doc.content


def test_load_document_json(tmp_path):
    """JSON-Dokument laden."""
    js = tmp_path / "data.json"
    js.write_text('{"key": "value", "n": 42}', encoding="utf-8")
    doc = load_document(str(js))
    assert "key" in doc.content and "value" in doc.content


def test_load_document_py(tmp_path):
    """Python-Datei laden."""
    py = tmp_path / "module.py"
    py.write_text('def foo():\n    return 42', encoding="utf-8")
    doc = load_document(str(py))
    assert "def foo" in doc.content


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

def test_chunker_basic():
    """Chunker erzeugt Chunks mit korrekter Struktur."""
    doc = Document(
        id="doc1",
        path="/x/test.md",
        content="Erster Satz. Zweiter Satz. Dritter Satz. " * 50,
        metadata={"filename": "test.md"},
    )
    chunker = Chunker(chunk_size_tokens=100, overlap_tokens=10)
    chunks = chunker.chunk_document(doc)
    assert len(chunks) >= 1
    for c in chunks:
        assert c.document_id == "doc1"
        assert c.content
        assert c.id
        assert c.position >= 0


def test_chunker_small_doc():
    """Kleines Dokument ergibt einen Chunk."""
    doc = Document(id="d", path="/x", content="Kurz.", metadata={})
    chunker = Chunker(chunk_size_tokens=500, overlap_tokens=50)
    chunks = chunker.chunk_document(doc)
    assert len(chunks) == 1
    assert chunks[0].content == "Kurz."


# --- Context Builder ---

def test_context_builder_empty():
    """Leere Chunk-Liste ergibt leeren Kontext."""
    cb = ContextBuilder()
    assert cb.build([]) == ""


def test_context_builder_single_chunk():
    """Ein Chunk wird korrekt formatiert."""
    cb = ContextBuilder()
    chunks = [
        Chunk(id="c1", document_id="d1", content="Inhalt", metadata={}, position=0),
    ]
    ctx = cb.build(chunks)
    assert "Inhalt" in ctx


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


def test_context_builder_respects_max_tokens():
    """Kontext wird bei max_context_tokens begrenzt."""
    cb = ContextBuilder(max_context_tokens=10)
    long_content = "x" * 200
    chunks = [
        Chunk(id="c1", document_id="d1", content=long_content, metadata={}, position=0),
    ]
    ctx = cb.build(chunks)
    assert len(ctx) <= 50  # grob 10 * 4 + Puffer

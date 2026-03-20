"""
Contract Tests: LLM Streaming-Chunk-Struktur.

Sichert den Vertrag zwischen Ollama/Provider-Response und ChatWidget/_extract_chunk_parts.
Verhindert: LLM-Stream-Schema-Drift, fehlende Felder, strukturelle Änderungen.
"""

from typing import Any, Dict

import pytest

from app.gui.legacy import _extract_chunk_parts


# Pflicht-Struktur: Chunk muss entweder error ODER message haben
# message ist Dict mit optional content, thinking
# done markiert Stream-Ende (Ollama-Format)


@pytest.mark.contract
def test_extract_chunk_parts_accepts_content_chunk():
    """Chunk mit message.content wird korrekt extrahiert."""
    chunk = {"message": {"content": "Hello", "thinking": ""}, "done": False}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == "Hello"
    assert thinking == ""
    assert error is None


@pytest.mark.contract
def test_extract_chunk_parts_accepts_thinking_only_chunk():
    """Chunk mit nur message.thinking (kein content) wird extrahiert."""
    chunk = {"message": {"content": "", "thinking": "Let me think..."}, "done": False}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == ""
    assert thinking == "Let me think..."
    assert error is None


@pytest.mark.contract
def test_extract_chunk_parts_accepts_error_chunk():
    """Chunk mit error-Feld liefert Fehler, kein Crash."""
    chunk = {"error": "Model not found"}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == ""
    assert thinking == ""
    assert error == "Model not found"


@pytest.mark.contract
def test_extract_chunk_parts_handles_missing_message():
    """Chunk ohne message (leeres Dict) crasht nicht."""
    chunk = {}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == ""
    assert thinking == ""
    assert error is None


@pytest.mark.contract
def test_extract_chunk_parts_handles_message_none():
    """Chunk mit message=None crasht nicht."""
    chunk = {"message": None}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == ""
    assert thinking == ""
    assert error is None


@pytest.mark.contract
def test_chunk_done_field_used_by_chat_widget():
    """
    chunk.get('done', False) wird von run_chat für update_chat_signal genutzt.
    Chunk muss 'done' als bool oder fehlend unterstützen.
    """
    chunk_with_done = {"message": {"content": "x", "thinking": ""}, "done": True}
    content, _, _ = _extract_chunk_parts(chunk_with_done)
    assert content == "x"
    # done wird nicht von _extract_chunk_parts genutzt, aber vom Caller
    assert chunk_with_done.get("done", False) is True

    chunk_without_done = {"message": {"content": "y", "thinking": ""}}
    assert chunk_without_done.get("done", False) is False


@pytest.mark.contract
def test_valid_chunk_structures_are_stable():
    """
    Dokumentiert die stabilen Chunk-Strukturen.
    Änderungen an diesen Formaten müssen _extract_chunk_parts anpassen.
    """
    valid_chunks = [
        {"message": {"content": "a", "thinking": ""}, "done": False},
        {"message": {"content": "", "thinking": "t"}, "done": False},
        {"message": {"content": "b", "thinking": "t"}, "done": True},
        {"error": "error message"},
    ]
    for chunk in valid_chunks:
        content, thinking, error = _extract_chunk_parts(chunk)
        assert isinstance(content, str)
        assert isinstance(thinking, str)
        if "error" in chunk:
            assert error == chunk["error"]
        else:
            assert error is None

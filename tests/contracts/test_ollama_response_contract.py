"""
Contract Tests: Ollama Chat Response Format.

Sichert den Vertrag zwischen Ollama-API-Response und Parser (ChatWidget, LLM).
Ollama liefert Streaming-Chunks im Format:
  {"message": {"role": "assistant", "content": "...", "thinking": "..."}, "done": bool, "error": "..."}

Tests stellen sicher: Parser verhält sich defensiv, Fehler führt nicht zu Crash.
"""

from typing import Any, Dict

import pytest

from app.gui.legacy import _extract_chunk_parts


# Erwartete Ollama-Streaming-Chunk-Struktur (Dokumentation)
OLLAMA_CHUNK_SCHEMA = {
    "message": {"role": "assistant", "content": "...", "thinking": "..."},
    "done": False,
    "error": None,  # optional, bei Fehler gesetzt
}


@pytest.mark.contract
def test_ollama_valid_response_chunk():
    """Gültige Ollama-Response: message mit content und role."""
    chunk: Dict[str, Any] = {
        "model": "llama3",
        "message": {"role": "assistant", "content": "Hallo!", "thinking": ""},
        "done": False,
    }
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == "Hallo!"
    assert thinking == ""
    assert error is None


@pytest.mark.contract
def test_ollama_chunk_missing_message_field():
    """Chunk ohne message-Feld → leere Rückgabe, kein Crash."""
    chunk = {"model": "llama3", "done": False}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == ""
    assert thinking == ""
    assert error is None


@pytest.mark.contract
def test_ollama_chunk_missing_content_in_message():
    """message ohne content → content leer, thinking falls vorhanden."""
    chunk = {"message": {"role": "assistant", "thinking": "..."}, "done": False}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == ""
    assert thinking == "..."
    assert error is None


@pytest.mark.contract
def test_ollama_chunk_unexpected_structure_message_is_int():
    """message als int/ungültiger Typ → kein Crash, Fallback auf leere Rückgabe."""
    chunk = {"message": 42}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == ""
    assert thinking == ""
    assert error is None


@pytest.mark.contract
def test_ollama_chunk_content_is_not_string():
    """message.content als Nicht-String → kein Crash, Parser liefert was er bekommt."""
    chunk = {"message": {"content": ["a", "b"], "thinking": ""}}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert error is None
    assert thinking == ""
    # Parser crasht nicht; content kann list sein (Ollama-Schema erwartet str)


@pytest.mark.contract
def test_ollama_error_chunk_returns_error_not_crash():
    """Chunk mit error → Fehlertext zurück, kein Crash."""
    chunk = {"error": "Connection refused", "message": {"content": "x"}}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == ""
    assert thinking == ""
    assert error == "Connection refused"


@pytest.mark.contract
def test_ollama_done_chunk_with_content():
    """done=True mit content → Stream-Ende, content wird extrahiert."""
    chunk = {"message": {"content": "Fertig.", "thinking": ""}, "done": True}
    content, thinking, error = _extract_chunk_parts(chunk)
    assert content == "Fertig."
    assert error is None
    assert chunk.get("done", False) is True

"""
Failure Injection: Kaputte Ollama-Antwort.

Simuliert: API-Fehler, leere Antwort, ungültige Chunk-Struktur.
"""

from typing import Dict, List

import pytest

from tests.failure_modes.conftest import MinimalChatWidget, FakeDB, failure_settings


class BrokenOllamaClient:
    """Client der verschiedene Fehlerszenarien liefert."""

    def __init__(self, mode: str = "error"):
        self.mode = mode
        self.call_count = 0

    async def get_models(self):
        return []

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs):
        self.call_count += 1
        if self.mode == "error":
            raise ConnectionError("Ollama nicht erreichbar")
        if self.mode == "empty_stream":
            async def _empty():
                return
                yield  # Generator
            return _empty()
        if self.mode == "malformed_chunk":
            async def _malformed():
                yield {"invalid": "structure"}
                yield {"message": {"content": "ok", "thinking": ""}, "done": True}
            return _malformed()
        if self.mode == "error_chunk":
            async def _err():
                yield {"error": "Model not found"}
            return _err()
        return iter([])


@pytest.mark.failure_mode
@pytest.mark.asyncio
@pytest.mark.integration
async def test_ollama_connection_error_handled_gracefully(failure_settings):
    """ConnectionError von Ollama führt zu Fehlermeldung, kein Crash."""
    client = BrokenOllamaClient(mode="error")
    db = FakeDB()
    widget = MinimalChatWidget(client, failure_settings, db)
    widget.chat_id = db.create_chat()

    await widget.run_chat("Test")

    assert client.call_count == 1
    # Fehler muss in DB gespeichert sein (Fehlermeldung)
    rows = db.load_chat(widget.chat_id)
    assistant_msgs = [r for r in rows if r[0] == "assistant"]
    assert len(assistant_msgs) == 1
    assert "Fehler" in assistant_msgs[0][1] or "Error" in assistant_msgs[0][1].lower()


@pytest.mark.failure_mode
@pytest.mark.asyncio
@pytest.mark.integration
async def test_ollama_error_chunk_handled(failure_settings):
    """Chunk mit error-Feld wird als Fehler angezeigt."""
    client = BrokenOllamaClient(mode="error_chunk")
    db = FakeDB()
    widget = MinimalChatWidget(client, failure_settings, db)
    widget.chat_id = db.create_chat()

    await widget.run_chat("Test")

    rows = db.load_chat(widget.chat_id)
    assistant_msgs = [r for r in rows if r[0] == "assistant"]
    assert len(assistant_msgs) == 1
    assert "Model not found" in assistant_msgs[0][1] or "Ollama" in assistant_msgs[0][1]

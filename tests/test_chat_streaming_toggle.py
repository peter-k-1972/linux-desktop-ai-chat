"""
Tests für den Streaming-Toggle (chat.streaming_enabled).

Prüft:
- ChatService respektiert stream-Parameter
- stream=False: ein Chunk am Ende
- stream=True: mehrere Chunks
- Settings-Integration
"""

import asyncio
from typing import Any, AsyncGenerator, Dict, List

import pytest

from app.services.chat_service import ChatService
from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend


class FakeOllamaClient:
    """Fake, der stream=True/False unterstützt und Chunks entsprechend liefert."""

    def __init__(self):
        self.last_stream: bool | None = None

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        stream: bool = True,
        think: Any = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        self.last_stream = stream
        full_response = {"message": {"content": "Vollständige Antwort", "thinking": ""}, "done": True}
        if stream:
            for part in ["Voll", "ständige ", "Antwort"]:
                await asyncio.sleep(0)
                yield {"message": {"content": part, "thinking": ""}, "done": False}
            yield full_response
        else:
            yield full_response

    async def close(self) -> None:
        pass


class FakeInfrastructure:
    """Minimale Infra mit FakeOllamaClient und InMemory-Settings."""

    def __init__(self):
        self._client = FakeOllamaClient()
        self._settings = AppSettings(backend=InMemoryBackend())
        self._settings.model_usage_tracking_enabled = False

    @property
    def ollama_client(self) -> FakeOllamaClient:
        return self._client

    @property
    def database(self):
        raise NotImplementedError("Nicht benötigt für diesen Test")

    @property
    def settings(self) -> AppSettings:
        return self._settings


@pytest.fixture
def chat_service(monkeypatch):
    """ChatService mit Fake-Infrastruktur."""
    from app.services.model_orchestrator_service import reset_model_orchestrator

    infra = FakeInfrastructure()
    reset_model_orchestrator()
    monkeypatch.setattr("app.services.infrastructure.get_infrastructure", lambda: infra)
    svc = ChatService()
    yield svc, infra


@pytest.mark.asyncio
async def test_chat_service_stream_true_yields_multiple_chunks(chat_service):
    """Streaming EIN: ChatService liefert mehrere Chunks."""
    svc, infra = chat_service
    chunks = []
    async for chunk in svc.chat(
        model="test",
        messages=[{"role": "user", "content": "Hallo"}],
        stream=True,
    ):
        chunks.append(chunk)
    assert infra.ollama_client.last_stream is True
    assert len(chunks) >= 2  # Mindestens 2 Teile + done


@pytest.mark.asyncio
async def test_chat_service_stream_false_yields_single_chunk(chat_service):
    """Streaming AUS: ChatService liefert einen Chunk am Ende."""
    svc, infra = chat_service
    chunks = []
    async for chunk in svc.chat(
        model="test",
        messages=[{"role": "user", "content": "Hallo"}],
        stream=False,
    ):
        chunks.append(chunk)
    assert infra.ollama_client.last_stream is False
    assert len(chunks) == 1
    msg = chunks[0].get("message") or {}
    assert msg.get("content") == "Vollständige Antwort"
    assert chunks[0].get("done") is True


@pytest.mark.asyncio
async def test_settings_chat_streaming_enabled_default():
    """chat_streaming_enabled hat Default True."""
    backend = InMemoryBackend()
    s = AppSettings(backend=backend)
    assert s.chat_streaming_enabled is True


@pytest.mark.asyncio
async def test_settings_chat_streaming_enabled_persisted():
    """chat_streaming_enabled wird geladen und gespeichert."""
    backend = InMemoryBackend()
    s = AppSettings(backend=backend)
    s.chat_streaming_enabled = False
    s.save()
    s2 = AppSettings(backend=backend)
    s2.load()
    assert s2.chat_streaming_enabled is False

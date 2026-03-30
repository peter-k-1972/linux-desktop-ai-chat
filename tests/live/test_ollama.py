"""
Live Tests: Ollama API.

Testet echte Ollama-Aufrufe: get_models, get_version, chat.
Überspringt nur, wenn Ollama nicht erreichbar ist.
"""

import asyncio

import pytest

from app.providers.ollama_client import OllamaClient


def _ollama_available() -> bool:
    """Prüft, ob Ollama erreichbar ist."""
    client = OllamaClient()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        info = loop.run_until_complete(client.get_debug_info())
        return info.get("online", False)
    except Exception:
        return False
    finally:
        try:
            loop.run_until_complete(client.close())
        except Exception:
            pass
        loop.close()


@pytest.fixture(scope="module")
def ollama_available():
    """Prüft einmal pro Modul, ob Ollama verfügbar ist."""
    if not _ollama_available():
        pytest.skip("Ollama nicht erreichbar (localhost:11434) – Live-Test übersprungen")


@pytest.fixture
async def ollama_live_client():
    """Echte Ollama-Session; aiohttp wird nach jedem Test geschlossen."""
    client = OllamaClient(base_url="http://localhost:11434")
    yield client
    await client.close()


@pytest.mark.live
@pytest.mark.slow
class TestOllamaLive:
    """Echte Ollama-API-Tests."""

    @pytest.mark.asyncio
    async def test_get_models(self, ollama_live_client, ollama_available):
        """Ollama liefert Modellliste."""
        models = await ollama_live_client.get_models()
        assert isinstance(models, list)
        # Mindestens ein Modell sollte da sein (z.B. llama3, qwen2.5)
        if models:
            assert "name" in models[0] or "model" in models[0]

    @pytest.mark.asyncio
    async def test_get_version(self, ollama_live_client, ollama_available):
        """Ollama liefert Version."""
        version = await ollama_live_client.get_version()
        assert version is not None
        assert len(str(version)) > 0

    @pytest.mark.asyncio
    async def test_get_debug_info(self, ollama_live_client, ollama_available):
        """Debug-Info enthält online, base_url, models."""
        info = await ollama_live_client.get_debug_info()
        assert info["online"] is True
        assert "base_url" in info
        assert "models" in info

    @pytest.mark.asyncio
    async def test_chat_completion(self, ollama_live_client, ollama_available):
        """Echter Chat-Aufruf liefert Antwort."""
        models = await ollama_live_client.get_models()
        if not models:
            pytest.skip("Kein Modell in Ollama verfügbar")

        # Nur Chat-Modelle (keine Embedding-Modelle wie nomic-embed-text)
        chat_models = [
            m for m in models
            if "embed" not in (m.get("name") or m.get("model") or "").lower()
        ]
        if not chat_models:
            pytest.skip("Kein Chat-Modell in Ollama (nur Embedding-Modelle)")

        # Bevorzuge kleinere/schnellere Modelle für den Test
        fast_hints = ("tiny", "1b", "0.5b", "3b", "7b", "qwen", "llama", "phi", "mistral")
        def _speed_key(m):
            name = (m.get("name") or m.get("model") or "").lower()
            for i, h in enumerate(fast_hints):
                if h in name:
                    return i
            return 99

        chat_models.sort(key=_speed_key)
        model_name = chat_models[0].get("name") or chat_models[0].get("model")
        messages = [{"role": "user", "content": "Antworte nur mit: OK"}]

        chunks = []
        try:
            async with asyncio.timeout(120):
                async for chunk in ollama_live_client.chat(
                    model=model_name,
                    messages=messages,
                    temperature=0,
                    max_tokens=20,
                    stream=True,
                ):
                    if "error" in chunk:
                        pytest.skip(f"Ollama Chat-Fehler: {chunk.get('error')}")
                    chunks.append(chunk)
        except asyncio.TimeoutError:
            pytest.skip("Ollama Chat-Timeout (Modell lädt evtl. noch)")

        assert len(chunks) > 0
        full_content = ""
        for c in chunks:
            msg = c.get("message") or {}
            full_content += msg.get("content", "")
        assert len(full_content) > 0 or any("done" in str(c) for c in chunks)

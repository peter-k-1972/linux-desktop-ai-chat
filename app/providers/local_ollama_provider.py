"""
Lokaler Ollama-Provider.

Verwendet die bestehende OllamaClient-Logik für lokale Aufrufe.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional

from app.providers.ollama_client import OllamaClient
from app.providers.base_provider import BaseChatProvider


class LocalOllamaProvider(BaseChatProvider):
    """Provider für lokale Ollama-Instanz."""

    def __init__(
        self,
        client: Optional[OllamaClient] = None,
        base_url: str = "http://localhost:11434",
        session=None,
    ):
        self._client = client or OllamaClient(session=session, base_url=base_url)

    @property
    def provider_id(self) -> str:
        return "local"

    @property
    def source_type(self) -> str:
        return "local"

    @property
    def client(self) -> OllamaClient:
        """Zugriff auf den zugrunde liegenden OllamaClient."""
        return self._client

    async def is_available(self) -> bool:
        info = await self._client.get_debug_info()
        return info.get("online", False)

    async def get_models(self) -> List[Dict[str, Any]]:
        return await self._client.get_models()

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        stream: bool = True,
        think: Any = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        async for chunk in self._client.chat(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            think=think,
        ):
            yield chunk

    async def close(self) -> None:
        await self._client.close()

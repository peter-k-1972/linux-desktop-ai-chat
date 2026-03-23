"""
Cloud-Ollama-Provider für Ollama Cloud API.

Nutzt https://ollama.com/api mit Bearer-Token.
API-Key aus .env (OLLAMA_API_KEY) oder Umgebungsvariable.
"""

import os
from typing import Any, AsyncGenerator, Dict, List, Optional

import aiohttp

from app.providers.base_provider import BaseChatProvider
from app.providers.ollama_client import iter_ndjson_dicts
from app.utils.env_loader import load_env

OLLAMA_CLOUD_URL = "https://ollama.com/api"


def get_ollama_api_key() -> Optional[str]:
    """Liefert den Ollama-API-Key aus .env oder Umgebung."""
    load_env()
    return os.environ.get("OLLAMA_API_KEY") or None


def verify_api_key_loaded() -> tuple:
    """
    Prüft, ob OLLAMA_API_KEY geladen wurde.
    Returns: (loaded: bool, source: str)
    """
    load_env()
    key = os.environ.get("OLLAMA_API_KEY")
    if key:
        return True, ".env oder Umgebungsvariable"
    return False, "nicht gefunden"


class CloudOllamaProvider(BaseChatProvider):
    """Provider für Ollama Cloud API."""

    def __init__(self, api_key: Optional[str] = None, base_url: str = OLLAMA_CLOUD_URL):
        raw = api_key or get_ollama_api_key()
        self._api_key = (raw or "").strip() or None
        self._base_url = base_url.rstrip("/")
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def provider_id(self) -> str:
        return "ollama_cloud"

    @property
    def source_type(self) -> str:
        return "cloud"

    def has_api_key(self) -> bool:
        """Prüft, ob ein API-Key konfiguriert ist."""
        return bool(self._api_key)

    def set_api_key(self, key: Optional[str]) -> None:
        """Setzt den API-Key (z.B. aus Settings)."""
        self._api_key = (key or "").strip() or None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=300, connect=15)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        key = (self._api_key or "").strip()
        if key:
            headers["Authorization"] = f"Bearer {key}"
        return headers

    async def is_available(self) -> bool:
        """Prüft, ob der API-Key gültig ist. Nutzt /api/chat (nicht /tags – das liefert 200 ohne Auth)."""
        if not (self._api_key or "").strip():
            return False
        try:
            session = await self._get_session()
            # /api/tags liefert auf ollama.com oft 200 ohne Auth – nutze /api/chat zur echten Validierung
            payload = {
                "model": "gpt-oss:120b",
                "messages": [{"role": "user", "content": "x"}],
                "stream": False,
            }
            async with session.post(
                f"{self._base_url}/chat",
                json=payload,
                headers=self._headers(),
            ) as r:
                if r.status == 401:
                    await r.read()
                    return False
                if r.status == 200:
                    await r.read()
                    return True
                # 404/500 etc. = Key war auth-ok, Modell/Server-Problem
                await r.read()
                return r.status < 500
        except Exception:
            return False

    async def get_models(self) -> List[Dict[str, Any]]:
        """Liefert Cloud-Modelle (falls API verfügbar)."""
        if not self._api_key:
            return []
        try:
            session = await self._get_session()
            async with session.get(
                f"{self._base_url}/tags",
                headers=self._headers(),
            ) as r:
                if r.status != 200:
                    return []
                data = await r.json()
                return data.get("models", [])
        except Exception:
            return []

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        stream: bool = True,
        think: Any = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        if not self._api_key:
            yield {"error": "OLLAMA_API_KEY fehlt. Bitte in .env oder Einstellungen setzen."}
            return

        payload: Dict[str, Any] = {
            "model": model,
            "messages": messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
            "stream": stream,
        }
        if think is not None:
            payload["think"] = think
        elif "gpt-oss" in (model or "").lower():
            payload["think"] = "low"

        try:
            session = await self._get_session()
            async with session.post(
                f"{self._base_url}/chat",
                json=payload,
                headers=self._headers(),
            ) as r:
                if r.status != 200:
                    error_text = await r.text()
                    yield {"error": f"Cloud API Fehler {r.status}: {error_text[:300]}"}
                    return

                if stream:
                    async for data in iter_ndjson_dicts(r.content):
                        yield data
                else:
                    data = await r.json()
                    yield data
        except aiohttp.ClientError as e:
            yield {"error": f"Cloud-Netzwerkfehler: {e}"}
        except Exception as e:
            yield {"error": str(e)}

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

"""
Erzeugt Standard-Local-/Cloud-Chat-Provider für ModelOrchestrator.

Services importieren keine Provider-Klassen direkt (Governance-Tests).
"""

from __future__ import annotations

from typing import Optional, Set

from app.providers.ollama_client import OllamaClient


def create_default_orchestrator_providers(
    *,
    ollama_client: OllamaClient,
    api_key: Optional[str] = None,
):
    from app.providers.cloud_ollama_provider import CloudOllamaProvider
    from app.providers.local_ollama_provider import LocalOllamaProvider

    local = LocalOllamaProvider(client=ollama_client)
    cloud = CloudOllamaProvider(api_key=api_key)
    return local, cloud


_EMBED_SUBSTR = ("embed", "embedding", "nomic-embed", "bge-", "e5-")


def _is_embedding_name(name: str) -> bool:
    if not name:
        return False
    lower = name.lower()
    return any(p in lower for p in _EMBED_SUBSTR)


async def fetch_cloud_chat_model_names(api_key: Optional[str]) -> Set[str]:
    """Cloud-Modellnamen (ohne Embedding-Kandidaten) für Kataloge; nur in providers."""
    from app.providers.cloud_ollama_provider import CloudOllamaProvider

    cloud = CloudOllamaProvider(api_key=api_key)
    names: Set[str] = set()
    try:
        if not cloud.has_api_key():
            return names
        try:
            cm = await cloud.get_models()
            for m in cm:
                n = (m.get("name") or m.get("model") or "").strip()
                if n and not _is_embedding_name(n):
                    names.add(n)
        except Exception:
            pass
        return names
    finally:
        try:
            await cloud.close()
        except Exception:
            pass

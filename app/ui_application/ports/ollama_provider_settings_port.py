"""
OllamaProviderSettingsPort — .env-Key lesen + Cloud-Key validieren (Qt-frei).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class OllamaProviderSettingsPort(Protocol):
    def get_ollama_api_key_from_env(self) -> str | None:
        """Key aus Umgebung (.env / OLLAMA_API_KEY), oder None."""
        ...

    async def validate_cloud_api_key(self, api_key: str) -> bool:
        """True wenn der Key gültig wirkt (Provider-Service)."""
        ...

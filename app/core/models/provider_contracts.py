"""
Provider-neutrale Contracts fuer den Model-Orchestrator.
"""

from __future__ import annotations

from typing import Any, AsyncGenerator, Dict, List, Protocol


class ChatProvider(Protocol):
    @property
    def provider_id(self) -> str:
        """Eindeutige Provider-ID."""

    @property
    def source_type(self) -> str:
        """Quelle des Providers, z. B. local oder cloud."""

    async def get_models(self) -> List[Dict[str, Any]]:
        """Liefert die verfuegbaren Modelle."""

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        stream: bool = True,
        think: Any = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Streamt Chat-Antworten im Provider-Format."""

    async def close(self) -> None:
        """Schliesst Provider-Ressourcen."""


class CloudChatProvider(ChatProvider, Protocol):
    def has_api_key(self) -> bool:
        """Prueft, ob Cloud-Zugriff verfuegbar ist."""

    def set_api_key(self, key: str | None) -> None:
        """Aktualisiert den konfigurierten API-Key."""

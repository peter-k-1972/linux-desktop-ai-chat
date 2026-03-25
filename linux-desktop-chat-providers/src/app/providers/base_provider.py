"""
Abstrakte Basis für Chat-Provider.

Gemeinsame Schnittstelle für lokale und Cloud-Backends.
"""

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional


class BaseChatProvider(ABC):
    """Abstrakte Basis für Chat-Provider."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """Eindeutige Provider-ID (z.B. 'local', 'cloud')."""
        pass

    @property
    @abstractmethod
    def source_type(self) -> str:
        """'local' oder 'cloud'."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Prüft, ob der Provider erreichbar ist."""
        pass

    @abstractmethod
    async def get_models(self) -> List[Dict[str, Any]]:
        """Liefert die verfügbaren Modelle."""
        pass

    @abstractmethod
    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        stream: bool = True,
        think: Any = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Sendet eine Chat-Anfrage und streamt die Antwort.

        Yields:
            Chunks im Ollama-Format: {"message": {"content": "...", "thinking": "..."}, "done": bool, "error": "..."}
        """
        pass

    async def close(self) -> None:
        """Schließt Ressourcen (Session etc.)."""
        pass

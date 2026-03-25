"""
Provider-Abstraktion für Chat-Backends.

- OllamaClient: Low-Level Ollama API
- LocalOllamaProvider: lokale Ollama-Instanz
- CloudOllamaProvider: Ollama Cloud API
"""

from app.providers.base_provider import BaseChatProvider
from app.providers.cloud_ollama_provider import CloudOllamaProvider
from app.providers.local_ollama_provider import LocalOllamaProvider
from app.providers.ollama_client import OllamaClient, OLLAMA_URL

__all__ = [
    "BaseChatProvider",
    "CloudOllamaProvider",
    "LocalOllamaProvider",
    "OllamaClient",
    "OLLAMA_URL",
]

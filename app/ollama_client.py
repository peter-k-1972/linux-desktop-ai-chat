"""
Re-Export für Rückwärtskompatibilität.
OllamaClient wurde nach app.providers.ollama_client verschoben.
"""

from app.providers.ollama_client import OLLAMA_URL, OllamaClient

__all__ = ["OllamaClient", "OLLAMA_URL"]

"""
ModelService – verfügbare Modelle, Standardmodell, Modellstatus.

Verantwortlich für:
- Modellliste von Ollama
- Standardmodell (Settings)
- Modell-Metadaten

GUI spricht nur mit ModelService, nicht mit Ollama direkt.
"""

from typing import Any, Dict, List, Optional

from app.services.infrastructure import get_infrastructure
from app.services.result import ServiceResult

# Modelle, die nur für Embeddings sind – nicht für Chat geeignet
_EMBED_PATTERNS = ("embed", "embedding", "nomic-embed", "bge-", "e5-")


def _is_embedding_model(name: str) -> bool:
    """Prüft, ob der Modellname auf ein Embedding-Modell hindeutet."""
    if not name:
        return False
    lower = name.lower()
    return any(p in lower for p in _EMBED_PATTERNS)


class ModelService:
    """
    Service für Modelle: Liste, Standard, Metadaten.
    """

    def __init__(self):
        self._infra = get_infrastructure()

    async def get_models(self) -> ServiceResult[List[str]]:
        """Liefert verfügbare Modellnamen von Ollama (alle)."""
        try:
            models = await self._infra.ollama_client.get_models()
            names = [
                m.get("name", m.get("model", ""))
                for m in models
                if m.get("name") or m.get("model")
            ]
            return ServiceResult.ok(names)
        except Exception as e:
            return ServiceResult.fail(str(e))

    async def get_chat_models(self) -> ServiceResult[List[str]]:
        """Liefert nur Chat-fähige Modelle (ohne Embedding-Modelle)."""
        result = await self.get_models()
        if not result.success:
            return result
        chat_models = [n for n in result.data if not _is_embedding_model(n)]
        return ServiceResult.ok(chat_models)

    def get_default_chat_model(self, available: List[str]) -> str:
        """Liefert das Standard-Chat-Modell; fällt auf erstes verfügbares zurück, wenn Default ein Embedding-Modell ist."""
        stored = self.get_default_model()
        if stored and stored in available and not _is_embedding_model(stored):
            return stored
        return available[0] if available else (stored or "llama2")

    async def get_models_full(self) -> ServiceResult[List[Dict[str, Any]]]:
        """Liefert Modelle mit Metadaten (name, size, digest, etc.)."""
        try:
            models = await self._infra.ollama_client.get_models()
            return ServiceResult.ok(models)
        except Exception as e:
            return ServiceResult.fail(str(e))

    def get_default_model(self) -> str:
        """Aktuelles Standardmodell aus Settings."""
        return getattr(self._infra.settings, "model", "llama2") or "llama2"

    def set_default_model(self, model_name: str) -> ServiceResult[None]:
        """Setzt das Standardmodell und speichert in Settings."""
        try:
            self._infra.settings.model = model_name
            self._infra.settings.save()
            return ServiceResult.ok(None)
        except Exception as e:
            return ServiceResult.fail(str(e))


_model_service: Optional[ModelService] = None


def get_model_service() -> ModelService:
    """Liefert den globalen ModelService."""
    global _model_service
    if _model_service is None:
        _model_service = ModelService()
    return _model_service

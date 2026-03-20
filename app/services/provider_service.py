"""
ProviderService – Providerliste, Ollama-Status, Erreichbarkeit.

Verantwortlich für:
- Provider-Status (Ollama online/offline)
- Provider-Metadaten (Version, Modellanzahl, Base-URL)

GUI spricht nur mit ProviderService, nicht mit Ollama direkt.
"""

from typing import Any, Dict, Optional

from app.services.infrastructure import get_infrastructure
from app.services.result import ServiceResult


class ProviderService:
    """
    Service für Provider: Status, Erreichbarkeit, Metadaten.
    """

    def __init__(self):
        self._infra = get_infrastructure()

    async def get_provider_status(self) -> ServiceResult[Dict[str, Any]]:
        """
        Liefert Provider-Status (Ollama).
        Keys: online, base_url, version, models, model_count, processes, vram_used_mib
        """
        try:
            info = await self._infra.ollama_client.get_debug_info()
            return ServiceResult.ok(info)
        except Exception as e:
            return ServiceResult.fail(str(e))

    async def get_ollama_status(self) -> Dict[str, Any]:
        """
        Legacy-kompatibel: Liefert Ollama-Status direkt.
        Für schrittweise Migration.
        """
        result = await self.get_provider_status()
        if result.success and result.data:
            return result.data
        return {
            "online": False,
            "base_url": "http://localhost:11434",
            "version": None,
            "models": [],
            "model_count": 0,
        }

    def get_ollama_api_key_from_env(self) -> Optional[str]:
        """
        Liefert den Ollama Cloud API-Key aus .env (OLLAMA_API_KEY).
        Für GUI-Einstellungen; GUI importiert keine Provider direkt.
        """
        from app.providers.cloud_ollama_provider import get_ollama_api_key
        return get_ollama_api_key() or None

    async def validate_cloud_api_key(self, api_key: str) -> bool:
        """
        Prüft, ob der API-Key für Ollama Cloud gültig ist.
        Für GUI-Einstellungen; GUI importiert keine Provider direkt.
        """
        if not api_key or not api_key.strip():
            return False
        try:
            from app.providers.cloud_ollama_provider import CloudOllamaProvider
            provider = CloudOllamaProvider(api_key=api_key.strip())
            ok = await provider.is_available()
            await provider.close()
            return ok
        except Exception:
            return False


_provider_service: Optional[ProviderService] = None


def get_provider_service() -> ProviderService:
    """Liefert den globalen ProviderService."""
    global _provider_service
    if _provider_service is None:
        _provider_service = ProviderService()
    return _provider_service

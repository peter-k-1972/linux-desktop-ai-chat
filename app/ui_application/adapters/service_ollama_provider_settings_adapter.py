"""
Adapter: OllamaProviderSettingsPort → provider_service.
"""

from __future__ import annotations


class ServiceOllamaProviderSettingsAdapter:
    def get_ollama_api_key_from_env(self) -> str | None:
        from app.services.provider_service import get_provider_service

        return get_provider_service().get_ollama_api_key_from_env()

    async def validate_cloud_api_key(self, api_key: str) -> bool:
        from app.services.provider_service import get_provider_service

        return await get_provider_service().validate_cloud_api_key(api_key)

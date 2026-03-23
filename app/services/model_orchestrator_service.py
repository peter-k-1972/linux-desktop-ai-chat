"""
Singleton ModelOrchestrator mit gemeinsamem OllamaClient aus der Infrastructure.

Vermeidet parallele Provider-Pfade: Chat und GUI nutzen dieselbe lokale Session/URL.
"""

from __future__ import annotations

from typing import Optional

from app.core.models.orchestrator import ModelOrchestrator
from app.providers import CloudOllamaProvider, LocalOllamaProvider
from app.providers.cloud_ollama_provider import get_ollama_api_key

_orchestrator: Optional[ModelOrchestrator] = None


def get_model_orchestrator() -> ModelOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        from app.services.infrastructure import get_infrastructure

        infra = get_infrastructure()
        key = (infra.settings.ollama_api_key or "").strip() or get_ollama_api_key()
        local = LocalOllamaProvider(client=infra.ollama_client)
        cloud = CloudOllamaProvider(api_key=key)
        _orchestrator = ModelOrchestrator(local_provider=local, cloud_provider=cloud)
    return _orchestrator


def reset_model_orchestrator() -> None:
    """Tests / Infrastruktur-Reset: Orchestrator verwerfen (wird lazy neu erstellt)."""
    global _orchestrator
    _orchestrator = None

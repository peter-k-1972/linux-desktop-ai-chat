"""
Modell-Orchestrator: vereint Registry, Router, Eskalation und Provider.

Zentrale Anlaufstelle für die Chat-Logik.
"""

from typing import Any, AsyncGenerator, Dict, List, Optional, Set

from app.core.models.roles import ModelRole, get_default_model_for_role
from app.core.models.registry import ModelRegistry, get_registry, ModelEntry
from app.core.models.router import route_prompt
from app.core.models.escalation_manager import get_escalation_model
from app.core.models.provider_contracts import ChatProvider, CloudChatProvider


class _NullLocalProvider:
    provider_id = "local"
    source_type = "local"

    async def get_models(self) -> List[Dict[str, Any]]:
        return []

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        stream: bool = True,
        think: Any = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        yield {"error": "Kein lokaler Chat-Provider konfiguriert.", "done": True}

    async def close(self) -> None:
        return None


class _NullCloudProvider:
    provider_id = "ollama_cloud"
    source_type = "cloud"

    def __init__(self) -> None:
        self._api_key: Optional[str] = None

    def has_api_key(self) -> bool:
        return bool((self._api_key or "").strip())

    def set_api_key(self, key: str | None) -> None:
        self._api_key = (key or "").strip() or None

    async def get_models(self) -> List[Dict[str, Any]]:
        return []

    async def chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        stream: bool = True,
        think: Any = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        yield {"error": "Kein Cloud-Chat-Provider konfiguriert.", "done": True}

    async def close(self) -> None:
        return None


class ModelOrchestrator:
    """
    Orchestriert Modellauswahl, Provider und Chat-Aufrufe.
    """

    def __init__(
        self,
        local_provider: Optional[ChatProvider] = None,
        cloud_provider: Optional[CloudChatProvider] = None,
        registry: Optional[ModelRegistry] = None,
    ):
        self._local: ChatProvider = local_provider or _NullLocalProvider()
        self._cloud: CloudChatProvider = cloud_provider or _NullCloudProvider()
        self._registry = registry or get_registry()

        self._available_local: Set[str] = set()
        self._available_cloud: Set[str] = set()

    @property
    def local_provider(self) -> ChatProvider:
        return self._local

    @property
    def cloud_provider(self) -> CloudChatProvider:
        return self._cloud

    async def refresh_available_models(self) -> None:
        """Aktualisiert die Liste der verfügbaren Modelle von beiden Providern."""
        local_models = await self._local.get_models()
        self._available_local = {m.get("name", m.get("model", "")) for m in local_models}

        if self._cloud.has_api_key():
            try:
                cloud_models = await self._cloud.get_models()
                self._available_cloud = {m.get("name", m.get("model", "")) for m in cloud_models}
            except Exception:
                self._available_cloud = set()
        else:
            self._available_cloud = set()

    def get_provider_for_model(
        self, model_id: str, cloud_via_local: bool = False
    ) -> ChatProvider:
        """Liefert den passenden Provider für eine Modell-ID."""
        entry = self._registry.get(model_id)
        if entry and entry.source_type == "cloud":
            if cloud_via_local:
                return self._local
            return self._cloud
        return self._local

    @staticmethod
    def cloud_model_for_local(model_id: str) -> str:
        """Wandelt Cloud-Modell-ID in lokalen Modellnamen um (für ollama signin)."""
        if ":" in model_id:
            return f"{model_id}-cloud"
        return f"{model_id}:cloud"

    def resolve_model(
        self,
        role: ModelRole,
        *,
        force_model: Optional[str] = None,
        cloud_enabled: bool = False,
        cloud_via_local: bool = False,
    ) -> Optional[str]:
        """
        Löst eine Rolle auf ein konkretes Modell auf.

        Args:
            role: Gewünschte Rolle
            force_model: Wenn gesetzt, wird dieses Modell verwendet (falls verfügbar)
            cloud_enabled: Cloud-Modelle erlauben
            cloud_via_local: Cloud über lokales Ollama (ollama signin), kein API-Key nötig

        Returns:
            Modell-ID oder None
        """
        cloud_ok = self._cloud.has_api_key() or cloud_via_local
        if force_model:
            entry = self._registry.get(force_model)
            if entry and entry.enabled:
                if entry.source_type == "local":
                    return force_model
                if entry.source_type == "cloud" and cloud_enabled and cloud_ok:
                    return force_model
        return self._registry.get_best_model_for_role(
            role,
            available_local=self._available_local,
            available_cloud=self._available_cloud if cloud_enabled else None,
            prefer_local=True,
            cloud_enabled=cloud_enabled,
        )

    def select_model_for_prompt(
        self,
        prompt: str,
        *,
        current_role: Optional[ModelRole] = None,
        force_role: Optional[ModelRole] = None,
        force_model: Optional[str] = None,
        auto_routing: bool = True,
        cloud_enabled: bool = False,
        cloud_via_local: bool = False,
        overkill_mode: bool = False,
    ) -> tuple[ModelRole, Optional[str]]:
        """
        Wählt Rolle und Modell für einen Prompt.

        Returns:
            (role, model_id)
        """
        if overkill_mode:
            role = ModelRole.OVERKILL
        elif force_role is not None:
            role = force_role
        elif force_model:
            entry = self._registry.get(force_model)
            role = entry.role_candidates[0] if entry and entry.role_candidates else ModelRole.DEFAULT
        elif auto_routing:
            role = route_prompt(prompt)
        else:
            role = current_role or ModelRole.DEFAULT

        model_id = self.resolve_model(
            role,
            force_model=force_model,
            cloud_enabled=cloud_enabled,
            cloud_via_local=cloud_via_local,
        )
        return role, model_id

    async def stream_raw_chat(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        stream: bool = True,
        think: Any = None,
        cloud_via_local: bool = False,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Direkter Provider-Stream ohne Usage/Preflight (nur für Runtime-Instrumentierung)."""
        provider = self.get_provider_for_model(model_id, cloud_via_local=cloud_via_local)
        entry = self._registry.get(model_id)
        actual_model = model_id
        if cloud_via_local and entry and entry.source_type == "cloud":
            actual_model = self.cloud_model_for_local(model_id)
        async for chunk in provider.chat(
            model=actual_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            think=think,
        ):
            yield chunk

    async def chat(
        self,
        model_id: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 512,
        stream: bool = True,
        think: Any = None,
        cloud_via_local: bool = False,
        *,
        chat_id: Optional[int] = None,
        usage_type: str = "chat",
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Direkter Provider-Stream ohne Preflight/Usage (Legacy, Agents, Tests).

        Produktiver Chat-Pfad: :func:`app.services.chat_service.ChatService.chat` nutzt
        :func:`app.services.model_chat_runtime.stream_instrumented_model_chat`.
        ``chat_id`` / ``usage_type`` werden hier ignoriert (Signatur-Kompatibilität).
        """
        async for chunk in self.stream_raw_chat(
            model_id,
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            think=think,
            cloud_via_local=cloud_via_local,
        ):
            yield chunk

    def get_escalation_model(
        self,
        from_role: ModelRole,
        cloud_enabled: bool = False,
    ) -> Optional[str]:
        """Liefert das Modell für die nächste Eskalationsstufe."""
        return get_escalation_model(
            from_role,
            registry=self._registry,
            available_local=self._available_local,
            available_cloud=self._available_cloud,
            cloud_enabled=cloud_enabled,
        )

    async def close(self) -> None:
        """Schließt alle Provider."""
        await self._local.close()
        await self._cloud.close()

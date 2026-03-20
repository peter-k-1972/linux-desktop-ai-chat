"""
Modell-Registry für den Desktop-Chat.

Zentrale Konfiguration aller Modelle mit Metadaten für Routing,
Eskalation und Provider-Zuordnung.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set

from app.core.models.roles import ModelRole


@dataclass
class ModelEntry:
    """Metadaten eines Modells."""

    id: str
    display_name: str
    provider: str  # z.B. "local", "ollama_cloud"
    source_type: str  # "local" | "cloud"
    role_candidates: List[ModelRole] = field(default_factory=list)
    supports_chat: bool = True
    supports_code: bool = False
    supports_vision: bool = False
    supports_tools: bool = True
    priority: int = 0  # Höher = bevorzugt bei gleicher Rolle
    enabled: bool = True
    requires_api_key: bool = False
    context_hint: Optional[str] = None
    notes: Optional[str] = None

    def __post_init__(self):
        if not self.role_candidates:
            self.role_candidates = []


class ModelRegistry:
    """Zentrale Registry aller konfigurierten Modelle."""

    def __init__(self):
        self._models: Dict[str, ModelEntry] = {}
        self._role_to_models: Dict[ModelRole, List[str]] = {r: [] for r in ModelRole}
        self._load_defaults()

    def _load_defaults(self) -> None:
        """Lädt die Standard-Modellkonfiguration."""
        defaults = [
            ModelEntry(
                id="mistral:latest",
                display_name="Mistral",
                provider="local",
                source_type="local",
                role_candidates=[ModelRole.FAST, ModelRole.RESEARCH],
                supports_chat=True,
                supports_code=False,
                priority=10,
                context_hint="Schnell, Critic",
            ),
            ModelEntry(
                id="qwen2.5:latest",
                display_name="Qwen 2.5",
                provider="local",
                source_type="local",
                role_candidates=[ModelRole.DEFAULT, ModelRole.RESEARCH],
                supports_chat=True,
                supports_code=True,
                priority=10,
                context_hint="Allround, Planner",
            ),
            ModelEntry(
                id="llama3:latest",
                display_name="Llama 3",
                provider="local",
                source_type="local",
                role_candidates=[ModelRole.CHAT],
                supports_chat=True,
                supports_code=False,
                priority=10,
                context_hint="Natürlicher Dialog",
            ),
            ModelEntry(
                id="gpt-oss:latest",
                display_name="GPT-OSS",
                provider="local",
                source_type="local",
                role_candidates=[ModelRole.THINK, ModelRole.RESEARCH],
                supports_chat=True,
                supports_code=True,
                supports_tools=True,
                priority=10,
                context_hint="Analyse, Research",
            ),
            ModelEntry(
                id="qwen2.5-coder:7b",
                display_name="Qwen 2.5 Coder",
                provider="local",
                source_type="local",
                role_candidates=[ModelRole.CODE],
                supports_chat=True,
                supports_code=True,
                supports_tools=True,
                priority=10,
                context_hint="Code, Debugging",
            ),
            # Cloud-Modelle
            ModelEntry(
                id="gpt-oss:120b",
                display_name="GPT-OSS 120B",
                provider="ollama_cloud",
                source_type="cloud",
                role_candidates=[ModelRole.OVERKILL],
                supports_chat=True,
                supports_code=True,
                requires_api_key=True,
                priority=5,
                context_hint="Cloud-Eskalation",
            ),
            ModelEntry(
                id="qwen3.5",
                display_name="Qwen 3.5",
                provider="ollama_cloud",
                source_type="cloud",
                role_candidates=[ModelRole.OVERKILL, ModelRole.THINK],
                supports_chat=True,
                supports_code=True,
                requires_api_key=True,
                priority=5,
            ),
            ModelEntry(
                id="qwen3-coder",
                display_name="Qwen 3 Coder",
                provider="ollama_cloud",
                source_type="cloud",
                role_candidates=[ModelRole.CODE, ModelRole.OVERKILL],
                supports_chat=True,
                supports_code=True,
                requires_api_key=True,
                priority=5,
            ),
            ModelEntry(
                id="nemotron-3-super",
                display_name="Nemotron 3 Super",
                provider="ollama_cloud",
                source_type="cloud",
                role_candidates=[ModelRole.OVERKILL],
                supports_chat=True,
                supports_code=True,
                requires_api_key=True,
                priority=5,
            ),
            ModelEntry(
                id="qwen3-vl",
                display_name="Qwen 3 VL",
                provider="ollama_cloud",
                source_type="cloud",
                role_candidates=[ModelRole.VISION],
                supports_chat=True,
                supports_vision=True,
                requires_api_key=True,
                priority=5,
            ),
            ModelEntry(
                id="glm-5",
                display_name="GLM-5",
                provider="ollama_cloud",
                source_type="cloud",
                role_candidates=[ModelRole.OVERKILL, ModelRole.THINK],
                supports_chat=True,
                supports_code=True,
                requires_api_key=True,
                priority=5,
            ),
            ModelEntry(
                id="kimi-k2.5",
                display_name="Kimi K2.5",
                provider="ollama_cloud",
                source_type="cloud",
                role_candidates=[ModelRole.OVERKILL, ModelRole.THINK],
                supports_chat=True,
                supports_code=True,
                requires_api_key=True,
                priority=5,
            ),
        ]
        for entry in defaults:
            self.register(entry)

    def register(self, entry: ModelEntry) -> None:
        """Registriert ein Modell."""
        self._models[entry.id] = entry
        for role in entry.role_candidates:
            if entry.id not in self._role_to_models[role]:
                self._role_to_models[role].append(entry.id)

    def get(self, model_id: str) -> Optional[ModelEntry]:
        """Liefert den Eintrag für eine Modell-ID."""
        return self._models.get(model_id)

    def get_models_for_role(
        self, role: ModelRole, local_only: bool = False, cloud_only: bool = False
    ) -> List[ModelEntry]:
        """Liefert alle Modelle, die für eine Rolle geeignet sind."""
        model_ids = self._role_to_models.get(role, [])
        result = []
        for mid in model_ids:
            entry = self._models.get(mid)
            if not entry or not entry.enabled:
                continue
            if local_only and entry.source_type != "local":
                continue
            if cloud_only and entry.source_type != "cloud":
                continue
            result.append(entry)
        result.sort(key=lambda e: (-e.priority, e.display_name))
        return result

    def get_best_model_for_role(
        self,
        role: ModelRole,
        available_local: Optional[Set[str]] = None,
        available_cloud: Optional[Set[str]] = None,
        prefer_local: bool = True,
        cloud_enabled: bool = False,
    ) -> Optional[str]:
        """
        Wählt das beste verfügbare Modell für eine Rolle.

        - available_local: Set der lokal verfügbaren Modell-IDs (z.B. aus Ollama)
        - available_cloud: Set der Cloud-verfügbaren Modell-IDs (falls bekannt)
        - prefer_local: Lokale Modelle bevorzugen
        - cloud_enabled: Cloud-Eskalation erlaubt
        """
        candidates = self.get_models_for_role(role)
        for entry in candidates:
            if entry.source_type == "local":
                if available_local is None or entry.id in available_local:
                    return entry.id
            else:
                if not cloud_enabled:
                    continue
                if entry.requires_api_key and (available_cloud is None or entry.id in available_cloud):
                    return entry.id
                if not entry.requires_api_key or available_cloud is None:
                    return entry.id
        return None

    def list_all(self) -> List[ModelEntry]:
        """Liefert alle registrierten Modelle."""
        return list(self._models.values())

    def list_local(self) -> List[ModelEntry]:
        """Liefert alle lokalen Modelle."""
        return [e for e in self._models.values() if e.source_type == "local" and e.enabled]

    def list_cloud(self) -> List[ModelEntry]:
        """Liefert alle Cloud-Modelle."""
        return [e for e in self._models.values() if e.source_type == "cloud" and e.enabled]


# Singleton für App-weite Nutzung
_registry: Optional[ModelRegistry] = None


def get_registry() -> ModelRegistry:
    """Liefert die globale Modell-Registry."""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry

"""Registry für Pipeline-Definitionen."""

from typing import Dict, List, Optional

from app.pipelines.models import PipelineDefinition


class PipelineDefinitionRegistry:
    """
    Registry für Pipeline-Definitionen.

    In-Memory. Erweiterbar für Datei-/Projekt-basierte Definitionen.
    """

    def __init__(self) -> None:
        self._definitions: Dict[str, PipelineDefinition] = {}

    def register(self, definition: PipelineDefinition) -> None:
        """Registriert eine Pipeline-Definition."""
        self._definitions[definition.pipeline_id] = definition

    def get(self, pipeline_id: str) -> Optional[PipelineDefinition]:
        """Liefert eine Definition oder None."""
        return self._definitions.get(pipeline_id)

    def list_ids(self) -> List[str]:
        """Listet alle registrierten Pipeline-IDs."""
        return list(self._definitions.keys())


_default_registry: Optional[PipelineDefinitionRegistry] = None


def get_definition_registry() -> PipelineDefinitionRegistry:
    """Singleton-Zugriff auf die Definition-Registry."""
    global _default_registry
    if _default_registry is None:
        _default_registry = PipelineDefinitionRegistry()
    return _default_registry

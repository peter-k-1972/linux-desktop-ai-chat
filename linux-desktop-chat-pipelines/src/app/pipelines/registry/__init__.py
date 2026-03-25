"""
Pipeline-Registry – Registrierung von Pipeline-Definitionen.

Erweiterbar für spätere Definition-Loader (z.B. aus Projekt, Datei).
"""

from app.pipelines.registry.definition_registry import (
    PipelineDefinitionRegistry,
    get_definition_registry,
)

__all__ = [
    "PipelineDefinitionRegistry",
    "get_definition_registry",
]

"""
PipelineService – Service-Schicht für Pipeline-Operationen.

Delegiert an app.pipelines.services.
GUI und andere Schichten nutzen get_pipeline_service().
"""

from typing import Optional

from app.pipelines import PipelineDefinition, PipelineRun, PipelineService as _PipelineService


_pipeline_service: Optional[_PipelineService] = None


def get_pipeline_service() -> _PipelineService:
    """Liefert den PipelineService (Singleton)."""
    global _pipeline_service
    if _pipeline_service is None:
        _pipeline_service = _PipelineService()
    return _pipeline_service


def set_pipeline_service(service: Optional[_PipelineService]) -> None:
    """Setzt den PipelineService (für Tests)."""
    global _pipeline_service
    _pipeline_service = service

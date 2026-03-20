"""
Pipeline Engine – generische Ausführung von Medien- und Kreativpipelines.

Kernmodul für:
- Pipeline-Definition und -Ausführung
- Step-Executor-Abstraktion (Shell, Python, ComfyUI, Media)
- Statusführung, Logs, Artefakte

Nicht ComfyUI-spezifisch. Erweiterbar für Voice, Musik, Subtitles, Merge.
"""

from app.pipelines.models import (
    PipelineDefinition,
    PipelineStepDefinition,
    PipelineRun,
    PipelineStepRun,
    PipelineArtifact,
    PipelineStatus,
    StepStatus,
)

__all__ = [
    "PipelineDefinition",
    "PipelineStepDefinition",
    "PipelineRun",
    "PipelineStepRun",
    "PipelineArtifact",
    "PipelineStatus",
    "StepStatus",
]

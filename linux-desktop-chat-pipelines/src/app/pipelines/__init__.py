"""
Pipeline Engine – generische Ausführung von Medien- und Kreativpipelines.

Kernmodul für:
- Pipeline-Definition und -Ausführung
- Step-Executor-Abstraktion (Shell, Python, ComfyUI, Media)
- Statusführung, Logs, Artefakte

Nicht ComfyUI-spezifisch. Erweiterbar für Voice, Musik, Subtitles, Merge.

Öffentliche API: Paket-Root (dieses Modul) **oder** genau eine der Submodulebenen
``app.pipelines.models``, ``.engine``, ``.services``, ``.executors``, ``.registry``.
Keine Imports aus tieferen Pfaden (z. B. ``app.pipelines.engine.engine``) außerhalb
der Paket-Implementierung — siehe ``tests/architecture/test_pipelines_public_surface_guard.py``.
"""

from app.pipelines.engine import PipelineEngine
from app.pipelines.executors import (
    ExecutorRegistry,
    PlaceholderComfyUIExecutor,
    PlaceholderMediaExecutor,
    PythonCallableExecutor,
    ShellExecutor,
    StepExecutor,
    StepResult,
    get_executor_registry,
)
from app.pipelines.models import (
    PipelineArtifact,
    PipelineDefinition,
    PipelineRun,
    PipelineStatus,
    PipelineStepDefinition,
    PipelineStepRun,
    StepStatus,
)
from app.pipelines.registry import (
    PipelineDefinitionRegistry,
    get_definition_registry,
)
from app.pipelines.services import PipelineService

__all__ = [
    # models
    "PipelineDefinition",
    "PipelineStepDefinition",
    "PipelineRun",
    "PipelineStepRun",
    "PipelineArtifact",
    "PipelineStatus",
    "StepStatus",
    # engine
    "PipelineEngine",
    # service
    "PipelineService",
    # executors
    "StepExecutor",
    "StepResult",
    "ExecutorRegistry",
    "get_executor_registry",
    "ShellExecutor",
    "PythonCallableExecutor",
    "PlaceholderComfyUIExecutor",
    "PlaceholderMediaExecutor",
    # definition registry
    "PipelineDefinitionRegistry",
    "get_definition_registry",
]

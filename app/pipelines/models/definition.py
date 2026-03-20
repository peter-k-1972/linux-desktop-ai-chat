"""Pipeline-Definition und Step-Definition."""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class PipelineStepDefinition:
    """
    Definition eines einzelnen Pipeline-Schritts.

    - step_id: Eindeutige ID innerhalb der Pipeline
    - executor_type: Typ des Executors (shell, python_callable, comfyui, media, …)
    - config: Executor-spezifische Konfiguration
    - name: Optionale Lesbarkeit
    """

    step_id: str
    executor_type: str
    config: Dict[str, Any] = field(default_factory=dict)
    name: str = ""

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.step_id


@dataclass
class PipelineDefinition:
    """
    Definition einer Pipeline.

    - pipeline_id: Eindeutige ID
    - steps: Geordnete Liste der Schritte (sequentielle Ausführung)
    - name: Optionale Lesbarkeit
    - metadata: Zusätzliche Metadaten
    """

    pipeline_id: str
    steps: List[PipelineStepDefinition]
    name: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            self.name = self.pipeline_id

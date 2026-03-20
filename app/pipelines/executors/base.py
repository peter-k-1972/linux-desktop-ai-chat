"""Step-Executor-Basis und StepResult."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.pipelines.models import PipelineArtifact


@dataclass
class StepResult:
    """
    Ergebnis der Ausführung eines Pipeline-Schritts.

    - success: True wenn erfolgreich
    - error: Fehlermeldung bei Fehler
    - logs: Log-Zeilen
    - artifacts: Erzeugte Artefakte
    - output: Zusätzliche Ausgabedaten
    """

    success: bool
    error: Optional[str] = None
    logs: List[str] = field(default_factory=list)
    artifacts: List[PipelineArtifact] = field(default_factory=list)
    output: Dict[str, Any] = field(default_factory=dict)


class StepExecutor(ABC):
    """
    Interface für die Ausführung eines Pipeline-Schritts.

    Die Engine kennt nur dieses Interface, nicht die konkreten Executor-Typen.
    """

    @abstractmethod
    def execute(
        self,
        step_id: str,
        config: Dict[str, Any],
        context: Dict[str, Any],
    ) -> StepResult:
        """
        Führt den Schritt aus.

        Args:
            step_id: ID des Schritts
            config: Executor-spezifische Konfiguration aus der Step-Definition
            context: Kontext (z.B. Artefakte vorheriger Schritte, Run-Metadaten)

        Returns:
            StepResult mit Erfolg/Fehler, Logs, Artefakten
        """
        ...

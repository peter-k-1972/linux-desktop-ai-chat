"""Pipeline-Run, Step-Run und Artefakte."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.pipelines.models.status import PipelineStatus, StepStatus


@dataclass
class PipelineArtifact:
    """
    Ein von einem Pipeline-Schritt erzeugtes Artefakt.

    - step_id: ID des erzeugenden Schritts
    - key: Eindeutiger Schlüssel (z.B. output_path)
    - value: Wert (z.B. Dateipfad, URL)
    - artifact_type: Typ (file, url, json, …)
    """

    step_id: str
    key: str
    value: Any
    artifact_type: str = "file"


@dataclass
class PipelineStepRun:
    """
    Laufzeit-Instanz eines Pipeline-Schritts.

    - step_id: ID aus der Definition
    - status: Aktueller Status
    - started_at / completed_at: Zeitstempel
    - logs: Sammelnde Log-Zeilen
    - error: Fehlermeldung bei Fehler
    - artifacts: Erzeugte Artefakte
    """

    step_id: str
    status: StepStatus = StepStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    logs: List[str] = field(default_factory=list)
    error: Optional[str] = None
    artifacts: List[PipelineArtifact] = field(default_factory=list)

    def add_log(self, line: str) -> None:
        self.logs.append(line)

    def add_artifact(self, artifact: PipelineArtifact) -> None:
        self.artifacts.append(artifact)


@dataclass
class PipelineRun:
    """
    Laufzeit-Instanz einer Pipeline-Ausführung.

    - run_id: Eindeutige ID
    - pipeline_id: ID der zugrunde liegenden Definition
    - status: Gesamtstatus
    - step_runs: Geordnete Step-Runs
    - started_at / completed_at: Zeitstempel
    - logs: Aggregierte Logs (optional)
    - error: Fehlermeldung bei Fehler
    - metadata: Zusätzliche Metadaten
    """

    run_id: str
    pipeline_id: str
    status: PipelineStatus = PipelineStatus.PENDING
    step_runs: List[PipelineStepRun] = field(default_factory=list)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    logs: List[str] = field(default_factory=list)
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_log(self, line: str) -> None:
        self.logs.append(line)

    def get_step_run(self, step_id: str) -> Optional[PipelineStepRun]:
        for sr in self.step_runs:
            if sr.step_id == step_id:
                return sr
        return None

    def get_all_artifacts(self) -> List[PipelineArtifact]:
        result: List[PipelineArtifact] = []
        for sr in self.step_runs:
            result.extend(sr.artifacts)
        return result

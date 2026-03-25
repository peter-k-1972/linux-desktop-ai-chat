"""
PipelineService – zentraler Zugriffspunkt für Pipeline-Operationen.

- create_run: Run aus Definition erstellen
- start_run: Run starten (synchron)
- get_run: Run abrufen
- list_runs: Runs auflisten

In-Memory-Speicherung. Keine Persistenz in Phase 1.
"""

from typing import Dict, List, Optional

from app.pipelines.models import PipelineDefinition, PipelineRun, PipelineStatus
from app.pipelines.engine import PipelineEngine


class PipelineService:
    """
    Service für Pipeline-Operationen.

    Delegiert an PipelineEngine.
    Speichert Runs in-memory (Phase 1).
    """

    def __init__(self, engine: Optional[PipelineEngine] = None) -> None:
        self._engine = engine or PipelineEngine()
        self._runs: Dict[str, PipelineRun] = {}
        self._definitions: Dict[str, PipelineDefinition] = {}

    def register_definition(self, definition: PipelineDefinition) -> None:
        """Registriert eine Pipeline-Definition für spätere Verwendung."""
        self._definitions[definition.pipeline_id] = definition

    def get_definition(self, pipeline_id: str) -> Optional[PipelineDefinition]:
        """Liefert eine registrierte Definition oder None."""
        return self._definitions.get(pipeline_id)

    def create_run(
        self,
        definition: PipelineDefinition,
        run_id: Optional[str] = None,
    ) -> PipelineRun:
        """
        Erstellt einen neuen Run aus der Definition.

        Der Run wird gespeichert und ist PENDING.
        """
        run = self._engine.create_run(definition, run_id=run_id)
        self._runs[run.run_id] = run
        return run

    def start_run(
        self,
        run: PipelineRun,
        definition: Optional[PipelineDefinition] = None,
        context: Optional[dict] = None,
    ) -> PipelineRun:
        """
        Startet die Ausführung eines Runs.

        Falls definition nicht übergeben wird, wird sie aus der Registrierung geladen.
        """
        if definition is None:
            definition = self._definitions.get(run.pipeline_id)
        if definition is None:
            run.status = PipelineStatus.FAILED
            run.error = f"Unknown pipeline_id: {run.pipeline_id}"
            return run

        self._engine.execute(definition, run, context)
        return run

    def get_run(self, run_id: str) -> Optional[PipelineRun]:
        """Liefert einen Run nach ID oder None."""
        return self._runs.get(run_id)

    def list_runs(
        self,
        pipeline_id: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[PipelineRun]:
        """
        Listet Runs auf.

        Optional gefiltert nach pipeline_id und/oder status.
        """
        result = list(self._runs.values())
        if pipeline_id:
            result = [r for r in result if r.pipeline_id == pipeline_id]
        if status:
            result = [r for r in result if r.status.value == status]
        return sorted(result, key=lambda r: (r.started_at or r.run_id), reverse=True)

    def cancel_run(self, run_id: str) -> bool:
        """Fordert Abbruch eines laufenden Runs an. Gibt True zurück wenn Run existiert."""
        run = self._runs.get(run_id)
        if run is None:
            return False
        self._engine.cancel()
        return True

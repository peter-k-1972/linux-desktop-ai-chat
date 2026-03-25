"""
Pipeline Engine – sequentielle Ausführung von Pipeline-Definitionen.

- Nimmt PipelineDefinition entgegen
- Führt Schritte sequentiell aus
- Aktualisiert Status, sammelt Logs, erfasst Fehler
- Registriert Artefakte
- Unterstützt Abbruch und Fehlerbehandlung
"""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional

from app.pipelines.models import (
    PipelineDefinition,
    PipelineRun,
    PipelineStepRun,
    PipelineArtifact,
    PipelineStatus,
    StepStatus,
)
from app.pipelines.executors.registry import ExecutorRegistry, get_executor_registry

logger = logging.getLogger(__name__)


class PipelineEngine:
    """
    Generische Pipeline-Engine.

    Führt PipelineDefinition sequentiell aus.
    Nutzt ExecutorRegistry zur Auflösung der Executor-Typen.
    """

    def __init__(
        self,
        executor_registry: Optional[ExecutorRegistry] = None,
        run_id_factory: Optional[Callable[[], str]] = None,
    ) -> None:
        self._registry = executor_registry or get_executor_registry()
        self._run_id_factory = run_id_factory or (lambda: f"run_{uuid.uuid4().hex[:12]}")
        self._cancelled: bool = False

    def create_run(
        self,
        definition: PipelineDefinition,
        run_id: Optional[str] = None,
    ) -> PipelineRun:
        """
        Erstellt einen neuen PipelineRun aus der Definition.

        Der Run ist noch nicht gestartet (PENDING).
        """
        run_id = run_id or self._run_id_factory()
        step_runs = [
            PipelineStepRun(step_id=step.step_id, status=StepStatus.PENDING)
            for step in definition.steps
        ]
        return PipelineRun(
            run_id=run_id,
            pipeline_id=definition.pipeline_id,
            status=PipelineStatus.PENDING,
            step_runs=step_runs,
            metadata=definition.metadata.copy(),
        )

    def execute(
        self,
        definition: PipelineDefinition,
        run: PipelineRun,
        context: Optional[Dict[str, Any]] = None,
    ) -> PipelineRun:
        """
        Führt die Pipeline aus.

        Modifiziert run in-place (Status, Logs, Artefakte).
        Bei Fehler oder Abbruch wird gestoppt.

        Args:
            definition: Pipeline-Definition
            run: Bereits erstellter Run (von create_run)
            context: Zusätzlicher Kontext für Executors

        Returns:
            run (modifiziert)
        """
        self._cancelled = False
        ctx = dict(context or {})

        run.status = PipelineStatus.RUNNING
        run.started_at = datetime.now(timezone.utc)
        run.add_log(f"Pipeline {definition.pipeline_id} started (run_id={run.run_id})")

        for step_def in definition.steps:
            if self._cancelled:
                run.status = PipelineStatus.CANCELLED
                run.add_log("Pipeline cancelled by request")
                run.completed_at = datetime.now(timezone.utc)
                return run

            step_run = run.get_step_run(step_def.step_id)
            if not step_run:
                run.add_log(f"Warning: step {step_def.step_id} not in run, skipping")
                continue

            executor = self._registry.get(step_def.executor_type)
            if not executor:
                run.status = PipelineStatus.FAILED
                run.error = f"Unknown executor type: {step_def.executor_type}"
                run.add_log(run.error)
                run.completed_at = datetime.now(timezone.utc)
                return run

            step_run.status = StepStatus.RUNNING
            step_run.started_at = datetime.now(timezone.utc)
            run.add_log(f"Step {step_def.step_id} started")

            exec_ctx = {
                "run_id": run.run_id,
                "pipeline_id": definition.pipeline_id,
                "artifacts": {a.key: a.value for a in run.get_all_artifacts()},
                **ctx,
            }

            try:
                result = executor.execute(
                    step_id=step_def.step_id,
                    config=step_def.config,
                    context=exec_ctx,
                )
            except Exception as e:
                step_run.status = StepStatus.FAILED
                step_run.error = str(e)
                step_run.completed_at = datetime.now(timezone.utc)
                step_run.add_log(str(e))
                run.status = PipelineStatus.FAILED
                run.error = str(e)
                run.add_log(f"Step {step_def.step_id} failed: {e}")
                run.completed_at = datetime.now(timezone.utc)
                return run

            for log_line in result.logs:
                step_run.add_log(log_line)
                run.add_log(f"[{step_def.step_id}] {log_line}")

            if not result.success:
                step_run.status = StepStatus.FAILED
                step_run.error = result.error
                step_run.completed_at = datetime.now(timezone.utc)
                run.status = PipelineStatus.FAILED
                run.error = result.error
                run.add_log(f"Step {step_def.step_id} failed: {result.error}")
                run.completed_at = datetime.now(timezone.utc)
                return run

            step_run.status = StepStatus.COMPLETED
            step_run.completed_at = datetime.now(timezone.utc)
            for art in result.artifacts:
                step_run.add_artifact(art)
            run.add_log(f"Step {step_def.step_id} completed")

        run.status = PipelineStatus.COMPLETED
        run.completed_at = datetime.now(timezone.utc)
        run.add_log(f"Pipeline {definition.pipeline_id} completed")
        return run

    def cancel(self) -> None:
        """Markiert die laufende Ausführung zum Abbruch."""
        self._cancelled = True

"""
WorkflowService – Fassade für Validierung, Persistenz und Ausführung.

Keine Qt-/GUI-Abhängigkeit. Konsumiert ausschließlich app.workflows.
"""

from __future__ import annotations

import copy
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from app.workflows.execution.context import AbortToken
from app.workflows.execution.executor import WorkflowExecutor
from app.workflows.models.definition import WorkflowDefinition
from app.workflows.models.run import NodeRun, WorkflowRun
from app.workflows.models.run_summary import WorkflowRunSummary
from app.workflows.persistence.workflow_repository import WorkflowRepository
from app.workflows.registry.node_registry import NodeRegistry, build_default_node_registry
from app.workflows.status import NodeRunStatus, WorkflowDefinitionStatus, WorkflowRunStatus
from app.workflows.validation.graph_validator import GraphValidator, ValidationResult

if TYPE_CHECKING:
    from app.services.audit_service import AuditService
    from app.services.incident_service import IncidentService


class WorkflowValidationError(Exception):
    """Workflow ist nicht ausführbar (Validierungsfehler)."""

    def __init__(self, errors: List[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


class WorkflowNotFoundError(Exception):
    """Unbekannte workflow_id."""


class RunNotFoundError(Exception):
    """Unbekannte run_id."""


class IncompleteHistoricalRunError(Exception):
    """Historischer Run ist für Re-Run nicht verwendbar (z. B. fehlende workflow_id)."""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WorkflowService:
    """CRUD, Validierung und synchrone Ausführung (Phase 1–2)."""

    def __init__(
        self,
        repository: WorkflowRepository,
        registry: Optional[NodeRegistry] = None,
        executor: Optional[WorkflowExecutor] = None,
        run_id_factory: Optional[Callable[[], str]] = None,
        audit_service: Optional["AuditService"] = None,
        incident_service: Optional["IncidentService"] = None,
    ) -> None:
        self._repo = repository
        self._registry = registry or build_default_node_registry()
        self._executor = executor or WorkflowExecutor()
        self._run_id_factory = run_id_factory or (lambda: f"wr_{uuid.uuid4().hex[:12]}")
        self._validator = GraphValidator()
        self._active_aborts: Dict[str, AbortToken] = {}
        self._audit = audit_service
        self._incident = incident_service

    def validate_workflow(self, definition: WorkflowDefinition) -> ValidationResult:
        """Struktur- und Graphprüfung inkl. Registry."""
        return self._validator.validate(definition, self._registry)

    def save_workflow(self, definition: WorkflowDefinition) -> ValidationResult:
        """
        Validiert, setzt status auf VALID/INVALID und persistiert die Definition.
        """
        vr = self.validate_workflow(definition)
        definition.status = WorkflowDefinitionStatus.VALID if vr.is_valid else WorkflowDefinitionStatus.INVALID
        definition.updated_at = _utc_now()
        self._repo.save_workflow(definition)
        return vr

    def load_workflow(self, workflow_id: str) -> WorkflowDefinition:
        w = self._repo.load_workflow(workflow_id)
        if w is None:
            raise WorkflowNotFoundError(workflow_id)
        return w

    def list_workflows(
        self,
        *,
        project_scope_id: Optional[int] = None,
        include_global: bool = True,
    ) -> List[WorkflowDefinition]:
        """
        Workflows auflisten.

        project_scope_id None: alle Einträge.
        Mit gesetzter ID: Standard inkl. globaler Workflows (project_id IS NULL).
        """
        return self._repo.list_workflows(
            project_scope_id=project_scope_id,
            include_global=include_global,
        )

    def delete_workflow(self, workflow_id: str) -> bool:
        return self._repo.delete_workflow(workflow_id)

    def duplicate_workflow(
        self,
        source_id: str,
        new_workflow_id: str,
        new_name: Optional[str] = None,
    ) -> WorkflowDefinition:
        """Kopiert eine Definition unter neuer ID (Version 1, neue Zeitstempel)."""
        new_id = (new_workflow_id or "").strip()
        if not new_id:
            raise ValueError("new_workflow_id darf nicht leer sein.")
        src = self.load_workflow(source_id)
        data = copy.deepcopy(src.to_dict())
        data["workflow_id"] = new_id
        data["version"] = 1
        nm = (new_name or f"{src.name} (Kopie)").strip()
        data["name"] = nm or new_id
        now = _utc_now()
        data["created_at"] = now.isoformat()
        data["updated_at"] = now.isoformat()
        dup = WorkflowDefinition.from_dict(data)
        self.save_workflow(dup)
        return self.load_workflow(new_id)

    def start_run(
        self,
        workflow_id: str,
        initial_input: Optional[Dict[str, Any]] = None,
        *,
        is_rerun: bool = False,
    ) -> WorkflowRun:
        definition = self.load_workflow(workflow_id)
        vr = self.validate_workflow(definition)
        if not vr.is_valid:
            raise WorkflowValidationError(vr.errors)

        run_id = self._run_id_factory()
        snap = definition.to_dict()
        run = WorkflowRun(
            run_id=run_id,
            workflow_id=definition.workflow_id,
            workflow_version=definition.version,
            status=WorkflowRunStatus.PENDING,
            initial_input=copy.deepcopy(dict(initial_input or {})),
            definition_snapshot=snap,
        )
        self._repo.save_run(run)
        if self._audit is not None:
            self._audit.record_workflow_started(
                run_id=run.run_id,
                workflow_id=definition.workflow_id,
                project_id=definition.project_id,
                is_rerun=is_rerun,
            )

        abort = AbortToken()
        self._active_aborts[run_id] = abort

        def on_after_node(r: WorkflowRun, nr: NodeRun) -> None:
            if nr.status == NodeRunStatus.RUNNING and nr.finished_at is None:
                self._repo.save_node_run(nr)
            else:
                self._repo.update_node_run(nr)

        try:
            self._executor.execute(definition, run, self._registry, abort, on_after_node=on_after_node)
        finally:
            self._active_aborts.pop(run_id, None)
            self._repo.update_run(run)
            if run.status == WorkflowRunStatus.FAILED and self._incident is not None:
                self._incident.sync_from_failed_run(run)

        return run

    def start_run_from_previous(
        self,
        run_id: str,
        initial_input_override: Optional[Dict[str, Any]] = None,
    ) -> WorkflowRun:
        """
        Startet einen neuen Lauf mit derselben ``workflow_id`` und den Eingaben des
        angegebenen historischen Laufs (optional überschreibbar).

        Der bestehende Lauf wird nicht verändert.
        """
        prev = self.get_run(run_id)
        wid = (prev.workflow_id or "").strip()
        if not wid:
            raise IncompleteHistoricalRunError(
                f"Run {run_id!r} hat keine gültige workflow_id und kann nicht erneut gestartet werden."
            )
        if initial_input_override is not None:
            inp = copy.deepcopy(dict(initial_input_override))
        else:
            inp = copy.deepcopy(dict(prev.initial_input or {}))
        return self.start_run(wid, inp, is_rerun=True)

    def cancel_run(self, run_id: str) -> bool:
        token = self._active_aborts.get(run_id)
        if token is not None:
            token.cancel()
            return True
        run = self._repo.get_run(run_id)
        if run is None:
            raise RunNotFoundError(run_id)
        if run.status == WorkflowRunStatus.PENDING:
            run.status = WorkflowRunStatus.CANCELLED
            run.finished_at = _utc_now()
            self._repo.update_run(run)
            return True
        return False

    def get_run(self, run_id: str) -> WorkflowRun:
        r = self._repo.get_run(run_id)
        if r is None:
            raise RunNotFoundError(run_id)
        return r

    def list_runs(self, workflow_id: Optional[str] = None) -> List[WorkflowRun]:
        return self._repo.list_runs(workflow_id=workflow_id)

    def list_run_summaries(
        self,
        *,
        workflow_id: Optional[str] = None,
        project_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0,
    ) -> List[WorkflowRunSummary]:
        """
        Schlankes Run-Listing ohne NodeRuns (O1).

        ``limit`` None → internes Cap (2000) gegen große Tabellen; für Tests explizit setzen.
        """
        cap = 2000 if limit is None else int(limit)
        return self._repo.list_run_summaries(
            workflow_id=workflow_id,
            project_id=project_id,
            status=status,
            limit=cap,
            offset=int(offset),
        )

    def get_project_workflow_monitoring_snapshot(self, project_id: int) -> Dict[str, Any]:
        """Aggregierte Run-Kennzahlen nur für Workflows mit gesetzter ``project_id``."""
        return self._repo.aggregate_project_workflow_runs(project_id)

    def list_node_runs(self, run_id: str) -> List[NodeRun]:
        """Alle NodeRuns eines Laufs (Persistenz über Repository; keine GUI-Logik)."""
        return self._repo.list_node_runs(run_id)

    def get_run_with_node_runs(self, run_id: str) -> WorkflowRun:
        """Lauf inkl. aktueller NodeRuns – entspricht get_run (Repository lädt node_runs mit)."""
        return self.get_run(run_id)


_workflow_service: Optional[WorkflowService] = None


def get_workflow_service() -> WorkflowService:
    """Singleton an die App-Datenbank gebunden (nach init_infrastructure)."""
    global _workflow_service
    if _workflow_service is None:
        from app.services.audit_service import get_audit_service
        from app.services.incident_service import get_incident_service
        from app.services.infrastructure import get_infrastructure

        db = get_infrastructure().database
        _workflow_service = WorkflowService(
            WorkflowRepository(db.db_path),
            audit_service=get_audit_service(),
            incident_service=get_incident_service(),
        )
    return _workflow_service


def reset_workflow_service() -> None:
    """Setzt die Fassade zurück (Tests)."""
    global _workflow_service
    _workflow_service = None
    from app.services.audit_service import reset_audit_service
    from app.services.incident_service import reset_incident_service

    reset_audit_service()
    reset_incident_service()

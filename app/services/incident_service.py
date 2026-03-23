"""IncidentService — Störungen aus terminal FAILED WorkflowRuns (R1)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from app.core.audit.fingerprint import compute_incident_fingerprint, diagnostic_code_for_run
from app.core.audit.models import IncidentRecord, IncidentSeverity, IncidentStatus
from app.core.audit.repository import AuditRepository
from app.services.audit_service import AuditService
from app.workflows.diagnostics import summarize_workflow_run
from app.workflows.models.run import WorkflowRun
from app.workflows.status import WorkflowRunStatus


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class IncidentService:
    def __init__(self, repository: AuditRepository, audit_service: AuditService) -> None:
        self._repo = repository
        self._audit = audit_service

    def sync_from_failed_run(self, run: WorkflowRun) -> Optional[int]:
        """
        Erzeugt oder aktualisiert ein Incident für einen terminal FAILED Run.
        Keine Op bei anderen Status. Audit nur bei neuem Incident (nicht bei Wiederholung).
        """
        if run.status != WorkflowRunStatus.FAILED:
            return None
        fp = compute_incident_fingerprint(run)
        diag = summarize_workflow_run(run)
        title = diag.headline
        short_description = diag.summary or (diag.failed_node_error_short or "") or (diag.run_error or "") or "Workflow fehlgeschlagen."
        dcode = diagnostic_code_for_run(run)
        now = _utc_iso()
        wid = (run.workflow_id or "").strip()
        raw_pid = run.definition_snapshot.get("project_id")
        project_id: Optional[int]
        if raw_pid is not None:
            try:
                project_id = int(raw_pid)
            except (TypeError, ValueError):
                project_id = None
        else:
            project_id = None

        existing = self._repo.get_incident_by_fingerprint(fp)
        if existing is None:
            rec = IncidentRecord(
                id=None,
                status=IncidentStatus.OPEN,
                severity=IncidentSeverity.MEDIUM,
                title=title[:500],
                short_description=short_description[:2000],
                workflow_run_id=run.run_id,
                workflow_id=wid,
                project_id=project_id,
                first_seen_at=now,
                last_seen_at=now,
                occurrence_count=1,
                fingerprint=fp,
                diagnostic_code=dcode,
                resolution_note=None,
                created_at=now,
                updated_at=now,
            )
            new_id = self._repo.insert_incident(rec)
            self._audit.record_incident_created(incident_id=new_id, fingerprint=fp, run_id=run.run_id)
            return new_id

        self._repo.update_incident_recurrence(
            fp,
            workflow_run_id=run.run_id,
            last_seen_at=now,
            updated_at=now,
            short_description=short_description[:2000],
        )
        return existing.id

    def list_incidents(
        self,
        *,
        status: Optional[str] = None,
        project_id: Optional[int] = None,
        limit: int = 500,
        offset: int = 0,
    ) -> List[IncidentRecord]:
        return self._repo.list_incidents(status=status, project_id=project_id, limit=limit, offset=offset)

    def get_incident(self, incident_id: int) -> Optional[IncidentRecord]:
        return self._repo.get_incident(incident_id)

    def set_status(
        self,
        incident_id: int,
        new_status: str,
        *,
        resolution_note: Optional[str] = None,
    ) -> None:
        cur = self._repo.get_incident(incident_id)
        if cur is None:
            raise ValueError(f"Unbekanntes Incident: {incident_id}")
        old = cur.status
        note = cur.resolution_note
        if resolution_note is not None:
            note = resolution_note
        if old == new_status and note == cur.resolution_note:
            return
        now = _utc_iso()
        self._repo.update_incident_status(incident_id, status=new_status, resolution_note=note, updated_at=now)
        if old != new_status:
            self._audit.record_incident_status_changed(
                incident_id=incident_id,
                old_status=old,
                new_status=new_status,
                project_id=cur.project_id,
                workflow_id=cur.workflow_id,
                run_id=cur.workflow_run_id,
            )


_incident_service: Optional[IncidentService] = None


def get_incident_service() -> IncidentService:
    global _incident_service
    if _incident_service is None:
        from app.services.infrastructure import get_infrastructure

        from app.services.audit_service import get_audit_service

        db_path = get_infrastructure().database.db_path
        repo = AuditRepository(db_path)
        _incident_service = IncidentService(repo, get_audit_service())
    return _incident_service


def reset_incident_service() -> None:
    global _incident_service
    _incident_service = None

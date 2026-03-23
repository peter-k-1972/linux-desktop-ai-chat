"""AuditService — append-only Aktivitätsprotokoll (R1)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.core.audit.models import AuditEventRecord, AuditEventType
from app.core.audit.repository import AuditRepository


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self._repo = repository

    def record_workflow_started(
        self,
        *,
        run_id: str,
        workflow_id: str,
        project_id: Optional[int],
        is_rerun: bool,
    ) -> None:
        et = AuditEventType.WORKFLOW_RERUN_STARTED if is_rerun else AuditEventType.WORKFLOW_STARTED
        label = "Workflow Re-Run gestartet" if is_rerun else "Workflow gestartet"
        self._repo.append_audit_event(
            event_type=et,
            summary=f"{label}: {workflow_id} → Run {run_id}",
            project_id=project_id,
            workflow_id=workflow_id,
            run_id=run_id,
            payload={"is_rerun": is_rerun},
        )

    def record_project_created(self, *, project_id: int, name: str) -> None:
        self._repo.append_audit_event(
            event_type=AuditEventType.PROJECT_CREATED,
            summary=f"Projekt erstellt: {name!r} (id={project_id})",
            project_id=project_id,
            payload={"name": name},
        )

    def record_project_updated(self, *, project_id: int, name_hint: Optional[str] = None) -> None:
        hint = f" ({name_hint!r})" if name_hint else ""
        self._repo.append_audit_event(
            event_type=AuditEventType.PROJECT_UPDATED,
            summary=f"Projekt bearbeitet: id={project_id}{hint}",
            project_id=project_id,
            payload={"name_hint": name_hint},
        )

    def record_project_deleted(self, *, project_id: int, name: Optional[str] = None) -> None:
        hint = f" {name!r}" if name else ""
        self._repo.append_audit_event(
            event_type=AuditEventType.PROJECT_DELETED,
            summary=f"Projekt gelöscht: id={project_id}{hint}",
            project_id=project_id,
            payload={"name": name} if name else None,
        )

    def record_incident_created(self, *, incident_id: int, fingerprint: str, run_id: str) -> None:
        self._repo.append_audit_event(
            event_type=AuditEventType.INCIDENT_CREATED,
            summary=f"Incident erstellt: #{incident_id} (Run {run_id})",
            run_id=run_id,
            incident_id=incident_id,
            payload={"fingerprint": fingerprint},
        )

    def record_incident_status_changed(
        self,
        *,
        incident_id: int,
        old_status: str,
        new_status: str,
        project_id: Optional[int] = None,
        workflow_id: Optional[str] = None,
        run_id: Optional[str] = None,
    ) -> None:
        self._repo.append_audit_event(
            event_type=AuditEventType.INCIDENT_STATUS_CHANGED,
            summary=f"Incident #{incident_id}: {old_status} → {new_status}",
            project_id=project_id,
            workflow_id=workflow_id,
            run_id=run_id,
            incident_id=incident_id,
            payload={"old_status": old_status, "new_status": new_status},
        )

    def record_deployment_target_mutated(
        self,
        *,
        action: str,
        target_id: str,
        name: str,
        kind: Optional[str] = None,
        project_id: Optional[int] = None,
    ) -> None:
        self._repo.append_audit_event(
            event_type=AuditEventType.DEPLOYMENT_TARGET_MUTATED,
            summary=f"Deployment-Ziel {action}: {name!r} ({target_id})",
            project_id=project_id,
            payload={
                "action": action,
                "target_id": target_id,
                "name": name,
                "kind": kind,
                "project_id": project_id,
            },
        )

    def record_deployment_release_mutated(
        self,
        *,
        action: str,
        release_id: str,
        display_name: str,
        version_label: str,
        lifecycle_status: str,
        project_id: Optional[int] = None,
    ) -> None:
        self._repo.append_audit_event(
            event_type=AuditEventType.DEPLOYMENT_RELEASE_MUTATED,
            summary=f"Deployment-Release {action}: {display_name!r} {version_label!r} ({release_id})",
            project_id=project_id,
            payload={
                "action": action,
                "release_id": release_id,
                "display_name": display_name,
                "version_label": version_label,
                "lifecycle_status": lifecycle_status,
                "project_id": project_id,
            },
        )

    def record_deployment_rollout_recorded(
        self,
        *,
        rollout_id: str,
        release_id: str,
        target_id: str,
        target_name: str,
        display_name: str,
        version_label: str,
        outcome: str,
        workflow_run_id: Optional[str] = None,
        project_id: Optional[int] = None,
    ) -> None:
        self._repo.append_audit_event(
            event_type=AuditEventType.DEPLOYMENT_ROLLOUT_RECORDED,
            summary=f"Rollout {outcome}: {display_name!r} → {target_name!r} ({rollout_id})",
            project_id=project_id,
            run_id=workflow_run_id,
            payload={
                "rollout_id": rollout_id,
                "release_id": release_id,
                "target_id": target_id,
                "target_name": target_name,
                "display_name": display_name,
                "version_label": version_label,
                "outcome": outcome,
                "workflow_run_id": workflow_run_id,
                "project_id": project_id,
            },
        )

    def list_events(
        self,
        *,
        event_type: Optional[str] = None,
        project_id: Optional[int] = None,
        workflow_id: Optional[str] = None,
        run_id: Optional[str] = None,
        since_iso: Optional[str] = None,
        until_iso: Optional[str] = None,
        limit: int = 500,
        offset: int = 0,
    ) -> List[AuditEventRecord]:
        return self._repo.list_audit_events(
            event_type=event_type,
            project_id=project_id,
            workflow_id=workflow_id,
            run_id=run_id,
            since_iso=since_iso,
            until_iso=until_iso,
            limit=limit,
            offset=offset,
        )


_audit_service: Optional[AuditService] = None


def get_audit_service() -> AuditService:
    global _audit_service
    if _audit_service is None:
        from app.services.infrastructure import get_infrastructure

        db_path = get_infrastructure().database.db_path
        _audit_service = AuditService(AuditRepository(db_path))
    return _audit_service


def reset_audit_service() -> None:
    global _audit_service
    _audit_service = None

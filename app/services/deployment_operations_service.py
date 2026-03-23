"""R4: Deployment-Operations — mutierende API, Audit, keine Qt."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from app.core.deployment.models import (
    DeploymentReleaseRecord,
    DeploymentRolloutRecord,
    DeploymentTargetRecord,
    ReleaseLifecycle,
    RolloutListFilter,
    RolloutOutcome,
)
from app.core.deployment.repository import DeploymentRepository
from app.services.audit_service import AuditService


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class DeploymentOperationsService:
    def __init__(
        self,
        repository: DeploymentRepository,
        audit_service: AuditService,
    ) -> None:
        self._repo = repository
        self._audit = audit_service

    @staticmethod
    def _new_target_id() -> str:
        return f"dtgt_{uuid.uuid4().hex[:16]}"

    @staticmethod
    def _new_release_id() -> str:
        return f"drel_{uuid.uuid4().hex[:16]}"

    @staticmethod
    def _new_rollout_id() -> str:
        return f"drol_{uuid.uuid4().hex[:16]}"

    def list_targets(self) -> List[DeploymentTargetRecord]:
        return self._repo.list_targets()

    def get_target(self, target_id: str) -> Optional[DeploymentTargetRecord]:
        return self._repo.get_target(target_id)

    def create_target(
        self,
        *,
        name: str,
        kind: Optional[str] = None,
        notes: Optional[str] = None,
        project_id: Optional[int] = None,
    ) -> DeploymentTargetRecord:
        n = (name or "").strip()
        if not n:
            raise ValueError("name is required")
        now = _utc_iso()
        rec = DeploymentTargetRecord(
            target_id=self._new_target_id(),
            name=n,
            kind=(kind.strip() or None) if kind else None,
            notes=(notes.strip() or None) if notes else None,
            project_id=project_id,
            created_at=now,
            updated_at=now,
        )
        self._repo.insert_target(rec)
        self._audit.record_deployment_target_mutated(
            action="create",
            target_id=rec.target_id,
            name=rec.name,
            kind=rec.kind,
            project_id=rec.project_id,
        )
        return rec

    def update_target(
        self,
        *,
        target_id: str,
        name: str,
        kind: Optional[str] = None,
        notes: Optional[str] = None,
        project_id: Optional[int] = None,
    ) -> DeploymentTargetRecord:
        existing = self._repo.get_target(target_id)
        if existing is None:
            raise ValueError(f"unknown target: {target_id}")
        n = (name or "").strip()
        if not n:
            raise ValueError("name is required")
        now = _utc_iso()
        rec = DeploymentTargetRecord(
            target_id=target_id,
            name=n,
            kind=(kind.strip() or None) if kind else None,
            notes=(notes.strip() or None) if notes else None,
            project_id=project_id,
            created_at=existing.created_at,
            updated_at=now,
        )
        self._repo.update_target(rec)
        self._audit.record_deployment_target_mutated(
            action="update",
            target_id=rec.target_id,
            name=rec.name,
            kind=rec.kind,
            project_id=rec.project_id,
        )
        return rec

    def list_releases(
        self,
        *,
        lifecycle_status: Optional[str] = None,
        project_id: Optional[int] = None,
    ) -> List[DeploymentReleaseRecord]:
        return self._repo.list_releases(
            lifecycle_status=lifecycle_status, project_id=project_id
        )

    def get_release(self, release_id: str) -> Optional[DeploymentReleaseRecord]:
        return self._repo.get_release(release_id)

    def create_release(
        self,
        *,
        display_name: str,
        version_label: str,
        artifact_kind: str = "",
        artifact_ref: str = "",
        lifecycle_status: str = ReleaseLifecycle.DRAFT,
        project_id: Optional[int] = None,
    ) -> DeploymentReleaseRecord:
        dn = (display_name or "").strip()
        vl = (version_label or "").strip()
        if not dn or not vl:
            raise ValueError("display_name and version_label are required")
        if lifecycle_status not in (
            ReleaseLifecycle.DRAFT,
            ReleaseLifecycle.READY,
            ReleaseLifecycle.ARCHIVED,
        ):
            raise ValueError("invalid lifecycle_status")
        now = _utc_iso()
        rec = DeploymentReleaseRecord(
            release_id=self._new_release_id(),
            display_name=dn,
            version_label=vl,
            artifact_kind=(artifact_kind or "").strip(),
            artifact_ref=(artifact_ref or "").strip(),
            lifecycle_status=lifecycle_status,
            project_id=project_id,
            created_at=now,
            updated_at=now,
        )
        self._repo.insert_release(rec)
        self._audit.record_deployment_release_mutated(
            action="create",
            release_id=rec.release_id,
            display_name=rec.display_name,
            version_label=rec.version_label,
            lifecycle_status=rec.lifecycle_status,
            project_id=rec.project_id,
        )
        return rec

    def update_release(
        self,
        *,
        release_id: str,
        display_name: str,
        version_label: str,
        artifact_kind: str = "",
        artifact_ref: str = "",
        lifecycle_status: Optional[str] = None,
        project_id: Optional[int] = None,
    ) -> DeploymentReleaseRecord:
        existing = self._repo.get_release(release_id)
        if existing is None:
            raise ValueError(f"unknown release: {release_id}")
        dn = (display_name or "").strip()
        vl = (version_label or "").strip()
        if not dn or not vl:
            raise ValueError("display_name and version_label are required")
        lc = lifecycle_status if lifecycle_status is not None else existing.lifecycle_status
        if lc not in (ReleaseLifecycle.DRAFT, ReleaseLifecycle.READY, ReleaseLifecycle.ARCHIVED):
            raise ValueError("invalid lifecycle_status")
        now = _utc_iso()
        rec = DeploymentReleaseRecord(
            release_id=release_id,
            display_name=dn,
            version_label=vl,
            artifact_kind=(artifact_kind or "").strip(),
            artifact_ref=(artifact_ref or "").strip(),
            lifecycle_status=lc,
            project_id=project_id,
            created_at=existing.created_at,
            updated_at=now,
        )
        self._repo.update_release(rec)
        self._audit.record_deployment_release_mutated(
            action="update",
            release_id=rec.release_id,
            display_name=rec.display_name,
            version_label=rec.version_label,
            lifecycle_status=rec.lifecycle_status,
            project_id=rec.project_id,
        )
        return rec

    def archive_release(self, release_id: str) -> DeploymentReleaseRecord:
        existing = self._repo.get_release(release_id)
        if existing is None:
            raise ValueError(f"unknown release: {release_id}")
        now = _utc_iso()
        rec = DeploymentReleaseRecord(
            release_id=release_id,
            display_name=existing.display_name,
            version_label=existing.version_label,
            artifact_kind=existing.artifact_kind,
            artifact_ref=existing.artifact_ref,
            lifecycle_status=ReleaseLifecycle.ARCHIVED,
            project_id=existing.project_id,
            created_at=existing.created_at,
            updated_at=now,
        )
        self._repo.update_release(rec)
        self._audit.record_deployment_release_mutated(
            action="archive",
            release_id=rec.release_id,
            display_name=rec.display_name,
            version_label=rec.version_label,
            lifecycle_status=rec.lifecycle_status,
            project_id=rec.project_id,
        )
        return rec

    def list_rollouts(self, flt: Optional[RolloutListFilter] = None) -> List[DeploymentRolloutRecord]:
        return self._repo.list_rollouts(flt or RolloutListFilter())

    def get_last_rollout_per_target(self) -> Dict[str, DeploymentRolloutRecord]:
        return self._repo.get_last_rollout_per_target()

    def record_rollout(
        self,
        *,
        release_id: str,
        target_id: str,
        outcome: str,
        message: Optional[str] = None,
        started_at: Optional[str] = None,
        finished_at: Optional[str] = None,
        workflow_run_id: Optional[str] = None,
        project_id: Optional[int] = None,
    ) -> DeploymentRolloutRecord:
        rel = self._repo.get_release(release_id)
        if rel is None:
            raise ValueError(f"unknown release: {release_id}")
        if rel.lifecycle_status != ReleaseLifecycle.READY:
            raise ValueError("rollouts are only allowed for releases in lifecycle 'ready'")
        tgt = self._repo.get_target(target_id)
        if tgt is None:
            raise ValueError(f"unknown target: {target_id}")
        if outcome not in (RolloutOutcome.SUCCESS, RolloutOutcome.FAILED, RolloutOutcome.CANCELLED):
            raise ValueError("invalid outcome")
        wrid = (workflow_run_id.strip() or None) if workflow_run_id else None
        now = _utc_iso()
        rec = DeploymentRolloutRecord(
            rollout_id=self._new_rollout_id(),
            release_id=release_id,
            target_id=target_id,
            outcome=outcome,
            message=(message.strip() or None) if message else None,
            started_at=(started_at.strip() or None) if started_at else None,
            finished_at=(finished_at.strip() or None) if finished_at else None,
            recorded_at=now,
            workflow_run_id=wrid,
            project_id=project_id,
        )
        self._repo.insert_rollout(rec)
        self._audit.record_deployment_rollout_recorded(
            rollout_id=rec.rollout_id,
            release_id=rec.release_id,
            target_id=rec.target_id,
            target_name=tgt.name,
            display_name=rel.display_name,
            version_label=rel.version_label,
            outcome=rec.outcome,
            workflow_run_id=rec.workflow_run_id,
            project_id=rec.project_id,
        )
        return rec


_deployment_ops_service: Optional[DeploymentOperationsService] = None


def get_deployment_operations_service() -> DeploymentOperationsService:
    global _deployment_ops_service
    if _deployment_ops_service is None:
        from app.services.infrastructure import get_infrastructure

        db_path = get_infrastructure().database.db_path
        from app.services.audit_service import get_audit_service

        _deployment_ops_service = DeploymentOperationsService(
            DeploymentRepository(db_path),
            get_audit_service(),
        )
    return _deployment_ops_service


def reset_deployment_operations_service() -> None:
    global _deployment_ops_service
    _deployment_ops_service = None

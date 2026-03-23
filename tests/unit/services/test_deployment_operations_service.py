"""R4: DeploymentOperationsService + Audit."""

from unittest.mock import MagicMock

import pytest

from app.core.audit.models import AuditEventType
from app.core.audit.repository import AuditRepository
from app.core.db.database_manager import DatabaseManager
from app.core.deployment.repository import DeploymentRepository
from app.services.audit_service import AuditService
from app.services.deployment_operations_service import DeploymentOperationsService
from app.core.deployment.models import ReleaseLifecycle, RolloutOutcome


@pytest.fixture
def dep_env(tmp_path):
    p = str(tmp_path / "deps.db")
    DatabaseManager(p, ensure_default_project=False)
    audit = AuditService(AuditRepository(p))
    repo = DeploymentRepository(p)
    return p, DeploymentOperationsService(repo, audit), audit


def test_create_target_audits_once(dep_env):
    _, svc, audit = dep_env
    svc.create_target(name="X", kind="k")
    rows = audit.list_events(event_type=AuditEventType.DEPLOYMENT_TARGET_MUTATED, limit=10)
    assert len(rows) == 1
    assert "create" in rows[0].summary.lower() or "X" in rows[0].summary


def test_archive_release_action_in_audit(dep_env):
    _, svc, audit = dep_env
    r = svc.create_release(display_name="A", version_label="1")
    svc.archive_release(r.release_id)
    rows = audit.list_events(event_type=AuditEventType.DEPLOYMENT_RELEASE_MUTATED, limit=20)
    assert len(rows) == 2
    assert any("archive" in e.summary.lower() for e in rows)


def test_record_rollout_rejects_non_ready_release(dep_env):
    _, svc, _ = dep_env
    t = svc.create_target(name="T")
    rel = svc.create_release(display_name="A", version_label="1")
    assert rel.lifecycle_status == ReleaseLifecycle.DRAFT
    with pytest.raises(ValueError, match="ready"):
        svc.record_rollout(
            release_id=rel.release_id,
            target_id=t.target_id,
            outcome=RolloutOutcome.SUCCESS,
        )


def test_record_rollout_rejects_archived_release(dep_env):
    _, svc, _ = dep_env
    t = svc.create_target(name="T")
    rel = svc.create_release(
        display_name="A",
        version_label="1",
        lifecycle_status=ReleaseLifecycle.READY,
    )
    svc.archive_release(rel.release_id)
    with pytest.raises(ValueError, match="ready"):
        svc.record_rollout(
            release_id=rel.release_id,
            target_id=t.target_id,
            outcome=RolloutOutcome.SUCCESS,
        )


def test_record_rollout_optional_workflow_run_id(dep_env):
    _, svc, audit = dep_env
    t = svc.create_target(name="T")
    rel0 = svc.create_release(display_name="A", version_label="1")
    rel = svc.update_release(
        release_id=rel0.release_id,
        display_name="A",
        version_label="1",
        lifecycle_status=ReleaseLifecycle.READY,
    )
    o = svc.record_rollout(
        release_id=rel.release_id,
        target_id=t.target_id,
        outcome=RolloutOutcome.SUCCESS,
        workflow_run_id=None,
    )
    assert o.workflow_run_id is None
    o2 = svc.record_rollout(
        release_id=rel.release_id,
        target_id=t.target_id,
        outcome=RolloutOutcome.FAILED,
        workflow_run_id="  wr_x  ",
    )
    assert o2.workflow_run_id == "wr_x"
    ar = audit.list_events(event_type=AuditEventType.DEPLOYMENT_ROLLOUT_RECORDED, limit=10)
    assert len(ar) == 2


def test_update_target_single_audit(dep_env):
    _, svc, audit = dep_env
    t = svc.create_target(name="A")
    audit.list_events(limit=100)
    n_before = len(audit.list_events(event_type=AuditEventType.DEPLOYMENT_TARGET_MUTATED, limit=50))
    svc.update_target(target_id=t.target_id, name="B")
    n_after = len(audit.list_events(event_type=AuditEventType.DEPLOYMENT_TARGET_MUTATED, limit=50))
    assert n_after == n_before + 1


def test_mock_audit_called_once_per_create_release():
    """Explizit: genau ein Audit-Call pro create_release."""
    mock_audit = MagicMock()
    repo = MagicMock()

    def _ins(_rec):
        return None

    repo.insert_release.side_effect = _ins
    svc = DeploymentOperationsService(repo, mock_audit)
    svc.create_release(display_name="Z", version_label="9")
    mock_audit.record_deployment_release_mutated.assert_called_once()

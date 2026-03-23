"""R4: DeploymentRepository."""

from app.core.audit.repository import AuditRepository
from app.core.db.database_manager import DatabaseManager
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


def _svc(tmp_path):
    p = str(tmp_path / "d.db")
    DatabaseManager(p, ensure_default_project=False)
    return p, DeploymentRepository(p)


def test_migrations_create_tables(tmp_path):
    p, repo = _svc(tmp_path)
    t = repo.list_targets()
    assert t == []


def test_target_crud(tmp_path):
    p, repo = _svc(tmp_path)
    rec = DeploymentTargetRecord(
        target_id="t1",
        name="Lab",
        kind="staging",
        notes="n",
        project_id=1,
        created_at="2025-01-01T00:00:00+00:00",
        updated_at="2025-01-01T00:00:00+00:00",
    )
    repo.insert_target(rec)
    got = repo.get_target("t1")
    assert got is not None
    assert got.name == "Lab"
    rec2 = DeploymentTargetRecord(
        target_id="t1",
        name="Lab2",
        kind=None,
        notes=None,
        project_id=None,
        created_at=rec.created_at,
        updated_at="2025-01-02T00:00:00+00:00",
    )
    repo.update_target(rec2)
    assert repo.get_target("t1").name == "Lab2"


def test_release_crud(tmp_path):
    p, repo = _svc(tmp_path)
    rec = DeploymentReleaseRecord(
        release_id="r1",
        display_name="App",
        version_label="1.0",
        artifact_kind="appimage",
        artifact_ref="/tmp/x",
        lifecycle_status=ReleaseLifecycle.DRAFT,
        project_id=None,
        created_at="2025-01-01T00:00:00+00:00",
        updated_at="2025-01-01T00:00:00+00:00",
    )
    repo.insert_release(rec)
    assert repo.get_release("r1").lifecycle_status == ReleaseLifecycle.DRAFT
    rec.lifecycle_status = ReleaseLifecycle.READY
    rec.updated_at = "2025-01-02T00:00:00+00:00"
    repo.update_release(rec)
    assert repo.get_release("r1").lifecycle_status == ReleaseLifecycle.READY


def test_rollout_insert_only_and_filters(tmp_path):
    p, repo = _svc(tmp_path)
    repo.insert_target(
        DeploymentTargetRecord(
            target_id="t1",
            name="T",
            kind=None,
            notes=None,
            project_id=None,
            created_at="a",
            updated_at="a",
        )
    )
    repo.insert_release(
        DeploymentReleaseRecord(
            release_id="rel1",
            display_name="A",
            version_label="v",
            artifact_kind="",
            artifact_ref="",
            lifecycle_status=ReleaseLifecycle.READY,
            project_id=None,
            created_at="a",
            updated_at="a",
        )
    )
    r1 = DeploymentRolloutRecord(
        rollout_id="o1",
        release_id="rel1",
        target_id="t1",
        outcome=RolloutOutcome.SUCCESS,
        message=None,
        started_at=None,
        finished_at=None,
        recorded_at="2025-01-10T10:00:00+00:00",
        workflow_run_id=None,
        project_id=None,
    )
    r2 = DeploymentRolloutRecord(
        rollout_id="o2",
        release_id="rel1",
        target_id="t1",
        outcome=RolloutOutcome.FAILED,
        message="x",
        started_at=None,
        finished_at=None,
        recorded_at="2025-01-15T12:00:00+00:00",
        workflow_run_id="wr_1",
        project_id=3,
    )
    repo.insert_rollout(r1)
    repo.insert_rollout(r2)
    all_rows = repo.list_rollouts(RolloutListFilter(limit=50))
    assert len(all_rows) == 2
    failed = repo.list_rollouts(RolloutListFilter(outcome=RolloutOutcome.FAILED, limit=50))
    assert len(failed) == 1
    assert failed[0].rollout_id == "o2"
    by_rel = repo.list_rollouts(RolloutListFilter(release_id="rel1", limit=50))
    assert len(by_rel) == 2
    since = repo.list_rollouts(
        RolloutListFilter(since_iso="2025-01-12T00:00:00+00:00", limit=50)
    )
    assert len(since) == 1


def test_last_rollout_per_target(tmp_path):
    p, repo = _svc(tmp_path)
    for tid, name in (("t1", "A"), ("t2", "B")):
        repo.insert_target(
            DeploymentTargetRecord(
                target_id=tid,
                name=name,
                kind=None,
                notes=None,
                project_id=None,
                created_at="a",
                updated_at="a",
            )
        )
    repo.insert_release(
        DeploymentReleaseRecord(
            release_id="rel1",
            display_name="X",
            version_label="1",
            artifact_kind="",
            artifact_ref="",
            lifecycle_status=ReleaseLifecycle.READY,
            project_id=None,
            created_at="a",
            updated_at="a",
        )
    )
    repo.insert_rollout(
        DeploymentRolloutRecord(
            rollout_id="a",
            release_id="rel1",
            target_id="t1",
            outcome=RolloutOutcome.SUCCESS,
            message=None,
            started_at=None,
            finished_at=None,
            recorded_at="2025-01-01T00:00:00+00:00",
            workflow_run_id=None,
            project_id=None,
        )
    )
    repo.insert_rollout(
        DeploymentRolloutRecord(
            rollout_id="b",
            release_id="rel1",
            target_id="t1",
            outcome=RolloutOutcome.SUCCESS,
            message=None,
            started_at=None,
            finished_at=None,
            recorded_at="2025-01-02T00:00:00+00:00",
            workflow_run_id=None,
            project_id=None,
        )
    )
    repo.insert_rollout(
        DeploymentRolloutRecord(
            rollout_id="c",
            release_id="rel1",
            target_id="t2",
            outcome=RolloutOutcome.SUCCESS,
            message=None,
            started_at=None,
            finished_at=None,
            recorded_at="2025-01-03T00:00:00+00:00",
            workflow_run_id=None,
            project_id=None,
        )
    )
    m = repo.get_last_rollout_per_target()
    assert m["t1"].rollout_id == "b"
    assert m["t2"].rollout_id == "c"


def test_audit_coexists(tmp_path):
    """Regression: Audit-Tabellen nach R4-Migration nutzbar."""
    p, _ = _svc(tmp_path)
    AuditService(AuditRepository(p)).record_project_created(project_id=1, name="P")
    rows = AuditRepository(p).list_audit_events(project_id=1)
    assert len(rows) == 1

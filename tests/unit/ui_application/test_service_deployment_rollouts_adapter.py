"""ServiceDeploymentRolloutsAdapter."""

from __future__ import annotations

from app.core.deployment.models import (
    DeploymentReleaseRecord,
    DeploymentRolloutRecord,
    DeploymentTargetRecord,
    RolloutListFilter,
)
from app.ui_application.adapters.service_deployment_rollouts_adapter import (
    ServiceDeploymentRolloutsAdapter,
    rollout_record_combo_snapshot_from_records,
)
from app.ui_contracts.workspaces.deployment_rollouts import (
    DeploymentRolloutsFilterSnapshot,
    RecordDeploymentRolloutCommand,
)


def _target(tid: str, name: str) -> DeploymentTargetRecord:
    return DeploymentTargetRecord(
        target_id=tid,
        name=name,
        kind=None,
        notes=None,
        project_id=None,
        created_at="c",
        updated_at="u",
    )


def _release(rid: str) -> DeploymentReleaseRecord:
    return DeploymentReleaseRecord(
        release_id=rid,
        display_name="App",
        version_label="1.0",
        artifact_kind="",
        artifact_ref="",
        lifecycle_status="ready",
        project_id=None,
        created_at="c",
        updated_at="u",
    )


def _rollout(rid: str, tid: str) -> DeploymentRolloutRecord:
    return DeploymentRolloutRecord(
        rollout_id="o1",
        release_id=rid,
        target_id=tid,
        outcome="success",
        message=None,
        started_at=None,
        finished_at=None,
        recorded_at="2025-01-01T00:00:00Z",
        workflow_run_id="run-1",
        project_id=None,
    )


class _FakeDepSvc:
    def __init__(self) -> None:
        self.targets: list[DeploymentTargetRecord] = []
        self.releases: list[DeploymentReleaseRecord] = []
        self.rollouts: list[DeploymentRolloutRecord] = []
        self.last_filter: RolloutListFilter | None = None
        self.record_calls: list[dict] = []

    def list_targets(self):
        return list(self.targets)

    def list_releases(self, lifecycle_status=None):
        rels = list(self.releases)
        if lifecycle_status is not None:
            rels = [r for r in rels if r.lifecycle_status == lifecycle_status]
        return rels

    def list_rollouts(self, flt):
        self.last_filter = flt
        return list(self.rollouts)

    def record_rollout(self, **kwargs):  # noqa: ANN003
        self.record_calls.append(dict(kwargs))


def test_adapter_happy(monkeypatch) -> None:
    fake = _FakeDepSvc()
    fake.targets = [_target("t1", "Prod")]
    fake.releases = [_release("r1")]
    fake.rollouts = [_rollout("r1", "t1")]
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    flt = DeploymentRolloutsFilterSnapshot(target_id="t1", release_id="r1")
    v = ServiceDeploymentRolloutsAdapter().load_rollouts_view(flt)
    assert v.phase == "ready"
    assert len(v.target_options) == 2
    assert len(v.release_options) == 2
    assert len(v.table_rows) == 1
    assert v.table_rows[0].target_display_name == "Prod"
    assert v.table_rows[0].release_display_name == "App"
    assert fake.last_filter is not None
    assert fake.last_filter.limit == 800


def test_adapter_empty_rollouts(monkeypatch) -> None:
    fake = _FakeDepSvc()
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    v = ServiceDeploymentRolloutsAdapter().load_rollouts_view(DeploymentRolloutsFilterSnapshot())
    assert v.phase == "ready"
    assert v.table_rows == ()


def test_rollout_record_combo_snapshot_from_records_maps_rows() -> None:
    snap = rollout_record_combo_snapshot_from_records(
        [_target("t1", "Prod")],
        [_release("r1")],
    )
    assert len(snap.targets) == 1
    assert snap.targets[0].value_id == "t1"
    assert snap.targets[0].label == "Prod"
    assert len(snap.ready_releases) == 1
    assert snap.ready_releases[0].value_id == "r1"
    assert snap.ready_releases[0].label == "App (1.0)"


def test_adapter_load_rollout_record_combo_options(monkeypatch) -> None:
    fake = _FakeDepSvc()
    fake.targets = [_target("t1", "Prod")]
    fake.releases = [_release("r1")]
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    snap = ServiceDeploymentRolloutsAdapter().load_rollout_record_combo_options()
    assert len(snap.targets) == 1
    assert len(snap.ready_releases) == 1


def test_adapter_record_deployment_rollout_ok(monkeypatch) -> None:
    fake = _FakeDepSvc()
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    cmd = RecordDeploymentRolloutCommand(
        release_id="r1",
        target_id="t1",
        outcome="success",
        message="hi",
    )
    r = ServiceDeploymentRolloutsAdapter().record_deployment_rollout(cmd)
    assert r.ok
    assert len(fake.record_calls) == 1
    assert fake.record_calls[0]["release_id"] == "r1"
    assert fake.record_calls[0]["target_id"] == "t1"


def test_adapter_record_deployment_rollout_error(monkeypatch) -> None:
    def _boom(**_kwargs):  # noqa: ANN003
        raise RuntimeError("db write")

    fake = _FakeDepSvc()
    fake.record_rollout = _boom  # type: ignore[method-assign]
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    cmd = RecordDeploymentRolloutCommand(release_id="r", target_id="t", outcome="failed")
    r = ServiceDeploymentRolloutsAdapter().record_deployment_rollout(cmd)
    assert not r.ok
    assert r.error_message is not None


def test_adapter_list_error(monkeypatch) -> None:
    def _boom():
        raise RuntimeError("db")

    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        _boom,
    )
    flt = DeploymentRolloutsFilterSnapshot()
    v = ServiceDeploymentRolloutsAdapter().load_rollouts_view(flt)
    assert v.phase == "error"
    assert v.error is not None
    assert "Rollouts" in (v.error.message or "")

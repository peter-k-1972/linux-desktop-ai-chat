"""ServiceDeploymentReleasesAdapter."""

from __future__ import annotations

import pytest

from app.core.deployment.models import (
    DeploymentReleaseRecord,
    DeploymentRolloutRecord,
    DeploymentTargetRecord,
    RolloutListFilter,
)
from app.ui_application.adapters.service_deployment_releases_adapter import ServiceDeploymentReleasesAdapter
from app.ui_contracts.workspaces.deployment_releases import (
    DeploymentReleaseCreateWrite,
    DeploymentReleaseUpdateWrite,
    DeploymentReleasesPortError,
)


def _release(rid: str, name: str = "R") -> DeploymentReleaseRecord:
    return DeploymentReleaseRecord(
        release_id=rid,
        display_name=name,
        version_label="1.0.0",
        artifact_kind="oci",
        artifact_ref="ref",
        lifecycle_status="ready",
        project_id=3,
        created_at="c",
        updated_at="u",
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


def _rollout(rid: str, tid: str) -> DeploymentRolloutRecord:
    return DeploymentRolloutRecord(
        rollout_id="o1",
        release_id=rid,
        target_id=tid,
        outcome="success",
        message="ok",
        started_at=None,
        finished_at=None,
        recorded_at="2025-01-01T00:00:00Z",
        workflow_run_id="run-1",
        project_id=None,
    )


class _FakeDepSvc:
    def __init__(self) -> None:
        self.releases: list[DeploymentReleaseRecord] = []
        self.rollouts: list[DeploymentRolloutRecord] = []
        self.targets: list[DeploymentTargetRecord] = []
        self.list_filter: RolloutListFilter | None = None
        self.create_calls: list[dict] = []
        self.update_calls: list[dict] = []
        self.archive_calls: list[str] = []

    def list_releases(self):
        return list(self.releases)

    def get_release(self, release_id: str):
        for r in self.releases:
            if r.release_id == release_id:
                return r
        return None

    def list_rollouts(self, flt: RolloutListFilter):
        self.list_filter = flt
        return [o for o in self.rollouts if o.release_id == flt.release_id]

    def list_targets(self):
        return list(self.targets)

    def create_release(self, **kwargs) -> DeploymentReleaseRecord:
        self.create_calls.append(dict(kwargs))
        return _release("new", kwargs.get("display_name", "R"))

    def update_release(self, **kwargs) -> DeploymentReleaseRecord:
        self.update_calls.append(dict(kwargs))
        return _release(kwargs["release_id"], kwargs.get("display_name", "R"))

    def archive_release(self, release_id: str) -> DeploymentReleaseRecord:
        self.archive_calls.append(release_id)
        return _release(release_id)


def test_adapter_list_happy(monkeypatch) -> None:
    fake = _FakeDepSvc()
    fake.releases = [_release("r1", "One")]
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    ad = ServiceDeploymentReleasesAdapter()
    v = ad.load_releases_list_view()
    assert v.phase == "ready"
    assert len(v.rows) == 1
    assert v.rows[0].release_id == "r1"
    assert v.rows[0].project_id == 3


def test_adapter_list_empty(monkeypatch) -> None:
    fake = _FakeDepSvc()
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    v = ServiceDeploymentReleasesAdapter().load_releases_list_view()
    assert v.phase == "ready"
    assert v.rows == ()


def test_adapter_list_error(monkeypatch) -> None:
    def _boom():
        raise RuntimeError("db down")

    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        _boom,
    )
    v = ServiceDeploymentReleasesAdapter().load_releases_list_view()
    assert v.phase == "error"
    assert v.error is not None
    assert "Releases" in (v.error.message or "")


def test_adapter_selection_happy(monkeypatch) -> None:
    fake = _FakeDepSvc()
    fake.releases = [_release("r1")]
    fake.targets = [_target("t1", "Prod")]
    fake.rollouts = [_rollout("r1", "t1")]
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    ad = ServiceDeploymentReleasesAdapter()
    s = ad.load_release_selection_state("r1")
    assert s.selected_release_id == "r1"
    assert s.detail is not None
    assert s.detail.display_name == "R"
    assert len(s.history_rows) == 1
    assert s.history_rows[0].target_display_name == "Prod"
    assert fake.list_filter is not None
    assert fake.list_filter.limit == 200


def test_adapter_selection_missing_release(monkeypatch) -> None:
    fake = _FakeDepSvc()
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    s = ServiceDeploymentReleasesAdapter().load_release_selection_state("nope")
    assert s.selected_release_id is None
    assert s.detail is None


def test_adapter_selection_none_id(monkeypatch) -> None:
    fake = _FakeDepSvc()
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    s = ServiceDeploymentReleasesAdapter().load_release_selection_state(None)
    assert s.detail is None


def test_adapter_selection_empty_string_clears_like_falsy_id(monkeypatch) -> None:
    fake = _FakeDepSvc()
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    s = ServiceDeploymentReleasesAdapter().load_release_selection_state("")
    assert s.detail is None


def test_adapter_get_release_editor_snapshot(monkeypatch) -> None:
    fake = _FakeDepSvc()
    fake.releases = [_release("r1", "Name")]
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    snap = ServiceDeploymentReleasesAdapter().get_release_editor_snapshot("r1")
    assert snap is not None
    assert snap.display_name == "Name"
    assert ServiceDeploymentReleasesAdapter().get_release_editor_snapshot("x") is None


def test_adapter_create_and_update_and_archive(monkeypatch) -> None:
    fake = _FakeDepSvc()
    fake.releases = [_release("r1")]
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    ad = ServiceDeploymentReleasesAdapter()
    ad.create_release(DeploymentReleaseCreateWrite(display_name="A", version_label="1.0"))
    assert fake.create_calls
    ad.update_release(
        DeploymentReleaseUpdateWrite(release_id="r1", display_name="B", version_label="2.0"),
    )
    assert fake.update_calls[0]["release_id"] == "r1"
    ad.archive_release("r1")
    assert fake.archive_calls == ["r1"]


def test_adapter_create_validation_maps_to_port_error(monkeypatch) -> None:
    class _Err(_FakeDepSvc):
        def create_release(self, **_kwargs) -> DeploymentReleaseRecord:
            raise ValueError("required")

    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: _Err(),
    )
    with pytest.raises(DeploymentReleasesPortError) as ei:
        ServiceDeploymentReleasesAdapter().create_release(
            DeploymentReleaseCreateWrite(display_name="", version_label=""),
        )
    assert ei.value.code == "validation"

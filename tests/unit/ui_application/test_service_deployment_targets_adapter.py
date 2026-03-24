"""ServiceDeploymentTargetsAdapter."""

from __future__ import annotations

import pytest

from app.core.deployment.models import DeploymentRolloutRecord, DeploymentTargetRecord
from app.ui_application.adapters.service_deployment_targets_adapter import ServiceDeploymentTargetsAdapter
from app.ui_contracts.workspaces.deployment_targets import (
    DeploymentTargetCreateWrite,
    DeploymentTargetUpdateWrite,
    DeploymentTargetsPortError,
)


class _FakeDepSvc:
    def __init__(self) -> None:
        self.targets: list[DeploymentTargetRecord] = []
        self.last_map: dict[str, DeploymentRolloutRecord] = {}
        self.create_calls: list[tuple[str, object, object, object]] = []
        self.update_calls: list[dict] = []

    def list_targets(self) -> list[DeploymentTargetRecord]:
        return list(self.targets)

    def get_last_rollout_per_target(self) -> dict[str, DeploymentRolloutRecord]:
        return dict(self.last_map)

    def get_target(self, target_id: str) -> DeploymentTargetRecord | None:
        for t in self.targets:
            if t.target_id == target_id:
                return t
        return None

    def create_target(
        self,
        *,
        name: str,
        kind=None,
        notes=None,
        project_id=None,
    ) -> DeploymentTargetRecord:
        n = (name or "").strip()
        if not n:
            raise ValueError("name is required")
        self.create_calls.append((name, kind, notes, project_id))
        return _target("new", n, project_id)

    def update_target(
        self,
        *,
        target_id: str,
        name: str,
        kind=None,
        notes=None,
        project_id=None,
    ) -> DeploymentTargetRecord:
        self.update_calls.append(
            {
                "target_id": target_id,
                "name": name,
                "kind": kind,
                "notes": notes,
                "project_id": project_id,
            },
        )
        return _target(target_id, name, project_id)


def _target(tid: str, name: str, pid: int | None = None) -> DeploymentTargetRecord:
    return DeploymentTargetRecord(
        target_id=tid,
        name=name,
        kind="k",
        notes=None,
        project_id=pid,
        created_at="c",
        updated_at="u",
    )


def _rollout(tid: str) -> DeploymentRolloutRecord:
    return DeploymentRolloutRecord(
        rollout_id="rol1",
        release_id="rel1",
        target_id=tid,
        outcome="success",
        message=None,
        started_at=None,
        finished_at=None,
        recorded_at="2025-03-01T12:00:00+00:00",
        workflow_run_id=None,
        project_id=None,
    )


def test_adapter_happy_path(monkeypatch) -> None:
    fake = _FakeDepSvc()
    fake.targets = [_target("t1", "One", 5)]
    fake.last_map = {"t1": _rollout("t1")}
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    st = ServiceDeploymentTargetsAdapter().load_targets_view()
    assert st.phase == "ready"
    assert len(st.rows) == 1
    assert st.rows[0].target_id == "t1"
    assert st.rows[0].name == "One"
    assert st.rows[0].project_id == 5
    assert "2025-03-01" in st.rows[0].last_rollout_recorded_at
    assert st.rows[0].last_rollout_outcome == "success"


def test_adapter_empty_targets(monkeypatch) -> None:
    fake = _FakeDepSvc()
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    st = ServiceDeploymentTargetsAdapter().load_targets_view()
    assert st.phase == "ready"
    assert st.rows == ()


def test_adapter_error_state(monkeypatch) -> None:
    def _boom() -> _FakeDepSvc:
        raise RuntimeError("db down")

    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        _boom,
    )
    st = ServiceDeploymentTargetsAdapter().load_targets_view()
    assert st.phase == "error"
    assert st.error is not None
    assert "db down" in (st.error.detail or "")


def test_adapter_get_target_editor_snapshot(monkeypatch) -> None:
    fake = _FakeDepSvc()
    fake.targets = [_target("t1", "N", 3)]
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    snap = ServiceDeploymentTargetsAdapter().get_target_editor_snapshot("t1")
    assert snap is not None
    assert snap.name == "N"
    assert snap.project_id == 3
    assert ServiceDeploymentTargetsAdapter().get_target_editor_snapshot("missing") is None


def test_adapter_create_target(monkeypatch) -> None:
    fake = _FakeDepSvc()
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    ad = ServiceDeploymentTargetsAdapter()
    ad.create_target(DeploymentTargetCreateWrite(name="hello", kind="x", notes="n", project_id=1))
    assert len(fake.create_calls) == 1
    assert fake.create_calls[0][0] == "hello"


def test_adapter_create_target_validation_error(monkeypatch) -> None:
    fake = _FakeDepSvc()
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    with pytest.raises(DeploymentTargetsPortError) as ei:
        ServiceDeploymentTargetsAdapter().create_target(DeploymentTargetCreateWrite(name="   "))
    assert ei.value.code == "validation"


def test_adapter_update_target(monkeypatch) -> None:
    fake = _FakeDepSvc()
    monkeypatch.setattr(
        "app.services.deployment_operations_service.get_deployment_operations_service",
        lambda: fake,
    )
    ServiceDeploymentTargetsAdapter().update_target(
        DeploymentTargetUpdateWrite(target_id="t1", name="Z", kind=None, notes=None, project_id=None),
    )
    assert fake.update_calls[0]["target_id"] == "t1"
    assert fake.update_calls[0]["name"] == "Z"

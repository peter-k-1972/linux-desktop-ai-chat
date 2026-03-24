"""Deployment Targets (Slice 1–2) — Contracts."""

from __future__ import annotations

from dataclasses import asdict

from app.ui_contracts.workspaces.deployment_targets import (
    CreateDeploymentTargetCommand,
    DeploymentTargetCreateWrite,
    DeploymentTargetEditorSnapshotDto,
    DeploymentTargetTableRowDto,
    DeploymentTargetsPortError,
    DeploymentTargetsViewState,
    LoadDeploymentTargetsCommand,
    UpdateDeploymentTargetCommand,
    DeploymentTargetUpdateWrite,
    deployment_targets_loading_state,
)
from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo


def test_row_dto_asdict() -> None:
    r = DeploymentTargetTableRowDto(
        target_id="t1",
        name="Prod",
        kind="k8s",
        project_id=3,
        last_rollout_recorded_at="2024-01-01",
        last_rollout_outcome="success",
    )
    d = asdict(r)
    assert d["target_id"] == "t1"
    assert d["project_id"] == 3


def test_view_state_ready_empty() -> None:
    st = DeploymentTargetsViewState(phase="ready", rows=(), error=None, banner_message=None)
    assert st.phase == "ready"
    assert st.rows == ()


def test_view_state_error() -> None:
    err = SettingsErrorInfo(code="x", message="m")
    st = DeploymentTargetsViewState(phase="error", rows=(), error=err, banner_message=None)
    assert st.error == err


def test_view_state_banner() -> None:
    b = SettingsErrorInfo(code="v", message="validation")
    st = DeploymentTargetsViewState(phase="ready", rows=(), error=None, banner_message=b)
    assert st.banner_message == b


def test_loading_helper() -> None:
    st = deployment_targets_loading_state()
    assert st.phase == "loading"
    assert st.banner_message is None


def test_load_command_frozen() -> None:
    assert LoadDeploymentTargetsCommand() is not None


def test_create_update_commands() -> None:
    cw = DeploymentTargetCreateWrite(name="n")
    assert CreateDeploymentTargetCommand(cw).write.name == "n"
    uw = DeploymentTargetUpdateWrite(target_id="t", name="x")
    assert UpdateDeploymentTargetCommand(uw).write.target_id == "t"


def test_port_error_attrs() -> None:
    e = DeploymentTargetsPortError("c", "msg", recoverable=False)
    assert e.code == "c"
    assert e.recoverable is False


def test_editor_snapshot_dto() -> None:
    s = DeploymentTargetEditorSnapshotDto(
        target_id="1",
        name="N",
        kind="k",
        notes="",
        project_id=2,
    )
    assert asdict(s)["project_id"] == 2

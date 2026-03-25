"""Deployment Releases (Slice 3) — Contracts."""

from __future__ import annotations

from dataclasses import asdict

from app.ui_contracts.workspaces.deployment_releases import (
    ArchiveDeploymentReleaseCommand,
    CreateDeploymentReleaseCommand,
    DeploymentReleaseCreateWrite,
    DeploymentReleaseDetailDto,
    DeploymentReleaseEditorSnapshotDto,
    DeploymentReleaseHistoryRowDto,
    DeploymentReleaseSelectionState,
    DeploymentReleaseTableRowDto,
    DeploymentReleaseUpdateWrite,
    DeploymentReleasesPortError,
    DeploymentReleasesViewState,
    LoadDeploymentReleaseSelectionCommand,
    LoadDeploymentReleasesCommand,
    UpdateDeploymentReleaseCommand,
    deployment_releases_loading_state,
)
from app.ui_contracts.common.errors import SettingsErrorInfo


def test_table_row_asdict() -> None:
    r = DeploymentReleaseTableRowDto(
        release_id="r1",
        display_name="App",
        version_label="1.0",
        lifecycle_status="ready",
        artifact_kind="oci",
        project_id=7,
    )
    d = asdict(r)
    assert d["release_id"] == "r1"
    assert d["project_id"] == 7


def test_view_state_ready_empty() -> None:
    st = DeploymentReleasesViewState(phase="ready", rows=())
    assert st.phase == "ready"
    assert st.detail is None
    assert st.history_rows == ()


def test_view_state_error() -> None:
    err = SettingsErrorInfo(code="x", message="m")
    st = DeploymentReleasesViewState(phase="error", rows=(), error=err)
    assert st.error == err


def test_loading_helper() -> None:
    st = deployment_releases_loading_state()
    assert st.phase == "loading"


def test_load_commands_frozen() -> None:
    assert LoadDeploymentReleasesCommand() is not None
    assert LoadDeploymentReleaseSelectionCommand("x").release_id == "x"


def test_view_state_banner() -> None:
    b = SettingsErrorInfo(code="v", message="mut fail")
    st = DeploymentReleasesViewState(phase="ready", rows=(), banner_message=b)
    assert st.banner_message == b


def test_mutation_commands() -> None:
    c = CreateDeploymentReleaseCommand(DeploymentReleaseCreateWrite("a", "1.0"))
    assert c.write.version_label == "1.0"
    u = UpdateDeploymentReleaseCommand(
        DeploymentReleaseUpdateWrite("rid", "n", "v"),
        reselect_release_id_after="rid",
    )
    assert u.write.release_id == "rid"
    assert ArchiveDeploymentReleaseCommand("x").release_id == "x"


def test_port_error() -> None:
    e = DeploymentReleasesPortError("c", "m", recoverable=False)
    assert e.recoverable is False


def test_editor_snapshot_dto() -> None:
    s = DeploymentReleaseEditorSnapshotDto(
        release_id="1",
        display_name="D",
        version_label="v",
        artifact_kind="k",
        artifact_ref="r",
        lifecycle_status="draft",
        project_id=2,
    )
    assert asdict(s)["project_id"] == 2


def test_selection_state() -> None:
    d = DeploymentReleaseDetailDto(
        display_name="A",
        version_label="v",
        lifecycle_status="draft",
        artifact_ref="ref",
        artifact_kind="k",
    )
    h = DeploymentReleaseHistoryRowDto(
        recorded_at="t",
        target_display_name="T",
        outcome="success",
        workflow_run_id="w",
        message="",
    )
    s = DeploymentReleaseSelectionState(
        selected_release_id="r",
        detail=d,
        history_rows=(h,),
    )
    assert len(s.history_rows) == 1

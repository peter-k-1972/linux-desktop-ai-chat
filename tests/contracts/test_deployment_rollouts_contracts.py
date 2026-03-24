"""Deployment Rollouts (Slice 4) — Contracts."""

from __future__ import annotations

from dataclasses import asdict

from app.ui_contracts.workspaces.deployment_rollouts import (
    DeploymentRolloutFilterOptionDto,
    DeploymentRolloutRecordMutationResult,
    DeploymentRolloutTableRowDto,
    DeploymentRolloutsFilterSnapshot,
    DeploymentRolloutsViewState,
    LoadDeploymentRolloutsCommand,
    RecordDeploymentRolloutCommand,
    RolloutRecordComboRowDto,
    RolloutRecordComboSnapshot,
    deployment_rollouts_loading_state,
)
from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo


def test_filter_snapshot_asdict() -> None:
    f = DeploymentRolloutsFilterSnapshot(
        target_id="t1",
        release_id="r1",
        outcome="success",
        since_iso="a",
        until_iso="b",
        range_preset=7,
    )
    d = asdict(f)
    assert d["range_preset"] == 7


def test_table_row_dto() -> None:
    r = DeploymentRolloutTableRowDto(
        recorded_at="t",
        target_display_name="T",
        release_display_name="R",
        version_label="1",
        outcome="success",
        workflow_run_id="w",
        message="m",
    )
    assert asdict(r)["workflow_run_id"] == "w"


def test_view_state_ready_empty() -> None:
    af = DeploymentRolloutsFilterSnapshot()
    st = DeploymentRolloutsViewState(phase="ready", active_filter=af)
    assert st.table_rows == ()


def test_view_state_error() -> None:
    af = DeploymentRolloutsFilterSnapshot()
    err = SettingsErrorInfo(code="x", message="m")
    st = DeploymentRolloutsViewState(phase="error", active_filter=af, error=err)
    assert st.error == err


def test_loading_helper() -> None:
    af = DeploymentRolloutsFilterSnapshot(range_preset=30)
    st = deployment_rollouts_loading_state(af)
    assert st.phase == "loading"
    assert st.active_filter.range_preset == 30


def test_load_command() -> None:
    af = DeploymentRolloutsFilterSnapshot(target_id="x")
    assert LoadDeploymentRolloutsCommand(af).filter.target_id == "x"


def test_filter_option() -> None:
    o = DeploymentRolloutFilterOptionDto(value_id=None, label="alle")
    assert o.value_id is None


def test_record_rollout_command_asdict() -> None:
    c = RecordDeploymentRolloutCommand(
        release_id="r",
        target_id="t",
        outcome="success",
        message="m",
        workflow_run_id="w",
    )
    d = asdict(c)
    assert d["release_id"] == "r"
    assert d["target_id"] == "t"


def test_rollout_record_mutation_result() -> None:
    r = DeploymentRolloutRecordMutationResult(ok=False, error_message="e")
    assert asdict(r)["ok"] is False


def test_rollout_record_combo_snapshot_asdict() -> None:
    snap = RolloutRecordComboSnapshot(
        targets=(RolloutRecordComboRowDto("t", "T"),),
        ready_releases=(RolloutRecordComboRowDto("r", "R (v)"),),
    )
    d = asdict(snap)
    assert d["targets"][0]["value_id"] == "t"
    assert d["ready_releases"][0]["label"] == "R (v)"

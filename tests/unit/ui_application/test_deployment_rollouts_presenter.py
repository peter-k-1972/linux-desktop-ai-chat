"""DeploymentRolloutsPresenter — Load (Slice 4)."""

from __future__ import annotations

from app.ui_application.presenters.deployment_rollouts_presenter import DeploymentRolloutsPresenter
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
)
from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo


class _Sink:
    def __init__(self) -> None:
        self.states: list[DeploymentRolloutsViewState] = []

    def apply_full_state(self, state: DeploymentRolloutsViewState) -> None:
        self.states.append(state)


class _FakePort:
    def __init__(self, view: DeploymentRolloutsViewState) -> None:
        self._view = view
        self.loads = 0
        self.last_filter: DeploymentRolloutsFilterSnapshot | None = None
        self.record_combo_calls = 0
        self.record_calls: list[RecordDeploymentRolloutCommand] = []
        self._record_combo = RolloutRecordComboSnapshot(
            targets=(RolloutRecordComboRowDto("t1", "T1"),),
            ready_releases=(RolloutRecordComboRowDto("r1", "R1 (1.0)"),),
        )

    def load_rollouts_view(self, filter_snapshot: DeploymentRolloutsFilterSnapshot) -> DeploymentRolloutsViewState:
        self.loads += 1
        self.last_filter = filter_snapshot
        return self._view

    def load_rollout_record_combo_options(self) -> RolloutRecordComboSnapshot:
        self.record_combo_calls += 1
        return self._record_combo

    def record_deployment_rollout(
        self,
        command: RecordDeploymentRolloutCommand,
    ) -> DeploymentRolloutRecordMutationResult:
        self.record_calls.append(command)
        return DeploymentRolloutRecordMutationResult(ok=True)


def _ready_view(flt: DeploymentRolloutsFilterSnapshot) -> DeploymentRolloutsViewState:
    row = DeploymentRolloutTableRowDto(
        recorded_at="t",
        target_display_name="T",
        release_display_name="R",
        version_label="v",
        outcome="success",
        workflow_run_id="",
        message="",
    )
    return DeploymentRolloutsViewState(
        phase="ready",
        active_filter=flt,
        target_options=(
            DeploymentRolloutFilterOptionDto(None, "(alle Ziele)"),
            DeploymentRolloutFilterOptionDto("t1", "One"),
        ),
        release_options=(DeploymentRolloutFilterOptionDto(None, "(alle Releases)"),),
        table_rows=(row,),
    )


def test_presenter_load_shows_loading_then_ready() -> None:
    flt = DeploymentRolloutsFilterSnapshot()
    ready = _ready_view(flt)
    sink = _Sink()
    port = _FakePort(ready)
    pres = DeploymentRolloutsPresenter(sink, port)
    pres.handle_command(LoadDeploymentRolloutsCommand(flt))
    assert len(sink.states) == 2
    assert sink.states[0].phase == "loading"
    assert sink.states[1].phase == "ready"
    assert port.loads == 1
    assert port.last_filter == flt


def test_presenter_handle_record_rollout_refreshes_on_success() -> None:
    flt = DeploymentRolloutsFilterSnapshot(target_id="t1")
    ready = _ready_view(flt)
    sink = _Sink()
    port = _FakePort(ready)
    pres = DeploymentRolloutsPresenter(sink, port)
    cmd = RecordDeploymentRolloutCommand(
        release_id="r1",
        target_id="t1",
        outcome="success",
    )
    n_before = len(sink.states)
    result = pres.handle_record_rollout(cmd, flt)
    assert result.ok
    assert port.record_calls == [cmd]
    assert len(sink.states) == n_before + 2
    assert sink.states[-2].phase == "loading"
    assert sink.states[-1].phase == "ready"


def test_presenter_handle_record_rollout_skips_refresh_on_error() -> None:
    flt = DeploymentRolloutsFilterSnapshot()

    class _ErrPort(_FakePort):
        def record_deployment_rollout(
            self,
            command: RecordDeploymentRolloutCommand,
        ) -> DeploymentRolloutRecordMutationResult:
            self.record_calls.append(command)
            return DeploymentRolloutRecordMutationResult(ok=False, error_message="x")

    ready = _ready_view(flt)
    sink = _Sink()
    port = _ErrPort(ready)
    pres = DeploymentRolloutsPresenter(sink, port)
    loads_before = port.loads
    cmd = RecordDeploymentRolloutCommand(release_id="r", target_id="t", outcome="success")
    result = pres.handle_record_rollout(cmd, flt)
    assert not result.ok
    assert port.loads == loads_before


def test_presenter_load_rollout_record_combo_options_delegates_to_port() -> None:
    flt = DeploymentRolloutsFilterSnapshot()
    sink = _Sink()
    port = _FakePort(_ready_view(flt))
    pres = DeploymentRolloutsPresenter(sink, port)
    snap = pres.load_rollout_record_combo_options()
    assert port.record_combo_calls == 1
    assert snap.targets[0].value_id == "t1"
    assert snap.ready_releases[0].label == "R1 (1.0)"


def test_presenter_load_error() -> None:
    flt = DeploymentRolloutsFilterSnapshot(target_id="t")
    err = DeploymentRolloutsViewState(
        phase="error",
        active_filter=flt,
        error=SettingsErrorInfo(code="e", message="fail"),
    )
    sink = _Sink()
    pres = DeploymentRolloutsPresenter(sink, _FakePort(err))
    pres.handle_command(LoadDeploymentRolloutsCommand(flt))
    assert sink.states[-1].phase == "error"

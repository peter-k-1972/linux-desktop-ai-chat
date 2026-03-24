"""DeploymentTargetsPresenter — Load + Mutationen (Slice 2)."""

from __future__ import annotations

from app.ui_application.presenters.deployment_targets_presenter import DeploymentTargetsPresenter
from app.ui_contracts.workspaces.deployment_targets import (
    CreateDeploymentTargetCommand,
    DeploymentTargetCreateWrite,
    DeploymentTargetTableRowDto,
    DeploymentTargetUpdateWrite,
    DeploymentTargetsPortError,
    DeploymentTargetsViewState,
    LoadDeploymentTargetsCommand,
    UpdateDeploymentTargetCommand,
)
from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo


class _Sink:
    def __init__(self) -> None:
        self.states: list[DeploymentTargetsViewState] = []

    def apply_full_state(self, state: DeploymentTargetsViewState) -> None:
        self.states.append(state)


class _FakePort:
    def __init__(self, view: DeploymentTargetsViewState, *, fail_create: bool = False) -> None:
        self._view = view
        self.loads = 0
        self.creates = 0
        self.updates = 0
        self._fail_create = fail_create

    def load_targets_view(self) -> DeploymentTargetsViewState:
        self.loads += 1
        return self._view

    def get_target_editor_snapshot(self, target_id: str):
        from app.ui_contracts.workspaces.deployment_targets import DeploymentTargetEditorSnapshotDto

        del target_id
        return DeploymentTargetEditorSnapshotDto(
            target_id="x",
            name="N",
            kind="",
            notes="",
            project_id=None,
        )

    def create_target(self, write: DeploymentTargetCreateWrite) -> None:
        self.creates += 1
        del write
        if self._fail_create:
            raise DeploymentTargetsPortError("validation", "name required")

    def update_target(self, write: DeploymentTargetUpdateWrite) -> None:
        self.updates += 1
        del write


def _ready_row(name: str = "A") -> DeploymentTargetsViewState:
    row = DeploymentTargetTableRowDto(
        target_id="a",
        name=name,
        kind="",
        project_id=None,
        last_rollout_recorded_at="—",
        last_rollout_outcome="—",
    )
    return DeploymentTargetsViewState(phase="ready", rows=(row,), error=None, banner_message=None)


def test_presenter_load_shows_loading_then_ready() -> None:
    ready = _ready_row()
    sink = _Sink()
    port = _FakePort(ready)
    pres = DeploymentTargetsPresenter(sink, port)
    pres.handle_command(LoadDeploymentTargetsCommand())
    assert len(sink.states) == 2
    assert sink.states[0].phase == "loading"
    assert sink.states[1].phase == "ready"
    assert port.loads == 1


def test_presenter_load_error_state() -> None:
    err = DeploymentTargetsViewState(
        phase="error",
        rows=(),
        error=SettingsErrorInfo(code="e", message="fail"),
        banner_message=None,
    )
    sink = _Sink()
    pres = DeploymentTargetsPresenter(sink, _FakePort(err))
    pres.handle_command(LoadDeploymentTargetsCommand())
    assert sink.states[-1].phase == "error"


def test_presenter_create_reloads_table() -> None:
    ready = _ready_row()
    sink = _Sink()
    port = _FakePort(ready)
    pres = DeploymentTargetsPresenter(sink, port)
    pres.handle_command(CreateDeploymentTargetCommand(DeploymentTargetCreateWrite(name="z")))
    assert port.creates == 1
    assert port.loads == 1
    assert sink.states[-1].phase == "ready"


def test_presenter_create_failure_banner() -> None:
    ready = _ready_row()
    sink = _Sink()
    port = _FakePort(ready, fail_create=True)
    pres = DeploymentTargetsPresenter(sink, port)
    pres.handle_command(CreateDeploymentTargetCommand(DeploymentTargetCreateWrite(name="")))
    assert port.creates == 1
    assert port.loads == 1
    assert sink.states[-1].banner_message is not None
    assert sink.states[-1].banner_message.message == "name required"


def test_presenter_update_reloads() -> None:
    ready = _ready_row()
    sink = _Sink()
    port = _FakePort(ready)
    pres = DeploymentTargetsPresenter(sink, port)
    pres.handle_command(
        UpdateDeploymentTargetCommand(
            DeploymentTargetUpdateWrite(target_id="a", name="B"),
        ),
    )
    assert port.updates == 1
    assert port.loads == 1

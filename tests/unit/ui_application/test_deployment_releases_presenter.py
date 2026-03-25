"""DeploymentReleasesPresenter — Load Liste + Auswahl (Slice 3) + Mutationen (Batch 4)."""

from __future__ import annotations

from app.ui_application.presenters.deployment_releases_presenter import DeploymentReleasesPresenter
from app.ui_contracts.workspaces.deployment_releases import (
    ArchiveDeploymentReleaseCommand,
    CreateDeploymentReleaseCommand,
    DeploymentReleaseCreateWrite,
    DeploymentReleaseDetailDto,
    DeploymentReleaseHistoryRowDto,
    DeploymentReleaseSelectionState,
    DeploymentReleaseTableRowDto,
    DeploymentReleaseUpdateWrite,
    DeploymentReleasesPortError,
    DeploymentReleasesViewState,
    LoadDeploymentReleaseSelectionCommand,
    LoadDeploymentReleasesCommand,
    UpdateDeploymentReleaseCommand,
)
from app.ui_contracts.common.errors import SettingsErrorInfo


class _Sink:
    def __init__(self) -> None:
        self.states: list[DeploymentReleasesViewState] = []

    def apply_full_state(self, state: DeploymentReleasesViewState) -> None:
        self.states.append(state)


class _FakePort:
    def __init__(self, view: DeploymentReleasesViewState, *, fail_create: bool = False) -> None:
        self._view = view
        self.list_loads = 0
        self.selection_calls: list[str | None] = []
        self.creates = 0
        self.updates = 0
        self.archives = 0
        self._fail_create = fail_create

    def load_releases_list_view(self) -> DeploymentReleasesViewState:
        self.list_loads += 1
        return self._view

    def load_release_selection_state(self, release_id: str | None) -> DeploymentReleaseSelectionState:
        self.selection_calls.append(release_id)
        if not release_id:
            return DeploymentReleaseSelectionState(
                selected_release_id=None,
                detail=None,
                history_rows=(),
            )
        return DeploymentReleaseSelectionState(
            selected_release_id=release_id,
            detail=DeploymentReleaseDetailDto(
                display_name="R",
                version_label="1",
                lifecycle_status="ready",
                artifact_ref="x",
                artifact_kind="y",
            ),
            history_rows=(
                DeploymentReleaseHistoryRowDto(
                    recorded_at="t",
                    target_display_name="Z",
                    outcome="success",
                    workflow_run_id="",
                    message="",
                ),
            ),
        )

    def get_release_editor_snapshot(self, release_id: str):
        del release_id
        return None

    def create_release(self, write: DeploymentReleaseCreateWrite) -> None:
        self.creates += 1
        del write
        if self._fail_create:
            raise DeploymentReleasesPortError("validation", "bad")

    def update_release(self, write: DeploymentReleaseUpdateWrite) -> None:
        self.updates += 1
        del write

    def archive_release(self, release_id: str) -> None:
        self.archives += 1
        del release_id


def _ready_one_row() -> DeploymentReleasesViewState:
    row = DeploymentReleaseTableRowDto(
        release_id="rel1",
        display_name="N",
        version_label="v",
        lifecycle_status="ready",
        artifact_kind="",
        project_id=None,
    )
    return DeploymentReleasesViewState(phase="ready", rows=(row,), banner_message=None)


def test_presenter_load_shows_loading_then_ready() -> None:
    ready = _ready_one_row()
    sink = _Sink()
    port = _FakePort(ready)
    pres = DeploymentReleasesPresenter(sink, port)
    pres.handle_command(LoadDeploymentReleasesCommand())
    assert len(sink.states) == 2
    assert sink.states[0].phase == "loading"
    assert sink.states[1].phase == "ready"
    assert port.list_loads == 1


def test_presenter_load_then_refresh_selection_at_end_of_flow() -> None:
    ready = _ready_one_row()
    sink = _Sink()
    port = _FakePort(ready)
    pres = DeploymentReleasesPresenter(sink, port)
    pres.handle_command(LoadDeploymentReleasesCommand())
    pres.handle_command(LoadDeploymentReleaseSelectionCommand(None))
    assert port.selection_calls[-1] is None


def test_presenter_selection_merges_rows() -> None:
    ready = _ready_one_row()
    sink = _Sink()
    port = _FakePort(ready)
    pres = DeploymentReleasesPresenter(sink, port)
    pres.handle_command(LoadDeploymentReleasesCommand())
    pres.handle_command(LoadDeploymentReleaseSelectionCommand("rel1"))
    last = sink.states[-1]
    assert last.rows == ready.rows
    assert last.detail is not None
    assert last.detail.display_name == "R"
    assert len(last.history_rows) == 1


def test_presenter_load_error_skips_selection_merge_content() -> None:
    err = DeploymentReleasesViewState(
        phase="error",
        rows=(),
        error=SettingsErrorInfo(code="e", message="fail"),
        banner_message=None,
    )
    sink = _Sink()
    port = _FakePort(err)
    pres = DeploymentReleasesPresenter(sink, port)
    pres.handle_command(LoadDeploymentReleasesCommand())
    pres.handle_command(LoadDeploymentReleaseSelectionCommand("rel1"))
    assert sink.states[-1].phase == "error"
    assert sink.states[-1].detail is None


def test_presenter_create_reloads_list() -> None:
    ready = _ready_one_row()
    sink = _Sink()
    port = _FakePort(ready)
    pres = DeploymentReleasesPresenter(sink, port)
    pres.handle_command(
        CreateDeploymentReleaseCommand(
            DeploymentReleaseCreateWrite(display_name="a", version_label="1"),
            reselect_release_id_after=None,
        ),
    )
    assert port.creates == 1
    assert port.list_loads >= 1
    assert sink.states[-1].phase == "ready"


def test_presenter_create_failure_shows_banner() -> None:
    ready = _ready_one_row()
    sink = _Sink()
    port = _FakePort(ready, fail_create=True)
    pres = DeploymentReleasesPresenter(sink, port)
    pres.handle_command(
        CreateDeploymentReleaseCommand(
            DeploymentReleaseCreateWrite(display_name="a", version_label="1"),
        ),
    )
    assert port.creates == 1
    assert sink.states[-1].banner_message is not None
    assert sink.states[-1].banner_message.message == "bad"


def test_presenter_update_and_archive_call_port() -> None:
    ready = _ready_one_row()
    sink = _Sink()
    port = _FakePort(ready)
    pres = DeploymentReleasesPresenter(sink, port)
    pres.handle_command(LoadDeploymentReleasesCommand())
    pres.handle_command(
        UpdateDeploymentReleaseCommand(
            DeploymentReleaseUpdateWrite(
                release_id="rel1",
                display_name="x",
                version_label="v",
            ),
            reselect_release_id_after="rel1",
        ),
    )
    assert port.updates == 1
    pres.handle_command(ArchiveDeploymentReleaseCommand("rel1", reselect_release_id_after="rel1"))
    assert port.archives == 1

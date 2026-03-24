"""
DeploymentReleasesPresenter — Releases-Tab: Lesen (Slice 3) + Mutationen (Batch 4).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.deployment_releases_port import DeploymentReleasesPort
from app.ui_application.view_models.protocols import DeploymentReleasesUiSink
from app.ui_contracts.workspaces.deployment_releases import (
    ArchiveDeploymentReleaseCommand,
    CreateDeploymentReleaseCommand,
    DeploymentReleasesCommand,
    DeploymentReleasesPortError,
    DeploymentReleasesViewState,
    LoadDeploymentReleaseSelectionCommand,
    LoadDeploymentReleasesCommand,
    UpdateDeploymentReleaseCommand,
    deployment_releases_loading_state,
)
from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo


class DeploymentReleasesPresenter(BasePresenter):
    def __init__(self, sink: DeploymentReleasesUiSink, port: DeploymentReleasesPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port
        self._last_list_view: DeploymentReleasesViewState | None = None

    def handle_command(self, command: DeploymentReleasesCommand) -> None:
        if isinstance(command, LoadDeploymentReleasesCommand):
            self._load_list()
        elif isinstance(command, LoadDeploymentReleaseSelectionCommand):
            self._load_selection(command.release_id)
        elif isinstance(command, CreateDeploymentReleaseCommand):
            self._mutate_after(
                lambda: self._port.create_release(command.write),
                command.reselect_release_id_after,
            )
        elif isinstance(command, UpdateDeploymentReleaseCommand):
            self._mutate_after(
                lambda: self._port.update_release(command.write),
                command.reselect_release_id_after,
            )
        elif isinstance(command, ArchiveDeploymentReleaseCommand):
            self._mutate_after(
                lambda: self._port.archive_release(command.release_id),
                command.reselect_release_id_after,
            )

    def load_release_editor_snapshot(self, release_id: str):
        """Panel: Editor-Daten ohne direkten Service-Zugriff."""
        return self._port.get_release_editor_snapshot(release_id)

    def _load_list(self) -> None:
        self._sink.apply_full_state(deployment_releases_loading_state())
        view = self._port.load_releases_list_view()
        self._last_list_view = view
        self._sink.apply_full_state(view)

    def _load_selection(self, release_id: str | None) -> None:
        base = self._last_list_view
        if base is None:
            return
        if base.phase != "ready":
            self._sink.apply_full_state(
                replace(base, banner_message=None),
            )
            return
        sel = self._port.load_release_selection_state(release_id)
        self._sink.apply_full_state(
            replace(
                base,
                banner_message=None,
                selected_release_id=sel.selected_release_id,
                detail=sel.detail,
                history_rows=sel.history_rows,
            ),
        )

    def _mutate_after(self, fn: Callable[[], None], reselect_release_id: str | None) -> None:
        try:
            fn()
        except DeploymentReleasesPortError as exc:
            self._apply_mutation_failure(exc)
            return
        self._after_mutation_success(reselect_release_id)

    def _after_mutation_success(self, reselect_release_id: str | None) -> None:
        self._sink.apply_full_state(deployment_releases_loading_state())
        view = self._port.load_releases_list_view()
        self._last_list_view = view
        if view.phase != "ready":
            self._sink.apply_full_state(view)
            return
        sel = self._port.load_release_selection_state(reselect_release_id)
        self._sink.apply_full_state(
            replace(
                view,
                banner_message=None,
                selected_release_id=sel.selected_release_id,
                detail=sel.detail,
                history_rows=sel.history_rows,
            ),
        )

    def _apply_mutation_failure(self, exc: DeploymentReleasesPortError) -> None:
        view = self._port.load_releases_list_view()
        self._last_list_view = view
        if view.phase == "ready":
            self._sink.apply_full_state(
                replace(
                    view,
                    banner_message=SettingsErrorInfo(
                        code=exc.code,
                        message=exc.message,
                        recoverable=exc.recoverable,
                    ),
                    selected_release_id=None,
                    detail=None,
                    history_rows=(),
                ),
            )
        else:
            self._sink.apply_full_state(view)

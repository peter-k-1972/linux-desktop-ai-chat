"""
DeploymentTargetsPresenter — Targets-Tab: Laden + Mutationen (Slice 1–2).
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.deployment_targets_port import DeploymentTargetsPort
from app.ui_application.view_models.protocols import DeploymentTargetsUiSink
from app.ui_contracts.workspaces.deployment_targets import (
    CreateDeploymentTargetCommand,
    DeploymentTargetsCommand,
    DeploymentTargetsPortError,
    DeploymentTargetsViewState,
    LoadDeploymentTargetsCommand,
    DeploymentTargetCreateWrite,
    DeploymentTargetUpdateWrite,
    UpdateDeploymentTargetCommand,
    deployment_targets_loading_state,
)
from app.ui_contracts.common.errors import SettingsErrorInfo


class DeploymentTargetsPresenter(BasePresenter):
    def __init__(self, sink: DeploymentTargetsUiSink, port: DeploymentTargetsPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_command(self, command: DeploymentTargetsCommand) -> None:
        if isinstance(command, LoadDeploymentTargetsCommand):
            self._load_clearing_banner()
        elif isinstance(command, CreateDeploymentTargetCommand):
            self._mutate_after(lambda: self._port.create_target(command.write))
        elif isinstance(command, UpdateDeploymentTargetCommand):
            self._mutate_after(lambda: self._port.update_target(command.write))

    @staticmethod
    def _ready_without_banner(view: DeploymentTargetsViewState) -> DeploymentTargetsViewState:
        if view.phase == "ready":
            return replace(view, banner_message=None)
        return view

    def _load_clearing_banner(self) -> None:
        self._sink.apply_full_state(deployment_targets_loading_state())
        view = self._port.load_targets_view()
        self._sink.apply_full_state(self._ready_without_banner(view))

    def _mutate_after(self, fn: Callable[[], None]) -> None:
        try:
            fn()
        except DeploymentTargetsPortError as exc:
            self._apply_mutation_failure(exc)
            return
        self._load_clearing_banner()

    def _apply_mutation_failure(self, exc: DeploymentTargetsPortError) -> None:
        view = self._port.load_targets_view()
        if view.phase == "ready":
            self._sink.apply_full_state(
                replace(
                    view,
                    banner_message=SettingsErrorInfo(
                        code=exc.code,
                        message=exc.message,
                        recoverable=exc.recoverable,
                    ),
                )
            )
        else:
            self._sink.apply_full_state(view)

    def load_snapshot_for_editor(self, target_id: str):
        """Panel: Editor-Daten ohne direkten Service-Zugriff."""
        return self._port.get_target_editor_snapshot(target_id)

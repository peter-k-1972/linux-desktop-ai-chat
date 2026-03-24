"""
DeploymentRolloutsPresenter — Rollouts-Tab: Lesen (Slice 4).
"""

from __future__ import annotations

from app.ui_application.presenters.base_presenter import BasePresenter
from app.ui_application.ports.deployment_rollouts_port import DeploymentRolloutsPort
from app.ui_application.view_models.protocols import DeploymentRolloutsUiSink
from app.ui_contracts.workspaces.deployment_rollouts import (
    DeploymentRolloutRecordMutationResult,
    DeploymentRolloutsFilterSnapshot,
    LoadDeploymentRolloutsCommand,
    RecordDeploymentRolloutCommand,
    RolloutRecordComboSnapshot,
    deployment_rollouts_loading_state,
)


class DeploymentRolloutsPresenter(BasePresenter):
    def __init__(self, sink: DeploymentRolloutsUiSink, port: DeploymentRolloutsPort) -> None:
        super().__init__()
        self._sink = sink
        self._port = port

    def handle_command(self, command: LoadDeploymentRolloutsCommand) -> None:
        self._sink.apply_full_state(deployment_rollouts_loading_state(command.filter))
        view = self._port.load_rollouts_view(command.filter)
        self._sink.apply_full_state(view)

    def load_rollout_record_combo_options(self) -> RolloutRecordComboSnapshot:
        """Dialog-Combos: Presenter → Port → Adapter (kein direkter Widget-Service-Zugriff)."""
        return self._port.load_rollout_record_combo_options()

    def handle_record_rollout(
        self,
        command: RecordDeploymentRolloutCommand,
        refresh_filter: DeploymentRolloutsFilterSnapshot,
    ) -> DeploymentRolloutRecordMutationResult:
        result = self._port.record_deployment_rollout(command)
        if result.ok:
            self.handle_command(LoadDeploymentRolloutsCommand(refresh_filter))
        return result

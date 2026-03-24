"""
DeploymentRolloutsPort — Rollouts-Tab: Lesen inkl. Filter (Slice 4).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.ui_contracts.workspaces.deployment_rollouts import (
    DeploymentRolloutRecordMutationResult,
    DeploymentRolloutsFilterSnapshot,
    DeploymentRolloutsViewState,
    RecordDeploymentRolloutCommand,
    RolloutRecordComboSnapshot,
)


@runtime_checkable
class DeploymentRolloutsPort(Protocol):
    def load_rollouts_view(self, filter_snapshot: DeploymentRolloutsFilterSnapshot) -> DeploymentRolloutsViewState:
        """
        Liefert Ziel-/Release-Optionen für die Combos und die gefilterte Tabelle.

        ``active_filter`` im Ergebnis entspricht typischerweise ``filter_snapshot`` (Echo für den Sink).
        """
        ...

    def load_rollout_record_combo_options(self) -> RolloutRecordComboSnapshot:
        """Ziele + nur „ready“-Releases für ``RolloutRecordDialog`` (ohne Filter-„alle“-Einträge)."""
        ...

    def record_deployment_rollout(
        self,
        command: RecordDeploymentRolloutCommand,
    ) -> DeploymentRolloutRecordMutationResult:
        """Rollout protokollieren (Mutation)."""
        ...

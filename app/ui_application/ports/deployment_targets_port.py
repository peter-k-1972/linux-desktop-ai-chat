"""
DeploymentTargetsPort — Targets-Tab: Lesen + Mutationen (Slice 1–2).

Kein Mega-Port für Releases/Rollouts.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.ui_contracts.workspaces.deployment_targets import (
    DeploymentTargetCreateWrite,
    DeploymentTargetEditorSnapshotDto,
    DeploymentTargetUpdateWrite,
    DeploymentTargetsViewState,
)


@runtime_checkable
class DeploymentTargetsPort(Protocol):
    def load_targets_view(self) -> DeploymentTargetsViewState:
        """
        Liefert ``phase=ready`` mit Zeilen (ggf. leer) oder ``phase=error`` mit ``error`` gesetzt.

        Wirft bei erwartbaren Service-/DB-Fehlern nicht — Fehler werden im State transportiert.
        """
        ...

    def get_target_editor_snapshot(self, target_id: str) -> DeploymentTargetEditorSnapshotDto | None:
        """Liefert None, wenn das Ziel fehlt (wie Legacy „Ziel nicht gefunden“)."""
        ...

    def create_target(self, write: DeploymentTargetCreateWrite) -> None:
        """
        Delegiert an ``DeploymentOperationsService.create_target``.

        Raises:
            DeploymentTargetsPortError: Validierung / Persistenz (wie Legacy-Exception-Texte).
        """
        ...

    def update_target(self, write: DeploymentTargetUpdateWrite) -> None:
        """
        Delegiert an ``DeploymentOperationsService.update_target``.

        Raises:
            DeploymentTargetsPortError: unbekanntes Ziel, Validierung, Persistenz.
        """
        ...

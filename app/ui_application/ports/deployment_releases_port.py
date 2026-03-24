"""
DeploymentReleasesPort — Releases-Tab: Lesen (Slice 3) + Mutationen (Batch 4).

Kein Rollouts-Tab-Mutationspfad.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.ui_contracts.workspaces.deployment_releases import (
    DeploymentReleaseCreateWrite,
    DeploymentReleaseEditorSnapshotDto,
    DeploymentReleaseSelectionState,
    DeploymentReleaseUpdateWrite,
    DeploymentReleasesViewState,
)


@runtime_checkable
class DeploymentReleasesPort(Protocol):
    def load_releases_list_view(self) -> DeploymentReleasesViewState:
        """
        Liefert ``phase=ready`` mit Zeilen (ggf. leer) oder ``phase=error``.

        Auswahl-Felder sind leer bzw. ``None`` (nur Liste).
        """
        ...

    def load_release_selection_state(self, release_id: str | None) -> DeploymentReleaseSelectionState:
        """
        Liest ``get_release``, ``list_rollouts`` (Limit 200) und Zielnamen wie Legacy.

        Bei unbekanntem ``release_id`` oder fehlendem Release: leere Auswahl (wie Legacy).
        """
        ...

    def get_release_editor_snapshot(self, release_id: str) -> DeploymentReleaseEditorSnapshotDto | None:
        """Wie Legacy „Release nicht gefunden“ → ``None``."""
        ...

    def create_release(self, write: DeploymentReleaseCreateWrite) -> None:
        """
        Delegiert an ``DeploymentOperationsService.create_release``.

        Raises:
            DeploymentReleasesPortError: Validierung / Persistenz.
        """
        ...

    def update_release(self, write: DeploymentReleaseUpdateWrite) -> None:
        """
        Delegiert an ``DeploymentOperationsService.update_release``.

        Raises:
            DeploymentReleasesPortError: unbekanntes Release, Validierung, Persistenz.
        """
        ...

    def archive_release(self, release_id: str) -> None:
        """
        Delegiert an ``DeploymentOperationsService.archive_release``.

        Raises:
            DeploymentReleasesPortError: unbekanntes Release, Persistenz.
        """
        ...

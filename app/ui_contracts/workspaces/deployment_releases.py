"""
Deployment — Releases-Tab (Qt-frei).

Slice 3: Liste + Auswahl-Detail + Rollout-Historie pro Release (read).
Batch 4: Create / Update / Archive über Port (mit Legacy-Fallback).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union

from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo

DeploymentReleasesLoadPhase = Literal["loading", "ready", "error"]


@dataclass(frozen=True, slots=True)
class DeploymentReleaseTableRowDto:
    """Eine Zeile der Release-Hauptliste (wie ``ReleasesPanel``-Tabelle)."""

    release_id: str
    display_name: str
    version_label: str
    lifecycle_status: str
    artifact_kind: str
    project_id: int | None


@dataclass(frozen=True, slots=True)
class DeploymentReleaseDetailDto:
    """Detailbereich unterhalb der Liste (ohne HTML — Sink formatiert)."""

    display_name: str
    version_label: str
    lifecycle_status: str
    artifact_ref: str
    artifact_kind: str


@dataclass(frozen=True, slots=True)
class DeploymentReleaseHistoryRowDto:
    """Eine Zeile der Rollout-Historie zum gewählten Release."""

    recorded_at: str
    target_display_name: str
    outcome: str
    workflow_run_id: str
    message: str


@dataclass(frozen=True, slots=True)
class DeploymentReleasesViewState:
    """Vollzustand: Liste + optionale Auswahl inkl. Historie."""

    phase: DeploymentReleasesLoadPhase
    rows: tuple[DeploymentReleaseTableRowDto, ...]
    error: SettingsErrorInfo | None = None
    banner_message: SettingsErrorInfo | None = None
    selected_release_id: str | None = None
    detail: DeploymentReleaseDetailDto | None = None
    history_rows: tuple[DeploymentReleaseHistoryRowDto, ...] = ()


@dataclass(frozen=True, slots=True)
class DeploymentReleaseSelectionState:
    """Nur Auswahl-Teil; Presenter merged mit zuletzt geladener Liste."""

    selected_release_id: str | None
    detail: DeploymentReleaseDetailDto | None
    history_rows: tuple[DeploymentReleaseHistoryRowDto, ...]


@dataclass(frozen=True, slots=True)
class LoadDeploymentReleasesCommand:
    """Release-Liste neu laden (wie ``refresh``)."""


@dataclass(frozen=True, slots=True)
class LoadDeploymentReleaseSelectionCommand:
    """Detail + Historie für ``release_id``; ``None`` leert die rechte Seite."""

    release_id: str | None


@dataclass(frozen=True, slots=True)
class DeploymentReleaseEditorSnapshotDto:
    """Lese-Modell für ReleaseEditDialog (kein ORM/Record im Contract)."""

    release_id: str
    display_name: str
    version_label: str
    artifact_kind: str
    artifact_ref: str
    lifecycle_status: str
    project_id: int | None


@dataclass(frozen=True, slots=True)
class DeploymentReleaseCreateWrite:
    """Payload für ``create_release`` (Dialog → Port)."""

    display_name: str
    version_label: str
    artifact_kind: str = ""
    artifact_ref: str = ""
    project_id: int | None = None


@dataclass(frozen=True, slots=True)
class DeploymentReleaseUpdateWrite:
    """Payload für ``update_release``."""

    release_id: str
    display_name: str
    version_label: str
    artifact_kind: str = ""
    artifact_ref: str = ""
    lifecycle_status: str | None = None
    project_id: int | None = None


@dataclass(frozen=True, slots=True)
class CreateDeploymentReleaseCommand:
    write: DeploymentReleaseCreateWrite
    reselect_release_id_after: str | None = None


@dataclass(frozen=True, slots=True)
class UpdateDeploymentReleaseCommand:
    write: DeploymentReleaseUpdateWrite
    reselect_release_id_after: str | None = None


@dataclass(frozen=True, slots=True)
class ArchiveDeploymentReleaseCommand:
    release_id: str
    reselect_release_id_after: str | None = None


DeploymentReleasesCommand = Union[
    LoadDeploymentReleasesCommand,
    LoadDeploymentReleaseSelectionCommand,
    CreateDeploymentReleaseCommand,
    UpdateDeploymentReleaseCommand,
    ArchiveDeploymentReleaseCommand,
]


def deployment_releases_loading_state() -> DeploymentReleasesViewState:
    return DeploymentReleasesViewState(phase="loading", rows=())


class DeploymentReleasesPortError(Exception):
    """Mutation schlägt im Adapter mit bekannter Ursache fehl."""

    def __init__(self, code: str, message: str, *, recoverable: bool = True) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.recoverable = recoverable

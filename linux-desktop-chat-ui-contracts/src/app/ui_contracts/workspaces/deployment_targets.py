"""
Deployment — Targets-Tab (Qt-frei).

Slice 1: Liste inkl. letztem Rollout pro Ziel (read).
Slice 2: Create/Update über Port; Editor-Snapshot für Dialoge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Union

from app.ui_contracts.common.errors import SettingsErrorInfo

DeploymentTargetsLoadPhase = Literal["loading", "ready", "error"]


@dataclass(frozen=True, slots=True)
class DeploymentTargetTableRowDto:
    """Eine Tabellenzeile wie im TargetsPanel."""

    target_id: str
    name: str
    kind: str
    project_id: int | None
    last_rollout_recorded_at: str
    last_rollout_outcome: str


@dataclass(frozen=True, slots=True)
class DeploymentTargetsViewState:
    """Vollzustand für Anzeige (Lade-/Fehlerphase, optionales Banner nach Mutation)."""

    phase: DeploymentTargetsLoadPhase
    rows: tuple[DeploymentTargetTableRowDto, ...]
    error: SettingsErrorInfo | None = None
    banner_message: SettingsErrorInfo | None = None


@dataclass(frozen=True, slots=True)
class LoadDeploymentTargetsCommand:
    """Ziele inkl. letzter Rollouts neu laden."""


@dataclass(frozen=True, slots=True)
class DeploymentTargetCreateWrite:
    """Payload für ``create_target`` (Dialog → Port)."""

    name: str
    kind: str | None = None
    notes: str | None = None
    project_id: int | None = None


@dataclass(frozen=True, slots=True)
class DeploymentTargetUpdateWrite:
    """Payload für ``update_target``."""

    target_id: str
    name: str
    kind: str | None = None
    notes: str | None = None
    project_id: int | None = None


@dataclass(frozen=True, slots=True)
class DeploymentTargetEditorSnapshotDto:
    """Lese-Modell für TargetEditDialog (kein vollständiges Record-DTO)."""

    target_id: str
    name: str
    kind: str
    notes: str
    project_id: int | None


@dataclass(frozen=True, slots=True)
class CreateDeploymentTargetCommand:
    write: DeploymentTargetCreateWrite


@dataclass(frozen=True, slots=True)
class UpdateDeploymentTargetCommand:
    write: DeploymentTargetUpdateWrite


DeploymentTargetsCommand = Union[
    LoadDeploymentTargetsCommand,
    CreateDeploymentTargetCommand,
    UpdateDeploymentTargetCommand,
]


def deployment_targets_loading_state() -> DeploymentTargetsViewState:
    return DeploymentTargetsViewState(phase="loading", rows=(), error=None, banner_message=None)


class DeploymentTargetsPortError(Exception):
    """Mutation oder Lesen schlägt im Adapter mit bekannter Ursache fehl."""

    def __init__(self, code: str, message: str, *, recoverable: bool = True) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.recoverable = recoverable

"""
Deployment — Rollouts-Tab (Qt-frei).

Slice 4: Gefilterte Rollout-Historie + Combo-Optionen (read-only).
Batch 7: Mutation „Rollout protokollieren“ über Port/Adapter auf Hauptpfad.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo

DeploymentRolloutsLoadPhase = Literal["loading", "ready", "error"]


@dataclass(frozen=True, slots=True)
class DeploymentRolloutsFilterSnapshot:
    """
    Aktive Filter, wie das Legacy-``refresh`` sie aus den Combos baut.

    ``since_iso`` / ``until_iso``: wie ``RolloutListFilter`` (UTC-ISO), beide ``None`` = alle Zeiten.
    ``range_preset``: Spiegel von ``QComboBox.currentData()`` der Zeitraum-Combo (``None``, ``7``, ``30``),
    nur damit der Sink die Combo ohne Datums-Rückrechnung setzen kann.
    """

    target_id: str | None = None
    release_id: str | None = None
    outcome: str | None = None
    since_iso: str | None = None
    until_iso: str | None = None
    range_preset: int | None = None


@dataclass(frozen=True, slots=True)
class DeploymentRolloutFilterOptionDto:
    """Eintrag für Ziel- oder Release-Filter-Combo (erster Eintrag: ``value_id=None`` = alle)."""

    value_id: str | None
    label: str


@dataclass(frozen=True, slots=True)
class DeploymentRolloutTableRowDto:
    """Eine Zeile der Rollout-Haupttabelle (7 Spalten wie Legacy)."""

    recorded_at: str
    target_display_name: str
    release_display_name: str
    version_label: str
    outcome: str
    workflow_run_id: str
    message: str


@dataclass(frozen=True, slots=True)
class DeploymentRolloutsViewState:
    """Liste + Filteroptionen + zuletzt angewandter Filter."""

    phase: DeploymentRolloutsLoadPhase
    active_filter: DeploymentRolloutsFilterSnapshot
    target_options: tuple[DeploymentRolloutFilterOptionDto, ...] = ()
    release_options: tuple[DeploymentRolloutFilterOptionDto, ...] = ()
    table_rows: tuple[DeploymentRolloutTableRowDto, ...] = ()
    error: SettingsErrorInfo | None = None


@dataclass(frozen=True, slots=True)
class LoadDeploymentRolloutsCommand:
    """Rollouts inkl. Filter-Combos neu laden (wie ``refresh``)."""

    filter: DeploymentRolloutsFilterSnapshot


@dataclass(frozen=True, slots=True)
class RolloutRecordComboRowDto:
    """Eine Zeile für Ziel- bzw. Release-Combo im Dialog „Rollout protokollieren“ (ohne „alle“-Eintrag)."""

    value_id: str
    label: str


@dataclass(frozen=True, slots=True)
class RolloutRecordComboSnapshot:
    """Ziele (alle) + Releases nur mit Lifecycle „ready“, wie ``RolloutRecordDialog`` sie braucht."""

    targets: tuple[RolloutRecordComboRowDto, ...]
    ready_releases: tuple[RolloutRecordComboRowDto, ...]


@dataclass(frozen=True, slots=True)
class RecordDeploymentRolloutCommand:
    """Insert-only Rollout wie ``DeploymentOperationsService.record_rollout``."""

    release_id: str
    target_id: str
    outcome: str
    message: str | None = None
    started_at: str | None = None
    finished_at: str | None = None
    workflow_run_id: str | None = None
    project_id: int | None = None


@dataclass(frozen=True, slots=True)
class DeploymentRolloutRecordMutationResult:
    ok: bool
    error_message: str | None = None


def deployment_rollouts_loading_state(
    active_filter: DeploymentRolloutsFilterSnapshot,
) -> DeploymentRolloutsViewState:
    return DeploymentRolloutsViewState(phase="loading", active_filter=active_filter)

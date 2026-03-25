"""
Adapter: DeploymentOperationsService → Rollouts-Tab (Slice 4).

Technische Schuld:
- Pro Refresh mehrere Service-Leseaufrufe (Ziele, Releases, Rollouts, erneut Ziele/Releases für Join)
  — entspricht dem bisherigen ``refresh`` plus ``_reload_filter_combos``.
- Bei Fehlern wird ein konsolidierter Fehler-State geliefert (leere Optionen/Tabelle); im Legacy
  wäre die Exception durchgereicht worden.
"""

from __future__ import annotations

import logging

from app.core.deployment.models import (
    DeploymentReleaseRecord,
    DeploymentRolloutRecord,
    DeploymentTargetRecord,
    ReleaseLifecycle,
    RolloutListFilter,
)
from app.ui_contracts.workspaces.deployment_rollouts import (
    DeploymentRolloutFilterOptionDto,
    DeploymentRolloutRecordMutationResult,
    DeploymentRolloutTableRowDto,
    DeploymentRolloutsFilterSnapshot,
    DeploymentRolloutsViewState,
    RecordDeploymentRolloutCommand,
    RolloutRecordComboRowDto,
    RolloutRecordComboSnapshot,
)
from app.ui_contracts.common.errors import SettingsErrorInfo

logger = logging.getLogger(__name__)


def _target_options(targets: list[DeploymentTargetRecord]) -> tuple[DeploymentRolloutFilterOptionDto, ...]:
    opts = [DeploymentRolloutFilterOptionDto(value_id=None, label="(alle Ziele)")]
    for t in targets:
        opts.append(DeploymentRolloutFilterOptionDto(value_id=t.target_id, label=t.name))
    return tuple(opts)


def _release_options(releases: list[DeploymentReleaseRecord]) -> tuple[DeploymentRolloutFilterOptionDto, ...]:
    opts = [DeploymentRolloutFilterOptionDto(value_id=None, label="(alle Releases)")]
    for r in releases:
        label = f"{r.display_name} ({r.version_label})"
        opts.append(DeploymentRolloutFilterOptionDto(value_id=r.release_id, label=label))
    return tuple(opts)


def rollout_record_combo_snapshot_from_records(
    targets: list[DeploymentTargetRecord],
    ready_releases: list[DeploymentReleaseRecord],
) -> RolloutRecordComboSnapshot:
    """Reine Abbildung Service-Records → Dialog-DTOs (testbar ohne Qt/Service)."""
    t_rows = tuple(RolloutRecordComboRowDto(value_id=t.target_id, label=t.name) for t in targets)
    r_rows = tuple(
        RolloutRecordComboRowDto(
            value_id=r.release_id,
            label=f"{r.display_name} ({r.version_label})",
        )
        for r in ready_releases
    )
    return RolloutRecordComboSnapshot(targets=t_rows, ready_releases=r_rows)


def _table_row(
    o: DeploymentRolloutRecord,
    targets: dict[str, str],
    releases: dict[str, DeploymentReleaseRecord],
) -> DeploymentRolloutTableRowDto:
    rel = releases.get(o.release_id)
    rn = rel.display_name if rel else o.release_id
    rv = rel.version_label if rel else ""
    return DeploymentRolloutTableRowDto(
        recorded_at=o.recorded_at,
        target_display_name=targets.get(o.target_id, o.target_id),
        release_display_name=rn,
        version_label=rv,
        outcome=o.outcome,
        workflow_run_id=o.workflow_run_id or "",
        message=o.message or "",
    )


class ServiceDeploymentRolloutsAdapter:
    """Delegiert an ``get_deployment_operations_service()``."""

    def record_deployment_rollout(
        self,
        command: RecordDeploymentRolloutCommand,
    ) -> DeploymentRolloutRecordMutationResult:
        try:
            from app.services.deployment_operations_service import get_deployment_operations_service

            get_deployment_operations_service().record_rollout(
                release_id=command.release_id,
                target_id=command.target_id,
                outcome=command.outcome,
                message=command.message,
                started_at=command.started_at,
                finished_at=command.finished_at,
                workflow_run_id=command.workflow_run_id,
                project_id=command.project_id,
            )
            return DeploymentRolloutRecordMutationResult(ok=True)
        except Exception as exc:
            logger.warning("Rollout protokollieren fehlgeschlagen: %s", exc, exc_info=True)
            return DeploymentRolloutRecordMutationResult(
                ok=False,
                error_message=str(exc).strip()[:500],
            )

    def load_rollout_record_combo_options(self) -> RolloutRecordComboSnapshot:
        try:
            from app.services.deployment_operations_service import get_deployment_operations_service

            svc = get_deployment_operations_service()
            t_recs = svc.list_targets()
            r_recs = svc.list_releases(lifecycle_status=ReleaseLifecycle.READY)
            return rollout_record_combo_snapshot_from_records(t_recs, r_recs)
        except Exception as exc:
            logger.warning("Rollout-Record-Combos laden fehlgeschlagen: %s", exc, exc_info=True)
            return RolloutRecordComboSnapshot(targets=(), ready_releases=())

    def load_rollouts_view(self, filter_snapshot: DeploymentRolloutsFilterSnapshot) -> DeploymentRolloutsViewState:
        try:
            from app.services.deployment_operations_service import get_deployment_operations_service

            svc = get_deployment_operations_service()
            t_recs = svc.list_targets()
            r_recs = svc.list_releases()
            target_opts = _target_options(t_recs)
            release_opts = _release_options(r_recs)
            flt = RolloutListFilter(
                target_id=filter_snapshot.target_id,
                release_id=filter_snapshot.release_id,
                outcome=filter_snapshot.outcome,
                since_iso=filter_snapshot.since_iso,
                until_iso=filter_snapshot.until_iso,
                limit=800,
            )
            rollouts = svc.list_rollouts(flt)
            targets_map = {t.target_id: t.name for t in t_recs}
            releases_map = {r.release_id: r for r in r_recs}
            rows = tuple(_table_row(o, targets_map, releases_map) for o in rollouts)
            return DeploymentRolloutsViewState(
                phase="ready",
                active_filter=filter_snapshot,
                target_options=target_opts,
                release_options=release_opts,
                table_rows=rows,
            )
        except Exception as exc:
            logger.warning("Deployment-Rollouts laden fehlgeschlagen: %s", exc, exc_info=True)
            return DeploymentRolloutsViewState(
                phase="error",
                active_filter=filter_snapshot,
                error=SettingsErrorInfo(
                    code="load_rollouts_failed",
                    message="Rollouts konnten nicht geladen werden.",
                    recoverable=True,
                    detail=str(exc),
                ),
            )

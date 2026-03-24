"""
Adapter: DeploymentOperationsService → Deployment Targets View + Mutationen (Slice 1–2).

Technische Schuld:
- Zwei Service-Aufrufe pro Refresh (``list_targets`` + ``get_last_rollout_per_target``) — 1:1 Legacy.
- ``load_targets_view`` mappt Exceptions in State; Mutationen werfen :class:`DeploymentTargetsPortError`
  (Presenter zeigt Banner + Tabellen-Reload).
"""

from __future__ import annotations

import logging

from app.core.deployment.models import DeploymentRolloutRecord, DeploymentTargetRecord
from app.ui_contracts.workspaces.deployment_targets import (
    DeploymentTargetCreateWrite,
    DeploymentTargetEditorSnapshotDto,
    DeploymentTargetTableRowDto,
    DeploymentTargetUpdateWrite,
    DeploymentTargetsPortError,
    DeploymentTargetsViewState,
)
from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo

logger = logging.getLogger(__name__)


def _row_from_records(
    t: DeploymentTargetRecord,
    last: DeploymentRolloutRecord | None,
) -> DeploymentTargetTableRowDto:
    lr_at = last.recorded_at if last else "—"
    oc = last.outcome if last else "—"
    return DeploymentTargetTableRowDto(
        target_id=t.target_id,
        name=t.name,
        kind=(t.kind or "").strip(),
        project_id=t.project_id,
        last_rollout_recorded_at=lr_at,
        last_rollout_outcome=oc,
    )


class ServiceDeploymentTargetsAdapter:
    """Delegiert an ``get_deployment_operations_service()``."""

    def load_targets_view(self) -> DeploymentTargetsViewState:
        try:
            from app.services.deployment_operations_service import get_deployment_operations_service

            svc = get_deployment_operations_service()
            last_by_t = svc.get_last_rollout_per_target()
            targets = svc.list_targets()
            rows = tuple(_row_from_records(t, last_by_t.get(t.target_id)) for t in targets)
            return DeploymentTargetsViewState(
                phase="ready",
                rows=rows,
                error=None,
                banner_message=None,
            )
        except Exception as exc:
            logger.warning("Deployment-Ziele laden fehlgeschlagen: %s", exc, exc_info=True)
            return DeploymentTargetsViewState(
                phase="error",
                rows=(),
                error=SettingsErrorInfo(
                    code="load_targets_failed",
                    message="Ziele konnten nicht geladen werden.",
                    recoverable=True,
                    detail=str(exc),
                ),
                banner_message=None,
            )

    def get_target_editor_snapshot(self, target_id: str) -> DeploymentTargetEditorSnapshotDto | None:
        from app.services.deployment_operations_service import get_deployment_operations_service

        t = get_deployment_operations_service().get_target(target_id)
        if t is None:
            return None
        return DeploymentTargetEditorSnapshotDto(
            target_id=t.target_id,
            name=t.name or "",
            kind=(t.kind or "").strip(),
            notes=(t.notes or "").strip(),
            project_id=t.project_id,
        )

    def create_target(self, write: DeploymentTargetCreateWrite) -> None:
        from app.services.deployment_operations_service import get_deployment_operations_service

        try:
            get_deployment_operations_service().create_target(
                name=write.name,
                kind=write.kind,
                notes=write.notes,
                project_id=write.project_id,
            )
        except ValueError as exc:
            raise DeploymentTargetsPortError("validation", str(exc), recoverable=True) from exc
        except Exception as exc:
            logger.warning("create_target fehlgeschlagen: %s", exc, exc_info=True)
            raise DeploymentTargetsPortError(
                "create_target_failed",
                str(exc),
                recoverable=True,
            ) from exc

    def update_target(self, write: DeploymentTargetUpdateWrite) -> None:
        from app.services.deployment_operations_service import get_deployment_operations_service

        try:
            get_deployment_operations_service().update_target(
                target_id=write.target_id,
                name=write.name,
                kind=write.kind,
                notes=write.notes,
                project_id=write.project_id,
            )
        except ValueError as exc:
            raise DeploymentTargetsPortError("validation", str(exc), recoverable=True) from exc
        except Exception as exc:
            logger.warning("update_target fehlgeschlagen: %s", exc, exc_info=True)
            raise DeploymentTargetsPortError(
                "update_target_failed",
                str(exc),
                recoverable=True,
            ) from exc

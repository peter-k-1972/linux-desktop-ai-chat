"""
Adapter: DeploymentOperationsService → Releases-Listen- und Auswahl-View (Slice 3).

Technische Schuld:
- Auswahl lädt jedes Mal ``list_targets()`` für die Namensauflösung — 1:1 wie Legacy ``_on_sel``.
- Keine Batch-API im Service; Reihenfolge der Aufrufe entspricht dem bisherigen Panel.
"""

from __future__ import annotations

import logging

from app.core.deployment.models import DeploymentReleaseRecord, DeploymentRolloutRecord, ReleaseLifecycle, RolloutListFilter
from app.ui_contracts.workspaces.deployment_releases import (
    DeploymentReleaseCreateWrite,
    DeploymentReleaseDetailDto,
    DeploymentReleaseEditorSnapshotDto,
    DeploymentReleaseHistoryRowDto,
    DeploymentReleaseSelectionState,
    DeploymentReleaseTableRowDto,
    DeploymentReleaseUpdateWrite,
    DeploymentReleasesPortError,
    DeploymentReleasesViewState,
)
from app.ui_contracts.workspaces.settings_appearance import SettingsErrorInfo

logger = logging.getLogger(__name__)


def _row_from_release(r: DeploymentReleaseRecord) -> DeploymentReleaseTableRowDto:
    ak = (r.artifact_kind or "").strip()
    return DeploymentReleaseTableRowDto(
        release_id=r.release_id,
        display_name=r.display_name,
        version_label=r.version_label,
        lifecycle_status=r.lifecycle_status,
        artifact_kind=ak,
        project_id=r.project_id,
    )


def _detail_from_release(rel: DeploymentReleaseRecord) -> DeploymentReleaseDetailDto:
    return DeploymentReleaseDetailDto(
        display_name=rel.display_name,
        version_label=rel.version_label,
        lifecycle_status=rel.lifecycle_status,
        artifact_ref=(rel.artifact_ref or "").strip(),
        artifact_kind=(rel.artifact_kind or "").strip(),
    )


class ServiceDeploymentReleasesAdapter:
    """Delegiert an ``get_deployment_operations_service()``."""

    def load_releases_list_view(self) -> DeploymentReleasesViewState:
        try:
            from app.services.deployment_operations_service import get_deployment_operations_service

            svc = get_deployment_operations_service()
            releases = svc.list_releases()
            rows = tuple(_row_from_release(r) for r in releases)
            return DeploymentReleasesViewState(
                phase="ready",
                rows=rows,
                banner_message=None,
            )
        except Exception as exc:
            logger.warning("Deployment-Releases laden fehlgeschlagen: %s", exc, exc_info=True)
            return DeploymentReleasesViewState(
                phase="error",
                rows=(),
                error=SettingsErrorInfo(
                    code="load_releases_failed",
                    message="Releases konnten nicht geladen werden.",
                    recoverable=True,
                    detail=str(exc),
                ),
                banner_message=None,
            )

    def load_release_selection_state(self, release_id: str | None) -> DeploymentReleaseSelectionState:
        if not release_id:
            return DeploymentReleaseSelectionState(
                selected_release_id=None,
                detail=None,
                history_rows=(),
            )
        try:
            from app.services.deployment_operations_service import get_deployment_operations_service

            svc = get_deployment_operations_service()
            rel = svc.get_release(release_id)
            if rel is None:
                return DeploymentReleaseSelectionState(
                    selected_release_id=None,
                    detail=None,
                    history_rows=(),
                )
            rollouts = svc.list_rollouts(RolloutListFilter(release_id=release_id, limit=200))
            targets = {t.target_id: t.name for t in svc.list_targets()}
            hist = tuple(_history_row(o, targets) for o in rollouts)
            return DeploymentReleaseSelectionState(
                selected_release_id=release_id,
                detail=_detail_from_release(rel),
                history_rows=hist,
            )
        except Exception as exc:
            logger.warning("Deployment-Release-Auswahl laden fehlgeschlagen: %s", exc, exc_info=True)
            return DeploymentReleaseSelectionState(
                selected_release_id=None,
                detail=None,
                history_rows=(),
            )

    def get_release_editor_snapshot(self, release_id: str) -> DeploymentReleaseEditorSnapshotDto | None:
        from app.services.deployment_operations_service import get_deployment_operations_service

        rel = get_deployment_operations_service().get_release(release_id)
        if rel is None:
            return None
        return DeploymentReleaseEditorSnapshotDto(
            release_id=rel.release_id,
            display_name=rel.display_name or "",
            version_label=rel.version_label or "",
            artifact_kind=(rel.artifact_kind or "").strip(),
            artifact_ref=(rel.artifact_ref or "").strip(),
            lifecycle_status=rel.lifecycle_status or "",
            project_id=rel.project_id,
        )

    def create_release(self, write: DeploymentReleaseCreateWrite) -> None:
        from app.services.deployment_operations_service import get_deployment_operations_service

        try:
            get_deployment_operations_service().create_release(
                display_name=write.display_name,
                version_label=write.version_label,
                artifact_kind=write.artifact_kind,
                artifact_ref=write.artifact_ref,
                lifecycle_status=ReleaseLifecycle.DRAFT,
                project_id=write.project_id,
            )
        except ValueError as exc:
            raise DeploymentReleasesPortError("validation", str(exc), recoverable=True) from exc
        except Exception as exc:
            logger.warning("create_release fehlgeschlagen: %s", exc, exc_info=True)
            raise DeploymentReleasesPortError(
                "create_release_failed",
                str(exc),
                recoverable=True,
            ) from exc

    def update_release(self, write: DeploymentReleaseUpdateWrite) -> None:
        from app.services.deployment_operations_service import get_deployment_operations_service

        try:
            get_deployment_operations_service().update_release(
                release_id=write.release_id,
                display_name=write.display_name,
                version_label=write.version_label,
                artifact_kind=write.artifact_kind,
                artifact_ref=write.artifact_ref,
                lifecycle_status=write.lifecycle_status,
                project_id=write.project_id,
            )
        except ValueError as exc:
            raise DeploymentReleasesPortError("validation", str(exc), recoverable=True) from exc
        except Exception as exc:
            logger.warning("update_release fehlgeschlagen: %s", exc, exc_info=True)
            raise DeploymentReleasesPortError(
                "update_release_failed",
                str(exc),
                recoverable=True,
            ) from exc

    def archive_release(self, release_id: str) -> None:
        from app.services.deployment_operations_service import get_deployment_operations_service

        try:
            get_deployment_operations_service().archive_release(release_id)
        except ValueError as exc:
            raise DeploymentReleasesPortError("validation", str(exc), recoverable=True) from exc
        except Exception as exc:
            logger.warning("archive_release fehlgeschlagen: %s", exc, exc_info=True)
            raise DeploymentReleasesPortError(
                "archive_release_failed",
                str(exc),
                recoverable=True,
            ) from exc


def _history_row(
    o: DeploymentRolloutRecord,
    targets: dict[str, str],
) -> DeploymentReleaseHistoryRowDto:
    return DeploymentReleaseHistoryRowDto(
        recorded_at=o.recorded_at,
        target_display_name=targets.get(o.target_id, o.target_id),
        outcome=o.outcome,
        workflow_run_id=o.workflow_run_id or "",
        message=o.message or "",
    )

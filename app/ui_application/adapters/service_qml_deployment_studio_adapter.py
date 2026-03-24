"""Adapter: :class:`QmlDeploymentStudioPort` → :class:`app.services.deployment_operations_service`."""

from __future__ import annotations

from typing import Optional

from app.core.deployment.models import DeploymentReleaseRecord, DeploymentTargetRecord
from app.services.deployment_operations_service import get_deployment_operations_service


class ServiceQmlDeploymentStudioAdapter:
    def list_releases(self) -> list[DeploymentReleaseRecord]:
        return get_deployment_operations_service().list_releases()

    def get_release(self, release_id: str) -> DeploymentReleaseRecord | None:
        return get_deployment_operations_service().get_release(release_id)

    def update_release(
        self,
        *,
        release_id: str,
        display_name: str,
        version_label: str,
        artifact_kind: str,
        artifact_ref: str,
        lifecycle_status: str,
        project_id: Optional[int],
    ) -> None:
        get_deployment_operations_service().update_release(
            release_id=release_id,
            display_name=display_name,
            version_label=version_label,
            artifact_kind=artifact_kind,
            artifact_ref=artifact_ref,
            lifecycle_status=lifecycle_status,
            project_id=project_id,
        )

    def list_targets(self) -> list[DeploymentTargetRecord]:
        return get_deployment_operations_service().list_targets()

    def record_rollout(
        self,
        *,
        release_id: str,
        target_id: str,
        outcome: str,
        message: str,
        project_id: Optional[int],
    ) -> None:
        get_deployment_operations_service().record_rollout(
            release_id=release_id,
            target_id=target_id,
            outcome=outcome,
            message=message,
            project_id=project_id,
        )

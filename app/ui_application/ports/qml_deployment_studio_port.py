"""
QML Deployment-Studio — Lesen/Schreiben von Releases, Zielen und Rollouts.
"""

from __future__ import annotations

from typing import Optional, Protocol, runtime_checkable

from app.core.deployment.models import DeploymentReleaseRecord, DeploymentTargetRecord


@runtime_checkable
class QmlDeploymentStudioPort(Protocol):
    def list_releases(self) -> list[DeploymentReleaseRecord]:
        ...

    def get_release(self, release_id: str) -> DeploymentReleaseRecord | None:
        ...

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
        ...

    def list_targets(self) -> list[DeploymentTargetRecord]:
        ...

    def record_rollout(
        self,
        *,
        release_id: str,
        target_id: str,
        outcome: str,
        message: str,
        project_id: Optional[int],
    ) -> None:
        ...

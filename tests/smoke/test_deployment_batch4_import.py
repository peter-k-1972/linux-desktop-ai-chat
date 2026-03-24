"""Smoke: Deployment Batch 4 (Targets-/Releases-Mutationen am Port)."""


def test_deployment_batch4_imports() -> None:
    from app.ui_application.adapters.service_deployment_releases_adapter import ServiceDeploymentReleasesAdapter
    from app.ui_application.ports.deployment_releases_port import DeploymentReleasesPort
    from app.ui_application.presenters.deployment_releases_presenter import DeploymentReleasesPresenter
    from app.ui_contracts.workspaces.deployment_releases import (
        ArchiveDeploymentReleaseCommand,
        CreateDeploymentReleaseCommand,
        DeploymentReleaseCreateWrite,
    )

    a = ServiceDeploymentReleasesAdapter()
    assert hasattr(a, "create_release")
    assert hasattr(a, "archive_release")
    assert hasattr(DeploymentReleasesPort, "get_release_editor_snapshot")
    assert DeploymentReleasesPresenter.__name__ == "DeploymentReleasesPresenter"
    assert CreateDeploymentReleaseCommand(DeploymentReleaseCreateWrite("a", "1")).write.display_name == "a"
    assert ArchiveDeploymentReleaseCommand("r").release_id == "r"

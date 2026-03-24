"""Smoke: Deployment Slice 3 (Releases read-only)."""


def test_deployment_slice3_contracts_port_presenter_sink() -> None:
    from app.gui.domains.operations.deployment.deployment_releases_sink import DeploymentReleasesSink
    from app.ui_application.adapters.service_deployment_releases_adapter import ServiceDeploymentReleasesAdapter
    from app.ui_application.ports.deployment_releases_port import DeploymentReleasesPort
    from app.ui_application.presenters.deployment_releases_presenter import DeploymentReleasesPresenter
    from app.ui_contracts.workspaces.deployment_releases import (
        LoadDeploymentReleasesCommand,
        deployment_releases_loading_state,
    )

    assert LoadDeploymentReleasesCommand() is not None
    assert deployment_releases_loading_state().phase == "loading"
    assert DeploymentReleasesPort.__name__ == "DeploymentReleasesPort"
    assert ServiceDeploymentReleasesAdapter.__name__ == "ServiceDeploymentReleasesAdapter"
    assert DeploymentReleasesPresenter.__name__ == "DeploymentReleasesPresenter"
    assert DeploymentReleasesSink.__name__ == "DeploymentReleasesSink"


def test_deployment_workspace_imports() -> None:
    from app.gui.domains.operations.deployment.deployment_workspace import DeploymentWorkspace

    assert DeploymentWorkspace.__name__ == "DeploymentWorkspace"

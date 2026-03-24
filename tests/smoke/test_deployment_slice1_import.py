"""Smoke: Deployment Slice 1 (Targets read-path)."""


def test_deployment_slice1_imports() -> None:
    from app.gui.domains.operations.deployment.deployment_targets_sink import DeploymentTargetsSink
    from app.gui.domains.operations.deployment.deployment_workspace import DeploymentWorkspace
    from app.gui.domains.operations.deployment.panels.targets_panel import TargetsPanel
    from app.ui_application.adapters.service_deployment_targets_adapter import ServiceDeploymentTargetsAdapter
    from app.ui_application.presenters.deployment_targets_presenter import DeploymentTargetsPresenter
    from app.ui_application.ports.deployment_targets_port import DeploymentTargetsPort
    from app.ui_contracts.workspaces.deployment_targets import DeploymentTargetsViewState

    assert DeploymentWorkspace.__name__ == "DeploymentWorkspace"
    assert TargetsPanel.__name__ == "TargetsPanel"
    assert DeploymentTargetsViewState.__name__ == "DeploymentTargetsViewState"
    assert callable(ServiceDeploymentTargetsAdapter().load_targets_view)
    assert DeploymentTargetsPort.__name__ == "DeploymentTargetsPort"
    assert DeploymentTargetsPresenter.__name__ == "DeploymentTargetsPresenter"
    assert DeploymentTargetsSink.__name__ == "DeploymentTargetsSink"

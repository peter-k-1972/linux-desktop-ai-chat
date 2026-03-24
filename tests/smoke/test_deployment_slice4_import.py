"""Smoke: Deployment Slice 4 (Rollouts read-only)."""


def test_deployment_slice4_stack_imports() -> None:
    from app.gui.domains.operations.deployment.deployment_rollouts_sink import DeploymentRolloutsSink
    from app.ui_application.adapters.service_deployment_rollouts_adapter import ServiceDeploymentRolloutsAdapter
    from app.ui_application.ports.deployment_rollouts_port import DeploymentRolloutsPort
    from app.ui_application.presenters.deployment_rollouts_presenter import DeploymentRolloutsPresenter
    from app.ui_contracts.workspaces.deployment_rollouts import (
        DeploymentRolloutsFilterSnapshot,
        LoadDeploymentRolloutsCommand,
        RolloutRecordComboSnapshot,
        deployment_rollouts_loading_state,
    )

    flt = DeploymentRolloutsFilterSnapshot()
    assert LoadDeploymentRolloutsCommand(flt).filter == flt
    assert deployment_rollouts_loading_state(flt).phase == "loading"
    assert RolloutRecordComboSnapshot(targets=(), ready_releases=()).targets == ()
    assert DeploymentRolloutsPort.__name__ == "DeploymentRolloutsPort"
    assert ServiceDeploymentRolloutsAdapter.__name__ == "ServiceDeploymentRolloutsAdapter"
    assert DeploymentRolloutsPresenter.__name__ == "DeploymentRolloutsPresenter"
    assert DeploymentRolloutsSink.__name__ == "DeploymentRolloutsSink"


def test_deployment_workspace_still_imports() -> None:
    from app.gui.domains.operations.deployment.deployment_workspace import DeploymentWorkspace

    assert DeploymentWorkspace.__name__ == "DeploymentWorkspace"

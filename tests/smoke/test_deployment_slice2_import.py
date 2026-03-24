"""Smoke: Deployment Slice 2 (Targets-Mutationen)."""


def test_deployment_slice2_contracts_and_port() -> None:
    from app.ui_contracts.workspaces.deployment_targets import (
        CreateDeploymentTargetCommand,
        DeploymentTargetCreateWrite,
        DeploymentTargetsPortError,
        UpdateDeploymentTargetCommand,
    )
    from app.ui_application.ports.deployment_targets_port import DeploymentTargetsPort

    assert CreateDeploymentTargetCommand(DeploymentTargetCreateWrite(name="x")).write.name == "x"
    assert DeploymentTargetsPort.__name__ == "DeploymentTargetsPort"
    assert DeploymentTargetsPortError("c", "m").message == "m"

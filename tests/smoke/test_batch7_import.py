"""Smoke: Batch 7 — Rollout-Record + Library-Delete + Template-Mutationen."""

from __future__ import annotations


def test_batch7_modules_import() -> None:
    from app.ui_application.ports.deployment_rollouts_port import DeploymentRolloutsPort
    from app.ui_application.ports.prompt_studio_port import PromptStudioPort
    from app.ui_contracts.workspaces.deployment_rollouts import RecordDeploymentRolloutCommand
    from app.ui_contracts.workspaces.prompt_studio_library import DeletePromptLibraryCommand
    from app.ui_contracts.workspaces.prompt_studio_templates import CreatePromptTemplateCommand

    assert hasattr(DeploymentRolloutsPort, "record_deployment_rollout")
    assert hasattr(PromptStudioPort, "delete_prompt_library_entry")
    assert hasattr(PromptStudioPort, "create_prompt_template")
    assert isinstance(RecordDeploymentRolloutCommand("r", "t", "success"), RecordDeploymentRolloutCommand)
    assert DeletePromptLibraryCommand(1, None).prompt_id == 1
    assert CreatePromptTemplateCommand("a", "", "", "global", None).title == "a"

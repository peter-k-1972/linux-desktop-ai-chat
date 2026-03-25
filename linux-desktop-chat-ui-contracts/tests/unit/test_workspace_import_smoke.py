"""Stichprobe: Workspace-Submodule importierbar."""

from __future__ import annotations

from app.ui_contracts.workspaces.chat import merge_chat_state
from app.ui_contracts.workspaces.deployment_targets import DeploymentTargetsPortError


def test_workspace_modules_importable():
    assert merge_chat_state is not None
    assert DeploymentTargetsPortError is not None

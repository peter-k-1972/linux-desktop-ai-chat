"""Prompt Studio Workspace op result — Batch 3."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from app.ui_contracts.workspaces.prompt_studio_editor import PromptStudioPromptSnapshotDto
from app.ui_contracts.workspaces.prompt_studio_workspace import PromptStudioWorkspaceOpResult


def test_workspace_op_result_ok() -> None:
    snap = PromptStudioPromptSnapshotDto(
        prompt_id=1,
        title="t",
        content="",
        description="",
        category="general",
        scope="global",
        project_id=None,
        prompt_type="user",
        tags=(),
    )
    r = PromptStudioWorkspaceOpResult(ok=True, snapshot=snap)
    assert r.ok and r.error_message is None

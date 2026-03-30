"""Prompt Studio Editor — Batch-3-Contracts."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.contract  # @pytest.mark.contract (Marker-Disziplin)


from app.ui_contracts.workspaces.prompt_studio_editor import (
    PromptEditorSaveResultState,
    PromptStudioPromptSnapshotDto,
    SavePromptVersionEditorCommand,
    UpdatePromptMetadataEditorCommand,
    prompt_editor_save_idle_state,
    prompt_editor_save_saving_state,
)


def test_save_version_command_fields() -> None:
    c = SavePromptVersionEditorCommand(prompt_id=3, title="A", content="B")
    assert c.prompt_id == 3


def test_update_metadata_command_fields() -> None:
    c = UpdatePromptMetadataEditorCommand(
        prompt_id=1,
        title="t",
        content="c",
        description="d",
        category="general",
        scope="global",
        project_id=None,
    )
    assert c.scope == "global"


def test_save_result_phases() -> None:
    assert prompt_editor_save_saving_state().phase == "saving"
    assert prompt_editor_save_idle_state().phase == "idle"
    snap = PromptStudioPromptSnapshotDto(
        prompt_id=9,
        title="x",
        content="y",
        description="",
        category="general",
        scope="global",
        project_id=None,
        prompt_type="user",
        tags=(),
    )
    ok = PromptEditorSaveResultState(phase="success", snapshot=snap)
    assert ok.snapshot is not None
    assert ok.snapshot.prompt_id == 9

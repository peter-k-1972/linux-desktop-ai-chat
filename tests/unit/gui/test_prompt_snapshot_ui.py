"""prompt_snapshot_ui — reine DTO→Prompt-Abbildung (Batch 8)."""

from __future__ import annotations

from app.gui.domains.operations.prompt_studio.prompt_snapshot_ui import prompt_from_snapshot
from app.ui_contracts.workspaces.prompt_studio_editor import PromptStudioPromptSnapshotDto


def test_prompt_from_snapshot_maps_fields() -> None:
    dto = PromptStudioPromptSnapshotDto(
        prompt_id=7,
        title="T",
        content="body",
        description="d",
        category="c",
        scope="project",
        project_id=3,
        prompt_type="user",
        tags=("a", "b"),
    )
    p = prompt_from_snapshot(dto)
    assert p.id == 7
    assert p.title == "T"
    assert p.content == "body"
    assert p.tags == ["a", "b"]
    assert p.scope == "project"
    assert p.project_id == 3

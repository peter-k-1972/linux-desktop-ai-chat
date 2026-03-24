"""Smoke: Batch 8 — Snapshot-Helper, keine Zyklen über Templates ↔ Workspace."""

from __future__ import annotations


def test_batch8_prompt_snapshot_and_panels_import() -> None:
    from app.gui.domains.operations.prompt_studio.prompt_snapshot_ui import prompt_from_snapshot
    from app.gui.domains.operations.prompt_studio.panels.library_panel import PromptLibraryPanel
    from app.gui.domains.operations.prompt_studio.panels.prompt_templates_panel import (
        PromptTemplatesPanel,
    )
    from app.ui_contracts.workspaces.prompt_studio_editor import PromptStudioPromptSnapshotDto

    assert callable(prompt_from_snapshot)
    dto = PromptStudioPromptSnapshotDto(
        prompt_id=1,
        title="x",
        content="",
        description="",
        category="general",
        scope="global",
        project_id=None,
        prompt_type="user",
        tags=(),
    )
    assert prompt_from_snapshot(dto).id == 1
    assert PromptLibraryPanel.__name__ == "PromptLibraryPanel"
    assert PromptTemplatesPanel.__name__ == "PromptTemplatesPanel"

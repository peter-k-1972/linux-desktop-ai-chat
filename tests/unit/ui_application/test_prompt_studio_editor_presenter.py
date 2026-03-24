"""PromptStudioEditorPresenter."""

from __future__ import annotations

from unittest.mock import MagicMock

from app.ui_application.presenters.prompt_studio_editor_presenter import PromptStudioEditorPresenter
from app.ui_contracts.workspaces.prompt_studio_editor import (
    PromptEditorSaveResultState,
    PromptStudioPromptSnapshotDto,
    SavePromptVersionEditorCommand,
)


def test_persist_emits_saving_then_result() -> None:
    sink = MagicMock()
    port = MagicMock()
    snap = PromptStudioPromptSnapshotDto(
        prompt_id=1,
        title="a",
        content="b",
        description="",
        category="general",
        scope="global",
        project_id=None,
        prompt_type="user",
        tags=(),
    )
    port.persist_prompt_editor.return_value = PromptEditorSaveResultState(
        phase="success",
        snapshot=snap,
    )
    pre = PromptStudioEditorPresenter(sink, port)
    cmd = SavePromptVersionEditorCommand(prompt_id=1, title="a", content="b")
    pre.persist(cmd)
    assert sink.apply_save_result.call_count == 2
    first = sink.apply_save_result.call_args_list[0][0][0]
    second = sink.apply_save_result.call_args_list[1][0][0]
    assert first.phase == "saving"
    assert second.phase == "success"
    port.persist_prompt_editor.assert_called_once_with(cmd)

"""PromptStudioEditorSink."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QLabel, QApplication

from app.gui.domains.operations.prompt_studio.prompt_studio_editor_sink import PromptStudioEditorSink
from app.ui_contracts.workspaces.prompt_studio_editor import (
    PromptEditorSaveResultState,
    PromptStudioPromptSnapshotDto,
)


@pytest.fixture
def qapplication():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_sink_success_calls_on_success(qapplication) -> None:
    lbl = QLabel()
    ok = MagicMock()
    err = MagicMock()
    sink = PromptStudioEditorSink(lbl, on_success=ok, on_error=err)
    snap = PromptStudioPromptSnapshotDto(
        prompt_id=1,
        title="t",
        content="c",
        description="",
        category="general",
        scope="global",
        project_id=None,
        prompt_type="user",
        tags=(),
    )
    sink.apply_save_result(PromptEditorSaveResultState(phase="success", snapshot=snap))
    ok.assert_called_once_with(snap)
    err.assert_not_called()


def test_sink_error_calls_on_error(qapplication) -> None:
    lbl = QLabel()
    ok = MagicMock()
    err = MagicMock()
    sink = PromptStudioEditorSink(lbl, on_success=ok, on_error=err)
    sink.apply_save_result(PromptEditorSaveResultState(phase="error", error_message="bad"))
    err.assert_called_once_with("bad")
    ok.assert_not_called()

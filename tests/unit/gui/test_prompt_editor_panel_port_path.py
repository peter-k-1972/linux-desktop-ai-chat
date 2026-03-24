"""PromptEditorPanel — Port-Pfad (Batch 3)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.prompt_studio.panels.prompt_editor_panel import PromptEditorPanel
from app.prompts.prompt_models import Prompt
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


def test_port_path_save_invokes_presenter_persist(qapplication, monkeypatch) -> None:
    port = MagicMock()
    snap = PromptStudioPromptSnapshotDto(
        prompt_id=5,
        title="n",
        content="c",
        description="",
        category="general",
        scope="global",
        project_id=None,
        prompt_type="user",
        tags=(),
    )
    port.persist_prompt_editor.return_value = PromptEditorSaveResultState(phase="success", snapshot=snap)

    panel = PromptEditorPanel(prompt_studio_port=port)
    p = Prompt(
        id=5,
        title="old",
        category="general",
        description="",
        content="x",
        tags=[],
        prompt_type="user",
        scope="global",
        project_id=None,
        created_at=None,
        updated_at=None,
    )
    panel.load_prompt(p)
    panel._name.setText("n")
    panel._content.setPlainText("c")

    assert panel._editor_presenter is not None
    panel._on_save()
    port.persist_prompt_editor.assert_called_once()
    assert panel.get_current_prompt() is not None
    assert panel.get_current_prompt().title == "n"

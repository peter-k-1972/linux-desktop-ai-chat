"""PromptStudioWorkspace — Batch 3 presenter wiring."""

from __future__ import annotations

import pytest

pytest.importorskip("PySide6")

from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.prompt_studio.prompt_studio_workspace import PromptStudioWorkspace


@pytest.fixture
def qapplication():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_workspace_presenter_disabled_flag(qapplication) -> None:
    ws = PromptStudioWorkspace(prompt_studio_workspace_flow=False)
    assert ws._workspace_presenter is None
    assert ws._editor is not None
    assert ws._editor._editor_presenter is not None


def test_workspace_default_has_presenter(qapplication) -> None:
    ws = PromptStudioWorkspace()
    assert ws._workspace_presenter is not None

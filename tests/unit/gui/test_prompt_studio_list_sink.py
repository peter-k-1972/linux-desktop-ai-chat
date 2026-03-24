"""PromptStudioListSink — Slice 1."""

from __future__ import annotations

from typing import Any

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.prompt_studio.prompt_studio_list_sink import PromptStudioListSink
from app.ui_contracts.workspaces.prompt_studio_list import PromptStudioListState


def _qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _qapp()
    yield


def test_sink_forwards_to_panel(qapp) -> None:
    calls: list[tuple[Any, ...]] = []

    class _Panel:
        def apply_prompt_list_state(self, state, prompt_models=()) -> None:
            calls.append((state, prompt_models))

    st = PromptStudioListState(phase="empty", empty_hint="x")
    PromptStudioListSink(_Panel()).apply_full_state(st, ())
    assert len(calls) == 1
    assert calls[0][0].phase == "empty"

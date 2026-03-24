"""PromptDetailSink — Slice 2."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.prompt_studio.prompt_detail_sink import PromptDetailSink
from app.ui_contracts.workspaces.prompt_studio_detail import PromptStudioDetailState


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
    calls: list[PromptStudioDetailState] = []

    class _Panel:
        def apply_prompt_detail_state(self, state: PromptStudioDetailState) -> None:
            calls.append(state)

    st = PromptStudioDetailState(phase="ready", detail=None, error_message=None)
    PromptDetailSink(_Panel()).apply_prompt_detail_state(st)
    assert len(calls) == 1
    assert calls[0].phase == "ready"

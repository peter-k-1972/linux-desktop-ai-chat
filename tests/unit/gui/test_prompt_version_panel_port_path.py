"""PromptVersionPanel — Port-Pfad (Batch 2)."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.prompt_studio.panels.prompt_version_panel import PromptVersionPanel
from app.ui_contracts.workspaces.prompt_studio_versions import (
    PromptVersionPanelState,
    PromptVersionRowDto,
)


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


class _FakePort:
    def __init__(self) -> None:
        self.calls = 0

    def load_prompt_versions(self, prompt_id: int) -> PromptVersionPanelState:
        self.calls += 1
        return PromptVersionPanelState(
            phase="ready",
            prompt_id=prompt_id,
            rows=(PromptVersionRowDto(1, "t", "c", None),),
        )


def test_version_panel_port_path_loads_via_presenter(qapp) -> None:
    port = _FakePort()
    p = PromptVersionPanel(prompt_studio_port=port)
    p.set_prompt(42)
    assert port.calls >= 1
    assert p._list_layout.count() >= 1

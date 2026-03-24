"""PromptListPanel — Detail-Port-Pfad (Slice 2)."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.prompt_studio.panels.prompt_inspector_panel import PromptInspectorPanel
from app.gui.domains.operations.prompt_studio.panels.prompt_list_panel import PromptListPanel
from app.ui_contracts.workspaces.prompt_studio_detail import PromptDetailDto
from app.ui_contracts.workspaces.prompt_studio_list import PromptListEntryDto, PromptStudioListState


def _ensure_qapp() -> QApplication:
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


@dataclass
class _P:
    id: int
    title: str = "T"
    scope: str = "global"
    project_id: int | None = None


class _FakePort:
    def __init__(self) -> None:
        self.detail_calls: list[tuple[str, str | None]] = []
        self._models = (_P(1),)

    def load_prompt_list(self, project_id: int | None, filter_text: str = "") -> PromptStudioListState:
        del project_id, filter_text
        return PromptStudioListState(
            phase="ready",
            rows=(PromptListEntryDto(1, "global", 1),),
        )

    def load_prompt_detail(self, prompt_id: str, project_id: str | None) -> PromptDetailDto:
        self.detail_calls.append((prompt_id, project_id))
        return PromptDetailDto(prompt_id, "n", "c", 1, None)

    @property
    def last_prompt_list_models(self) -> tuple:
        return self._models


def test_detail_port_triggers_load_on_item_click(qapp) -> None:
    insp = PromptInspectorPanel(on_version_selected=None)
    port = _FakePort()
    p = PromptListPanel(prompt_studio_port=port, detail_inspector_panel=insp)
    p._current_project_id = 1
    n_detail_before = len(port.detail_calls)
    p.apply_prompt_list_state(
        PromptStudioListState(phase="ready", rows=(PromptListEntryDto(1, "global", 1),)),
        (_P(1),),
    )
    item = p._prompt_widgets.get(1)
    assert item is not None
    p._on_item_clicked(item.prompt)
    assert port.detail_calls[n_detail_before:] == [("1", "1")]

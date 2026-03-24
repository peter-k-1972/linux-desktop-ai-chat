"""PromptListPanel — Port-Pfad vs. Legacy (Slice 1)."""

from __future__ import annotations

from dataclasses import dataclass

import pytest
from PySide6.QtWidgets import QApplication

from app.gui.domains.operations.prompt_studio.panels.prompt_list_panel import PromptListPanel
from app.ui_contracts.workspaces.prompt_studio_list import (
    PromptListEntryDto,
    PromptStudioListState,
    prompt_studio_list_loading_state,
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


@dataclass
class _P:
    id: int
    title: str = "T"
    scope: str = "global"
    project_id: int | None = None


class _FakePort:
    def __init__(self) -> None:
        self.calls = 0
        self._models = (_P(1),)

    def load_prompt_list(self, project_id: int | None, filter_text: str = "") -> PromptStudioListState:
        self.calls += 1
        del project_id, filter_text
        return PromptStudioListState(
            phase="ready",
            rows=(PromptListEntryDto(1, "global", 1),),
        )

    @property
    def last_prompt_list_models(self) -> tuple:
        return self._models


def test_legacy_refresh_calls_prompt_service(qapp, monkeypatch) -> None:
    called: list[str] = []

    class _S:
        def list_project_prompts(self, *a, **k):  # noqa: ANN002
            called.append("lp")
            return []

        def list_global_prompts(self, *a, **k):  # noqa: ANN002
            called.append("lg")
            return []

    monkeypatch.setattr(
        "app.prompts.prompt_service.get_prompt_service",
        lambda: _S(),
    )
    p = PromptListPanel(prompt_studio_port=None)
    p._current_project_id = 1
    p.refresh()
    assert "lp" in called
    assert "lg" in called


def test_port_path_uses_fake_port(qapp) -> None:
    port = _FakePort()
    p = PromptListPanel(prompt_studio_port=port)
    n_after_init = port.calls
    assert n_after_init >= 1
    p._current_project_id = 2
    p.refresh()
    assert port.calls == n_after_init + 1

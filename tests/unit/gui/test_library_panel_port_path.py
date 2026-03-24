"""PromptLibraryPanel — Port-Pfad vs. Legacy (Batch 2)."""

from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace

import pytest
from PySide6.QtWidgets import QApplication, QMessageBox

from app.gui.domains.operations.prompt_studio.panels.library_panel import PromptLibraryPanel
from app.ui_contracts.workspaces.prompt_studio_library import PromptLibraryMutationResult
from app.ui_contracts.workspaces.prompt_studio_list import (
    PromptListEntryDto,
    PromptStudioListState,
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
    title: str = "Lib"
    scope: str = "global"
    project_id: int | None = None


class _FakePort:
    def __init__(self) -> None:
        self.calls = 0
        self._models = (_P(1),)
        self.deleted: list[int] = []

    def load_prompt_list(self, project_id: int | None, filter_text: str = "") -> PromptStudioListState:
        self.calls += 1
        del project_id, filter_text
        return PromptStudioListState(
            phase="ready",
            rows=(PromptListEntryDto(1, "global", 1),),
        )

    def delete_prompt_library_entry(self, prompt_id: int) -> PromptLibraryMutationResult:
        self.deleted.append(prompt_id)
        return PromptLibraryMutationResult(ok=True)

    @property
    def last_prompt_list_models(self) -> tuple:
        return self._models


def test_library_legacy_uses_service(qapp, monkeypatch) -> None:
    called: list[str] = []

    class _S:
        def list_project_prompts(self, *a, **k):  # noqa: ANN002
            called.append("lp")
            return []

        def list_global_prompts(self, *a, **k):  # noqa: ANN002
            called.append("lg")
            return []

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", lambda: _S())
    p = PromptLibraryPanel(prompt_studio_port=None)
    p._current_project_id = 1
    p.refresh()
    assert "lp" in called


def test_library_port_path_uses_fake_port(qapp) -> None:
    port = _FakePort()
    p = PromptLibraryPanel(prompt_studio_port=port)
    n0 = port.calls
    p._current_project_id = 2
    p.refresh()
    assert port.calls == n0 + 1


def test_library_port_path_refresh_ignores_broken_global_prompt_service(qapp, monkeypatch) -> None:
    def _boom():
        raise AssertionError("panel port path must not call get_prompt_service for list/counts")

    monkeypatch.setattr("app.prompts.prompt_service.get_prompt_service", _boom)
    port = _FakePort()
    p = PromptLibraryPanel(prompt_studio_port=port)
    p._current_project_id = 2
    p.refresh()
    assert port.calls >= 1


def test_library_port_path_delete_uses_port(qapp, monkeypatch) -> None:
    monkeypatch.setattr(
        "app.gui.domains.operations.prompt_studio.panels.library_panel.QMessageBox.question",
        lambda *a, **k: QMessageBox.StandardButton.Yes,
    )
    port = _FakePort()
    p = PromptLibraryPanel(prompt_studio_port=port)
    p._current_project_id = 1
    loads_before = port.calls
    p._on_delete_prompt(SimpleNamespace(id=1, title="X"))
    assert port.deleted == [1]
    assert port.calls >= loads_before + 1

"""PromptStudioListPresenter — Slice 1."""

from __future__ import annotations

from typing import Any

from app.ui_application.presenters.prompt_studio_list_presenter import PromptStudioListPresenter
from app.ui_contracts.workspaces.prompt_studio_library import (
    DeletePromptLibraryCommand,
    PromptLibraryMutationResult,
)
from app.ui_contracts.workspaces.prompt_studio_list import (
    LoadPromptStudioListCommand,
    PromptListEntryDto,
    PromptStudioListState,
    prompt_studio_list_loading_state,
)


class _Sink:
    def __init__(self) -> None:
        self.calls: list[tuple[PromptStudioListState, tuple[Any, ...]]] = []

    def apply_full_state(
        self,
        state: PromptStudioListState,
        prompt_models: tuple[Any, ...] = (),
    ) -> None:
        self.calls.append((state, prompt_models))


class _FakePort:
    def __init__(self, view: PromptStudioListState) -> None:
        self._view = view
        self._models: tuple[Any, ...] = ("m",)
        self.deleted: list[int] = []

    def load_prompt_list(self, project_id: int | None, filter_text: str = "") -> PromptStudioListState:
        del project_id, filter_text
        return self._view

    def delete_prompt_library_entry(self, prompt_id: int) -> PromptLibraryMutationResult:
        self.deleted.append(prompt_id)
        return PromptLibraryMutationResult(ok=True)

    @property
    def last_prompt_list_models(self) -> tuple[Any, ...]:
        return self._models


def test_presenter_delete_refreshes_list() -> None:
    row = PromptListEntryDto(prompt_id=1, list_section="project", version_count=1)
    ready = PromptStudioListState(phase="ready", rows=(row,))
    sink = _Sink()
    port = _FakePort(ready)
    pres = PromptStudioListPresenter(sink, port)
    n = len(sink.calls)
    r = pres.handle_delete_library_prompt(DeletePromptLibraryCommand(42, 1, "q"))
    assert r.ok
    assert port.deleted == [42]
    assert len(sink.calls) == n + 2


def test_presenter_loading_then_ready() -> None:
    row = PromptListEntryDto(prompt_id=1, list_section="project", version_count=1)
    ready = PromptStudioListState(phase="ready", rows=(row,))
    sink = _Sink()
    port = _FakePort(ready)
    pres = PromptStudioListPresenter(sink, port)
    pres.handle_command(LoadPromptStudioListCommand(1, ""))
    assert len(sink.calls) == 2
    assert sink.calls[0][0].phase == "loading"
    assert sink.calls[1][0].phase == "ready"
    assert sink.calls[1][1] == ("m",)

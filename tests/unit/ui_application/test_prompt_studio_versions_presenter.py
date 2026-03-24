"""PromptStudioVersionsPresenter — Batch 2."""

from __future__ import annotations

from app.ui_application.presenters.prompt_studio_versions_presenter import PromptStudioVersionsPresenter
from app.ui_contracts.workspaces.prompt_studio_versions import (
    LoadPromptVersionsCommand,
    PromptVersionPanelState,
    PromptVersionRowDto,
    prompt_versions_loading_state,
)


class _Sink:
    def __init__(self) -> None:
        self.states: list[PromptVersionPanelState] = []

    def apply_version_state(self, state: PromptVersionPanelState) -> None:
        self.states.append(state)


class _Port:
    def __init__(self, view: PromptVersionPanelState) -> None:
        self._view = view
        self.calls = 0

    def load_prompt_versions(self, prompt_id: int) -> PromptVersionPanelState:
        self.calls += 1
        assert prompt_id == 5
        return self._view


def test_versions_presenter_loading_then_ready() -> None:
    row = PromptVersionRowDto(1, "a", "b", None)
    ready = PromptVersionPanelState(phase="ready", prompt_id=5, rows=(row,))
    sink = _Sink()
    port = _Port(ready)
    p = PromptStudioVersionsPresenter(sink, port)
    p.handle_command(LoadPromptVersionsCommand(5))
    assert len(sink.states) == 2
    assert sink.states[0].phase == "loading"
    assert sink.states[1].phase == "ready"
    assert port.calls == 1
    assert sink.states[0] == prompt_versions_loading_state(5)

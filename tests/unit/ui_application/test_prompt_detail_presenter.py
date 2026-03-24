"""PromptStudioDetailPresenter — Slice 2."""

from __future__ import annotations

from app.ui_application.presenters.prompt_studio_detail_presenter import PromptStudioDetailPresenter
from app.ui_contracts.workspaces.prompt_studio_detail import (
    LoadPromptDetailCommand,
    PromptDetailDto,
    PromptStudioDetailState,
    prompt_studio_detail_loading_state,
)


def test_presenter_emits_loading_then_ready() -> None:
    states: list[PromptStudioDetailState] = []
    dto = PromptDetailDto("7", "N", "x", 1, None)

    class _Sink:
        def apply_prompt_detail_state(self, state: PromptStudioDetailState) -> None:
            states.append(state)

    class _Port:
        def load_prompt_detail(self, prompt_id: str, project_id: str | None) -> PromptDetailDto:
            assert prompt_id == "7"
            assert project_id == "3"
            return dto

    p = PromptStudioDetailPresenter(_Sink(), _Port())
    p.handle_command(LoadPromptDetailCommand("7", "3"))
    assert len(states) == 2
    assert states[0].phase == prompt_studio_detail_loading_state().phase
    assert states[1].phase == "ready"
    assert states[1].detail == dto


def test_presenter_empty_prompt_id_skips_port() -> None:
    states: list[PromptStudioDetailState] = []

    class _Sink:
        def apply_prompt_detail_state(self, state: PromptStudioDetailState) -> None:
            states.append(state)

    class _Port:
        def load_prompt_detail(self, prompt_id: str, project_id: str | None) -> PromptDetailDto:
            raise AssertionError("port should not be called")

    p = PromptStudioDetailPresenter(_Sink(), _Port())
    p.handle_command(LoadPromptDetailCommand("  ", None))
    assert len(states) == 2
    assert states[1].phase == "ready"
    assert states[1].detail is None


def test_presenter_error_path() -> None:
    states: list[PromptStudioDetailState] = []

    class _Sink:
        def apply_prompt_detail_state(self, state: PromptStudioDetailState) -> None:
            states.append(state)

    class _Port:
        def load_prompt_detail(self, prompt_id: str, project_id: str | None) -> PromptDetailDto:
            del project_id
            raise RuntimeError("boom")

    p = PromptStudioDetailPresenter(_Sink(), _Port())
    p.handle_command(LoadPromptDetailCommand("1", None))
    assert states[-1].phase == "error"
    assert "boom" in (states[-1].error_message or "")

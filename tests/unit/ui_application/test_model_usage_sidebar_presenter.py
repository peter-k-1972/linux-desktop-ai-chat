"""ModelUsageSidebarHintPresenter — Fake-Port + Recording-Sink."""

from __future__ import annotations

from app.ui_application.presenters.model_usage_sidebar_presenter import ModelUsageSidebarHintPresenter
from app.ui_contracts.workspaces.model_usage_sidebar import (
    ModelUsageSidebarHintState,
    RefreshModelUsageSidebarHintCommand,
)


class _RecSink:
    def __init__(self) -> None:
        self.states: list[ModelUsageSidebarHintState] = []

    def apply_full_state(self, state: ModelUsageSidebarHintState) -> None:
        self.states.append(state)


class _FakePort:
    def __init__(self, text: str = "hint", *, fail: bool = False) -> None:
        self._text = text
        self._fail = fail

    def quick_sidebar_hint(self) -> str:
        if self._fail:
            raise RuntimeError("boom")
        return self._text


def test_refresh_pushes_hint() -> None:
    sink = _RecSink()
    p = ModelUsageSidebarHintPresenter(sink, _FakePort("hello"))
    p.handle_command(RefreshModelUsageSidebarHintCommand())
    assert len(sink.states) == 1
    assert sink.states[0].hint_text == "hello"


def test_refresh_failure_empty_string() -> None:
    sink = _RecSink()
    p = ModelUsageSidebarHintPresenter(sink, _FakePort(fail=True))
    p.handle_command(RefreshModelUsageSidebarHintCommand())
    assert sink.states[0].hint_text == ""

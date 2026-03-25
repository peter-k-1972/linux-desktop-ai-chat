"""Presenter-Skelett: Backend nicht verdrahtet → definierter Fehler-Patch."""

from __future__ import annotations

from app.ui_contracts import (
    ChatStatePatch,
    ChatWorkspaceLoadState,
    ChatWorkspaceState,
    SelectChatCommand,
)
from app.ui_application.presenters.chat_presenter import ChatPresenter


class _Sink:
    def __init__(self) -> None:
        self.patches: list[ChatStatePatch] = []
        self.full: list[ChatWorkspaceState] = []

    def apply_full_state(self, state: ChatWorkspaceState) -> None:
        self.full.append(state)

    def apply_chat_patch(self, patch: ChatStatePatch) -> None:
        self.patches.append(patch)


def test_chat_presenter_without_port_reports_wiring_error():
    sink = _Sink()
    p = ChatPresenter(sink, port=None)
    p.handle_command(SelectChatCommand(chat_id=1))
    assert sink.patches
    patch = sink.patches[-1]
    assert patch.load_state == ChatWorkspaceLoadState.ERROR
    assert patch.error is not None
    assert patch.error.code == "backend_not_wired"

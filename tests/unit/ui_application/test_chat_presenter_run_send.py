"""Presenter Send-Pipeline mit minimalem Fake-Port (ohne DB/Services)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest

from app.ui_application.presenters.chat_presenter import ChatPresenter
from app.ui_application.presenters.chat_send_callbacks import ChatSendCallbacks, ChatSendSession
from app.ui_contracts import (
    ChatConnectionStatus,
    ChatStreamPhase,
    ChatWorkspaceLoadState,
    ChatWorkspaceState,
    ProjectContextEntry,
    SendMessageCommand,
)


class _Sink:
    def apply_full_state(self, state: ChatWorkspaceState) -> None:
        del state

    def apply_chat_patch(self, patch: object) -> None:
        del patch


class FakeChatPort:
    """Erfüllt die für ``run_send_async`` benötigten Port-Methoden."""

    def __init__(self) -> None:
        self.saved_user: list[tuple[int, str]] = []
        self.saved_assistant: list[tuple[int, str, str, str | None]] = []

    def get_active_project_id(self) -> int | None:
        return None

    def create_chat_global(self, title: str) -> int:
        del title
        return 42

    def create_chat_in_project(self, project_id: int, title: str) -> int:
        del project_id, title
        return 42

    def save_user_message(self, chat_id: int, text: str) -> None:
        self.saved_user.append((chat_id, text))

    def maybe_autotitle_from_first_message(self, chat_id: int, user_text: str) -> bool:
        del chat_id, user_text
        return False

    def build_api_messages(self, chat_id: int) -> list[dict[str, str]]:
        del chat_id
        return [{"role": "user", "content": "hi"}]

    def get_stream_settings(self) -> tuple[float, int, bool]:
        return 0.7, 4096, True

    async def iter_chat_chunks(
        self,
        *,
        model: str,
        chat_id: int,
        api_messages: list[dict[str, str]],
        temperature: float,
        max_tokens: int,
        stream: bool,
    ) -> AsyncIterator[dict[str, Any]]:
        del model, chat_id, api_messages, temperature, max_tokens, stream
        yield {"message": {"content": "Hello"}, "done": False}
        yield {"done": True}

    def merge_invocation_payload(
        self, prior: dict[str, Any] | None, chunk: dict[str, Any]
    ) -> dict[str, Any] | None:
        return prior or {}

    def invocation_error_kind(self, chunk: dict[str, Any]) -> str | None:
        del chunk
        return None

    def completion_status_for_outcome(
        self,
        full_content: str,
        *,
        provider_finished_normally: bool,
        had_error: bool,
        had_exception: bool,
    ) -> str | None:
        del full_content, provider_finished_normally, had_error, had_exception
        return "complete"

    def build_chat_invocation_view(
        self,
        merged_invocation: dict[str, Any] | None,
        *,
        last_error_text: str | None,
        last_error_kind: str | None,
        completion_status_db: str | None,
        model_name: str,
    ) -> dict[str, Any]:
        del merged_invocation, last_error_text, last_error_kind, completion_status_db, model_name
        return {"ok": True}

    def save_assistant_message(
        self,
        chat_id: int,
        content: str,
        *,
        model: str,
        completion_status: str | None,
    ) -> None:
        self.saved_assistant.append((chat_id, content, model, completion_status))


@pytest.mark.asyncio
async def test_run_send_async_persists_turns():
    port = FakeChatPort()
    state = ChatWorkspaceState(
        load_state=ChatWorkspaceLoadState.IDLE,
        connection=ChatConnectionStatus.UNKNOWN,
        selected_chat_id=None,
        filter_text="",
        chats=(),
        messages=(),
        models=(),
        default_model_id=None,
        project=ProjectContextEntry(None, None),
        stream_phase=ChatStreamPhase.IDLE,
        streaming_message_index=None,
    )
    p = ChatPresenter(_Sink(), port=port, initial_state=state)

    updates: list[str] = []

    async def _run() -> None:
        session = ChatSendSession(None)
        await p.run_send_async(
            text="hi",
            model="m1",
            session=session,
            callbacks=ChatSendCallbacks(
                conversation_add_user=lambda t: updates.append(f"u:{t}"),
                conversation_scroll_bottom=lambda: updates.append("scroll"),
                conversation_add_placeholder=lambda m: updates.append(f"p:{m}"),
                conversation_update_last_assistant=lambda t: updates.append(f"a:{t}"),
                conversation_set_last_completion=lambda _s: None,
                conversation_finalize_streaming=lambda: updates.append("fin"),
                input_set_sending=lambda _b: None,
                details_set_invocation_view=lambda _v: None,
                refresh_session_explorer=lambda: None,
                set_session_explorer_current=lambda _i: None,
                refresh_context_bar=lambda: None,
                refresh_details_panel=lambda: None,
                refresh_inspector=lambda: None,
                show_error_inline=lambda _m: None,
            ),
        )
        assert session.chat_id == 42

    await _run()
    assert port.saved_user and port.saved_user[0][1] == "hi"
    assert port.saved_assistant and "Hello" in port.saved_assistant[0][1]
    assert any(x.startswith("a:Hello") for x in updates)


def _noop_send_callbacks(
    *, notify_send_session_completed=None
) -> ChatSendCallbacks:
    return ChatSendCallbacks(
        conversation_add_user=lambda _t: None,
        conversation_scroll_bottom=lambda: None,
        conversation_add_placeholder=lambda _m: None,
        conversation_update_last_assistant=lambda _t: None,
        conversation_set_last_completion=lambda _s: None,
        conversation_finalize_streaming=lambda: None,
        input_set_sending=lambda _b: None,
        details_set_invocation_view=lambda _v: None,
        refresh_session_explorer=lambda: None,
        set_session_explorer_current=lambda _i: None,
        refresh_context_bar=lambda: None,
        refresh_details_panel=lambda: None,
        refresh_inspector=lambda: None,
        show_error_inline=lambda _m: None,
        notify_send_session_completed=notify_send_session_completed,
    )


def test_handle_send_message_command_schedules_coroutine():
    scheduled: list = []
    port = FakeChatPort()
    state = ChatWorkspaceState(
        load_state=ChatWorkspaceLoadState.IDLE,
        connection=ChatConnectionStatus.UNKNOWN,
        selected_chat_id=None,
        filter_text="",
        chats=(),
        messages=(),
        models=(),
        default_model_id=None,
        project=ProjectContextEntry(None, None),
        stream_phase=ChatStreamPhase.IDLE,
        streaming_message_index=None,
    )
    p = ChatPresenter(_Sink(), port=port, initial_state=state)
    p.attach_send_pipeline(
        schedule_coro=lambda c: scheduled.append(c),
        callbacks=_noop_send_callbacks(),
        session_factory=lambda: ChatSendSession(None),
    )
    p.handle_command(SendMessageCommand(text="  hi  ", model_id=" m1 "))
    assert len(scheduled) == 1
    scheduled[0].close()


@pytest.mark.asyncio
async def test_send_message_command_smoke_await_scheduled():
    scheduled: list = []
    port = FakeChatPort()
    state = ChatWorkspaceState(
        load_state=ChatWorkspaceLoadState.IDLE,
        connection=ChatConnectionStatus.UNKNOWN,
        selected_chat_id=None,
        filter_text="",
        chats=(),
        messages=(),
        models=(),
        default_model_id=None,
        project=ProjectContextEntry(None, None),
        stream_phase=ChatStreamPhase.IDLE,
        streaming_message_index=None,
    )
    p = ChatPresenter(_Sink(), port=port, initial_state=state)
    completed: list[ChatSendSession] = []
    p.attach_send_pipeline(
        schedule_coro=lambda c: scheduled.append(c),
        callbacks=_noop_send_callbacks(notify_send_session_completed=completed.append),
        session_factory=lambda: ChatSendSession(None),
    )
    p.handle_command(SendMessageCommand(text="hi", model_id="m1"))
    assert len(scheduled) == 1
    await scheduled[0]
    assert port.saved_user and port.saved_user[0][1] == "hi"
    assert completed and completed[0].chat_id == 42


@pytest.mark.asyncio
async def test_run_send_async_calls_notify_send_session_completed():
    port = FakeChatPort()
    state = ChatWorkspaceState(
        load_state=ChatWorkspaceLoadState.IDLE,
        connection=ChatConnectionStatus.UNKNOWN,
        selected_chat_id=None,
        filter_text="",
        chats=(),
        messages=(),
        models=(),
        default_model_id=None,
        project=ProjectContextEntry(None, None),
        stream_phase=ChatStreamPhase.IDLE,
        streaming_message_index=None,
    )
    p = ChatPresenter(_Sink(), port=port, initial_state=state)
    done: list[ChatSendSession] = []
    session = ChatSendSession(None)
    await p.run_send_async(
        text="x",
        model="m",
        session=session,
        callbacks=_noop_send_callbacks(notify_send_session_completed=done.append),
    )
    assert len(done) == 1 and done[0] is session and session.chat_id == 42

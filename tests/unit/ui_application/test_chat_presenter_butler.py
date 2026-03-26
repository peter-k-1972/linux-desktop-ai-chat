"""ChatPresenter: Butler-Zweig ohne echten WorkflowService."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import asyncio
import pytest

from app.ui_application.presenters.chat_presenter import ChatPresenter
from app.ui_application.presenters.chat_send_callbacks import ChatSendCallbacks, ChatSendSession
from app.ui_contracts import (
    ChatConnectionStatus,
    ChatStreamPhase,
    ChatWorkspaceLoadState,
    ChatWorkspaceState,
    ProjectContextEntry,
)


class _Sink:
    def apply_full_state(self, state: ChatWorkspaceState) -> None:
        del state

    def apply_chat_patch(self, patch: object) -> None:
        del patch


class FakePortForButler:
    def __init__(self) -> None:
        self.saved_assistant: list[tuple[int, str, str, str | None]] = []

    def get_active_project_id(self) -> int | None:
        return None

    def create_chat_global(self, title: str) -> int:
        del title
        return 99

    def create_chat_in_project(self, project_id: int, title: str) -> int:
        del project_id, title
        return 99

    def save_user_message(self, chat_id: int, text: str) -> None:
        del chat_id, text

    def maybe_autotitle_from_first_message(self, chat_id: int, user_text: str) -> bool:
        del chat_id, user_text
        return False

    def build_api_messages(self, chat_id: int) -> list[dict[str, str]]:
        del chat_id
        raise AssertionError("LLM-Pfad darf bei Butler nicht laufen")

    def get_stream_settings(self) -> tuple[float, int, bool]:
        return 0.7, 4096, True

    async def iter_chat_chunks(self, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
        del kwargs
        raise AssertionError("LLM-Stream darf bei Butler nicht laufen")
        yield {}  # pragma: no cover

    def merge_invocation_payload(self, prior: dict[str, Any] | None, chunk: dict[str, Any]) -> dict[str, Any] | None:
        del chunk
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

    def build_chat_invocation_view(self, merged_invocation: dict[str, Any] | None, **kwargs: Any) -> dict[str, Any]:
        del kwargs
        return {"butler": merged_invocation}

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
async def test_presenter_butler_bugfix_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    port = FakePortForButler()
    p = ChatPresenter(
        _Sink(),
        port=port,
        initial_state=ChatWorkspaceState(
            load_state=ChatWorkspaceLoadState.IDLE,
            connection=ChatConnectionStatus.UNKNOWN,
            selected_chat_id=99,
            filter_text="",
            chats=(),
            messages=(),
            models=(),
            default_model_id=None,
            project=ProjectContextEntry(None, None),
            stream_phase=ChatStreamPhase.IDLE,
            streaming_message_index=None,
        ),
    )

    async def fake_to_thread(fn, /, *args, **kwargs):  # noqa: ANN001
        assert fn.__name__ == "run_project_butler_sync"
        return {
            "selected_workflow": "workflow.dev_assist.analyze_modify_test_review",
            "reasoning": "Treffer: fix",
            "result": {
                "outcome": "workflow_finished",
                "status": "completed",
                "final_output": {"analysis": "A", "plan": "P"},
            },
        }

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)

    updates: list[str] = []

    await p.run_send_async(
        text="fix the timeout",
        model="m1",
        session=ChatSendSession(99),
        callbacks=ChatSendCallbacks(
            conversation_add_user=lambda t: updates.append(f"u:{t}"),
            conversation_scroll_bottom=lambda: updates.append("scroll"),
            conversation_add_placeholder=lambda m: updates.append(f"p:{m}"),
            conversation_update_last_assistant=lambda t: updates.append(f"a:{t[:40]}"),
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

    assert any(x.startswith("a:Project Butler") for x in updates)
    assert port.saved_assistant
    assert "dev_assist" in port.saved_assistant[0][1]


@pytest.mark.asyncio
async def test_presenter_butler_passes_optional_context_with_chat_id(monkeypatch: pytest.MonkeyPatch) -> None:
    port = FakePortForButler()
    p = ChatPresenter(
        _Sink(),
        port=port,
        initial_state=ChatWorkspaceState(
            load_state=ChatWorkspaceLoadState.IDLE,
            connection=ChatConnectionStatus.UNKNOWN,
            selected_chat_id=99,
            filter_text="",
            chats=(),
            messages=(),
            models=(),
            default_model_id=None,
            project=ProjectContextEntry(None, None),
            stream_phase=ChatStreamPhase.IDLE,
            streaming_message_index=None,
        ),
    )
    captured: dict[str, Any] = {}

    async def fake_to_thread(fn, /, *args):  # noqa: ANN001
        captured["func"] = fn
        captured["args"] = args  # (user_request, optional_context)
        return {
            "selected_workflow": None,
            "reasoning": "test",
            "result": {"outcome": "no_workflow_matched", "detail": "test"},
        }

    monkeypatch.setattr(asyncio, "to_thread", fake_to_thread)

    await p.run_send_async(
        text="fix nothing",
        model="m1",
        session=ChatSendSession(99),
        callbacks=ChatSendCallbacks(
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
        ),
    )

    user_req, opt = captured["args"]
    assert captured["func"].__name__ == "run_project_butler_sync"
    assert user_req == "fix nothing"
    assert isinstance(opt, dict)
    assert opt.get("chat_id") == 99


@pytest.mark.asyncio
async def test_presenter_butler_to_thread_failure_returns_message(monkeypatch: pytest.MonkeyPatch) -> None:
    port = FakePortForButler()
    p = ChatPresenter(
        _Sink(),
        port=port,
        initial_state=ChatWorkspaceState(
            load_state=ChatWorkspaceLoadState.IDLE,
            connection=ChatConnectionStatus.UNKNOWN,
            selected_chat_id=3,
            filter_text="",
            chats=(),
            messages=(),
            models=(),
            default_model_id=None,
            project=ProjectContextEntry(None, None),
            stream_phase=ChatStreamPhase.IDLE,
            streaming_message_index=None,
        ),
    )

    async def boom(_fn, /, *_a):  # noqa: ANN001
        raise RuntimeError("workflow db locked")

    monkeypatch.setattr(asyncio, "to_thread", boom)

    await p.run_send_async(
        text="refactor this",
        model="m1",
        session=ChatSendSession(3),
        callbacks=ChatSendCallbacks(
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
        ),
    )

    assert port.saved_assistant
    body = port.saved_assistant[0][1]
    assert "Project Butler" in body
    assert "workflow db locked" in body


@pytest.mark.asyncio
async def test_presenter_normal_message_uses_stream(monkeypatch: pytest.MonkeyPatch) -> None:
    streamed = {"n": 0}

    class PortStream(FakePortForButler):
        async def iter_chat_chunks(self, **kwargs: Any) -> AsyncIterator[dict[str, Any]]:
            del kwargs
            streamed["n"] += 1
            yield {"message": {"content": "Hi"}, "done": True}

        def build_api_messages(self, chat_id: int) -> list[dict[str, str]]:
            del chat_id
            return [{"role": "user", "content": "yo"}]

    port = PortStream()
    p = ChatPresenter(
        _Sink(),
        port=port,
        initial_state=ChatWorkspaceState(
            load_state=ChatWorkspaceLoadState.IDLE,
            connection=ChatConnectionStatus.UNKNOWN,
            selected_chat_id=5,
            filter_text="",
            chats=(),
            messages=(),
            models=(),
            default_model_id=None,
            project=ProjectContextEntry(None, None),
            stream_phase=ChatStreamPhase.IDLE,
            streaming_message_index=None,
        ),
    )

    async def boom_to_thread(*_a, **_kw):  # noqa: ANN001
        raise AssertionError("Butler darf nicht laufen")

    monkeypatch.setattr(asyncio, "to_thread", boom_to_thread)

    await p.run_send_async(
        text="Wie geht es dir heute?",
        model="m1",
        session=ChatSendSession(5),
        callbacks=ChatSendCallbacks(
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
        ),
    )

    assert streamed["n"] == 1
    assert port.saved_assistant and "Hi" in port.saved_assistant[0][1]

"""Kanonische Stream-Consume-Orchestrierung (app.chat.stream_consume)."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest

from app.chat.stream_consume import (
    ChatStreamConsumeContext,
    ChatStreamConsumeHooks,
    consume_chat_model_stream,
)
from app.chat.stream_accumulator import ChatStreamAccumulator
from app.ui_application.presenters.chat_stream_assembler import (
    final_assistant_message_for_persistence,
)


class _CapturingHooks(ChatStreamConsumeHooks):
    def __init__(self) -> None:
        self.texts: list[str] = []
        super().__init__(
            update_assistant_text=self.texts.append,
            scroll_bottom=lambda: None,
        )


async def _chunks(*items: dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
    for x in items:
        yield x


def _merge(prior: dict[str, Any] | None, chunk: Any) -> dict[str, Any] | None:
    return prior or {}


def _no_ek(_chunk: Any) -> str | None:
    return None


def _completion(
    content: str,
    *,
    provider_finished_normally: bool,
    had_error: bool,
    had_exception: bool,
) -> str:
    del provider_finished_normally, had_error, had_exception
    return "complete" if content else "empty"


@pytest.mark.asyncio
async def test_consume_matches_parallel_accumulator():
    """Gleiche Chunks wie manuelles feed() -> gleicher sichtbarer Text und Final."""
    seq = [
        {"message": {"content": "a", "thinking": ""}, "done": False},
        {"message": {"content": "b", "thinking": ""}, "done": True},
    ]
    acc = ChatStreamAccumulator()
    for c in seq:
        acc.feed(c)
    ctx = ChatStreamConsumeContext()
    hooks = _CapturingHooks()
    await consume_chat_model_stream(
        ctx,
        chunk_source=_chunks(*seq),
        merge_invocation=_merge,
        invocation_error_kind=_no_ek,
        completion_status_for_outcome=_completion,
        hooks=hooks,
    )
    assert ctx.full_content == acc.visible_assistant_text
    assert final_assistant_message_for_persistence(ctx.accumulator) == ctx.full_content
    assert hooks.texts[-1] == ctx.full_content


@pytest.mark.asyncio
async def test_consume_thinking_only_no_visible():
    ctx = ChatStreamConsumeContext()
    await consume_chat_model_stream(
        ctx,
        chunk_source=_chunks({"message": {"content": "", "thinking": "x"}, "done": True}),
        merge_invocation=_merge,
        invocation_error_kind=_no_ek,
        completion_status_for_outcome=_completion,
        hooks=_CapturingHooks(),
    )
    assert ctx.full_content == ""
    assert ctx.accumulator.visible_assistant_text == ""


@pytest.mark.asyncio
async def test_consume_chunk_error_breaks_with_message():
    ctx = ChatStreamConsumeContext()
    hooks = _CapturingHooks()
    await consume_chat_model_stream(
        ctx,
        chunk_source=_chunks({"error": "boom", "done": True}),
        merge_invocation=_merge,
        invocation_error_kind=_no_ek,
        completion_status_for_outcome=_completion,
        hooks=hooks,
    )
    assert ctx.had_error is True
    assert "boom" in ctx.full_content


def test_run_send_async_has_no_iter_chat_chunks_loop():
    """Presenter-Modellstream: keine eigene async-for-Chunkschleife mehr."""
    path = Path(__file__).resolve().parents[3] / "app/ui_application/presenters/chat_presenter.py"
    text = path.read_text(encoding="utf-8")
    assert "async for chunk in port.iter_chat_chunks" not in text
    assert "consume_chat_model_stream" in text


def test_chat_stream_consume_imports_no_gui():
    import app.chat.stream_consume as sc

    src = Path(sc.__file__).read_text(encoding="utf-8")
    assert "PySide6" not in src
    assert "ui_application" not in src
    assert "gui.domains" not in src

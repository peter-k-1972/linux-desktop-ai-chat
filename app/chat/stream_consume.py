"""
Kanonische Orchestrierung fuer Modell-Chat-Streaming (Qt-frei).

Kapselt: Chunk-Iterator konsumieren, Akkumulator speisen, Trace, Finalisierung,
completion_status-Vorbereitung. Keine Widgets, keine ui_contracts.

Project-Butler und aehnliche Nicht-Stream-Pfade bleiben bewusst im Presenter:
sie nutzen keinen Provider-Chunk-Stream und gehoeren nicht in diese API.
"""

from __future__ import annotations

from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from typing import Any

from app.chat.final_assistant_message import final_assistant_message_for_persistence
from app.chat.stream_accumulator import ChatStreamAccumulator
from app.chat.stream_pipeline_trace import (
    ensure_trace_logger_info,
    trace_post_finalize,
    trace_raw_provider_chunk,
    trace_ui_bubble_update,
)


@dataclass
class ChatStreamConsumeHooks:
    """UI-neutrale Sichtbarkeits-Updates (Presenter/Legacy mappen auf Widgets)."""

    update_assistant_text: Callable[[str], None]
    scroll_bottom: Callable[[], None]


@dataclass
class ChatStreamConsumeContext:
    """Mutabler Sitzungszustand; vor Butler/Stream anlegen (fuer Cancel/Exception sicher)."""

    accumulator: ChatStreamAccumulator = field(default_factory=ChatStreamAccumulator)
    merged_invocation: dict[str, Any] | None = None
    last_error_kind: str | None = None
    last_error_text: str | None = None
    provider_done: bool = False
    had_error: bool = False
    full_content: str = ""
    completion_status_str: str | None = None


async def consume_chat_model_stream(
    ctx: ChatStreamConsumeContext,
    *,
    chunk_source: AsyncIterator[Any],
    merge_invocation: Callable[[dict[str, Any] | None, Any], dict[str, Any] | None],
    invocation_error_kind: Callable[[Any], str | None],
    completion_status_for_outcome: Callable[..., str | None],
    hooks: ChatStreamConsumeHooks,
) -> None:
    """
    Vollstaendigen Provider-Stream abarbeiten und ``ctx`` befuellen.

    Setzt u. a. ``ctx.full_content``, ``ctx.completion_status_str``, ``ctx.merged_invocation``.
    Wirft nicht bei Chunk-``error``: setzt ``ctx.had_error`` und bricht die Schleife ab.
    """
    ensure_trace_logger_info()

    async for chunk in chunk_source:
        ctx.merged_invocation = merge_invocation(ctx.merged_invocation, chunk)
        ek = invocation_error_kind(chunk)
        if ek:
            ctx.last_error_kind = ek
        if isinstance(chunk, dict):
            trace_raw_provider_chunk(ctx.accumulator.trace_seq_for_next_chunk, chunk)
        else:
            trace_raw_provider_chunk(
                ctx.accumulator.trace_seq_for_next_chunk,
                {"_non_dict_chunk": repr(chunk)},
            )
        err, done, changed = ctx.accumulator.feed(chunk)
        if done:
            ctx.provider_done = True
        if err:
            ctx.had_error = True
            ctx.last_error_text = str(err)
            ctx.full_content = f"Fehler: {err}"
            hooks.update_assistant_text(ctx.full_content)
            hooks.scroll_bottom()
            trace_ui_bubble_update(
                ctx.accumulator.last_feed_seq,
                text_len=len(ctx.full_content),
                text_preview=ctx.full_content,
                reason="stream_error",
            )
            break
        ctx.full_content = ctx.accumulator.visible_assistant_text
        if changed:
            hooks.update_assistant_text(ctx.full_content)
            hooks.scroll_bottom()
            trace_ui_bubble_update(
                ctx.accumulator.last_feed_seq,
                text_len=len(ctx.full_content),
                text_preview=ctx.full_content,
                reason="stream_delta",
            )

    if not ctx.had_error:
        ctx.full_content = final_assistant_message_for_persistence(ctx.accumulator)
        hooks.update_assistant_text(ctx.full_content)
        hooks.scroll_bottom()
        trace_ui_bubble_update(
            ctx.accumulator.last_feed_seq,
            text_len=len(ctx.full_content or ""),
            text_preview=ctx.full_content or "",
            reason="stream_finalize_sync",
        )

    trace_post_finalize(
        text_len=len(ctx.full_content or ""),
        text_preview=ctx.full_content or "",
        had_error=ctx.had_error,
    )
    ctx.completion_status_str = completion_status_for_outcome(
        ctx.full_content,
        provider_finished_normally=ctx.provider_done,
        had_error=ctx.had_error,
        had_exception=False,
    )

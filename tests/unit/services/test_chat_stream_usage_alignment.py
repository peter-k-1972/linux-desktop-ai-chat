"""
Alignment: Usage-Pfad (model_chat_runtime) nutzt dieselbe sichtbare Extraktion + Absorb wie UI-Akkumulator.
"""

from __future__ import annotations

from app.chat.final_assistant_message import final_assistant_message_for_persistence
from app.chat.provider_stream_normalize import parse_provider_chat_chunk
from app.chat.stream_accumulator import ChatStreamAccumulator, absorb_incremental_or_cumulative
from app.chat import stream_assembler as stream_facet
from app.ui_application.presenters import chat_stream_assembler as presenter_shim


def _runtime_visible_after_chunks(chunks: list[dict]) -> str:
    buf = ""
    for c in chunks:
        p = parse_provider_chat_chunk(c)
        if p.visible_piece:
            buf = absorb_incremental_or_cumulative(buf, p.visible_piece)
    return buf


def test_runtime_visible_matches_accumulator_golden():
    chunks = [
        {"message": {"content": "The ", "thinking": ""}, "done": False},
        {"message": {"content": "quick ", "thinking": ""}, "done": False},
        {"message": {"content": "brown fox", "thinking": ""}, "done": True},
        {"choices": [{"delta": {"content": " tail"}}], "done": False},
    ]
    acc = ChatStreamAccumulator()
    for c in chunks:
        acc.feed(c)
    rt = _runtime_visible_after_chunks(chunks)
    assert acc.visible_assistant_text == rt
    assert final_assistant_message_for_persistence(acc) == rt


def test_visible_and_final_unchanged_for_simple_content():
    chunks = [{"message": {"content": "ok", "thinking": ""}, "done": True}]
    acc = ChatStreamAccumulator()
    for c in chunks:
        acc.feed(c)
    rt = _runtime_visible_after_chunks(chunks)
    assert acc.visible_assistant_text == rt == "ok"
    assert final_assistant_message_for_persistence(acc) == "ok"


def test_thinking_only_runtime_visible_empty():
    chunks = [
        {"message": {"content": "", "thinking": "plan"}, "done": False},
        {"message": {"content": "", "thinking": "more"}, "done": True},
    ]
    assert _runtime_visible_after_chunks(chunks) == ""
    acc = ChatStreamAccumulator()
    for c in chunks:
        acc.feed(c)
    assert acc.visible_assistant_text == ""
    assert "plan" in acc.reasoning_text


def test_openai_delta_visible_in_runtime_not_only_message():
    """Frueher: nur message.content-String; jetzt: choices[0].delta.content zaehlt."""
    chunks = [{"choices": [{"delta": {"content": "from_delta"}}], "done": True}]
    assert _runtime_visible_after_chunks(chunks) == "from_delta"


def test_stream_assembler_and_presenter_shim_same_objects():
    assert presenter_shim.parse_provider_chat_chunk is stream_facet.parse_provider_chat_chunk
    assert presenter_shim.ChatStreamAccumulator is stream_facet.ChatStreamAccumulator
    assert (
        presenter_shim.final_assistant_message_for_persistence
        is stream_facet.final_assistant_message_for_persistence
    )

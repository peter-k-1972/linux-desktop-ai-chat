"""Unit-Tests für Chat-Stream-Hilfsfunktionen (Qt-frei)."""

from __future__ import annotations

from app.ui_application.presenters.chat_stream_assembler import (
    ChatStreamAccumulator,
    append_stream_piece,
    dedupe_overlap_append,
    extract_stream_display,
)


def test_append_stream_piece_overlap_dedup():
    assert append_stream_piece("hello wor", "world") == "hello world"


def test_dedupe_overlap_append_respects_min_overlap():
    """1-Zeichen-Overlap verbindet das End-„a“ mit dem Anfang von „and…“ und frisst ein Zeichen."""
    assert dedupe_overlap_append("The value is a", "and the rest", min_overlap=1) == "The value is and the rest"
    assert dedupe_overlap_append("The value is a", "and the rest", min_overlap=2) == "The value is aand the rest"


def test_extract_stream_display_error_chunk():
    out, _th, err, done, src = extract_stream_display({"error": "x", "done": True})
    assert err == "x"
    assert done is True
    assert out == ""
    assert src == "none"


def test_extract_stream_display_visible_empty_when_only_thinking():
    chunk = {"message": {"content": "", "thinking": "  plan  "}, "done": False}
    out, thinking, err, done, src = extract_stream_display(chunk)
    assert err is None
    assert done is False
    assert thinking.strip() == "plan"
    assert out == ""
    assert src == "none"


def test_chat_stream_accumulator_many_content_deltas():
    acc = ChatStreamAccumulator()
    for part in ("The ", "quick ", "brown ", "fox"):
        err, _d, _c = acc.feed({"message": {"content": part}})
        assert err is None
    assert acc.full == "The quick brown fox"


def test_chat_stream_accumulator_no_false_overlap_across_content_deltas():
    acc = ChatStreamAccumulator()
    acc.feed({"message": {"content": "The value is a"}})
    acc.feed({"message": {"content": "and the rest"}})
    assert acc.full == "The value is aand the rest"


def test_chat_stream_accumulator_thinking_then_overlapping_content():
    acc = ChatStreamAccumulator()
    acc.feed({"message": {"content": "", "thinking": "Hello"}})
    acc.feed({"message": {"content": "Hello world", "thinking": ""}})
    assert acc.full == "Hello world"


def test_chat_stream_accumulator_final_content_only_on_done_chunk():
    """Letzter Chunk oft nur done=true — darf Text nicht zurücksetzen."""
    acc = ChatStreamAccumulator()
    acc.feed({"message": {"content": "x"}})
    err, done, _ = acc.feed({"done": True})
    assert err is None
    assert done is True
    assert acc.full == "x"


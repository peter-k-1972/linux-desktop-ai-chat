"""Unit-Tests für Chat-Stream-Hilfsfunktionen (Qt-frei)."""

from __future__ import annotations

from app.ui_application.presenters.chat_stream_assembler import append_stream_piece, extract_stream_display


def test_append_stream_piece_overlap_dedup():
    assert append_stream_piece("hello wor", "world") == "hello world"


def test_extract_stream_display_error_chunk():
    out, _th, err, done = extract_stream_display({"error": "x", "done": True})
    assert err == "x"
    assert done is True
    assert out == ""


def test_extract_stream_display_prefers_thinking_when_content_empty():
    chunk = {"message": {"content": "", "thinking": "  plan  "}, "done": False}
    out, thinking, err, done = extract_stream_display(chunk)
    assert err is None
    assert done is False
    assert thinking.strip() == "plan"
    assert "plan" in out

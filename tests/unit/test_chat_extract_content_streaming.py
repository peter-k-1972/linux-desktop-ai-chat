"""
Regression: Stream-Chunks mit leerem message.content aber gefülltem thinking
(z. B. Qwen) müssen in der Chat-Aggregation sichtbar werden.
"""

import pytest

from app.gui.domains.operations.chat.chat_workspace import (
    _append_stream_piece,
    _extract_content,
)


def test_thinking_fallback_when_content_empty():
    chunk = {
        "message": {"role": "assistant", "content": "", "thinking": "Schritt A"},
        "done": False,
    }
    content, thinking, error, done = _extract_content(chunk)
    assert error is None
    assert done is False
    assert thinking == "Schritt A"
    assert content == "Schritt A"


def test_content_wins_when_non_whitespace():
    chunk = {
        "message": {
            "role": "assistant",
            "content": "Antwort",
            "thinking": "intern",
        },
        "done": True,
    }
    content, thinking, error, done = _extract_content(chunk)
    assert content == "Antwort"
    assert thinking == "intern"
    assert done is True


def test_whitespace_only_content_uses_thinking():
    chunk = {
        "message": {"role": "assistant", "content": "  \n", "thinking": "X"},
        "done": False,
    }
    content, thinking, _, _ = _extract_content(chunk)
    assert content == "X"
    assert thinking == "X"


def test_streaming_sequence_thinking_deltas_then_content():
    """Wie gestreamte Teilstrings: thinking-Fragmente, dann echter content."""
    chunks = [
        {"message": {"content": "", "thinking": "a"}, "done": False},
        {"message": {"content": "", "thinking": "b"}, "done": False},
        {"message": {"content": "out", "thinking": ""}, "done": False},
        {"message": {"content": "", "thinking": ""}, "done": True},
    ]
    full = ""
    for c in chunks:
        text, _, err, _ = _extract_content(c)
        if err:
            break
        if text:
            full = _append_stream_piece(full, text)
    assert full == "about"


def test_final_chunk_done_with_thinking_only():
    chunk = {
        "message": {"content": "", "thinking": "letztes Stück"},
        "done": True,
    }
    content, _, _, done = _extract_content(chunk)
    assert done is True
    assert content == "letztes Stück"


def test_error_chunk_ignores_message():
    chunk = {"error": "modell weg", "done": False}
    content, thinking, error, done = _extract_content(chunk)
    assert content == ""
    assert thinking == ""
    assert error == "modell weg"


def test_conversation_panel_end_state_matches_aggregate():
    """UI-Endzustand (Bubble) = kumulierter _extract_content-Pfad ohne pytest-qt."""
    import sys

    from PySide6.QtWidgets import QApplication

    from app.gui.domains.operations.chat.panels.conversation_panel import (
        ChatConversationPanel,
    )

    _app = QApplication.instance() or QApplication(sys.argv)
    panel = ChatConversationPanel()
    panel.add_assistant_placeholder(model="m")
    chunks = [
        {"message": {"content": "", "thinking": "T1"}, "done": False},
        {"message": {"content": "", "thinking": "T2"}, "done": False},
        {"message": {"content": " C", "thinking": ""}, "done": True},
    ]
    full = ""
    for c in chunks:
        part, _, err, _ = _extract_content(c)
        if err:
            break
        if part:
            full = _append_stream_piece(full, part)
            panel.update_last_assistant(full)
    QApplication.processEvents()
    assert panel._last_assistant_bubble is not None
    assert panel._last_assistant_bubble.toPlainText() == full == "T1T2 C"


def test_append_stream_piece_overlap_thinking_then_content():
    """Thinking zeigt Text; gleicher Anfang im späteren content wird nicht verdoppelt."""
    chunks = [
        {"message": {"content": "", "thinking": "Hello"}, "done": False},
        {"message": {"content": "Hello world", "thinking": ""}, "done": True},
    ]
    full = ""
    for c in chunks:
        part, _, err, _ = _extract_content(c)
        if err:
            break
        if part:
            full = _append_stream_piece(full, part)
    assert full == "Hello world"


def test_append_stream_piece_cumulative_duplicate_thinking_suppressed():
    """Wiederholter identischer Thinking-Block (kumulativ) wird nicht erneut angehängt."""
    chunks = [
        {"message": {"content": "", "thinking": "Same"}, "done": False},
        {"message": {"content": "", "thinking": "Same"}, "done": True},
    ]
    full = ""
    for c in chunks:
        part, _, err, _ = _extract_content(c)
        if err:
            break
        if part:
            full = _append_stream_piece(full, part)
    assert full == "Same"


def test_placeholder_starts_empty_first_update_replaces():
    """Kein sichtbares '...' vor dem ersten Stream-Token."""
    import sys

    from PySide6.QtWidgets import QApplication

    from app.gui.domains.operations.chat.panels.conversation_panel import (
        ChatConversationPanel,
    )

    _app = QApplication.instance() or QApplication(sys.argv)
    panel = ChatConversationPanel()
    w = panel.add_assistant_placeholder(model="x")
    QApplication.processEvents()
    assert w.toPlainText() == ""
    panel.update_last_assistant("ok")
    QApplication.processEvents()
    assert w.toPlainText() == "ok"


def test_partial_overlap_answer_prefix():
    full = ""
    chunks = [
        {"message": {"content": "", "thinking": "The answer is "}, "done": False},
        {"message": {"content": "The answer is 42.", "thinking": ""}, "done": True},
    ]
    for c in chunks:
        part, _, err, _ = _extract_content(c)
        if err:
            break
        if part:
            full = _append_stream_piece(full, part)
    assert full == "The answer is 42."

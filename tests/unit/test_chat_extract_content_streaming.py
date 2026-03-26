"""
Stream-Chunks: sichtbarer Content nur aus Content-Feldern; Thinking separat (kein Fallback).
"""

from app.gui.domains.operations.chat.chat_workspace import _extract_content
from app.ui_application.presenters.chat_stream_assembler import ChatStreamAccumulator


def test_thinking_only_chunk_empty_visible_not_fallback():
    chunk = {
        "message": {"role": "assistant", "content": "", "thinking": "Schritt A"},
        "done": False,
    }
    content, thinking, error, done = _extract_content(chunk)
    assert error is None
    assert done is False
    assert thinking == "Schritt A"
    assert content == ""


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


def test_whitespace_only_content_no_thinking_fallback_visible():
    chunk = {
        "message": {"role": "assistant", "content": "  \n", "thinking": "X"},
        "done": False,
    }
    content, thinking, _, _ = _extract_content(chunk)
    assert content == ""
    assert thinking == "X"


def test_streaming_sequence_thinking_deltas_then_content():
    """Wie gestreamte Teilstrings: thinking-Fragmente, dann echter content."""
    chunks = [
        {"message": {"content": "", "thinking": "a"}, "done": False},
        {"message": {"content": "", "thinking": "b"}, "done": False},
        {"message": {"content": "out", "thinking": ""}, "done": False},
        {"message": {"content": "", "thinking": ""}, "done": True},
    ]
    acc = ChatStreamAccumulator()
    for c in chunks:
        err, _d, _ch = acc.feed(c)
        assert err is None
    assert acc.full == "out"


def test_final_chunk_done_with_thinking_only():
    chunk = {
        "message": {"content": "", "thinking": "letztes Stück"},
        "done": True,
    }
    content, _, _, done = _extract_content(chunk)
    assert done is True
    assert content == ""


def test_error_chunk_ignores_message():
    chunk = {"error": "modell weg", "done": False}
    content, thinking, error, done = _extract_content(chunk)
    assert content == ""
    assert thinking == ""
    assert error == "modell weg"


def test_conversation_panel_end_state_matches_aggregate():
    """UI-Endzustand (Bubble) = produktiver ChatStreamAccumulator-Pfad."""
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
    acc = ChatStreamAccumulator()
    for c in chunks:
        err, _d, ch = acc.feed(c)
        assert err is None
        if ch:
            panel.update_last_assistant(acc.full)
    QApplication.processEvents()
    assert panel._last_assistant_bubble is not None
    assert panel._last_assistant_bubble.toPlainText() == acc.full == " C"


def test_accumulator_overlap_thinking_then_content():
    """Thinking zeigt Text; gleicher Anfang im späteren content wird nicht verdoppelt."""
    chunks = [
        {"message": {"content": "", "thinking": "Hello"}, "done": False},
        {"message": {"content": "Hello world", "thinking": ""}, "done": True},
    ]
    acc = ChatStreamAccumulator()
    for c in chunks:
        err, _d, _ = acc.feed(c)
        assert err is None
    assert acc.full == "Hello world"


def test_accumulator_thinking_only_no_visible_growth():
    """Nur-Thinking-Chunks füllen nicht den sichtbaren Assistentenpuffer."""
    chunks = [
        {"message": {"content": "", "thinking": "Same"}, "done": False},
        {"message": {"content": "", "thinking": "Same"}, "done": True},
    ]
    acc = ChatStreamAccumulator()
    for c in chunks:
        err, _d, _ = acc.feed(c)
        assert err is None
    assert acc.full == ""
    assert "Same" in acc.reasoning_text


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
    acc = ChatStreamAccumulator()
    chunks = [
        {"message": {"content": "", "thinking": "The answer is "}, "done": False},
        {"message": {"content": "The answer is 42.", "thinking": ""}, "done": True},
    ]
    for c in chunks:
        err, _d, _ = acc.feed(c)
        assert err is None
    assert acc.full == "The answer is 42."

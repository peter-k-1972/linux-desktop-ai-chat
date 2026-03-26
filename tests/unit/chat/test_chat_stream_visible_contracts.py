"""
Pflichttests: sichtbarer Stream = nur Content; Thinking getrennt; lange Deltas; finaler Chunk.

Bezug: Abschlussbedingung „Ballade von der Glocke“ — Antwort aus Content-Feldern,
Thinking nicht in der Bubble, keine Kürzung durch falsche Dedupe-Logik.
"""

from __future__ import annotations

from app.ui_application.presenters.chat_stream_assembler import (
    ChatStreamAccumulator,
    final_assistant_message_for_persistence,
)


def test_thinking_and_content_separated_visible_is_only_content():
    acc = ChatStreamAccumulator()
    acc.feed(
        {
            "message": {
                "content": "Das ist die öffentliche Antwort.",
                "thinking": "intern " * 40,
            },
            "done": False,
        }
    )
    assert acc.visible_assistant_text == "Das ist die öffentliche Antwort."
    assert "intern" in acc.reasoning_text
    assert "intern" not in acc.visible_assistant_text


def test_thinking_only_visible_empty_not_reasoning():
    acc = ChatStreamAccumulator()
    acc.feed({"message": {"content": "", "thinking": "Modell denkt laut."}, "done": True})
    assert acc.visible_assistant_text == ""
    assert "Modell denkt" in acc.reasoning_text


def test_content_arrives_only_in_last_chunk_after_many_thinking_chunks():
    """Wie lange Thinking-Phase, dann ein finaler Content-Chunk (inkl. done)."""
    excerpt = (
        "Fest gemauert in der Erden\n"
        "Steht die Form, aus Lehm gebrannt,\n"
        "Die, des Schaffens dumpfe Last\n"
        "Aus des Glockenstuhles Mund,\n"
        "Als ein stummes, reines Kind,\n"
        "Zum freien Ringe sprengt."
    )
    acc = ChatStreamAccumulator()
    for i in range(40):
        acc.feed({"message": {"content": "", "thinking": f"plan_{i}\n"}, "done": False})
    err, done, changed = acc.feed({"message": {"content": excerpt, "thinking": ""}, "done": True})
    assert err is None
    assert done is True
    assert changed is True
    assert acc.visible_assistant_text == excerpt
    assert "plan_0" not in acc.visible_assistant_text
    assert "plan_0" in acc.reasoning_text
    assert final_assistant_message_for_persistence(acc) == excerpt


def test_many_small_deltas_ballade_marker_intact():
    """Viele kleine Content-Deltas (mit echten Fragmenten, kein reines-Leerzeichen-Delta): kein Abschneiden."""
    line = (
        "Viertakt wird es, wie der Sterne Chöre — "
        "Doch mit des Atems Welle hämmerst du neue."
    )
    acc = ChatStreamAccumulator()
    step = 3
    for i in range(0, len(line), step):
        acc.feed({"message": {"content": line[i : i + step], "thinking": ""}, "done": False})
    acc.feed({"done": True})
    assert acc.visible_assistant_text == line
    assert "Viertakt" in acc.visible_assistant_text
    assert "hämmerst" in acc.visible_assistant_text

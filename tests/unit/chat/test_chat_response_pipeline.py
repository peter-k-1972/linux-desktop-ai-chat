"""
End-to-end-Pipeline-Tests: Parser → Accumulator → Finalizer (Persistenz/History-Contract).

Kein Live-Provider; sichert Garantien A–E aus der Chat-Response-Spezifikation.
"""

from __future__ import annotations

import os
import tempfile

import pytest

from app.core.db.database_manager import DatabaseManager
from app.ui_application.mappers.chat_mapper import chat_message_from_row
from app.chat.provider_stream_normalize import STRUCTURED_REASONING_CONTENT_TYPES
from app.chat.think_payload import resolve_think_payload_for_ollama
from app.ui_application.presenters.chat_stream_assembler import (
    ChatStreamAccumulator,
    ParsedChatChunk,
    final_assistant_message_for_persistence,
    parse_provider_chat_chunk,
)


def test_parse_ollama_and_openai_delta_normalize_same_visible_rule():
    ollama = {"message": {"content": "hi", "thinking": ""}, "done": False}
    openai = {
        "choices": [
            {"delta": {"content": "hi", "role": "assistant"}},
        ],
        "done": False,
    }
    po, pz = parse_provider_chat_chunk(ollama), parse_provider_chat_chunk(openai)
    assert po.visible_piece == pz.visible_piece == "hi"
    assert po.visible_source == pz.visible_source == "content"
    assert po.reasoning_raw_piece == pz.reasoning_raw_piece == ""


def test_choices_delta_content_priority_over_message_object():
    chunk = {
        "choices": [
            {"delta": {"content": "from_delta"}, "message": {"content": "from_message"}}
        ],
        "done": False,
    }
    p = parse_provider_chat_chunk(chunk)
    assert p.visible_piece == "from_delta"


def test_output_text_used_when_no_nonempty_message_content():
    p = parse_provider_chat_chunk(
        {"message": {"content": ""}, "output_text": "via_output_text", "done": False}
    )
    assert p.visible_piece == "via_output_text"
    assert p.visible_source == "content"


def test_openai_style_choices_message_object_not_only_delta():
    """Gateway liefert manchmal choices[0].message statt .delta."""
    chunk = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "final from message object",
                    "thinking": "",
                }
            }
        ],
        "done": True,
    }
    p = parse_provider_chat_chunk(chunk)
    assert p.visible_piece == "final from message object"
    assert p.visible_source == "content"


def test_regression_provider_chunk_error_json_null_does_not_trigger_parse_error_path():
    """Regression: generierte Clients liefern oft ``error: null``; kein Parse-Fehler, sichtbarer Text bleibt."""
    p = parse_provider_chat_chunk(
        {"message": {"content": "ok", "thinking": ""}, "error": None, "done": False}
    )
    assert p.error is None
    assert p.visible_piece == "ok"


def test_regression_accumulator_stream_survives_chunk_with_error_json_null():
    acc = ChatStreamAccumulator()
    acc.feed({"message": {"content": "a", "thinking": ""}, "error": None, "done": False})
    acc.feed({"message": {"content": "b", "thinking": ""}, "done": False})
    assert acc.visible_assistant_text == "ab"


def test_regression_structured_content_type_think_routes_to_reasoning_channel():
    """Regression: ``type: think`` (HF/OpenAI-artige Listen) gehoert nicht in ``visible_piece``."""
    chunk = {
        "message": {
            "content": [
                {"type": "think", "text": "plan silently"},
                {"type": "text", "text": "Nur das hier ist sichtbar."},
            ],
            "thinking": "",
        },
        "done": False,
    }
    p = parse_provider_chat_chunk(chunk)
    assert p.visible_piece == "Nur das hier ist sichtbar."
    assert "plan silently" in p.reasoning_raw_piece


@pytest.mark.parametrize(
    "reasoning_type",
    sorted(STRUCTURED_REASONING_CONTENT_TYPES - frozenset({"think"})),
)
def test_regression_structured_content_list_reasoning_types_route_to_reasoning_channel(
    reasoning_type: str,
):
    """Jeder in STRUCTURED_REASONING_CONTENT_TYPES eingetragene Typ (ausser think: eigener Test oben)."""
    chunk = {
        "message": {
            "content": [
                {"type": reasoning_type, "text": "INTERNAL_ONLY"},
                {"type": "text", "text": "VISIBLE_ONLY"},
            ],
            "thinking": "",
        },
        "done": False,
    }
    p = parse_provider_chat_chunk(chunk)
    assert p.visible_piece == "VISIBLE_ONLY"
    assert "INTERNAL_ONLY" in p.reasoning_raw_piece


def test_structured_content_list_splits_reasoning_from_visible():
    chunk = {
        "message": {
            "content": [
                {"type": "reasoning", "text": "step1"},
                {"type": "text", "text": "Visible answer."},
            ],
            "thinking": "",
        },
        "done": False,
    }
    p = parse_provider_chat_chunk(chunk)
    assert p.visible_piece == "Visible answer."
    assert p.visible_source == "content"
    assert "step1" in p.reasoning_raw_piece


def test_finalizer_strips_embedded_think_block_from_single_content_string():
    acc = ChatStreamAccumulator()
    ot = "".join(("<", "think", ">"))
    ct = "".join(("<", "/think", ">"))
    blob = f"{ot}hidden reasoning{ct}User-visible tail."
    acc.feed({"message": {"content": blob, "thinking": ""}})
    final = final_assistant_message_for_persistence(acc)
    assert "User-visible tail" in final
    assert "hidden reasoning" not in final


def test_ldc_stream_trace_env_does_not_break_feed(monkeypatch):
    monkeypatch.setenv("LDC_CHAT_STREAM_TRACE", "1")
    from app.chat.stream_pipeline_trace import ensure_trace_logger_info

    ensure_trace_logger_info()
    acc = ChatStreamAccumulator()
    acc.feed({"message": {"content": "x"}})
    assert acc.visible_assistant_text == "x"


def test_think_payload_matches_legacy_widget_rules():
    class _S:
        think_mode = "off"

    class _A:
        think_mode = "auto"

    class _H:
        think_mode = "high"

    assert resolve_think_payload_for_ollama(_S()) is False
    assert resolve_think_payload_for_ollama(_A()) is None
    assert resolve_think_payload_for_ollama(_H()) == "high"


def test_parse_reasoning_field_openai_reasoning_content():
    chunk = {
        "choices": [
            {"delta": {"content": "out", "reasoning_content": "think"}},
        ],
        "done": False,
    }
    p = parse_provider_chat_chunk(chunk)
    assert p.reasoning_raw_piece == "think"
    assert p.thinking_stripped == "think"
    assert p.visible_piece == "out"
    assert p.visible_source == "content"


def test_reasoning_channel_does_not_truncate_visible_content():
    """Gleicher Chunk mit Thinking + Content: Reasoning separat, sichtbar nur Content."""
    acc = ChatStreamAccumulator()
    acc.feed(
        {
            "message": {
                "content": "ANSWER",
                "thinking": "long internal reasoning",
            },
            "done": False,
        }
    )
    assert "long internal reasoning" in acc.reasoning_text
    assert acc.visible_assistant_text == "ANSWER"
    assert acc.reasoning_text not in acc.visible_assistant_text


def test_many_deltas_append_order_preserved():
    acc = ChatStreamAccumulator()
    for i in range(50):
        err, _d, _ = acc.feed({"message": {"content": str(i % 10)}})
        assert err is None
    assert acc.visible_assistant_text == "".join(str(i % 10) for i in range(50))


def test_late_empty_done_chunk_preserves_visible():
    acc = ChatStreamAccumulator()
    acc.feed({"message": {"content": "Z"}})
    err, done, changed = acc.feed({"done": True})
    assert err is None
    assert done is True
    assert changed is False
    assert final_assistant_message_for_persistence(acc) == "Z"


def test_plain_response_no_reasoning():
    acc = ChatStreamAccumulator()
    for c in (
        {"message": {"content": "a"}},
        {"message": {"content": "b"}},
        {"done": True},
    ):
        acc.feed(c)
    assert acc.reasoning_text == ""
    assert acc.visible_assistant_text == "ab"


def test_persist_finalizer_equals_visible_buffer():
    acc = ChatStreamAccumulator()
    acc.feed({"message": {"content": "FULL"}})
    assert final_assistant_message_for_persistence(acc) == acc.visible_assistant_text == "FULL"


def test_history_mapper_round_trip_full_content_no_truncation():
    """Read-Pfad (chat_message_from_row): voller DB-Content → Contract, kein Slice."""
    long_text = "X" * 50_000
    entry = chat_message_from_row(
        {"role": "assistant", "content": long_text, "model": "m"},
        message_index=0,
    )
    assert entry.content == long_text
    assert len(entry.content) == 50_000


def test_content_list_normalized_to_concatenated_text():
    p = parse_provider_chat_chunk({"message": {"content": ["a", "b", "c"], "thinking": ""}})
    assert p.visible_piece == "abc"


def test_overwrite_regression_only_last_chunk_would_fail_without_accumulation():
    """Sicherstellen, dass nicht nur der letzte Chunk den Text darstellt."""
    acc = ChatStreamAccumulator()
    acc.feed({"message": {"content": "first"}})
    acc.feed({"message": {"content": "second"}})
    assert acc.visible_assistant_text == "firstsecond"


def test_parsed_chat_chunk_immutable_snapshot():
    p = ParsedChatChunk("r", "r", "v", "content", None, True)
    assert p.done is True


class TestPersistenceReload:
    """D: Reload / History = gespeicherter Volltext (kein kürzeres DTO)."""

    @pytest.fixture
    def db(self):
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        try:
            yield DatabaseManager(db_path=path)
        finally:
            try:
                os.unlink(path)
            except OSError:
                pass

    def test_assistant_message_round_trip_full_text(self, db):
        db.create_chat("t")
        chat_id = 1
        acc = ChatStreamAccumulator()
        for part in ("part-",) * 100:
            acc.feed({"message": {"content": part}})
        final = final_assistant_message_for_persistence(acc)
        db.save_message(chat_id, "assistant", final, model="m")
        rows = db.load_chat(chat_id)
        assert len(rows) == 1
        loaded = rows[0][1]
        assert loaded == final
        assert len(loaded) == len(final)

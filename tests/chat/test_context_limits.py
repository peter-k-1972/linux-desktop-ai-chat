"""
Tests für Context Compression Rules – truncate_text, enforce_line_limit, render_limits.

Feste Regeln, keine Heuristik, reproduzierbar testbar.
"""

import pytest

from app.chat.context import ChatRequestContext
from app.chat.context_limits import (
    ChatContextRenderLimits,
    compute_budget_accounting,
    enforce_line_limit,
    truncate_text,
)
from app.core.config.chat_context_enums import ChatContextDetailLevel, ChatContextMode
from app.chat.context import ChatContextRenderOptions


def test_truncate_text_no_limit():
    """max_chars=None => unverändert."""
    assert truncate_text("", None) == ""
    assert truncate_text("short", None) == "short"
    assert truncate_text("a" * 200, None) == "a" * 200


def test_truncate_text_shorter_than_limit():
    """Kürzer oder gleich max_chars => unverändert."""
    assert truncate_text("", 10) == ""
    assert truncate_text("abc", 10) == "abc"
    assert truncate_text("abcdefghij", 10) == "abcdefghij"


def test_truncate_text_longer_than_limit():
    """Länger als max_chars => gekürzt mit '...'."""
    assert truncate_text("abcdefghijk", 8) == "abcde..."
    assert truncate_text("xy", 5) == "xy"
    assert truncate_text("hello world", 8) == "hello..."


def test_truncate_text_limit_small():
    """max_chars <= 3 => nur Prefix ohne '...'."""
    assert truncate_text("abcdef", 3) == "abc"
    assert truncate_text("ab", 2) == "ab"


def test_enforce_line_limit_none():
    """max_total_lines=None => unverändert."""
    lines = ["a", "b", "c", "d", "e"]
    assert enforce_line_limit(lines, None) == lines


def test_enforce_line_limit_cuts_tail():
    """max_total_lines greift, Überstand wird abgeschnitten."""
    lines = ["a", "b", "c", "d", "e"]
    assert enforce_line_limit(lines, 3) == ["a", "b", "c"]
    assert enforce_line_limit(lines, 5) == lines
    assert enforce_line_limit(lines, 10) == lines
    assert enforce_line_limit(lines, 1) == ["a"]


def test_project_name_truncated_in_fragment():
    """Projektname wird bei max_project_chars gekürzt."""
    ctx = ChatRequestContext(
        project_name="A" * 100,
        chat_title="Chat",
        topic_name=None,
    )
    limits = ChatContextRenderLimits(max_project_chars=15, max_chat_chars=None, max_topic_chars=None, max_total_lines=None)
    opts = ChatContextRenderOptions(include_project=True, include_chat=True, include_topic=False)
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
        opts,
        limits,
    )
    assert "Projekt: " in frag
    assert "AAAAAAAAAAAA..." in frag  # 12 chars + "..." = 15
    assert "A" * 100 not in frag


def test_topic_truncated_in_fragment():
    """Topic wird bei max_topic_chars gekürzt."""
    ctx = ChatRequestContext(
        project_name="P",
        chat_title="C",
        topic_name="T" * 80,
    )
    limits = ChatContextRenderLimits(max_project_chars=None, max_chat_chars=None, max_topic_chars=20, max_total_lines=None)
    opts = ChatContextRenderOptions(include_project=True, include_chat=True, include_topic=True)
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
        opts,
        limits,
    )
    assert "Topic: TTTTTTTTTTTTTTTTT..." in frag
    assert "T" * 80 not in frag


def test_fragment_respects_max_total_lines():
    """Fragment wird bei max_total_lines hart abgeschnitten."""
    ctx = ChatRequestContext(
        project_name="Projekt",
        chat_title="Chat",
        topic_name="Topic",
    )
    limits = ChatContextRenderLimits(
        max_project_chars=None,
        max_chat_chars=None,
        max_topic_chars=None,
        max_total_lines=3,
    )
    opts = ChatContextRenderOptions(include_project=True, include_chat=True, include_topic=True)
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
        opts,
        limits,
    )
    lines = frag.strip().split("\n")
    assert len(lines) == 3
    assert "Kontext:" in lines[0]
    assert "Projekt:" in lines[1]
    assert "Chat:" in lines[2]
    assert "Topic:" not in frag


def test_max_total_lines_2_returns_empty():
    """max_total_lines=2 liefert nur Header + eine Zeile; len(lines) > 1, also gültig."""
    ctx = ChatRequestContext(project_name="P", chat_title="C", topic_name=None)
    limits = ChatContextRenderLimits(max_total_lines=2)
    opts = ChatContextRenderOptions(include_project=True, include_chat=True, include_topic=False)
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
        opts,
        limits,
    )
    assert "Kontext:" in frag
    assert "Projekt:" in frag
    assert frag.count("\n") >= 1


def test_max_total_lines_1_returns_empty():
    """max_total_lines=1 => nur Header, len(limited) <= 1 => leerer String."""
    ctx = ChatRequestContext(project_name="P", chat_title="C", topic_name=None)
    limits = ChatContextRenderLimits(max_total_lines=1)
    opts = ChatContextRenderOptions(include_project=True, include_chat=True, include_topic=False)
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
        opts,
        limits,
    )
    assert frag == ""


def test_compute_budget_accounting_all_fields():
    """Budget-Accounting: alle Felder, policy limits."""
    limits = ChatContextRenderLimits(
        max_project_chars=100,
        max_chat_chars=100,
        max_topic_chars=80,
        max_total_lines=8,
    )
    budget = compute_budget_accounting(
        limits, include_project=True, include_chat=True, include_topic=True, limits_source="policy"
    )
    assert budget["configured_budget_total"] == (100 + 100 + 80) // 4  # 70 tokens
    assert budget["effective_budget_total"] == 70
    assert budget["reserved_budget_system"] > 0
    assert budget["reserved_budget_user"] == 0
    assert budget["available_budget_for_context"] == 70 - budget["reserved_budget_system"]
    assert budget["budget_strategy"] == "per_field_and_lines"
    assert budget["budget_source"] == "policy"


def test_compute_budget_accounting_default_source():
    """Budget-Accounting: limits_source=default."""
    limits = ChatContextRenderLimits(max_project_chars=80, max_chat_chars=80, max_topic_chars=60, max_total_lines=6)
    budget = compute_budget_accounting(
        limits, include_project=True, include_chat=True, include_topic=False, limits_source="default"
    )
    assert budget["budget_source"] == "default"
    assert budget["configured_budget_total"] == (80 + 80) // 4  # 40 tokens


def test_to_system_prompt_fragment_populates_overflow_info():
    """to_system_prompt_fragment mit _overflow_info: budget_overflow_prevented gesetzt bei Line-Limit."""
    ctx = ChatRequestContext(
        project_name="Projekt",
        chat_title="Chat",
        topic_name="Topic",
    )
    limits = ChatContextRenderLimits(
        max_project_chars=None,
        max_chat_chars=None,
        max_topic_chars=None,
        max_total_lines=2,
    )
    opts = ChatContextRenderOptions(include_project=True, include_chat=True, include_topic=True)
    overflow_info = {}
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
        opts,
        limits,
        _overflow_info=overflow_info,
    )
    assert overflow_info["budget_overflow_prevented"] is True
    assert overflow_info["budget_exhausted_before_optional_sources"] is True
    assert "Topic:" not in frag

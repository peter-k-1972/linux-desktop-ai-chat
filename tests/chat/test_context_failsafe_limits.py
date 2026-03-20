"""
Tests für Fail-Safe-Regeln bei Truncation und Limits.

Keine kaputten Kontextblöcke, auch bei langen Namen oder kaputten Daten.
"""

import pytest

from app.chat.context import (
    ChatRequestContext,
    ChatContextRenderOptions,
    inject_chat_context_into_messages,
    CTX_MARKER,
)
from app.chat.context_limits import ChatContextRenderLimits
from app.core.config.chat_context_enums import ChatContextDetailLevel, ChatContextMode


def test_no_injection_when_all_fields_empty_after_limits():
    """Nach Truncation alle Felder leer → keine Injection (Fragment leer)."""
    ctx = ChatRequestContext(
        project_name="X",
        chat_title="Y",
        topic_name="Z",
    )
    limits = ChatContextRenderLimits(
        max_project_chars=0,
        max_chat_chars=0,
        max_topic_chars=0,
        max_total_lines=None,
    )
    opts = ChatContextRenderOptions(include_project=True, include_chat=True, include_topic=True)
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
        opts,
        limits,
    )
    assert frag == ""


def test_no_injection_when_line_limit_too_small():
    """Line limit erlaubt nur Header, kein Feld → keine Injection."""
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


def test_header_only_fragment_returns_empty():
    """Fragment nur aus Header (keine Inhaltszeilen) → leerer String."""
    ctx = ChatRequestContext(project_name="P", chat_title="C", topic_name=None)
    limits = ChatContextRenderLimits(
        max_project_chars=0,
        max_chat_chars=0,
        max_total_lines=10,
    )
    opts = ChatContextRenderOptions(include_project=True, include_chat=True, include_topic=False)
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
        opts,
        limits,
    )
    assert frag == ""


def test_marker_only_fragment_never_injected():
    """Leerer oder Header-only Fragment → keine Injection, Messages unverändert."""
    messages = [{"role": "user", "content": "Hallo"}]

    result_empty = inject_chat_context_into_messages(messages, "")
    assert result_empty == messages
    assert len(result_empty) == 1
    assert CTX_MARKER not in str(result_empty[0].get("content", ""))

    result_header_only = inject_chat_context_into_messages(messages, "Kontext:\n")
    assert result_header_only == messages
    assert CTX_MARKER not in str(result_header_only[0].get("content", ""))

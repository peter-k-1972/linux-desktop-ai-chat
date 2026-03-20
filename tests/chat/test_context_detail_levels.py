"""
Tests für Chat-Kontext-Detail-Level (minimal | standard | full).

Präzise steuerbar, keine Heuristik.
"""

import pytest

from app.core.config.settings import AppSettings, ChatContextDetailLevel, ChatContextMode
from app.core.config.settings_backend import InMemoryBackend
from app.chat.context import ChatRequestContext


def test_neutral_minimal_omits_topic():
    """NEUTRAL + MINIMAL: Topic-Zeile weggelassen."""
    ctx = ChatRequestContext(
        project_name="XYZ",
        chat_title="Debug Session",
        topic_name="API",
    )
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.MINIMAL,
    )
    assert "Kontext:" in frag
    assert "Projekt: XYZ" in frag
    assert "Chat: Debug Session" in frag
    assert "Topic:" not in frag


def test_neutral_standard_includes_topic():
    """NEUTRAL + STANDARD: Topic-Zeile enthalten."""
    ctx = ChatRequestContext(
        project_name="XYZ",
        chat_title="Debug Session",
        topic_name="API",
    )
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.NEUTRAL,
        ChatContextDetailLevel.STANDARD,
    )
    assert "Kontext:" in frag
    assert "Projekt: XYZ" in frag
    assert "Chat: Debug Session" in frag
    assert "Topic: API" in frag


def test_semantic_minimal_short_form():
    """SEMANTIC + MINIMAL: Kurze Form ohne Topic, ohne Semantik-Hints."""
    ctx = ChatRequestContext(
        project_name="XYZ",
        chat_title="Debug Session",
        topic_name="API",
    )
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.SEMANTIC,
        ChatContextDetailLevel.MINIMAL,
    )
    assert "Arbeitskontext:" in frag
    assert "Projekt: XYZ" in frag
    assert "Chat: Debug Session" in frag
    assert "Topic:" not in frag
    assert "Themenbereich" not in frag
    assert "Berücksichtige" not in frag


def test_semantic_standard_has_partial_semantics():
    """SEMANTIC + STANDARD: Teilweise Semantik (Projekt, Chat), Topic ohne Hints."""
    ctx = ChatRequestContext(
        project_name="XYZ",
        chat_title="Debug Session",
        topic_name="API",
    )
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.SEMANTIC,
        ChatContextDetailLevel.STANDARD,
    )
    assert "Arbeitskontext:" in frag
    assert "Projekt: XYZ (Themenbereich)" in frag
    assert "Chat: Debug Session (laufende Konversation)" in frag
    assert "Topic: API" in frag
    assert "fokussierter Bereich" not in frag
    assert "Berücksichtige" not in frag


def test_semantic_full_has_instruction_line():
    """SEMANTIC + FULL: Volle Semantik inkl. Instruktionszeile."""
    ctx = ChatRequestContext(
        project_name="XYZ",
        chat_title="Debug Session",
        topic_name="API",
    )
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.SEMANTIC,
        ChatContextDetailLevel.FULL,
    )
    assert "Arbeitskontext:" in frag
    assert "Projekt: XYZ (Themenbereich)" in frag
    assert "Chat: Debug Session (laufende Konversation)" in frag
    assert "Topic: API (fokussierter Bereich)" in frag
    assert "Berücksichtige diesen Kontext bei der Antwort." in frag


def test_invalid_detail_level_falls_back_to_standard():
    """Ungültiger chat_context_detail_level → STANDARD."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_detail_level", "invalid")
    s = AppSettings(backend=backend)
    assert s.get_chat_context_detail_level() == ChatContextDetailLevel.STANDARD

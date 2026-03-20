"""
Tests für Chat-Kontextmodus (off / neutral / semantic).

Backend-first, deterministisch, reproduzierbar testbar.
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.core.config.settings import AppSettings, ChatContextMode
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.chat.context import (
    ChatRequestContext,
    build_chat_context,
    inject_chat_context_into_messages,
)
from app.services.infrastructure import set_infrastructure, _ServiceInfrastructure


def _ensure_qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


@pytest.fixture
def qapp():
    _ensure_qapp()
    yield


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    try:
        yield path
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


@pytest.fixture
def services(temp_db, qapp):
    db = DatabaseManager(db_path=temp_db)
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = AppSettings()
    set_infrastructure(infra)
    from app.services.project_service import ProjectService
    from app.services.chat_service import ChatService
    from app.services.topic_service import TopicService
    from app.services.project_service import set_project_service
    from app.services.chat_service import set_chat_service
    from app.services.topic_service import set_topic_service
    set_project_service(ProjectService())
    set_chat_service(ChatService())
    set_topic_service(TopicService())
    yield
    set_project_service(None)
    set_chat_service(None)
    set_topic_service(None)
    set_infrastructure(None)


def test_mode_off_skips_injection(services):
    """Modus off: Keine Kontext-Injektion."""
    from app.services.chat_service import get_chat_service
    from app.services.project_service import get_project_service
    from app.services.infrastructure import get_infrastructure

    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    p1 = proj_svc.create_project("Projekt", "", "active")
    cid = chat_svc.create_chat_in_project(p1, "Test Chat")

    settings = get_infrastructure().settings
    settings.chat_context_mode = "off"
    settings.save()

    messages = [{"role": "user", "content": "Hallo"}]
    result = chat_svc._inject_chat_context(messages, cid)

    assert len(result) == 1
    assert result[0]["role"] == "user"
    assert result == messages


def test_mode_neutral_format():
    """Neutraler Modus: nüchternes Format."""
    ctx = ChatRequestContext(
        project_name="XYZ",
        chat_title="Debug Session",
        topic_name="API",
    )
    frag = ctx.to_system_prompt_fragment(ChatContextMode.NEUTRAL)
    assert "Kontext:" in frag
    assert "XYZ" in frag
    assert "Debug Session" in frag
    assert "API" in frag
    assert "Arbeitskontext" not in frag
    assert "Themenbereich" not in frag
    assert "Berücksichtige" not in frag


def test_mode_semantic_format():
    """Semantischer Modus FULL: angereichertes Format mit Hints."""
    from app.core.config.settings import ChatContextDetailLevel

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
    assert "XYZ" in frag
    assert "Debug Session" in frag
    assert "API" in frag
    assert "Themenbereich" in frag
    assert "fokussierter Bereich" in frag
    assert "Berücksichtige diesen Kontext" in frag


def test_invalid_setting_fallback_to_semantic():
    """Ungültiger chat_context_mode wird zu SEMANTIC normalisiert."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_mode", "invalid")
    s = AppSettings(backend=backend)
    assert s.get_chat_context_mode() == ChatContextMode.SEMANTIC


def test_injection_into_empty_messages():
    """Injection in leere Liste ändert nichts."""
    result = inject_chat_context_into_messages([], "Kontext:\n- Projekt: X\n")
    assert result == []


def test_injection_appends_to_existing_system_message():
    """Injection hängt Fragment an bestehende Systemnachricht an (nicht ersetzt)."""
    fragment = "Kontext:\n- Projekt: P\n- Chat: C\n- Topic: T\n"
    messages = [
        {"role": "system", "content": "Antworte formal."},
        {"role": "user", "content": "Hallo"},
    ]
    result = inject_chat_context_into_messages(messages, fragment)

    assert len(result) == 2
    assert result[0]["role"] == "system"
    content = result[0]["content"]
    assert "Antworte formal" in content
    assert "Kontext:" in content
    assert "Projekt: P" in content
    assert content.startswith("Antworte formal")
    assert content.endswith("Topic: T\n")


def test_no_duplicate_injection():
    """Keine Duplikate bei mehrfacher Injection."""
    fragment = "Kontext:\n- Projekt: P\n- Chat: C\n- Topic: T\n"
    messages = [
        {"role": "system", "content": "Antworte formal."},
        {"role": "user", "content": "Hallo"},
    ]
    result = inject_chat_context_into_messages(messages, fragment)
    result2 = inject_chat_context_into_messages(result, fragment)

    assert result[0]["content"].count("Kontext:") == 1
    assert result2[0]["content"].count("Kontext:") == 1
    assert result[0]["content"] == result2[0]["content"]


def test_no_duplicate_marker():
    """[[CTX]]-Marker verhindert erneute Injection."""
    from app.chat.context import CTX_MARKER

    fragment = "Arbeitskontext:\n- Projekt: P\n"
    messages = [{"role": "user", "content": "Hi"}]
    result = inject_chat_context_into_messages(messages, fragment)
    result2 = inject_chat_context_into_messages(result, fragment)

    assert CTX_MARKER in result[0]["content"]
    assert result[0]["content"].count(CTX_MARKER) == 1
    assert result[0]["content"] == result2[0]["content"]


def test_append_spacing_correct():
    """Append nutzt rstrip und sauberen Abstand (\\n\\n)."""
    fragment = "Kontext:\n- Projekt: X\n"
    messages = [
        {"role": "system", "content": "Antworte kurz.  \n\n  "},
        {"role": "user", "content": "Hallo"},
    ]
    result = inject_chat_context_into_messages(messages, fragment)

    content = result[0]["content"]
    assert content.startswith("Antworte kurz.")
    assert "  \n\n  " not in content
    assert "\n\n[[CTX]]" in content or "[[CTX]]" in content


def test_handles_empty_messages():
    """Leere Liste und kaputte Inputs: fail-safe, kein Crash."""
    valid_fragment = "Kontext:\n- Chat: X"
    assert inject_chat_context_into_messages([], valid_fragment) == []
    assert inject_chat_context_into_messages(None, valid_fragment) == []
    result = inject_chat_context_into_messages([{}], valid_fragment)
    assert len(result) == 2
    assert result[0]["role"] == "system"


def test_handles_missing_topic_neutral():
    """NEUTRAL: Fehlendes Topic → Zeile komplett weggelassen."""
    ctx = ChatRequestContext(
        project_name="P",
        chat_title="C",
        topic_name=None,
    )
    frag = ctx.to_system_prompt_fragment(ChatContextMode.NEUTRAL)
    assert "Kontext:" in frag
    assert "Projekt: P" in frag
    assert "Chat: C" in frag
    assert "Topic:" not in frag


def test_handles_missing_topic_semantic():
    """SEMANTIC FULL: Fehlendes Topic → '—' explizit sichtbar."""
    from app.core.config.settings import ChatContextDetailLevel

    ctx = ChatRequestContext(
        project_name="P",
        chat_title="C",
        topic_name=None,
    )
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.SEMANTIC,
        ChatContextDetailLevel.FULL,
    )
    assert "Arbeitskontext:" in frag
    assert "Topic:" in frag
    assert "—" in frag
    assert "fokussierter Bereich" in frag

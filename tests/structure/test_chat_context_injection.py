"""
Tests für Chat-Kontext-Injection.

Verifiziert:
- ChatContext wird korrekt erstellt
- Kontext wird korrekt injiziert
- Keine Regression (chat_id=None → keine Injection)
- Kontext fehlt nie bei Requests (wenn chat_id gesetzt)
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.core.db.database_manager import DatabaseManager
from app.services.infrastructure import set_infrastructure, _ServiceInfrastructure
from app.core.config.settings import AppSettings, ChatContextDetailLevel, ChatContextMode
from app.chat.context import (
    ChatContext,
    build_chat_context,
    inject_chat_context_into_messages,
)


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
    db = DatabaseManager(db_path=temp_db, ensure_default_project=False)
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


def test_chat_context_empty():
    """Leerer ChatContext ist leer."""
    ctx = ChatContext()
    assert ctx.is_empty()
    assert ctx.to_system_prompt_fragment(ChatContextMode.SEMANTIC) == ""


def test_chat_context_with_chat_title():
    """ChatContext mit nur chat_title."""
    ctx = ChatContext(chat_title="Debug Session")
    assert not ctx.is_empty()
    frag = ctx.to_system_prompt_fragment(ChatContextMode.SEMANTIC)
    assert "Debug Session" in frag
    assert "Chat" in frag


def test_chat_context_full():
    """ChatRequestContext mit Projekt, Chat, Topic – semantisch FULL angereichert."""
    ctx = ChatContext(
        project_name="XYZ",
        chat_title="Debug Session",
        topic_name="API",
    )
    assert not ctx.is_empty()
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


def test_build_chat_context_without_services():
    """build_chat_context ohne Services liefert leeren Kontext."""
    ctx = build_chat_context(None)
    assert ctx.is_empty()

    ctx = build_chat_context(0)
    assert ctx.is_empty()


def test_build_chat_context_with_chat(services):
    """build_chat_context mit existierendem Chat."""
    from app.services.chat_service import get_chat_service
    from app.services.project_service import get_project_service

    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    p1 = proj_svc.create_project("Projekt A", "", "active")
    cid = chat_svc.create_chat_in_project(p1, "Mein Chat", topic_id=None)

    ctx = build_chat_context(cid)
    assert ctx.project_id == p1
    assert ctx.project_name == "Projekt A"
    assert ctx.chat_id == cid
    assert ctx.chat_title == "Mein Chat"
    assert ctx.is_global_chat is False


def test_build_chat_context_global_chat(services):
    """Globale Chats: is_global_chat=True, kein Projekt."""
    from app.services.chat_service import get_chat_service

    chat_svc = get_chat_service()
    cid = chat_svc.create_chat("Globaler Chat")

    ctx = build_chat_context(cid)
    assert ctx.project_id is None
    assert ctx.project_name is None
    assert ctx.chat_id == cid
    assert ctx.chat_title == "Globaler Chat"
    assert ctx.is_global_chat is True


def test_global_chat_injection_format(services):
    """Globale Chats: Kontext wird injiziert (via ChatService)."""
    from app.services.chat_service import get_chat_service

    chat_svc = get_chat_service()
    cid = chat_svc.create_chat("Globaler Chat")

    messages = [{"role": "user", "content": "Hallo"}]
    result = chat_svc._inject_chat_context(messages, cid)

    assert len(result) == 2
    assert result[0]["role"] == "system"
    assert "Globaler Chat" in result[0]["content"]


def test_missing_topic_does_not_break(services):
    """Fehlendes Topic bricht nichts – Topic-Zeile mit —."""
    from app.services.chat_service import get_chat_service
    from app.services.project_service import get_project_service

    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    p1 = proj_svc.create_project("Projekt", "", "active")
    cid = chat_svc.create_chat_in_project(p1, "Chat ohne Topic", topic_id=None)

    ctx = build_chat_context(cid)
    assert ctx.topic_id is None
    assert ctx.topic_name is None
    frag = ctx.to_system_prompt_fragment(ChatContextMode.SEMANTIC)
    assert "Arbeitskontext:" in frag
    assert "Chat ohne Topic" in frag

    messages = [{"role": "user", "content": "Hi"}]
    result = chat_svc._inject_chat_context(messages, cid)
    assert len(result) == 2
    assert "Chat ohne Topic" in result[0]["content"]


def test_inject_context_empty_messages():
    """Injection in leere Liste ändert nichts."""
    result = inject_chat_context_into_messages([], "Kontext:\n- Projekt: X\n")
    assert result == []


def test_inject_context_no_chat_id(services):
    """ChatService mit chat_id=0 (leerer Kontext) injiziert nichts."""
    from app.services.chat_service import get_chat_service

    chat_svc = get_chat_service()
    messages = [{"role": "user", "content": "Hallo"}]
    result = chat_svc._inject_chat_context(messages, 0)
    assert result == messages


def test_inject_context_adds_system_message(services):
    """Injection fügt System-Nachricht hinzu."""
    from app.services.chat_service import get_chat_service
    from app.services.project_service import get_project_service

    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    p1 = proj_svc.create_project("Projekt", "", "active")
    cid = chat_svc.create_chat_in_project(p1, "Test Chat")

    messages = [{"role": "user", "content": "Hallo"}]
    result = chat_svc._inject_chat_context(messages, cid)

    assert len(result) == 2
    assert result[0]["role"] == "system"
    assert "Projekt" in result[0]["content"]
    assert "Test Chat" in result[0]["content"]
    assert result[1] == messages[0]


def test_inject_context_merges_with_existing_system(services):
    """Injection hängt an bestehende System-Nachricht an (Chat Guard)."""
    from app.services.chat_service import get_chat_service
    from app.services.project_service import get_project_service

    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    p1 = proj_svc.create_project("Projekt", "", "active")
    cid = chat_svc.create_chat_in_project(p1, "Test Chat")

    messages = [
        {"role": "system", "content": "Antworte formal."},
        {"role": "user", "content": "Hallo"},
    ]
    result = chat_svc._inject_chat_context(messages, cid)

    assert len(result) == 2
    assert result[0]["role"] == "system"
    assert "Projekt" in result[0]["content"]
    assert "Test Chat" in result[0]["content"]
    assert "Antworte formal" in result[0]["content"]
    assert result[1] == messages[1]


def test_semantic_context_not_overloaded():
    """Semantisch FULL angereicherter Kontext bleibt kompakt – keine Prompt-Explosion."""
    ctx = ChatContext(
        project_name="Projekt",
        chat_title="Chat",
        topic_name="Topic",
    )
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.SEMANTIC,
        ChatContextDetailLevel.FULL,
    )
    # Maximal ~280 Zeichen für typischen Kontext – keine Explosion
    assert len(frag) < 300
    assert "Berücksichtige" in frag
    assert "Themenbereich" in frag
    assert "laufende Konversation" in frag


def test_chat_service_accepts_chat_id():
    """ChatService.chat() akzeptiert chat_id als optionalen Parameter."""
    from app.services.chat_service import get_chat_service

    svc = get_chat_service()
    import inspect
    sig = inspect.signature(svc.chat)
    params = list(sig.parameters.keys())
    assert "chat_id" in params


# --- Kontextmodus (off / neutral / semantic) ---


def test_context_mode_neutral_format():
    """Neutraler Modus: nüchternes Format ohne semantische Hints."""
    ctx = ChatContext(
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


def test_context_mode_semantic_format():
    """Semantischer Modus FULL: angereichertes Format mit Hints."""
    ctx = ChatContext(
        project_name="XYZ",
        chat_title="Debug Session",
        topic_name="API",
    )
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.SEMANTIC,
        ChatContextDetailLevel.FULL,
    )
    assert "Arbeitskontext:" in frag
    assert "Themenbereich" in frag
    assert "Berücksichtige" in frag


def test_inject_context_mode_off_with_valid_chat(services):
    """Modus off: Auch bei gültigem Chat keine Injektion."""
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


def test_inject_context_mode_neutral(services):
    """Modus neutral: Nüchternes Format injiziert."""
    from app.services.chat_service import get_chat_service
    from app.services.project_service import get_project_service
    from app.services.infrastructure import get_infrastructure

    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    p1 = proj_svc.create_project("Projekt", "", "active")
    cid = chat_svc.create_chat_in_project(p1, "Test Chat")

    settings = get_infrastructure().settings
    settings.chat_context_mode = "neutral"
    settings.save()

    messages = [{"role": "user", "content": "Hallo"}]
    result = chat_svc._inject_chat_context(messages, cid)

    assert len(result) == 2
    assert result[0]["role"] == "system"
    content = result[0]["content"]
    assert "Kontext:" in content
    assert "Projekt" in content
    assert "Test Chat" in content
    assert "Arbeitskontext" not in content
    assert "Themenbereich" not in content
    assert "Berücksichtige" not in content


def test_settings_chat_context_mode_default():
    """chat_context_mode hat Default semantic und wird persistiert."""
    from app.core.config.settings_backend import InMemoryBackend

    backend = InMemoryBackend()
    s = AppSettings(backend=backend)
    assert s.chat_context_mode == "semantic"

    s.chat_context_mode = "neutral"
    s.save()
    s2 = AppSettings(backend=backend)
    assert s2.chat_context_mode == "neutral"


def test_settings_chat_context_mode_invalid_normalized():
    """Ungültiger chat_context_mode wird zu semantic normalisiert."""
    from app.core.config.settings_backend import InMemoryBackend

    backend = InMemoryBackend()
    backend.setValue("chat_context_mode", "invalid")
    s = AppSettings(backend=backend)
    assert s.chat_context_mode == "semantic"


def test_chat_service_uses_context_mode_from_settings(services):
    """ChatService liest chat_context_mode aus Settings via get_chat_context_mode()."""
    from app.services.infrastructure import get_infrastructure
    from app.services.chat_service import get_chat_service
    from app.services.project_service import get_project_service

    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    p1 = proj_svc.create_project("Projekt", "", "active")
    cid = chat_svc.create_chat_in_project(p1, "Test Chat")

    settings = get_infrastructure().settings
    settings.chat_context_mode = "neutral"
    settings.save()

    messages = [{"role": "user", "content": "Hi"}]
    result = chat_svc._inject_chat_context(messages, cid)

    assert "Kontext:" in result[0]["content"]
    assert "Arbeitskontext" not in result[0]["content"]

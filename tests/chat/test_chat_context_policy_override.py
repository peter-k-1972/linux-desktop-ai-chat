"""
Tests für Chat-Kontext-Policy-Override.

Einzelner Chat kann Projekt-Policy überschreiben.
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_policies import ChatContextPolicy
from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.services.chat_service import ChatService, get_chat_service, set_chat_service
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import ProjectService, get_project_service, set_project_service
from app.services.topic_service import TopicService, set_topic_service


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
    infra._settings = None
    set_infrastructure(infra)
    set_project_service(ProjectService())
    set_chat_service(ChatService())
    set_topic_service(TopicService())
    try:
        yield
    finally:
        set_project_service(None)
        set_chat_service(None)
        set_topic_service(None)
        set_infrastructure(None)


def test_chat_policy_overrides_project_policy(services):
    """Chat-Policy überschreibt Projekt-Policy."""
    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    db = proj_svc._infra.database

    pid = db.create_project(
        "Arch-Projekt", description="", status="active", default_context_policy="architecture"
    )
    cid = db.create_chat("Debug-Chat", default_context_policy="debug")
    db.add_chat_to_project(pid, cid, None)

    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", False)
    settings = AppSettings(backend)
    settings.load()

    chat_svc._infra._settings = settings

    _, _, _, trace, _ = chat_svc._resolve_context_configuration(
        request_context_hint=None,
        context_policy=None,
        chat_context_policy=ChatContextPolicy.DEBUG,
        project_context_policy=ChatContextPolicy.ARCHITECTURE,
    )

    assert trace.source == "chat_policy"
    assert trace.profile == "strict_minimal"


def test_chat_policy_used_when_no_explicit_policy(services):
    """Chat-Policy wird genutzt wenn keine explizite Policy übergeben."""
    chat_svc = get_chat_service()
    db = chat_svc._infra.database

    cid = db.create_chat("Arch-Chat", default_context_policy="architecture")

    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", False)
    settings = AppSettings(backend)
    settings.load()

    chat_svc._infra._settings = settings

    messages = [{"role": "user", "content": "Hello"}]
    result = chat_svc._inject_chat_context(messages, cid)

    assert result != messages
    fragment = result[0].get("content", "")
    assert "[[CTX]]" in fragment
    assert "- Topic:" in fragment


def test_chat_policy_precedence_chain(services):
    """Vollständige Kette: profile_enabled > explicit > chat > project."""
    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    db = proj_svc._infra.database

    pid = db.create_project(
        "Arch-Projekt", description="", status="active", default_context_policy="architecture"
    )
    cid = db.create_chat("Debug-Chat", default_context_policy="debug")
    db.add_chat_to_project(pid, cid, None)

    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", True)
    backend.setValue("chat_context_profile", "balanced")
    settings = AppSettings(backend)
    settings.load()

    chat_svc._infra._settings = settings

    _, _, _, trace, _ = chat_svc._resolve_context_configuration(
        request_context_hint=None,
        context_policy=ChatContextPolicy.DEBUG,
        chat_context_policy=ChatContextPolicy.DEBUG,
        project_context_policy=ChatContextPolicy.ARCHITECTURE,
    )

    assert trace.source == "profile"
    assert trace.profile == "balanced"

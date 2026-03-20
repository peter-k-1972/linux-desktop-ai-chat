"""
Tests für Projekt-Kontext-Policy.

Projekte können default_context_policy setzen.
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
from app.services.project_service import get_project_service
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import ProjectService, set_project_service
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


def test_project_policy_applied(services):
    """Projekt mit default_context_policy=architecture → full_guidance."""
    proj_svc = get_project_service()
    chat_svc = get_chat_service()

    pid = proj_svc._infra.database.create_project(
        "Arch-Projekt", description="", status="active", default_context_policy="architecture"
    )
    cid = chat_svc.create_chat("Test")
    proj_svc._infra.database.add_chat_to_project(pid, cid, None)

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


def test_project_policy_overridden_by_explicit_policy(services):
    """Explizite context_policy überschreibt Projekt-Policy."""
    proj_svc = get_project_service()
    chat_svc = get_chat_service()

    pid = proj_svc._infra.database.create_project(
        "Arch-Projekt", description="", status="active", default_context_policy="architecture"
    )
    cid = chat_svc.create_chat("Test")
    proj_svc._infra.database.add_chat_to_project(pid, cid, None)

    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", False)
    settings = AppSettings(backend)
    settings.load()

    chat_svc._infra._settings = settings

    _, _, _, trace, _ = chat_svc._resolve_context_configuration(
        request_context_hint=None,
        context_policy=ChatContextPolicy.DEBUG,
        project_context_policy=ChatContextPolicy.ARCHITECTURE,
    )

    assert trace.source == "policy"
    assert trace.profile == "strict_minimal"


def test_project_policy_overridden_by_profile_enabled(services):
    """profile_enabled=True überschreibt Projekt-Policy."""
    proj_svc = get_project_service()
    chat_svc = get_chat_service()

    pid = proj_svc._infra.database.create_project(
        "Arch-Projekt", description="", status="active", default_context_policy="architecture"
    )
    cid = chat_svc.create_chat("Test")
    proj_svc._infra.database.add_chat_to_project(pid, cid, None)

    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", True)
    backend.setValue("chat_context_profile", "strict_minimal")
    settings = AppSettings(backend)
    settings.load()

    chat_svc._infra._settings = settings

    _, _, _, trace, _ = chat_svc._resolve_context_configuration(
        request_context_hint=None,
        context_policy=None,
        project_context_policy=ChatContextPolicy.ARCHITECTURE,
    )

    assert trace.source == "profile"
    assert trace.profile == "strict_minimal"


def test_project_policy_fallback_to_settings(services):
    """Projekt ohne Policy → Einzelsettings."""
    proj_svc = get_project_service()
    chat_svc = get_chat_service()

    pid = proj_svc._infra.database.create_project(
        "Normal-Projekt", description="", status="active", default_context_policy=None
    )
    cid = chat_svc.create_chat("Test")
    proj_svc._infra.database.add_chat_to_project(pid, cid, None)

    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", False)
    backend.setValue("chat_context_mode", "off")
    settings = AppSettings(backend)
    settings.load()

    chat_svc._infra._settings = settings

    messages = [{"role": "user", "content": "Hello"}]
    result = chat_svc._inject_chat_context(messages, cid)

    assert result == messages

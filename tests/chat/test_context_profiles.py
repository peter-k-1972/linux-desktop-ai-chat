"""
Tests für Chat-Kontext-Profile.

Presets sind regelbasiert, keine Heuristik.
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_profiles import resolve_chat_context_profile
from app.core.config.chat_context_enums import ChatContextDetailLevel, ChatContextMode
from app.core.config.settings import AppSettings, ChatContextProfile
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.services.chat_service import ChatService, get_chat_service, set_chat_service
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


def test_strict_minimal_profile_resolution():
    """strict_minimal → semantic + minimal + project_only."""
    resolved = resolve_chat_context_profile(ChatContextProfile.STRICT_MINIMAL)
    assert resolved.mode == ChatContextMode.SEMANTIC
    assert resolved.detail == ChatContextDetailLevel.MINIMAL
    assert resolved.include_project is True
    assert resolved.include_chat is False
    assert resolved.include_topic is False


def test_balanced_profile_resolution():
    """balanced → semantic + standard + project_chat."""
    resolved = resolve_chat_context_profile(ChatContextProfile.BALANCED)
    assert resolved.mode == ChatContextMode.SEMANTIC
    assert resolved.detail == ChatContextDetailLevel.STANDARD
    assert resolved.include_project is True
    assert resolved.include_chat is True
    assert resolved.include_topic is False


def test_full_guidance_profile_resolution():
    """full_guidance → semantic + full + all."""
    resolved = resolve_chat_context_profile(ChatContextProfile.FULL_GUIDANCE)
    assert resolved.mode == ChatContextMode.SEMANTIC
    assert resolved.detail == ChatContextDetailLevel.FULL
    assert resolved.include_project is True
    assert resolved.include_chat is True
    assert resolved.include_topic is True


def test_invalid_profile_falls_back_to_balanced():
    """Ungültiger Profil-Wert → get_chat_context_profile liefert BALANCED."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_profile", "invalid_profile")
    settings = AppSettings(backend)
    settings.load()
    assert settings.get_chat_context_profile() == ChatContextProfile.BALANCED


@pytest.fixture
def services(temp_db, qapp):
    db = DatabaseManager(db_path=temp_db)
    db.create_chat("Test Chat")
    db.create_project("Test Project")
    db.add_chat_to_project(1, 1, None)
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = AppSettings()
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


def test_profile_enabled_overrides_individual_context_settings(services):
    """Profil aktiv: Einzelsettings werden ignoriert, Profil-Werte verwendet."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", True)
    backend.setValue("chat_context_profile", "strict_minimal")
    backend.setValue("chat_context_include_topic", True)
    backend.setValue("chat_context_include_chat", True)
    settings = AppSettings(backend)
    settings.load()

    infra = get_chat_service()._infra
    infra._settings = settings

    messages = [{"role": "user", "content": "Hello"}]
    result = get_chat_service()._inject_chat_context(messages, 1)

    assert result != messages
    fragment = result[0].get("content", "")
    assert "[[CTX]]" in fragment
    assert "Arbeitskontext:" in fragment
    assert "- Projekt:" in fragment
    assert "- Chat:" not in fragment
    assert "- Topic:" not in fragment


def test_profile_disabled_uses_individual_settings(services):
    """Profil deaktiviert: Einzelsettings (mode=off) → keine Injektion."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_profile_enabled", False)
    backend.setValue("chat_context_mode", "off")
    settings = AppSettings(backend)
    settings.load()

    infra = get_chat_service()._infra
    infra._settings = settings

    messages = [{"role": "user", "content": "Hello"}]
    result = get_chat_service()._inject_chat_context(messages, 1)

    assert result == messages

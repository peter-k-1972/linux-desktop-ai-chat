"""
Regressions-Tests für Chat-Kontext-Governance.

Architektur-Grenzen maschinell absichern:
- Context-Modul erzeugt Fragmente
- ChatService entscheidet Injection
- Settings liefern nur Konfiguration

Governance ist nicht nur Text – Governance ist testbar abgesichert.
"""

import inspect
import os
import tempfile
from pathlib import Path

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context import ChatRequestContext
from app.core.config.chat_context_enums import ChatContextDetailLevel, ChatContextMode
from app.core.config.settings import AppSettings
from app.core.db.database_manager import DatabaseManager
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.chat_service import ChatService, set_chat_service
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


def test_off_mode_never_injects(services):
    """mode=off: Keine Kontext-Injektion, Messages unverändert."""
    from app.services.chat_service import get_chat_service
    from app.services.infrastructure import get_infrastructure
    from app.services.project_service import get_project_service

    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    p1 = proj_svc.create_project("P", "", "active")
    cid = chat_svc.create_chat_in_project(p1, "Test")

    settings = get_infrastructure().settings
    settings.chat_context_mode = "off"
    settings.save()

    messages = [{"role": "user", "content": "Hallo"}]
    result = chat_svc._inject_chat_context(messages, cid)

    assert result == messages
    assert len(result) == 1
    assert result[0]["role"] == "user"


def test_empty_render_options_skip_injection(services):
    """Alle Render-Optionen aus: Kein Fragment → keine Injection."""
    from app.services.chat_service import get_chat_service
    from app.services.infrastructure import get_infrastructure
    from app.services.project_service import get_project_service

    proj_svc = get_project_service()
    chat_svc = get_chat_service()
    p1 = proj_svc.create_project("P", "", "active")
    cid = chat_svc.create_chat_in_project(p1, "Test")

    settings = get_infrastructure().settings
    settings.chat_context_mode = "semantic"
    settings.chat_context_include_project = False
    settings.chat_context_include_chat = False
    settings.chat_context_include_topic = False
    settings.save()

    messages = [{"role": "user", "content": "Hallo"}]
    result = chat_svc._inject_chat_context(messages, cid)

    assert result == messages
    assert len(result) == 1


def test_context_module_has_no_settings_dependency():
    """Context-Modul importiert nicht von app.core.config.settings."""
    context_path = Path(__file__).resolve().parent.parent.parent / "app" / "chat" / "context.py"
    source = context_path.read_text(encoding="utf-8")

    forbidden = [
        "from app.core.config.settings",
        "import app.core.config.settings",
    ]
    for pattern in forbidden:
        assert pattern not in source, (
            f"Context-Modul darf nicht von settings abhängen. Gefunden: {pattern}"
        )


def test_chat_service_controls_injection(services):
    """ChatService ist die einzige Stelle, die Kontext-Injection durchführt."""
    from app.services.chat_service import ChatService

    source = inspect.getsourcefile(ChatService)
    content = Path(source).read_text(encoding="utf-8")

    assert "_inject_chat_context" in content
    assert "inject_chat_context_into_messages" in content
    assert "build_chat_context" in content
    assert "get_chat_context_mode" in content or "chat_context_mode" in content


def test_semantic_full_contains_instruction():
    """SEMANTIC + FULL: Fragment enthält die Anweisungszeile."""
    ctx = ChatRequestContext(
        project_name="P",
        chat_title="C",
        topic_name="T",
    )
    frag = ctx.to_system_prompt_fragment(
        ChatContextMode.SEMANTIC,
        ChatContextDetailLevel.FULL,
    )
    assert "Berücksichtige diesen Kontext bei der Antwort." in frag


def test_default_configuration_matches_adr():
    """Default aus Settings entspricht ADR_CHAT_CONTEXT_DEFAULT.md (semantic + standard + project_chat)."""
    from app.core.config.settings_backend import InMemoryBackend

    backend = InMemoryBackend()
    settings = AppSettings(backend=backend)

    assert settings.chat_context_mode == "semantic", "ADR: mode=semantic"
    assert settings.chat_context_detail_level == "standard", "ADR: detail=standard"
    assert settings.chat_context_include_project is True, "ADR: include_project=true"
    assert settings.chat_context_include_chat is True, "ADR: include_chat=true"
    assert settings.chat_context_include_topic is False, "ADR: include_topic=false (project_chat)"


def test_neutral_modes_never_contain_instruction_line():
    """NEUTRAL (alle Detail-Level): Keine Anweisungszeile im Fragment."""
    ctx = ChatRequestContext(
        project_name="P",
        chat_title="C",
        topic_name="T",
    )
    for detail in (ChatContextDetailLevel.MINIMAL, ChatContextDetailLevel.STANDARD, ChatContextDetailLevel.FULL):
        frag = ctx.to_system_prompt_fragment(ChatContextMode.NEUTRAL, detail)
        assert "Berücksichtige diesen Kontext" not in frag, f"NEUTRAL+{detail} darf keine Anweisung enthalten"

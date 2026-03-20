"""
QA for source ordering – explainability reflects actual execution sequence.

Sources must be appended in resolver processing order only. No sorting applied later.
Formatter and serializer preserve list order.
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_policies import ChatContextPolicy
from app.context.debug.context_debug import format_context_source_summary
from app.context.explainability.context_explanation_serializer import explanation_to_dict
from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.services.chat_service import ChatService, get_chat_service, set_chat_service
from app.services.context_inspection_service import get_context_inspection_service
from app.services.context_explain_service import ContextExplainRequest
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import ProjectService, get_project_service, set_project_service
from app.services.topic_service import TopicService, get_topic_service, set_topic_service

pytestmark = pytest.mark.context_observability

# Expected resolver processing order: project (1), chat (2), topic (3)
EXPECTED_SOURCE_ORDER = ("project", "chat", "topic")


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


def _setup_chat_with_all_sources(services) -> int:
    """Create chat with project, chat, topic – all enabled for context."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_mode", "semantic")
    backend.setValue("chat_context_detail_level", "standard")
    backend.setValue("chat_context_profile_enabled", False)
    backend.setValue("chat_context_include_project", True)
    backend.setValue("chat_context_include_chat", True)
    backend.setValue("chat_context_include_topic", True)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("Proj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "Topic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "Chat", topic_id=topic_id
    )
    return chat_id


def test_sources_order_matches_resolver_processing_sequence(services):
    """Known fixture with multiple sources: order matches expected [project, chat, topic]."""
    chat_id = _setup_chat_with_all_sources(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None
    assert len(expl.sources) >= 3, "Fixture must have project, chat, topic sources"

    # Serializer: list order preserved
    d = explanation_to_dict(expl)
    sources = d.get("sources", [])
    actual_order = tuple(s["source_type"] for s in sources)
    assert actual_order[:3] == EXPECTED_SOURCE_ORDER, (
        f"Serializer order {actual_order} must match resolver order {EXPECTED_SOURCE_ORDER}"
    )

    # selection_order must be present and match position
    for i, s in enumerate(sources[:3]):
        assert "selection_order" in s, f"source {s.get('source_type')} must have selection_order"
        assert s["selection_order"] == i + 1, (
            f"selection_order {s['selection_order']} must be {i + 1} for {s['source_type']}"
        )


def test_formatter_uses_list_order(services):
    """Formatted sources block: order matches resolver processing order."""
    chat_id = _setup_chat_with_all_sources(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None
    assert len(expl.sources) >= 3

    lines = format_context_source_summary(expl)
    # Each line: "[CTX_SOURCES] project included=... order=1 ..." – source_type is first token after prefix
    source_lines = [ln for ln in lines if ln.startswith("[CTX_SOURCES] ") and "(none)" not in ln]
    source_types_in_line_order = []
    for ln in source_lines:
        parts = ln.replace("[CTX_SOURCES] ", "").split()
        if parts:
            source_types_in_line_order.append(parts[0])

    assert source_types_in_line_order[:3] == list(EXPECTED_SOURCE_ORDER), (
        f"Formatter order {source_types_in_line_order} must match {EXPECTED_SOURCE_ORDER}"
    )


def test_inspection_result_sources_order(services):
    """Inspection result: sources in JSON match resolver order."""
    chat_id = _setup_chat_with_all_sources(services)
    request = ContextExplainRequest(chat_id=chat_id)
    result = get_context_inspection_service().inspect(request)

    d = explanation_to_dict(result.explanation)
    sources = d.get("sources", [])
    actual_order = tuple(s["source_type"] for s in sources)
    assert actual_order[:3] == EXPECTED_SOURCE_ORDER, (
        f"Inspection sources order {actual_order} must match {EXPECTED_SOURCE_ORDER}"
    )

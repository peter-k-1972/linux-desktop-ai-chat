"""
QA coverage for ContextInspectionService.

Uses real resolver path. No mocking of inspection result.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from PySide6.QtWidgets import QApplication

from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.services.chat_service import ChatService, get_chat_service, set_chat_service
from app.services.context_explain_service import ContextExplainRequest
from app.services.context_inspection_service import (
    ContextInspectionResult,
    get_context_inspection_service,
)
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import ProjectService, get_project_service, set_project_service
from app.services.topic_service import TopicService, get_topic_service, set_topic_service

pytestmark = pytest.mark.context_observability


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


def _setup_chat(services) -> int:
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

    proj_id = get_project_service().create_project("InspectProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "InspectTopic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "InspectChat", topic_id=topic_id
    )
    return chat_id


def test_inspect_returns_complete_structure_no_none_in_required(services):
    """inspect() returns complete structure; explanation and trace never None."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    svc = get_context_inspection_service()
    result = svc.inspect(request)

    assert isinstance(result, ContextInspectionResult)
    # Required fields: never None
    assert result.explanation is not None, "explanation must always be present"
    assert result.trace is not None, "trace must always be present"
    # Optional payload_preview: present when requested
    assert result.payload_preview is not None, "payload_preview present with default include_payload_preview=True"
    assert hasattr(result.payload_preview, "sections")
    assert hasattr(result.payload_preview, "total_tokens")
    assert hasattr(result.payload_preview, "empty")
    # Optional formatted_blocks: present when requested
    assert result.formatted_blocks is not None, "formatted_blocks present with default include_formatted=True"
    assert "summary" in result.formatted_blocks
    assert "budget" in result.formatted_blocks
    assert "sources" in result.formatted_blocks


def test_inspect_returns_explanation_trace_payload_preview(services):
    """inspect() returns explanation, trace, payload_preview."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    svc = get_context_inspection_service()
    result = svc.inspect(request)

    assert isinstance(result, ContextInspectionResult)
    assert result.explanation is not None
    assert hasattr(result.explanation, "sources")
    assert hasattr(result.explanation, "decisions")
    assert result.trace is not None
    assert hasattr(result.trace, "source")
    assert hasattr(result.trace, "mode")
    assert hasattr(result.trace, "explanation")
    assert result.payload_preview is not None
    assert hasattr(result.payload_preview, "sections")
    assert hasattr(result.payload_preview, "total_tokens")
    assert hasattr(result.payload_preview, "empty")


def test_inspect_as_dict_deterministic(services):
    """inspect_as_dict() is deterministic (same input -> same output)."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    svc = get_context_inspection_service()

    d1 = svc.inspect_as_dict(request)
    d2 = svc.inspect_as_dict(request)
    assert d1 == d2, (
        "inspect_as_dict non-deterministic: two calls on same request produced different dicts. "
        "Check inspection_result_to_dict, resolver ordering, or timestamp injection."
    )

    json1 = json.dumps(d1, sort_keys=True)
    json2 = json.dumps(d2, sort_keys=True)
    assert json1 == json2, (
        "inspect_as_dict JSON output non-deterministic: same dict produced different JSON. "
        "Check key ordering or serialization of nested structures."
    )


def test_formatted_blocks_present_and_stable(services):
    """Formatted blocks (summary, budget, sources) are present and stable."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    svc = get_context_inspection_service()
    result = svc.inspect(request)

    assert isinstance(result.formatted_summary, str)
    assert isinstance(result.formatted_budget, str)
    assert isinstance(result.formatted_sources, str)

    assert "[CTX_RESOLUTION]" in result.formatted_summary
    assert "[CTX_BUDGET]" in result.formatted_budget
    assert "[CTX_SOURCES]" in result.formatted_sources

    result2 = svc.inspect(request)
    assert result.formatted_summary == result2.formatted_summary
    assert result.formatted_budget == result2.formatted_budget
    assert result.formatted_sources == result2.formatted_sources


def test_warnings_block_absent_when_no_warnings(services):
    """formatted_warnings is None when explanation has no warnings; str when present."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    svc = get_context_inspection_service()
    result = svc.inspect(request)

    if not result.explanation.warnings:
        assert result.formatted_warnings is None
    else:
        assert result.formatted_warnings is not None
        assert isinstance(result.formatted_warnings, str)
        assert "[CTX_WARN]" in result.formatted_warnings


def test_payload_preview_reflects_final_payload_only(services):
    """Payload preview reflects final payload only (no dropped content reconstruction)."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    svc = get_context_inspection_service()
    result = svc.inspect(request)

    preview = result.payload_preview
    assert hasattr(preview, "sections")
    assert hasattr(preview, "empty")

    for section in preview.sections:
        assert hasattr(section, "section_name")
        assert hasattr(section, "included")
        assert hasattr(section, "line_count")
        assert hasattr(section, "token_count")
        if section.preview_text:
            assert isinstance(section.preview_text, str)


def test_inspect_optional_payload_and_formatted(services):
    """include_payload_preview=False and include_formatted=False skip expensive work."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    svc = get_context_inspection_service()
    result = svc.inspect(
        request,
        include_payload_preview=False,
        include_formatted=False,
    )

    assert result.explanation is not None
    assert result.trace is not None
    assert result.payload_preview is None
    assert result.formatted_blocks is None
    assert result.formatted_summary is None
    assert result.formatted_budget is None
    assert result.formatted_sources is None

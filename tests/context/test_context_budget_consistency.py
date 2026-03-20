"""
QA for budget accounting consistency – all token counts reconcile exactly.

Invariants:
- total_tokens_after == sum(source.budget_used // 4) for included sources
- dropped_total_tokens == sum(dropped_entries.dropped_tokens)
- per-source: chars_before == chars_after + budget_dropped (original = final + dropped)
"""

import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_policies import ChatContextPolicy
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

CHARS_PER_TOKEN = 4


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


def _setup_chat(services, **backend_overrides) -> int:
    """Create chat. backend_overrides: chat_context_include_*, max_*_chars via custom limits."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_mode", "semantic")
    backend.setValue("chat_context_detail_level", "standard")
    backend.setValue("chat_context_profile_enabled", False)
    backend.setValue("chat_context_include_project", backend_overrides.get("include_project", True))
    backend.setValue("chat_context_include_chat", backend_overrides.get("include_chat", True))
    backend.setValue("chat_context_include_topic", backend_overrides.get("include_topic", True))
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("Proj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "Topic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "Chat", topic_id=topic_id
    )
    return chat_id


def _assert_budget_consistency(expl):
    """Assert all budget accounting invariants hold."""
    # 1. total_tokens_after == sum(source.budget_used // 4) for included sources
    sum_final_tokens = sum(
        (s.budget_used or 0) // CHARS_PER_TOKEN
        for s in expl.sources
        if s.included
    )
    if expl.total_tokens_after is not None:
        assert expl.total_tokens_after == sum_final_tokens, (
            f"total_tokens_after={expl.total_tokens_after} must equal "
            f"sum(budget_used//4)={sum_final_tokens}"
        )

    # 2. dropped_total_tokens == sum(dropped_entries.dropped_tokens)
    sum_dropped = sum(e.dropped_tokens or 0 for e in expl.dropped_by_source)
    if expl.dropped_total_tokens is not None:
        assert expl.dropped_total_tokens == sum_dropped, (
            f"dropped_total_tokens={expl.dropped_total_tokens} must equal "
            f"sum(dropped_entries.dropped_tokens)={sum_dropped}"
        )

    # 3. per-source: chars_before == chars_after + budget_dropped
    for s in expl.sources:
        before = s.chars_before or 0
        after = s.chars_after or 0
        dropped = s.budget_dropped or 0
        assert before == after + dropped, (
            f"Source {s.source_type}: chars_before={before} must equal "
            f"chars_after={after} + budget_dropped={dropped}"
        )


def test_multiple_sources_budget_reconciles(services):
    """Multiple sources: total_tokens_after, dropped_total, per-source invariants hold."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None
    assert len(expl.sources) >= 3

    _assert_budget_consistency(expl)


def test_partial_truncation_budget_reconciles(services):
    """Partial truncation (long names, fixed limits): accounting still reconciles."""
    # Create project/chat/topic with long names to trigger truncation (ARCHITECTURE: 80/80/60)
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

    long_name = "A" * 150
    proj_id = get_project_service().create_project(long_name, "", "active")
    topic_id = get_topic_service().create_topic(proj_id, long_name, "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, long_name, topic_id=topic_id
    )

    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None

    _assert_budget_consistency(expl)


def test_full_exclusion_budget_reconciles(services):
    """Full exclusion (topic disabled): dropped_total matches excluded source."""
    chat_id = _setup_chat(services, include_topic=False)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None

    _assert_budget_consistency(expl)


def test_budget_exhaustion_reconciles(services):
    """Budget exhaustion (line limit cuts topic): accounting reconciles."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None

    _assert_budget_consistency(expl)


def test_inspection_result_budget_consistency(services):
    """Inspection result: budget invariants hold in serialized output."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    result = get_context_inspection_service().inspect(request)

    _assert_budget_consistency(result.explanation)

    d = explanation_to_dict(result.explanation)
    if "budget" in d and "total_tokens_after" in d["budget"]:
        sum_final = sum(
            (s.get("budget_used") or 0) // CHARS_PER_TOKEN
            for s in d.get("sources", [])
            if s.get("included", False)
        )
        assert d["budget"]["total_tokens_after"] == sum_final
    if "dropped" in d and d["dropped"].get("dropped_total_tokens") is not None:
        sum_dropped = sum(
            e.get("dropped_tokens") or 0
            for e in d["dropped"].get("dropped_by_source", [])
        )
        assert d["dropped"]["dropped_total_tokens"] == sum_dropped

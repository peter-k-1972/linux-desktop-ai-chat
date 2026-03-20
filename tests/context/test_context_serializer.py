"""
QA for serializer determinism – JSON output stable across runs and environments.

No __dict__ dumping. Explicit field ordering. Byte-identical output for same input.
"""

import json
import os
import tempfile

import pytest

from PySide6.QtWidgets import QApplication

from app.chat.context_policies import ChatContextPolicy
from app.context.explainability.context_explanation_serializer import (
    explanation_to_dict,
    trace_to_dict,
)
from app.context.explainability.context_inspection_serializer import (
    inspection_result_to_dict,
)
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

# Stable JSON dump params – no sort_keys, explicit format for byte-identical output
JSON_DUMP_KWARGS = {"sort_keys": False, "ensure_ascii": False, "indent": 2}


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

    proj_id = get_project_service().create_project("Proj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "Topic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "Chat", topic_id=topic_id
    )
    return chat_id


def test_explanation_to_dict_byte_identical(services):
    """Serialize same explanation twice; JSON output is byte-identical."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None

    d1 = explanation_to_dict(expl)
    d2 = explanation_to_dict(expl)

    json1 = json.dumps(d1, **JSON_DUMP_KWARGS)
    json2 = json.dumps(d2, **JSON_DUMP_KWARGS)

    assert json1 == json2, "Same input must produce byte-identical JSON"
    assert json1.encode("utf-8") == json2.encode("utf-8"), "Byte-level identity"


def test_trace_to_dict_byte_identical(services):
    """Serialize same trace twice; JSON output is byte-identical."""
    chat_id = _setup_chat(services)
    trace = get_chat_service().get_context_explanation(
        chat_id, None, ChatContextPolicy.ARCHITECTURE, return_trace=True
    )

    d1 = trace_to_dict(trace)
    d2 = trace_to_dict(trace)

    json1 = json.dumps(d1, **JSON_DUMP_KWARGS)
    json2 = json.dumps(d2, **JSON_DUMP_KWARGS)

    assert json1 == json2, "Same input must produce byte-identical JSON"


def test_inspection_result_to_dict_byte_identical(services):
    """Serialize same inspection result twice; JSON output is byte-identical."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    result = get_context_inspection_service().inspect(request)

    d1 = inspection_result_to_dict(result)
    d2 = inspection_result_to_dict(result)

    json1 = json.dumps(d1, **JSON_DUMP_KWARGS)
    json2 = json.dumps(d2, **JSON_DUMP_KWARGS)

    assert json1 == json2, "Same input must produce byte-identical JSON"


def test_explanation_mode_off_byte_identical(services):
    """Empty-result explanation (mode=off) produces byte-identical JSON."""
    backend = InMemoryBackend()
    backend.setValue("chat_context_mode", "off")
    backend.setValue("chat_context_detail_level", "standard")
    backend.setValue("chat_context_profile_enabled", False)
    settings = AppSettings(backend=backend)
    settings.load()
    get_chat_service()._infra._settings = settings

    proj_id = get_project_service().create_project("P", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "T", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "C", topic_id=topic_id
    )

    trace = get_chat_service().get_context_explanation(
        chat_id, None, None, return_trace=True
    )
    expl = trace.explanation
    assert expl is not None

    d1 = explanation_to_dict(expl)
    d2 = explanation_to_dict(expl)
    json1 = json.dumps(d1, **JSON_DUMP_KWARGS)
    json2 = json.dumps(d2, **JSON_DUMP_KWARGS)

    assert json1 == json2, "Mode=off explanation must produce byte-identical JSON"

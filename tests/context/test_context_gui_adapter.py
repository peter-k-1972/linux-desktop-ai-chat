"""
QA coverage for ContextInspectionPanel GUI integration.

Headless: adapter output equals displayed model.
Ensures UI is a pure viewer – no filtering, no transformation.
"""

import os
import tempfile
from pathlib import Path

import pytest

from PySide6.QtWidgets import QApplication

from app.context.inspection import ContextInspectionViewAdapter, ContextInspectionViewModel
from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.gui.domains.debug import ContextInspectionPanel
from app.services.chat_service import ChatService, get_chat_service, set_chat_service
from app.services.context_explain_service import ContextExplainRequest
from app.services.context_inspection_service import get_context_inspection_service
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import ProjectService, get_project_service, set_project_service
from app.services.topic_service import TopicService, get_topic_service, set_topic_service

pytestmark = pytest.mark.context_observability


def _ensure_qapp():
    app = QApplication.instance()
    if not app:
        app = QApplication([])
    return app


def _lines_to_text(lines: list) -> str:
    if not lines:
        return "—"
    return "\n".join(lines)


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

    proj_id = get_project_service().create_project("GuiProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "GuiTopic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "GuiChat", topic_id=topic_id
    )
    return chat_id


def test_panel_displayed_equals_adapter_output(services):
    """Panel displayed content equals adapter output; UI is pure viewer."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    result = get_context_inspection_service().inspect(
        request,
        include_payload_preview=True,
        include_formatted=True,
    )
    vm = ContextInspectionViewAdapter.to_view_model(result)

    panel = ContextInspectionPanel()
    panel.set_request(request)
    displayed = panel.get_displayed_content()

    assert displayed["summary"] == _lines_to_text(vm.summary_lines)
    assert displayed["budget"] == _lines_to_text(vm.budget_lines)
    assert displayed["sources"] == _lines_to_text(vm.source_lines)
    assert displayed["warnings"] == _lines_to_text(vm.warning_lines)
    assert displayed["payload"] == "—"  # payload toggle off by default


def test_panel_with_payload_toggle_displayed_equals_adapter(services):
    """With payload toggle on, displayed payload equals adapter payload_preview_lines."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    result = get_context_inspection_service().inspect(
        request,
        include_payload_preview=True,
        include_formatted=True,
    )
    vm = ContextInspectionViewAdapter.to_view_model(result)

    panel = ContextInspectionPanel()
    panel.set_request(request)
    panel._payload_toggle.setChecked(True)
    displayed = panel.get_displayed_content()

    assert displayed["payload"] == _lines_to_text(vm.payload_preview_lines)


def test_panel_displays_all_sections(services):
    """Panel displays all sections: summary, budget, sources, warnings, payload."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    panel = ContextInspectionPanel()
    panel.set_request(request)

    displayed = panel.get_displayed_content()
    assert "summary" in displayed
    assert "budget" in displayed
    assert "sources" in displayed
    assert "warnings" in displayed
    assert "payload" in displayed

"""
QA coverage for ContextInspectionViewAdapter.

Uses real inspection result. No GUI instantiation. Snapshot test for view model lines.
"""

import os
import tempfile
from pathlib import Path

import pytest

from app.context.debug.context_debug import (
    format_context_budget_summary,
    format_context_resolution_summary,
    format_context_source_summary,
    format_context_warnings,
    format_payload_preview,
)
from app.context.inspection import ContextInspectionViewAdapter, ContextInspectionViewModel
from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.services.chat_service import ChatService, get_chat_service, set_chat_service
from app.services.context_explain_service import ContextExplainRequest
from app.services.context_inspection_service import get_context_inspection_service
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import ProjectService, get_project_service, set_project_service
from app.services.topic_service import TopicService, get_topic_service, set_topic_service

from tests.context.conftest import assert_snapshot

pytestmark = pytest.mark.context_observability

EXPECTED_DIR = Path(__file__).resolve().parent / "expected"


def _normalize_line(line: str) -> str:
    """Same normalization as adapter: \\n line endings, trim trailing whitespace."""
    return line.replace("\r\n", "\n").replace("\r", "\n").rstrip()


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
def services(temp_db):
    """Services without GUI. No QApplication."""
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

    proj_id = get_project_service().create_project("AdapterProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "AdapterTopic", "")
    chat_id = get_chat_service().create_chat_in_project(
        proj_id, "AdapterChat", topic_id=topic_id
    )
    return chat_id


def test_adapter_returns_all_sections(services):
    """Adapter returns all sections: summary, budget, sources, warnings, payload."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    result = get_context_inspection_service().inspect(request)
    vm = ContextInspectionViewAdapter.to_view_model(result)

    assert isinstance(vm, ContextInspectionViewModel)
    assert hasattr(vm, "summary_lines")
    assert hasattr(vm, "budget_lines")
    assert hasattr(vm, "source_lines")
    assert hasattr(vm, "warning_lines")
    assert hasattr(vm, "payload_preview_lines")
    assert hasattr(vm, "has_warnings")
    assert hasattr(vm, "has_payload")

    assert isinstance(vm.summary_lines, list)
    assert isinstance(vm.budget_lines, list)
    assert isinstance(vm.source_lines, list)
    assert isinstance(vm.warning_lines, list)
    assert isinstance(vm.payload_preview_lines, list)


def test_ordering_preserved(services):
    """Ordering of lines is preserved from formatter."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    result = get_context_inspection_service().inspect(request)
    vm = ContextInspectionViewAdapter.to_view_model(result)

    raw_summary = format_context_resolution_summary(result.trace)
    raw_budget = format_context_budget_summary(result.explanation)
    raw_sources = format_context_source_summary(result.explanation)

    normalized_summary = [_normalize_line(s) for s in raw_summary]
    normalized_budget = [_normalize_line(b) for b in raw_budget]
    normalized_sources = [_normalize_line(s) for s in raw_sources]

    assert vm.summary_lines == normalized_summary
    assert vm.budget_lines == normalized_budget
    assert vm.source_lines == normalized_sources


def test_warnings_flag_correct(services):
    """has_warnings matches result.formatted_warnings is not None."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    result = get_context_inspection_service().inspect(request)
    vm = ContextInspectionViewAdapter.to_view_model(result)

    expected = result.formatted_warnings is not None
    assert vm.has_warnings == expected


def test_payload_flag_correct(services):
    """has_payload matches not result.payload_preview.empty."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    result = get_context_inspection_service().inspect(request)
    vm = ContextInspectionViewAdapter.to_view_model(result)

    expected = not result.payload_preview.empty
    assert vm.has_payload == expected


def test_no_data_loss_between_formatter_and_view_model(services):
    """No line count loss; content preserved (normalized only)."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    result = get_context_inspection_service().inspect(request)
    vm = ContextInspectionViewAdapter.to_view_model(result)

    raw_summary = format_context_resolution_summary(result.trace)
    raw_budget = format_context_budget_summary(result.explanation)
    raw_sources = format_context_source_summary(result.explanation)
    raw_warnings = format_context_warnings(result.explanation)
    payload_str = format_payload_preview(result.payload_preview)
    raw_payload = payload_str.splitlines() if payload_str else []

    assert len(vm.summary_lines) == len(raw_summary)
    assert len(vm.budget_lines) == len(raw_budget)
    assert len(vm.source_lines) == len(raw_sources)
    assert len(vm.warning_lines) == len(raw_warnings)
    assert len(vm.payload_preview_lines) == len(raw_payload)


def _view_model_to_snapshot_text(vm: ContextInspectionViewModel) -> str:
    """Serialize view model lines for snapshot comparison."""
    parts = []
    parts.append("---summary---")
    parts.extend(vm.summary_lines)
    parts.append("---budget---")
    parts.extend(vm.budget_lines)
    parts.append("---sources---")
    parts.extend(vm.source_lines)
    parts.append("---warnings---")
    parts.extend(vm.warning_lines)
    parts.append("---payload---")
    parts.extend(vm.payload_preview_lines)
    parts.append("---flags---")
    parts.append(f"has_warnings={vm.has_warnings}")
    parts.append(f"has_payload={vm.has_payload}")
    return "\n".join(parts)


def _snapshot_path() -> Path:
    return EXPECTED_DIR / "view_adapter_lines.txt"


def test_snapshot_view_model_lines(services):
    """Snapshot: view model lines match golden file."""
    chat_id = _setup_chat(services)
    request = ContextExplainRequest(chat_id=chat_id)
    result = get_context_inspection_service().inspect(request)
    vm = ContextInspectionViewAdapter.to_view_model(result)

    actual = _view_model_to_snapshot_text(vm)
    golden = _snapshot_path()
    assert_snapshot(actual, golden, label="view_model")

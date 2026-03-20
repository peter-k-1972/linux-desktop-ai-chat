"""
QA coverage for context_inspect CLI.

Uses real resolver path. Snapshot tests for text output.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

from PySide6.QtWidgets import QApplication

from app.core.config.settings import AppSettings
from app.core.config.settings_backend import InMemoryBackend
from app.core.db.database_manager import DatabaseManager
from app.services.chat_service import ChatService, get_chat_service, set_chat_service
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import ProjectService, get_project_service, set_project_service
from app.services.topic_service import TopicService, get_topic_service, set_topic_service

from tests.context.conftest import assert_snapshot

pytestmark = pytest.mark.context_observability

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CLI_SCRIPT = PROJECT_ROOT / "scripts" / "dev" / "context_inspect.py"
FIXTURES_DIR = PROJECT_ROOT / "tests" / "fixtures" / "context_requests"
EXPECTED_DIR = Path(__file__).resolve().parent / "expected"


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
def populated_db(temp_db, qapp):
    """Create DB with project, topic, chat for inspection."""
    db = DatabaseManager(db_path=temp_db)
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = None
    set_infrastructure(infra)
    set_project_service(ProjectService())
    set_chat_service(ChatService())
    set_topic_service(TopicService())

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

    proj_id = get_project_service().create_project("CLIProj", "", "active")
    topic_id = get_topic_service().create_topic(proj_id, "CLITopic", "")
    get_chat_service().create_chat_in_project(proj_id, "CLIChat", topic_id=topic_id)

    try:
        yield temp_db
    finally:
        set_project_service(None)
        set_chat_service(None)
        set_topic_service(None)
        set_infrastructure(None)


def _run_cli(db_path: str, args: list[str]) -> tuple[int, str, str]:
    """Run context_inspect CLI. Returns (exit_code, stdout, stderr)."""
    cmd = [
        sys.executable,
        str(CLI_SCRIPT),
        "--db",
        db_path,
        *args,
    ]
    env = {**os.environ, "CONTEXT_DEBUG_ENABLED": "1"}
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(PROJECT_ROOT),
        env=env,
    )
    return result.returncode, result.stdout, result.stderr


def test_text_output_includes_summary(populated_db):
    """Text output includes summary block."""
    exit_code, stdout, stderr = _run_cli(
        populated_db,
        ["--chat-id", "1"],
    )
    assert exit_code == 0, stderr
    assert "[CTX_RESOLUTION]" in stdout
    assert "source=" in stdout


def test_show_budget_includes_budget_block(populated_db):
    """--show-budget includes budget block."""
    exit_code, stdout, stderr = _run_cli(
        populated_db,
        ["--chat-id", "1", "--show-budget"],
    )
    assert exit_code == 0, stderr
    assert "[CTX_BUDGET]" in stdout


def test_show_sources_includes_sources_block(populated_db):
    """--show-sources includes sources block."""
    exit_code, stdout, stderr = _run_cli(
        populated_db,
        ["--chat-id", "1", "--show-sources"],
    )
    assert exit_code == 0, stderr
    assert "[CTX_SOURCES]" in stdout


def test_format_json_returns_serializer_structure(populated_db):
    """--format json returns serializer-based structure."""
    exit_code, stdout, stderr = _run_cli(
        populated_db,
        ["--chat-id", "1", "--format", "json"],
    )
    assert exit_code == 0, stderr
    data = json.loads(stdout)
    assert "explainability_schema_version" in data
    assert "trace" in data
    assert "explanation" in data
    assert "payload_preview" in data
    assert "formatted_blocks" in data
    fb = data["formatted_blocks"]
    assert "summary" in fb
    assert "budget" in fb
    assert "sources" in fb


def test_fixture_loads_request_correctly(populated_db):
    """--fixture loads request fixture correctly."""
    fixture_path = FIXTURES_DIR / "minimal_default_request.json"
    assert fixture_path.exists()
    exit_code, stdout, stderr = _run_cli(
        populated_db,
        ["--fixture", str(fixture_path.relative_to(PROJECT_ROOT))],
    )
    assert exit_code == 0, stderr
    assert "[CTX_RESOLUTION]" in stdout


def test_invalid_fixture_fails_deterministically(populated_db):
    """Invalid fixture fails with deterministic error."""
    fd, invalid_path = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    try:
        with open(invalid_path, "w") as f:
            f.write('{"chat_id": 1, "request_context_hint": null}')
        exit_code, stdout, stderr = _run_cli(
            populated_db,
            ["--fixture", invalid_path],
        )
        assert exit_code == 1
        assert "unknown keys" in stderr or "request_context_hint" in stderr
    finally:
        try:
            os.unlink(invalid_path)
        except OSError:
            pass


# --- Snapshot tests (at least 3 fixtures) ---


def _snapshot_path(name: str) -> Path:
    return EXPECTED_DIR / f"context_inspect_{name}.txt"


def test_snapshot_minimal_default(populated_db):
    """Snapshot: minimal_default_request fixture text output."""
    fixture_path = FIXTURES_DIR / "minimal_default_request.json"
    exit_code, stdout, stderr = _run_cli(
        populated_db,
        ["--fixture", str(fixture_path.relative_to(PROJECT_ROOT)), "--show-budget", "--show-sources"],
    )
    assert exit_code == 0, stderr

    golden = _snapshot_path("minimal_default")
    assert_snapshot(stdout, golden, label="stdout")


def test_snapshot_explicit_policy_architecture(populated_db):
    """Snapshot: explicit_policy_architecture fixture text output."""
    fixture_path = FIXTURES_DIR / "explicit_policy_architecture.json"
    exit_code, stdout, stderr = _run_cli(
        populated_db,
        ["--fixture", str(fixture_path.relative_to(PROJECT_ROOT)), "--show-budget", "--show-sources"],
    )
    assert exit_code == 0, stderr

    golden = _snapshot_path("explicit_policy_architecture")
    assert_snapshot(stdout, golden, label="stdout")


def test_snapshot_invalid_policy_fallback(populated_db):
    """Snapshot: invalid_policy_fallback fixture text output."""
    fixture_path = FIXTURES_DIR / "invalid_policy_fallback.json"
    exit_code, stdout, stderr = _run_cli(
        populated_db,
        ["--fixture", str(fixture_path.relative_to(PROJECT_ROOT)), "--show-budget", "--show-sources"],
    )
    assert exit_code == 0, stderr

    golden = _snapshot_path("invalid_policy_fallback")
    assert_snapshot(stdout, golden, label="stdout")

"""
Fixtures für UI-Tests (pytest-qt).

Nutzt qt_event_loop für async Tests mit PySide6 + qasync.
"""

import os
import tempfile

import pytest

from app.agents.agent_repository import AgentRepository
from app.agents.agent_service import AgentService
from app.agents.agent_profile import AgentProfile, AgentStatus
from app.core.db import DatabaseManager
from app.core.config.settings import AppSettings


@pytest.fixture
def temp_db_path():
    """Temporärer DB-Pfad für UI-Tests."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def temp_db():
    """Temporäre Datenbank für UI-Tests."""
    fd, path = tempfile.mkstemp(suffix=".db")
    import os
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def app_settings():
    """AppSettings für Tests."""
    return AppSettings()


@pytest.fixture
def mock_ollama_client():
    """Gemockter Ollama-Client."""
    from unittest.mock import MagicMock, AsyncMock
    client = MagicMock()
    client.generate = AsyncMock(return_value="Mock-Antwort")
    client.list_models = AsyncMock(return_value=[])
    client.get_debug_info = AsyncMock(return_value={"online": True, "version": "test"})
    return client


@pytest.fixture
def mock_orchestrator(mock_ollama_client):
    """Gemockter ModelOrchestrator."""
    from unittest.mock import MagicMock, AsyncMock
    orch = MagicMock()
    orch.select_model_for_prompt = MagicMock(return_value=("default", "llama3:latest"))
    orch.complete = AsyncMock(return_value="Mock-Stream-Antwort")
    orch.chat = AsyncMock(return_value=iter([{"message": {"content": "Mock-Antwort"}}]))
    orch.close = AsyncMock(return_value=None)
    return orch


@pytest.fixture
def event_loop(qt_event_loop):
    """
    Überschreibt die Standard-Event-Loop für UI-Tests.
    Nutzt qasync QEventLoop, damit async PySide6-Tests nicht übersprungen werden.
    """
    import asyncio
    asyncio.set_event_loop(qt_event_loop)
    return qt_event_loop

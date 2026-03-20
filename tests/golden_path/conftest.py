"""
Fixtures für Golden-Path-Tests.

Echte DB, echte Services – minimale Mocks nur wo extern (Ollama).
"""

import os
import tempfile

import pytest

from app.agents.agent_repository import AgentRepository
from app.agents.agent_service import AgentService
from app.agents.agent_profile import AgentProfile, AgentStatus
from app.prompts.prompt_models import Prompt
from app.prompts.prompt_service import PromptService
from app.prompts.storage_backend import DatabasePromptStorage


@pytest.fixture
def temp_db_path():
    """Temporäre SQLite-DB für Golden-Path-Tests."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def agent_service(temp_db_path):
    """AgentService mit echter temporärer DB."""
    repo = AgentRepository(db_path=temp_db_path)
    return AgentService(repository=repo)


@pytest.fixture
def prompt_service(temp_db_path):
    """PromptService mit echter temporärer DB (prompts-Tabelle via DatabasePromptStorage)."""
    backend = DatabasePromptStorage(db_path=temp_db_path)
    return PromptService(backend=backend)


@pytest.fixture
def fake_ollama_chat():
    """Fake für Ollama chat() – liefert vorbereitete Antwort."""
    from unittest.mock import AsyncMock, MagicMock

    async def _chat(*, model, messages, **kwargs):
        async def _gen():
            yield {"message": {"content": "Golden-Path-Antwort", "thinking": ""}, "done": True}
        return _gen()

    client = MagicMock()
    client.chat = AsyncMock(side_effect=_chat)
    client.get_models = AsyncMock(return_value=[])
    client.get_debug_info = AsyncMock(return_value={"online": True})
    return client

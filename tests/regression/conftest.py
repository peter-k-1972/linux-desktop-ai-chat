"""
Fixtures für Regression-Tests.

Gleiche Basis-Fixtures wie andere Tests – echte DB, minimale Mocks.
"""

import os
import tempfile

import pytest

from app.agents.agent_repository import AgentRepository
from app.agents.agent_service import AgentService
from app.agents.agent_profile import AgentProfile, AgentStatus


@pytest.fixture
def temp_db_path():
    """Temporäre SQLite-DB."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def agent_service(temp_db_path):
    """AgentService mit temporärer DB."""
    repo = AgentRepository(db_path=temp_db_path)
    return AgentService(repository=repo)

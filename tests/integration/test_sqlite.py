"""
Integration Tests: SQLite Persistence.

Testet echte SQLite-Datenbank für AgentRepository.
Keine Mocks – reale CRUD-Operationen.
"""

import os
import tempfile

import pytest

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_repository import AgentRepository


@pytest.mark.integration
class TestSQLiteIntegration:
    """Echte SQLite-Integration für AgentRepository."""

    @pytest.fixture
    def db_path(self):
        """Temporäre SQLite-DB für jeden Test."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        try:
            os.unlink(path)
        except OSError:
            pass

    @pytest.fixture
    def repo(self, db_path):
        """AgentRepository mit echter SQLite-DB."""
        return AgentRepository(db_path=db_path)

    def test_create_and_get_agent(self, repo):
        """Agent erstellen und per ID laden."""
        profile = AgentProfile(
            id=None,
            name="Integration-Test-Agent",
            display_name="Integration Test",
            slug="integration_test",
            department="research",
            status=AgentStatus.ACTIVE.value,
            system_prompt="Test-System-Prompt",
        )
        agent_id = repo.create(profile)
        assert agent_id is not None
        assert len(agent_id) > 0

        loaded = repo.get(agent_id)
        assert loaded is not None
        assert loaded.name == "Integration-Test-Agent"
        assert loaded.slug == "integration_test"
        assert loaded.system_prompt == "Test-System-Prompt"

    def test_create_and_get_by_slug(self, repo):
        """Agent per Slug laden."""
        profile = AgentProfile(
            name="Slug-Test",
            slug="slug_test_unique",
            department="general",
        )
        agent_id = repo.create(profile)
        loaded = repo.get_by_slug("slug_test_unique")
        assert loaded is not None
        assert loaded.id == agent_id

    def test_update_agent(self, repo):
        """Agent aktualisieren."""
        profile = AgentProfile(
            name="Update-Test",
            slug="update_test",
            department="general",
        )
        agent_id = repo.create(profile)
        profile.id = agent_id
        profile.display_name = "Aktualisierter Name"
        profile.short_description = "Neue Beschreibung"

        success = repo.update(profile)
        assert success is True

        loaded = repo.get(agent_id)
        assert loaded.display_name == "Aktualisierter Name"
        assert loaded.short_description == "Neue Beschreibung"

    def test_delete_agent(self, repo):
        """Agent löschen."""
        profile = AgentProfile(
            name="Delete-Test",
            slug="delete_test",
            department="general",
        )
        agent_id = repo.create(profile)
        assert repo.get(agent_id) is not None

        success = repo.delete(agent_id)
        assert success is True
        assert repo.get(agent_id) is None

    def test_list_all_with_filters(self, repo):
        """Liste mit Filtern (Department, Status)."""
        for i, (dept, status) in enumerate([
            ("research", AgentStatus.ACTIVE.value),
            ("development", AgentStatus.ACTIVE.value),
            ("research", AgentStatus.INACTIVE.value),
        ]):
            profile = AgentProfile(
                name=f"Filter-Test-{i}",
                slug=f"filter_test_{i}",
                department=dept,
                status=status,
            )
            repo.create(profile)

        research = repo.list_all(department="research")
        assert len(research) >= 2

        active = repo.list_all(status=AgentStatus.ACTIVE.value)
        assert len(active) >= 2

        research_active = repo.list_all(
            department="research",
            status=AgentStatus.ACTIVE.value,
        )
        assert len(research_active) >= 1

    def test_persistence_across_connections(self, db_path):
        """Daten bleiben nach neuem Repository erhalten."""
        repo1 = AgentRepository(db_path=db_path)
        profile = AgentProfile(
            name="Persistence-Test",
            slug="persistence_test",
            department="general",
        )
        agent_id = repo1.create(profile)

        repo2 = AgentRepository(db_path=db_path)
        loaded = repo2.get(agent_id)
        assert loaded is not None
        assert loaded.name == "Persistence-Test"

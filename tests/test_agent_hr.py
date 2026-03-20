"""
Tests für Agenten-HR: Repository, Service, Registry, Validierung.
"""

import os
import tempfile
import pytest

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_repository import AgentRepository
from app.agents.agent_service import AgentService
from app.agents.agent_registry import AgentRegistry, get_agent_registry
from app.agents.departments import Department
from app.core.models.roles import ModelRole


@pytest.fixture
def temp_db():
    """Temporäre SQLite-DB für Tests."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def repo(temp_db):
    return AgentRepository(db_path=temp_db)


@pytest.fixture
def service(temp_db):
    return AgentService(repository=AgentRepository(db_path=temp_db))


@pytest.fixture
def sample_profile():
    return AgentProfile(
        name="Test Agent",
        display_name="Test Agent",
        slug="test_agent",
        short_description="Ein Test-Agent",
        department=Department.PLANNING.value,
        role="Tester",
        status=AgentStatus.ACTIVE.value,
        assigned_model="qwen2.5:latest",
        assigned_model_role=ModelRole.DEFAULT.value,
        system_prompt="Du bist ein Test-Agent.",
        capabilities=["test", "demo"],
        tools=["rag"],
        knowledge_spaces=["default"],
        tags=["test"],
    )


def test_agent_create(service, sample_profile):
    """Agent erstellen."""
    agent_id, err = service.create(sample_profile)
    assert err is None
    assert agent_id is not None
    loaded = service.get(agent_id)
    assert loaded is not None
    assert loaded.name == sample_profile.name
    assert loaded.slug == sample_profile.slug


def test_agent_save_load(repo, sample_profile):
    """Agent speichern und laden."""
    agent_id = repo.create(sample_profile)
    loaded = repo.get(agent_id)
    assert loaded is not None
    assert loaded.name == sample_profile.name
    assert loaded.assigned_model == sample_profile.assigned_model
    assert loaded.capabilities == sample_profile.capabilities


def test_agent_update(service, sample_profile):
    """Agent bearbeiten."""
    agent_id, _ = service.create(sample_profile)
    loaded = service.get(agent_id)
    loaded.short_description = "Geändert"
    ok, err = service.update(loaded)
    assert err is None
    assert ok is True
    reloaded = service.get(agent_id)
    assert reloaded.short_description == "Geändert"


def test_agent_delete(service, sample_profile):
    """Agent löschen."""
    agent_id, _ = service.create(sample_profile)
    ok, err = service.delete(agent_id)
    assert err is None
    assert ok is True
    assert service.get(agent_id) is None


def test_agent_duplicate(service, sample_profile):
    """Agent duplizieren."""
    agent_id, _ = service.create(sample_profile)
    new_id, err = service.duplicate(agent_id)
    assert err is None
    assert new_id is not None
    assert new_id != agent_id
    dup = service.get(new_id)
    assert dup is not None
    assert "Kopie" in dup.name


def test_filter_by_department(service, sample_profile):
    """Filter nach Department."""
    service.create(sample_profile)
    p2 = AgentProfile(
        name="Code Agent",
        display_name="Code",
        slug="code_agent",
        department=Department.DEVELOPMENT.value,
        status=AgentStatus.ACTIVE.value,
    )
    service.create(p2)
    planning = service.list_all(department=Department.PLANNING.value)
    development = service.list_all(department=Department.DEVELOPMENT.value)
    assert len(planning) >= 1
    assert len(development) >= 1
    assert all(a.department == Department.PLANNING.value for a in planning)
    assert all(a.department == Department.DEVELOPMENT.value for a in development)


def test_activate_deactivate(service, sample_profile):
    """Aktivieren/Deaktivieren."""
    sample_profile.status = AgentStatus.INACTIVE.value
    agent_id, _ = service.create(sample_profile)
    ok, err = service.activate(agent_id)
    assert err is None
    loaded = service.get(agent_id)
    assert loaded.status == AgentStatus.ACTIVE.value
    ok, err = service.deactivate(agent_id)
    assert err is None
    loaded = service.get(agent_id)
    assert loaded.status == AgentStatus.INACTIVE.value


def test_registry_lookup(repo, sample_profile):
    """Registry Lookup nach id, slug, name."""
    agent_id = repo.create(sample_profile)
    registry = AgentRegistry(repository=repo)
    registry.refresh()
    by_id = registry.get(agent_id)
    by_slug = registry.get_by_slug(sample_profile.slug)
    by_name = registry.get_by_name(sample_profile.name)
    assert by_id is not None
    assert by_slug is not None
    assert by_name is not None
    assert by_id.id == by_slug.id == by_name.id


def test_model_role_assignment(service, sample_profile):
    """Modell-/Rollenzuweisung."""
    sample_profile.assigned_model = "gpt-oss:latest"
    sample_profile.assigned_model_role = ModelRole.THINK.value
    agent_id, _ = service.create(sample_profile)
    loaded = service.get(agent_id)
    assert loaded.assigned_model == "gpt-oss:latest"
    assert loaded.assigned_model_role == ModelRole.THINK.value
    role_enum = loaded.get_model_role_enum()
    assert role_enum == ModelRole.THINK


def test_validation_duplicate_name(service, sample_profile):
    """Doppelter Name wird abgelehnt."""
    service.create(sample_profile)
    p2 = AgentProfile(
        name="Test Agent",
        display_name="Anderer",
        slug="other_slug",
        status=AgentStatus.ACTIVE.value,
    )
    agent_id, err = service.create(p2)
    assert err is not None
    assert "existiert bereits" in err


def test_validation_empty_name(service):
    """Leerer Name wird abgelehnt."""
    p = AgentProfile(name="", display_name="", slug="x", status=AgentStatus.ACTIVE.value)
    agent_id, err = service.create(p)
    assert err is not None
    assert "Name" in err


def test_profile_to_dict_roundtrip(sample_profile):
    """Profil-Serialisierung Roundtrip."""
    d = sample_profile.to_dict()
    restored = AgentProfile.from_dict(d)
    assert restored.name == sample_profile.name
    assert restored.department == sample_profile.department
    assert restored.capabilities == sample_profile.capabilities

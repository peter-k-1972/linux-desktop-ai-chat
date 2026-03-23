"""
Regression: aktives Projekt nur über ProjectContextManager setzen; APC als Spiegel.
"""

import os
import tempfile

import pytest

from app.core.config.settings import AppSettings
from app.core.context.active_project import ActiveProjectContext, get_active_project_context, set_active_project_context
from app.core.context.project_context_manager import (
    ProjectContextManager,
    get_project_context_manager,
    set_project_context_manager,
)
from app.core.db.database_manager import DatabaseManager
from app.services.infrastructure import _ServiceInfrastructure, set_infrastructure
from app.services.project_service import get_project_service, set_project_service


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def isolated_project_context(temp_db):
    """Frische PCM-/APC-Instanzen + temporäre DB für ProjectService."""
    set_project_context_manager(ProjectContextManager())
    set_active_project_context(ActiveProjectContext())

    db = DatabaseManager(temp_db, ensure_default_project=False)
    infra = _ServiceInfrastructure()
    infra._db = db
    infra._client = None
    infra._settings = AppSettings()
    set_infrastructure(infra)
    set_project_service(None)

    yield get_project_context_manager(), get_project_service()

    set_project_service(None)
    set_infrastructure(None)
    set_project_context_manager(None)
    set_active_project_context(None)


def test_pcm_set_active_mirrors_to_active_project_context(isolated_project_context):
    pcm, svc = isolated_project_context
    pid = svc.create_project("Alpha", "", "active")
    apc = get_active_project_context()

    pcm.set_active_project(pid)

    assert pcm.get_active_project_id() == pid
    assert apc.active_project_id == pid
    loaded = pcm.get_active_project()
    assert loaded is not None
    assert loaded.get("name") == "Alpha"
    assert apc.active_project is loaded


def test_project_service_set_active_delegates_to_pcm(isolated_project_context):
    _, svc = isolated_project_context
    pcm = get_project_context_manager()
    pid = svc.create_project("Beta", "", "active")

    svc.set_active_project(project_id=pid)

    assert pcm.get_active_project_id() == pid
    assert get_active_project_context().active_project_id == pid


def test_project_service_set_active_from_project_dict_only(isolated_project_context):
    _, svc = isolated_project_context
    pcm = get_project_context_manager()
    pid = svc.create_project("Gamma", "", "active")
    row = svc.get_project(pid)
    assert row is not None

    svc.set_active_project(project=row)

    assert pcm.get_active_project_id() == pid


def test_project_service_clear_and_get_active_use_pcm(isolated_project_context):
    _, svc = isolated_project_context
    pcm = get_project_context_manager()
    pid = svc.create_project("Delta", "", "active")
    svc.set_active_project(project_id=pid)
    assert svc.get_active_project_id() == pid
    assert svc.get_active_project() and svc.get_active_project()["name"] == "Delta"

    svc.clear_active_project()

    assert pcm.get_active_project_id() is None
    assert svc.get_active_project_id() is None
    assert get_active_project_context().active_project_id is None


def test_project_service_set_both_none_clears(isolated_project_context):
    _, svc = isolated_project_context
    pcm = get_project_context_manager()
    pid = svc.create_project("Epsilon", "", "active")
    svc.set_active_project(project_id=pid)
    svc.set_active_project(project_id=None, project=None)
    assert pcm.get_active_project_id() is None

"""
Unit Tests: Prompt System.

Testet Prompt speichern, laden, editieren.
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.prompts.prompt_models import Prompt, PROMPT_TYPES, PROMPT_CATEGORIES
from app.prompts.prompt_service import PromptService, create_storage_backend
from app.prompts.storage_backend import (
    PromptStorageBackend,
    DatabasePromptStorage,
    DirectoryPromptStorage,
)


# --- Prompt Model ---

def test_prompt_empty():
    """Prompt.empty() erstellt leeren Prompt."""
    p = Prompt.empty()
    assert p.id is None
    assert p.title == ""
    assert p.category == "general"
    assert p.prompt_type == "user"
    assert p.scope == "global"
    assert p.project_id is None
    assert p.tags == []


def test_prompt_to_dict(test_prompt):
    """Prompt.to_dict() serialisiert korrekt."""
    d = test_prompt.to_dict()
    assert d["title"] == "Code Review"
    assert d["category"] == "code"
    assert d["scope"] == "global"
    assert d["project_id"] is None
    assert "content" in d
    assert "tags" in d


def test_prompt_from_dict(test_prompt):
    """Prompt.from_dict() deserialisiert korrekt."""
    d = test_prompt.to_dict()
    restored = Prompt.from_dict(d)
    assert restored.title == test_prompt.title
    assert restored.content == test_prompt.content


def test_prompt_types_defined():
    """PROMPT_TYPES enthält erwartete Typen."""
    assert "user" in PROMPT_TYPES
    assert "system" in PROMPT_TYPES
    assert "template" in PROMPT_TYPES


def test_prompt_categories_defined():
    """PROMPT_CATEGORIES enthält erwartete Kategorien."""
    assert "general" in PROMPT_CATEGORIES
    assert "code" in PROMPT_CATEGORIES


# --- Database Storage ---

def test_prompt_service_create(temp_db_path, test_prompt):
    """PromptService.create() speichert Prompt."""
    backend = DatabasePromptStorage(db_path=temp_db_path)
    service = PromptService(backend=backend)
    test_prompt.id = None
    created = service.create(test_prompt)
    assert created is not None
    assert created.id is not None
    assert created.title == test_prompt.title


def test_prompt_service_create_rejects_empty_title(temp_db_path):
    """Create lehnt leeren Titel ab."""
    service = PromptService(backend=DatabasePromptStorage(db_path=temp_db_path))
    p = Prompt.empty()
    p.title = ""
    result = service.create(p)
    assert result is None


def test_prompt_service_get(temp_db_path, test_prompt):
    """PromptService.get() lädt Prompt."""
    backend = DatabasePromptStorage(db_path=temp_db_path)
    service = PromptService(backend=backend)
    created = service.create(test_prompt)
    loaded = service.get(created.id)
    assert loaded is not None
    assert loaded.title == created.title
    assert loaded.content == test_prompt.content


def test_prompt_service_update(temp_db_path, test_prompt):
    """PromptService.update() aktualisiert Prompt."""
    backend = DatabasePromptStorage(db_path=temp_db_path)
    service = PromptService(backend=backend)
    created = service.create(test_prompt)
    created.content = "Neuer Inhalt"
    ok = service.update(created)
    assert ok is True
    loaded = service.get(created.id)
    assert loaded.content == "Neuer Inhalt"


def test_prompt_service_delete(temp_db_path, test_prompt):
    """PromptService.delete() löscht Prompt."""
    backend = DatabasePromptStorage(db_path=temp_db_path)
    service = PromptService(backend=backend)
    created = service.create(test_prompt)
    ok = service.delete(created.id)
    assert ok is True
    assert service.get(created.id) is None


def test_prompt_service_list_all(temp_db_path, test_prompt):
    """PromptService.list_all() listet Prompts."""
    backend = DatabasePromptStorage(db_path=temp_db_path)
    service = PromptService(backend=backend)
    service.create(test_prompt)
    prompts = service.list_all()
    assert len(prompts) >= 1
    titles = [p.title for p in prompts]
    assert test_prompt.title in titles


def test_prompt_service_duplicate(temp_db_path, test_prompt):
    """PromptService.duplicate() erstellt Kopie."""
    backend = DatabasePromptStorage(db_path=temp_db_path)
    service = PromptService(backend=backend)
    created = service.create(test_prompt)
    copy = service.duplicate(created)
    assert copy is not None
    assert copy.id != created.id
    assert "Kopie" in copy.title


# --- Directory Storage ---

def test_directory_storage_create(tmp_path):
    """DirectoryPromptStorage speichert als JSON."""
    backend = DirectoryPromptStorage(directory=str(tmp_path))
    p = Prompt(
        id=None,
        title="Dir-Test",
        category="general",
        description="",
        content="Inhalt",
        tags=[],
        prompt_type="user",
        scope="global",
        project_id=None,
        created_at=None,
        updated_at=None,
    )
    pid = backend.create(p)
    assert pid > 0
    path = tmp_path / f"{pid:05d}.json"
    assert path.exists()
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["title"] == "Dir-Test"


def test_directory_storage_get(tmp_path):
    """DirectoryPromptStorage lädt Prompt."""
    backend = DirectoryPromptStorage(directory=str(tmp_path))
    p = Prompt(
        id=None,
        title="Load-Test",
        category="general",
        description="",
        content="C",
        tags=[],
        prompt_type="user",
        scope="global",
        project_id=None,
        created_at=None,
        updated_at=None,
    )
    pid = backend.create(p)
    loaded = backend.get(pid)
    assert loaded is not None
    assert loaded.title == "Load-Test"


# --- create_storage_backend ---

def test_create_storage_backend_database():
    """create_storage_backend liefert DatabasePromptStorage."""
    backend = create_storage_backend("database", db_path=":memory:")
    assert isinstance(backend, DatabasePromptStorage)


def test_create_storage_backend_directory(tmp_path):
    """create_storage_backend liefert DirectoryPromptStorage."""
    backend = create_storage_backend("directory", directory=str(tmp_path))
    assert isinstance(backend, DirectoryPromptStorage)

"""
Golden-Path 2: Prompt anlegen -> speichern -> laden -> bearbeiten -> löschen.

Prüft den vollständigen CRUD-Flow mit Persistenz und Listen-Konsistenz.
"""

import pytest

from app.prompts.prompt_models import Prompt
from app.prompts.prompt_service import PromptService
from app.prompts.storage_backend import DatabasePromptStorage


@pytest.mark.golden_path
def test_prompt_create_save_load_edit_delete(prompt_service, temp_db_path):
    """
    Golden Path: Prompt erstellen -> in Liste -> laden (gleicher Inhalt) ->
    bearbeiten -> speichern -> laden (neuer Inhalt) -> löschen -> weg aus Liste.
    """
    # 1. Anlegen & Speichern
    p = Prompt(
        id=None,
        title="Golden-Path-Prompt",
        category="code",
        description="Test-Beschreibung",
        content="Ursprünglicher Inhalt",
        tags=["test", "golden"],
        prompt_type="user",
        scope="global",
        project_id=None,
        created_at=None,
        updated_at=None,
    )
    created = prompt_service.create(p)
    assert created is not None
    assert created.id is not None
    assert created.title == "Golden-Path-Prompt"
    assert created.content == "Ursprünglicher Inhalt"

    # 2. In Liste sichtbar
    all_prompts = prompt_service.list_all()
    titles = [x.title for x in all_prompts]
    assert "Golden-Path-Prompt" in titles

    # 3. Laden -> gleicher Inhalt
    loaded = prompt_service.get(created.id)
    assert loaded is not None
    assert loaded.title == created.title
    assert loaded.content == "Ursprünglicher Inhalt"
    assert loaded.category == "code"

    # 4. Bearbeiten & Speichern
    loaded.content = "Bearbeiteter Inhalt"
    loaded.description = "Neue Beschreibung"
    ok = prompt_service.update(loaded)
    assert ok is True

    # 5. Erneut laden -> neuer Inhalt
    reloaded = prompt_service.get(created.id)
    assert reloaded.content == "Bearbeiteter Inhalt"
    assert reloaded.description == "Neue Beschreibung"

    # 6. Löschen
    ok = prompt_service.delete(created.id)
    assert ok is True

    # 7. Weg aus Liste und get liefert None
    assert prompt_service.get(created.id) is None
    after_delete = prompt_service.list_all()
    assert "Golden-Path-Prompt" not in [x.title for x in after_delete]

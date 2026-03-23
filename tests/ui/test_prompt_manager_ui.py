"""
UI Tests: PromptManagerPanel.

P0: Save erscheint in Liste, Load zeigt im Editor, Delete entfernt aus Liste.
"""

import os
import tempfile
from unittest.mock import patch

import pytest

from app.gui.domains.operations.prompt_studio.panels.prompt_manager_panel import PromptManagerPanel
from app.prompts import PromptService
from app.prompts.storage_backend import DatabasePromptStorage
from tests.qt_ui import process_events_and_wait


@pytest.fixture
def temp_db_path():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def prompt_service(temp_db_path):
    backend = DatabasePromptStorage(db_path=temp_db_path)
    return PromptService(backend=backend)


def _global_prompt_kwargs(**extra):
    base = dict(
        scope="global",
        project_id=None,
        created_at=None,
        updated_at=None,
    )
    base.update(extra)
    return base


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.cross_layer
def test_prompt_manager_panel_save_appears_in_list(qapplication, temp_db_path, prompt_service):
    """
    Neu -> Editor füllen -> Speichern -> in Liste.
    Verhindert: Prompt speichern -> Liste leer / falscher Inhalt.
    """
    panel = PromptManagerPanel(prompt_service=prompt_service, theme="dark")
    panel.show()

    panel._on_new()
    panel.editor.title_edit.setText("P0-Save-Test")
    panel.editor.content_edit.setPlainText("Inhalt für Save-Test")

    with patch("app.gui.domains.operations.prompt_studio.panels.prompt_manager_panel.QMessageBox.information"):
        panel._on_save()
    process_events_and_wait(100)

    assert panel.prompt_list.count() >= 1
    titles = [panel.prompt_list.item(i).text() for i in range(panel.prompt_list.count())]
    assert any("P0-Save-Test" in t for t in titles)


@pytest.mark.ui
@pytest.mark.regression
def test_prompt_manager_panel_load_shows_in_editor(qapplication, temp_db_path, prompt_service):
    """
    Aus Liste laden -> Editor-Inhalt = Prompt.
    Verhindert: Prompt laden -> Editor zeigt anderen Prompt.
    """
    from app.prompts.prompt_models import Prompt

    created = prompt_service.create(
        Prompt(
            id=None,
            title="P0-Load-Test",
            category="code",
            description="Beschreibung",
            content="Editor soll diesen Inhalt zeigen",
            prompt_type="user",
            tags=["test"],
            **_global_prompt_kwargs(),
        )
    )
    assert created is not None

    panel = PromptManagerPanel(prompt_service=prompt_service, theme="dark")
    panel.show()
    panel._refresh_list()
    process_events_and_wait(50)

    for i in range(panel.prompt_list.count()):
        item = panel.prompt_list.item(i)
        if item and hasattr(item, "prompt") and item.prompt and item.prompt.id == created.id:
            panel.prompt_list.setCurrentItem(item)
            panel._on_prompt_selected(item.prompt)
            break
    process_events_and_wait(50)

    assert "P0-Load-Test" in (panel.editor.title_edit.text() or "")
    assert "Editor soll diesen Inhalt zeigen" in (panel.editor.content_edit.toPlainText() or "")


@pytest.mark.ui
@pytest.mark.regression
@pytest.mark.cross_layer
def test_prompt_manager_panel_delete_removes_from_list(qapplication, temp_db_path, prompt_service):
    """
    Löschen -> nicht mehr in Liste.
    Verhindert: Delete ohne Effekt auf Liste.
    """
    from app.prompts.prompt_models import Prompt

    created = prompt_service.create(
        Prompt(
            id=None,
            title="P0-Delete-Test",
            category="general",
            description="",
            content="Wird gelöscht",
            prompt_type="user",
            tags=[],
            **_global_prompt_kwargs(),
        )
    )
    assert created is not None

    settings = type("Settings", (), {"prompt_confirm_delete": False})()
    panel = PromptManagerPanel(prompt_service=prompt_service, settings=settings, theme="dark")
    panel.show()
    panel._refresh_list()
    panel._current_prompt = created

    panel._on_delete()
    process_events_and_wait(100)

    panel._refresh_list()
    for i in range(panel.prompt_list.count()):
        item = panel.prompt_list.item(i)
        if item and hasattr(item, "prompt") and item.prompt:
            assert item.prompt.id != created.id, "Gelöschter Prompt darf nicht mehr in Liste sein"

    assert prompt_service.get(created.id) is None


@pytest.mark.ui
@pytest.mark.regression
def test_prompt_apply_requested_signal_emits(qapplication, temp_db_path, prompt_service):
    """
    "In Chat übernehmen" -> prompt_apply_requested emittiert mit Prompt.
    Verhindert: Button ohne Signal-Effekt.
    """
    from app.prompts.prompt_models import Prompt

    created = prompt_service.create(
        Prompt(
            id=None,
            title="P1-Signal-Test",
            category="general",
            description="",
            content="Inhalt für Signal-Test",
            prompt_type="user",
            tags=[],
            **_global_prompt_kwargs(),
        )
    )
    assert created is not None

    panel = PromptManagerPanel(prompt_service=prompt_service, theme="dark")
    panel.show()
    panel._refresh_list()
    process_events_and_wait(50)

    received = []

    def on_apply(p):
        received.append(p)

    panel.prompt_apply_requested.connect(on_apply)

    for i in range(panel.prompt_list.count()):
        item = panel.prompt_list.item(i)
        if item and hasattr(item, "prompt") and item.prompt and item.prompt.id == created.id:
            panel.prompt_list.setCurrentItem(item)
            panel._on_prompt_selected(item.prompt)
            break
    process_events_and_wait(50)

    panel.btn_apply.click()
    process_events_and_wait(100)

    assert len(received) >= 1
    assert received[0].content == "Inhalt für Signal-Test"


@pytest.mark.ui
def test_prompt_manager_panel_search_filter(qapplication, temp_db_path, prompt_service):
    """
    Suche/Filter zeigt korrekte Treffer.
    Verhindert: Filter zeigt falsche Prompts.
    """
    from app.prompts.prompt_models import Prompt

    for title, cat in [("Alpha-Suchtest", "code"), ("Beta-anderer", "general"), ("Gamma-Code", "code")]:
        prompt_service.create(
            Prompt(
                id=None,
                title=title,
                category=cat,
                description="",
                content="Inhalt",
                prompt_type="user",
                tags=[],
                **_global_prompt_kwargs(),
            )
        )

    panel = PromptManagerPanel(prompt_service=prompt_service, theme="dark")
    panel.show()
    panel._refresh_list()
    process_events_and_wait(50)

    assert panel.prompt_list.count() >= 3

    panel.search_edit.setText("Alpha")
    process_events_and_wait(100)
    titles_filtered = []
    for i in range(panel.prompt_list.count()):
        item = panel.prompt_list.item(i)
        if item and hasattr(item, "prompt") and item.prompt:
            titles_filtered.append(item.prompt.title)
    assert any("Alpha" in t for t in titles_filtered), "Suche 'Alpha' muss Alpha-Suchtest zeigen"
    assert all("Alpha" in t for t in titles_filtered), "Suche 'Alpha' darf nur passende Prompts zeigen"

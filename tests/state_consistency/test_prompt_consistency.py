"""
State-Consistency: Prompt in DB -> Liste -> Editor.

Prompt in DB gespeichert -> Liste zeigt denselben Prompt -> Editor lädt denselben Inhalt.
"""

import pytest

from app.prompts.prompt_models import Prompt
from app.prompts.prompt_service import PromptService
from app.prompts.storage_backend import DatabasePromptStorage


@pytest.fixture
def temp_db_path():
    import os
    import tempfile
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


def test_prompt_db_list_editor_consistency(prompt_service):
    """
    Konsistenz: DB-Speicherung -> list_all -> get liefert identischen Inhalt.
    """
    p = Prompt(
        id=None,
        title="Consistency-Test-Prompt",
        category="code",
        description="Beschreibung für Konsistenz",
        content="Inhalt Zeile 1\nInhalt Zeile 2",
        tags=["test", "consistency"],
        prompt_type="user",
        scope="global",
        project_id=None,
        created_at=None,
        updated_at=None,
    )
    created = prompt_service.create(p)
    assert created is not None

    # Liste muss denselben Prompt enthalten
    all_prompts = prompt_service.list_all()
    from_list = next((x for x in all_prompts if x.id == created.id), None)
    assert from_list is not None
    assert from_list.title == created.title
    assert from_list.content == created.content

    # get muss denselben Inhalt liefern
    from_get = prompt_service.get(created.id)
    assert from_get.title == created.title
    assert from_get.content == "Inhalt Zeile 1\nInhalt Zeile 2"
    assert from_get.category == "code"


@pytest.mark.state_consistency
@pytest.mark.ui
@pytest.mark.regression
def test_prompt_ui_service_storage_roundtrip(qapplication, temp_db_path, prompt_service):
    """
    UI -> Service -> DB -> Reload -> UI: gleicher Inhalt.
    Verhindert: Nach Reload zeigt Editor anderen Inhalt.
    """
    from unittest.mock import patch
    from PySide6.QtWidgets import QApplication
    from app.gui.domains.operations.prompt_studio.panels.prompt_manager_panel import PromptManagerPanel
    from tests.qt_ui import process_events_and_wait

    panel1 = PromptManagerPanel(prompt_service=prompt_service, theme="dark")
    panel1.show()
    panel1._on_new()
    panel1.editor.title_edit.setText("Roundtrip-Test")
    panel1.editor.content_edit.setPlainText("Inhalt bleibt erhalten")

    with patch("app.gui.domains.operations.prompt_studio.panels.prompt_manager_panel.QMessageBox.information"):
        panel1._on_save()
    process_events_and_wait(100)

    created_id = panel1._current_prompt.id if panel1._current_prompt else None
    assert created_id is not None

    panel2 = PromptManagerPanel(prompt_service=prompt_service, theme="dark")
    panel2.show()
    panel2._refresh_list()
    process_events_and_wait(50)

    for i in range(panel2.prompt_list.count()):
        item = panel2.prompt_list.item(i)
        if item and hasattr(item, "prompt") and item.prompt and item.prompt.id == created_id:
            panel2.prompt_list.setCurrentItem(item)
            panel2._on_prompt_selected(item.prompt)
            break
    process_events_and_wait(50)
    QApplication.processEvents()

    assert "Roundtrip-Test" in (panel2.editor.title_edit.text() or "")
    assert "Inhalt bleibt erhalten" in (panel2.editor.content_edit.toPlainText() or "")

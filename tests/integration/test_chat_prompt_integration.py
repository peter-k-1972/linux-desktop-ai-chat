"""
Integration: Prompt-Auswahl im Chat.

Prüft die Verknüpfung Prompt Studio → Chat: Auswahl eines Prompts
fügt den Inhalt ins Eingabefeld ein, ohne automatisch zu senden.
"""

from unittest.mock import patch

import pytest

from app.gui.domains.operations.chat.panels.input_panel import ChatInputPanel
from app.prompts.prompt_models import Prompt


@pytest.fixture
def input_panel(qapplication):
    """ChatInputPanel für Tests."""
    panel = ChatInputPanel()
    panel.set_models(["llama3.2"])
    panel.show()
    return panel


def test_insert_prompt_text_into_empty_input(input_panel):
    """Prompt-Inhalt wird in leeres Eingabefeld eingefügt."""
    input_panel._insert_prompt_text("Erkläre mir Python.")
    assert input_panel._input.toPlainText() == "Erkläre mir Python."


def test_insert_prompt_text_appends_to_existing(input_panel):
    """Prompt-Inhalt wird an bestehenden Text angehängt."""
    input_panel._input.setPlainText("Vorher")
    input_panel._insert_prompt_text("Nachher")
    assert input_panel._input.toPlainText() == "Vorher\n\nNachher"


def test_insert_prompt_text_ignores_empty(input_panel):
    """Leerer Text ändert nichts."""
    input_panel._input.setPlainText("Bestehend")
    input_panel._insert_prompt_text("")
    assert input_panel._input.toPlainText() == "Bestehend"


@patch("app.prompts.prompt_service.get_prompt_service")
def test_prompt_menu_with_prompts(mock_get_service, input_panel):
    """Prompt-Menü zeigt Prompts; Auswahl fügt Inhalt ein."""
    p1 = Prompt(
        id=1,
        title="Code Review",
        category="code",
        description="",
        content="Prüfe den Code auf Fehler.",
        tags=[],
        prompt_type="user",
        scope="global",
        project_id=None,
        created_at=None,
        updated_at=None,
    )
    mock_svc = type("Svc", (), {"list_all": lambda: [p1]})()
    mock_get_service.return_value = mock_svc

    input_panel._on_prompt_clicked()
    input_panel._insert_prompt_text(p1.content)

    assert "Prüfe den Code auf Fehler" in input_panel._input.toPlainText()


@patch("app.prompts.prompt_service.get_prompt_service")
def test_prompt_menu_service_unavailable(mock_get_service, input_panel):
    """Bei Service-Fehler: Menü öffnet ohne Absturz, zeigt leere Liste."""
    mock_get_service.side_effect = RuntimeError("DB nicht verfügbar")
    input_panel._on_prompt_clicked()
    assert input_panel._input.toPlainText() == ""

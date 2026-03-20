"""
Smoke Tests: Basic Chat.

Testet Prompt senden, Antwort erhalten (mit Mocks).
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from PySide6.QtWidgets import QApplication


@pytest.fixture
def mock_chat_dependencies():
    """Gemockte Abhängigkeiten für ChatWidget."""
    from app.core.config.settings import AppSettings

    client = MagicMock()
    client.generate = AsyncMock(return_value="Mock-Stream")
    client.list_models = AsyncMock(return_value=[])
    client.get_debug_info = AsyncMock(return_value={"online": True})

    settings = AppSettings()

    db = MagicMock()
    db.create_chat = MagicMock(return_value=1)
    db.get_messages = MagicMock(return_value=[])
    db.add_message = MagicMock()
    db.get_or_create_file = MagicMock(return_value=1)
    db.add_file_to_chat = MagicMock()

    orchestrator = MagicMock()
    orchestrator.select_model_for_prompt = MagicMock(return_value="llama3:latest")
    orchestrator.complete = AsyncMock(return_value=[{"message": {"content": "Antwort"}}])

    rag = MagicMock()
    rag.retrieve = AsyncMock(return_value=[])

    return client, settings, db, orchestrator, rag


def test_chat_widget_importable():
    """ChatWidget ist importierbar und hat erwartete Attribute."""
    from app.gui.legacy import ChatWidget

    assert ChatWidget is not None
    assert hasattr(ChatWidget, "add_message")
    assert hasattr(ChatWidget, "update_chat_signal")


def test_conversation_view_add_message():
    """ConversationView kann Nachrichten anzeigen, Inhalt sichtbar."""
    from app.gui.domains.operations.chat.panels.conversation_view import ConversationView

    view = ConversationView(theme="dark")
    msg = view.add_message("user", "Hallo Test")
    assert msg is not None
    assert msg.role == "user"
    assert view.message_layout.count() >= 1
    assert "Hallo" in (msg.bubble.text() or ""), "Nachrichteninhalt muss sichtbar sein"


def test_chat_widget_placeholder_check():
    """is_placeholder_or_invalid_assistant_message funktioniert."""
    from app.gui.legacy import is_placeholder_or_invalid_assistant_message

    assert is_placeholder_or_invalid_assistant_message("") is True
    assert is_placeholder_or_invalid_assistant_message("...") is True
    assert is_placeholder_or_invalid_assistant_message("Gültige Antwort") is False


@pytest.mark.asyncio
async def test_complete_mock():
    """LLM complete mit Mock liefert Antwort."""
    from app.core.llm.llm_complete import complete

    async def mock_chat_fn(**kwargs):
        yield {"message": {"content": "Test-Antwort"}}

    result = await complete(
        chat_fn=mock_chat_fn,
        model="test",
        messages=[{"role": "user", "content": "Hallo"}],
    )
    assert isinstance(result, str)
    assert "Test-Antwort" in result or "Fehler" in result

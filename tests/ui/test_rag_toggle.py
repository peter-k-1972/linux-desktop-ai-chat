"""
UI Tests: RAG-Toggle synchronisiert mit Settings.

P1: Header rag_check -> settings.rag_enabled.
"""

from unittest.mock import MagicMock, AsyncMock

import pytest

from PySide6.QtCore import Qt

from app.gui.legacy import ChatWidget


class FakeDB:
    def create_chat(self, title=""):
        return 1
    def save_message(self, cid, role, content):
        pass
    def load_chat(self, cid):
        return []
    def list_workspace_roots_for_chat(self, cid):
        return []


class MinimalChatWidget(ChatWidget):
    def load_models(self):
        pass
    def on_update_chat(self, text, is_final):
        pass


@pytest.mark.ui
@pytest.mark.regression
def test_rag_toggle_syncs_with_settings(qtbot):
    """
    Header rag_check an/aus -> settings.rag_enabled aktualisiert.
    Verhindert: RAG-Toggle ohne Wirkung auf Settings.
    """
    from app.core.config.settings import AppSettings

    client = MagicMock()
    client.get_models = AsyncMock(return_value=[])
    settings = AppSettings()
    settings.model = "test"
    settings.rag_enabled = False
    db = FakeDB()

    widget = MinimalChatWidget(client, settings, db)
    qtbot.addWidget(widget)

    assert settings.rag_enabled is False
    # Slot direkt aufrufen, um Sync Header->Settings zu prüfen (Signal kann verzögert sein)
    from PySide6.QtCore import Qt
    widget._on_rag_toggled(Qt.Checked)
    assert settings.rag_enabled is True, "RAG-Checkbox an -> settings.rag_enabled muss True sein"

    widget._on_rag_toggled(Qt.Unchecked)
    assert settings.rag_enabled is False, "RAG-Checkbox aus -> settings.rag_enabled muss False sein"

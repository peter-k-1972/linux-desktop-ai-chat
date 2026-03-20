"""
Golden-Path 6: Agent im Chat auswählen -> Agentenprofil/Systemprompt/Modell greift wirklich.

Prüft, dass _build_messages_for_api den System-Prompt des ausgewählten Agenten einfügt.
"""

from typing import Dict, List
from unittest.mock import MagicMock, patch

import pytest

from app.gui.legacy import ChatWidget
from app.core.config.settings import AppSettings
from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_repository import AgentRepository
from app.agents.agent_registry import AgentRegistry


class RecordingClient:
    """Zeichnet die an Ollama gesendeten Messages auf."""

    def __init__(self):
        self.last_messages = None

    async def get_models(self):
        return []

    async def chat(self, model: str, messages: List[Dict[str, str]], **kwargs):
        self.last_messages = list(messages)

        async def _gen():
            yield {"message": {"content": "OK", "thinking": ""}, "done": True}

        return _gen()


class FakeDB:
    def __init__(self):
        self._messages = {}
        self._next_id = 1

    def create_chat(self, title=""):
        cid = self._next_id
        self._next_id += 1
        self._messages[cid] = []
        return cid

    def save_message(self, cid, role, content):
        self._messages.setdefault(cid, []).append((role, content, "ts"))

    def load_chat(self, cid):
        return list(self._messages.get(cid, []))

    def list_workspace_roots_for_chat(self, cid):
        return []


class MinimalChatWidget(ChatWidget):
    def load_models(self):
        pass

    def on_update_chat(self, text, is_final):
        pass


@pytest.fixture
def agent_registry_for_chat(temp_db_path):
    """Registry mit Test-Agent für Chat-Header-Simulation."""
    repo = AgentRepository(db_path=temp_db_path)
    profile = AgentProfile(
        id=None,
        name="Chat-Agent-Test",
        display_name="Chat Agent",
        slug="chat_agent_test",
        department="research",
        status=AgentStatus.ACTIVE.value,
        system_prompt="Du bist der spezielle Chat-Agent mit diesem System-Prompt.",
    )
    agent_id = repo.create(profile)
    profile.id = agent_id

    registry = AgentRegistry(repository=repo)
    registry.refresh()
    return registry, agent_id


@pytest.fixture
def settings():
    s = AppSettings()
    s.model = "test:latest"
    return s


@pytest.mark.golden_path
@pytest.mark.asyncio
async def test_agent_system_prompt_in_messages_when_selected(
    settings, temp_db_path, agent_registry_for_chat
):
    """
    Wenn ein Agent im Header ausgewählt ist, muss dessen System-Prompt
    in den an die API gesendeten Messages erscheinen.
    """
    registry, agent_id = agent_registry_for_chat

    client = RecordingClient()
    db = FakeDB()
    chat_id = db.create_chat()

    widget = MinimalChatWidget(client, settings, db)
    widget.chat_id = chat_id

    # Agent im Header "auswählen"
    widget.header = MagicMock()
    widget.header.agent_combo = MagicMock()
    widget.header.agent_combo.currentData = MagicMock(return_value=agent_id)

    with patch("app.gui.legacy.chat_widget.get_agent_registry", return_value=registry):
        await widget.run_chat("Hallo")

    assert client.last_messages is not None
    # Erste Message muss System-Prompt des Agenten sein
    system_msgs = [m for m in client.last_messages if m.get("role") == "system"]
    assert len(system_msgs) >= 1
    assert "spezielle Chat-Agent" in system_msgs[0].get("content", "")
    assert "System-Prompt" in system_msgs[0].get("content", "")


@pytest.mark.golden_path
@pytest.mark.ui
@pytest.mark.asyncio
@pytest.mark.regression
async def test_agent_selection_in_chat_header_real_ui(qtbot, temp_db_path, agent_registry_for_chat, settings):
    """
    Echter ChatHeader mit Agent-Combo, Auswahl -> Messages enthalten System-Prompt.
    Verhindert: Agent-Auswahl ohne Wirkung auf API-Messages (ohne Header-Mock).
    """
    from unittest.mock import patch

    registry, agent_id = agent_registry_for_chat
    client = RecordingClient()
    db = FakeDB()
    chat_id = db.create_chat()

    widget = MinimalChatWidget(client, settings, db)
    qtbot.addWidget(widget)
    widget.chat_id = chat_id

    with patch("app.gui.legacy.chat_widget.get_agent_registry", return_value=registry):
        widget.header.agent_combo.clear()
        widget.header.agent_combo.addItem("Standard (kein Agent)", None)
        for a in registry.list_all():
            widget.header.agent_combo.addItem(a.effective_display_name, a.id)
        widget.header.agent_combo.setCurrentIndex(1)
        qtbot.wait(50)

        await widget.run_chat("Hallo mit echtem Header")

    assert client.last_messages is not None
    system_msgs = [m for m in client.last_messages if m.get("role") == "system"]
    assert len(system_msgs) >= 1
    assert "spezielle Chat-Agent" in system_msgs[0].get("content", "")

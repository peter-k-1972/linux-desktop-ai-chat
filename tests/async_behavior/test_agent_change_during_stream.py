"""
Async Test: Agentwechsel während Stream.

Verhindert: Antwort wird mit falschem Agent-System-Prompt erzeugt,
oder Agent-Wechsel führt zu korruptem State.
"""

import asyncio
from unittest.mock import patch

import pytest

from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_registry import AgentRegistry
from app.agents.agent_repository import AgentRepository


@pytest.fixture
def registry_with_two_agents(temp_db_path):
    """Registry mit zwei Agenten für Wechsel-Tests."""
    repo = AgentRepository(db_path=temp_db_path)
    a1 = AgentProfile(
        id="agent-a",
        name="AgentA",
        display_name="Agent A",
        slug="agent_a",
        system_prompt="Du bist Agent A.",
        status=AgentStatus.ACTIVE.value,
        visibility_in_chat=True,
    )
    a2 = AgentProfile(
        id="agent-b",
        name="AgentB",
        display_name="Agent B",
        slug="agent_b",
        system_prompt="Du bist Agent B.",
        status=AgentStatus.ACTIVE.value,
        visibility_in_chat=True,
    )
    repo.create(a1)
    repo.create(a2)
    registry = AgentRegistry(repository=repo)
    registry.refresh()
    return registry


@pytest.mark.async_behavior
@pytest.mark.asyncio
@pytest.mark.integration
async def test_agent_change_during_stream_uses_initial_agent(
    async_client,
    async_db,
    async_settings,
    registry_with_two_agents,
):
    """
    Während des Streams gewählter Agent wird ignoriert.
    Die beim Send-Start gewählte Agent-Konfiguration gilt für die gesamte Antwort.
    """
    from tests.async_behavior.conftest import MinimalChatWidget

    registry = registry_with_two_agents
    with patch("app.gui.legacy.chat_widget.get_agent_registry", return_value=registry):
        widget = MinimalChatWidget(async_client, async_settings, async_db)
        widget.chat_id = async_db.create_chat()

        # Header mit Agent-Combo befüllen
        agents = registry.list_active()
        widget.header.agent_combo.clear()
        widget.header.agent_combo.addItem("Standard (kein Agent)", None)
        for a in agents:
            widget.header.agent_combo.addItem(a.effective_display_name, a.id)

        # Agent A auswählen
        idx_a = widget.header.agent_combo.findData("agent-a")
        widget.header.agent_combo.setCurrentIndex(idx_a)

        task = asyncio.create_task(widget.run_chat("Frage an Agent A"))
        # Warten bis Streaming läuft
        for _ in range(50):
            if getattr(widget, "_streaming", False):
                break
            await asyncio.sleep(0.01)
        # Während Stream: Agent B auswählen
        idx_b = widget.header.agent_combo.findData("agent-b")
        if idx_b >= 0:
            widget.header.agent_combo.setCurrentIndex(idx_b)
        await task

        # Die an die API gesendeten Messages müssen den System-Prompt von Agent A enthalten
        assert async_client.last_messages is not None
        system_msgs = [m for m in async_client.last_messages if m.get("role") == "system"]
        assert len(system_msgs) >= 1
        assert "Agent A" in system_msgs[0].get("content", "")

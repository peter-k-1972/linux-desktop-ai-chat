"""Tests für Agenten (Planner, Critic, Research)."""

import pytest

from app.agents.planner import Planner
from app.agents.critic import CriticAgent


async def _mock_llm(model_id: str, messages: list) -> str:
    """Mock-LLM für Tests."""
    if "Recherche-Plan" in str(messages):
        return "1. Was ist X?\n2. Wie funktioniert Y?\n3. Vor- und Nachteile"
    if "Überprüfe" in str(messages):
        return "Verbesserte Antwort mit mehr Details."
    return "Antwort"


@pytest.mark.asyncio
async def test_planner_parses_response():
    """Planner parst Plan-Antwort."""
    planner = Planner(_mock_llm)
    plan = await planner.plan("Testfrage")
    assert len(plan) >= 1
    assert any("X" in p or "Y" in p for p in plan)


@pytest.mark.asyncio
async def test_planner_fallback_on_empty():
    """Planner gibt Query als Fallback zurück."""
    async def empty_llm(*args):
        return ""

    planner = Planner(empty_llm)
    plan = await planner.plan("Meine Frage")
    assert plan == ["Meine Frage"] or "Recherche" in str(plan)


@pytest.mark.asyncio
async def test_critic_returns_improved():
    """Critic gibt verbesserte Antwort zurück."""
    critic = CriticAgent(_mock_llm)
    result = await critic.review("Frage", "Originale Antwort")
    assert "Verbesserte" in result or "Details" in result


@pytest.mark.asyncio
async def test_critic_returns_original_on_empty():
    """Critic gibt Original zurück bei leerer Antwort."""
    critic = CriticAgent(_mock_llm)
    result = await critic.review("Frage", "")
    assert result == ""

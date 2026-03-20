"""
Research Service – Fassade für Chat-Integration des Research Agents.
"""

import logging
from typing import Optional

from app.agents.research_agent import ResearchAgent
from app.core.llm.llm_complete import complete

logger = logging.getLogger(__name__)


def create_research_agent(
    orchestrator_chat_fn,
    rag_get_context_fn,
    planner_model: str = "qwen2.5:latest",
    research_model: str = "gpt-oss:latest",
    critic_model: str = "mistral:latest",
) -> ResearchAgent:
    """
    Erstellt einen ResearchAgent mit gebundenen Abhängigkeiten.

    Args:
        orchestrator_chat_fn: orchestrator.chat (async generator)
        rag_get_context_fn: async (query, top_k) -> context str
        planner_model: Modell für Planner
        research_model: Modell für Research
        critic_model: Modell für Critic
    """

    async def llm_complete(model_id: str, messages: list):
        return await complete(orchestrator_chat_fn, model_id, messages)

    async def rag_retrieve(query: str, top_k: int = 5):
        return await rag_get_context_fn(query, top_k)

    return ResearchAgent(
        llm_complete_fn=llm_complete,
        rag_retrieve_fn=rag_retrieve,
        planner_model=planner_model,
        research_model=research_model,
        critic_model=critic_model,
        use_critic=True,
    )

"""
Research Agent – vollständiger Workflow: Planner → RAG → LLM → Critic.

Modell Research: gpt-oss
"""

import logging
from typing import Any, Callable, Dict, List, Optional

from app.agents.planner import Planner
from app.agents.critic import CriticAgent
from app.debug.emitter import emit_event
from app.debug.agent_event import EventType

logger = logging.getLogger(__name__)

RESEARCH_PROMPT = """Beantworte die Frage auf Basis des folgenden Kontexts.
Fasse die Informationen strukturiert zusammen. Zitiere den Kontext wo sinnvoll.

Kontext:
---
{context}
---

Frage: {query}

Antwort:"""


class ResearchAgent:
    """
    Research-Workflow: Plan → RAG-Retrieval → Analyse → Kritik.
    """

    def __init__(
        self,
        llm_complete_fn: Callable[[str, List[Dict[str, str]]], Any],
        rag_retrieve_fn: Callable[[str, int], Any],
        planner_model: str = "qwen2.5:latest",
        research_model: str = "gpt-oss:latest",
        critic_model: str = "mistral:latest",
        use_critic: bool = True,
    ):
        """
        Args:
            llm_complete_fn: Async (model, messages) -> str
            rag_retrieve_fn: Async (query, top_k) -> str (Kontext)
            planner_model: Modell für Planung
            research_model: Modell für Analyse
            critic_model: Modell für Kritik
            use_critic: Critic-Schritt aktivieren
        """
        self._llm = llm_complete_fn
        self._rag = rag_retrieve_fn
        self.planner = Planner(llm_complete_fn, model_id=planner_model)
        self.critic = CriticAgent(llm_complete_fn, model_id=critic_model)
        self.research_model = research_model
        self.use_critic = use_critic

    async def run(
        self,
        query: str,
        rag_top_k: int = 5,
    ) -> str:
        """
        Führt den Research-Workflow aus.

        Flow: Planner → RAG → LLM Analysis → Critic
        """
        # 1. Plan
        emit_event(EventType.TASK_STARTED, agent_name="Planner", message="Recherche-Planung")
        plan_items = await self.planner.plan(query)
        emit_event(EventType.TASK_COMPLETED, agent_name="Planner", message="Plan erstellt")
        logger.debug("Research-Plan: %s", plan_items)

        # 2. RAG: Kontext aus Hauptfrage + Plan-Items sammeln
        context_parts = []
        main_context = await self._rag(query, rag_top_k)
        if main_context:
            context_parts.append(main_context)
        for item in plan_items[:3]:
            ctx = await self._rag(item, 2)
            if ctx and ctx not in context_parts:
                context_parts.append(ctx)
        context = "\n\n".join(context_parts) if context_parts else "Kein relevanter Kontext gefunden."

        # 3. LLM-Analyse
        emit_event(EventType.TASK_STARTED, agent_name="Research Agent", message="LLM-Analyse")
        prompt = RESEARCH_PROMPT.format(context=context, query=query)
        messages = [{"role": "user", "content": prompt}]
        response = await self._llm(self.research_model, messages)
        emit_event(EventType.TASK_COMPLETED, agent_name="Research Agent", message="Analyse abgeschlossen")

        # 4. Critic (optional)
        if self.use_critic and response:
            emit_event(EventType.TASK_STARTED, agent_name="Critic", message="Kritik")
            response = await self.critic.review(query, response)
            emit_event(EventType.TASK_COMPLETED, agent_name="Critic", message="Kritik abgeschlossen")

        return response or "Keine Antwort erzeugt."

"""
Critic Agent – überprüft und verbessert Research-Antworten.

Modell: mistral
"""

import logging
from typing import Any, Callable, Dict, List

logger = logging.getLogger(__name__)

CRITIC_PROMPT = """Überprüfe die folgende Recherche-Antwort auf:
- Korrektheit und Vollständigkeit
- Klarheit und Struktur
- Relevanz zur ursprünglichen Frage

Ursprüngliche Frage: {query}

Antwort zur Überprüfung:
---
{response}
---

Gib eine verbesserte, vollständige Version der Antwort zurück. Behebe Fehler und Lücken, behalte gutes bei.
Antwort:"""


class CriticAgent:
    """
    Überprüft und verbessert Research-Ausgaben.
    """

    def __init__(
        self,
        llm_complete_fn: Callable[[str, List[Dict[str, str]]], Any],
        model_id: str = "mistral:latest",
    ):
        """
        Args:
            llm_complete_fn: Async (model, messages) -> str
            model_id: Modell für Kritik
        """
        self._llm = llm_complete_fn
        self.model_id = model_id

    async def review(
        self,
        query: str,
        response: str,
    ) -> str:
        """
        Überprüft und verbessert die Antwort.

        Returns:
            Verbesserte Antwort
        """
        if not response or not response.strip():
            return response

        prompt = CRITIC_PROMPT.format(query=query, response=response[:6000])
        messages = [{"role": "user", "content": prompt}]

        try:
            improved = await self._llm(self.model_id, messages)
            return (improved or "").strip() or response
        except Exception as e:
            logger.warning("Critic fehlgeschlagen: %s", e)
            return response

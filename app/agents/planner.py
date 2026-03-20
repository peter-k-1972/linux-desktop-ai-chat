"""
Planner – plant Recherche-Schritte für den Research Agent.

Modell: qwen2.5
"""

import logging
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

PLANNER_PROMPT = """Du bist ein Recherche-Planer. Analysiere die Frage und erstelle einen kurzen Recherche-Plan.

Frage: {query}

Antworte mit 2–5 konkreten Suchanfragen oder Unterthemen, die bei der Beantwortung helfen.
Format: Eine Zeile pro Suchanfrage, nummeriert.
Beispiel:
1. Was ist X?
2. Wie funktioniert Y?
3. Vor- und Nachteile von Z

Recherche-Plan:"""


class Planner:
    """
    Erzeugt Recherche-Pläne aus User-Prompts.
    """

    def __init__(
        self,
        llm_complete_fn: Callable[[str, List[Dict[str, str]]], Any],
        model_id: str = "qwen2.5:latest",
    ):
        """
        Args:
            llm_complete_fn: Async (model, messages) -> str
            model_id: Modell für Planung
        """
        self._llm = llm_complete_fn
        self.model_id = model_id

    async def plan(self, query: str) -> List[str]:
        """
        Erzeugt einen Recherche-Plan.

        Returns:
            Liste von Suchanfragen/Unterthemen
        """
        prompt = PLANNER_PROMPT.format(query=query)
        messages = [{"role": "user", "content": prompt}]

        try:
            response = await self._llm(self.model_id, messages)
            return self._parse_plan(response or "")
        except Exception as e:
            logger.warning("Planner fehlgeschlagen: %s", e)
            return [query]

    def _parse_plan(self, text: str) -> List[str]:
        """Parst die Plan-Antwort in Suchanfragen."""
        lines = []
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line:
                continue
            # Nummerierung entfernen: "1. ", "1) ", "- "
            for prefix in (". ", ") ", "- "):
                for i in range(1, 20):
                    if line.startswith(f"{i}{prefix}"):
                        line = line[len(f"{i}{prefix}"):].strip()
                        break
            if line and len(line) > 3:
                lines.append(line)
        return lines if lines else [text.strip() or "Recherche"]

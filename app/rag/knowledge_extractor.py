"""
Knowledge Extractor – extrahiert Wissenselemente aus LLM-Antworten.

Nutzt ein LLM, um strukturierte KnowledgeEntries aus freiem Text zu gewinnen.
"""

import json
import logging
import re
from typing import Any, Callable, Dict, List, Optional

from app.rag.knowledge_models import KnowledgeEntry

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """Extrahiere aus dem folgenden Text eigenständige Wissenselemente.
Jedes Element soll einen kurzen Titel, den Inhalt und eine Konfidenz (0.0–1.0) haben.
Antworte NUR mit einer JSON-Liste, kein anderer Text.

Format:
[
  {"title": "Kurzer Titel", "content": "Der Inhalt", "confidence": 0.9},
  ...
]

Text:
---
{text}
---

JSON-Liste:"""


class KnowledgeExtractor:
    """
    Extrahiert KnowledgeEntries aus LLM-Antworten.
    """

    def __init__(
        self,
        llm_complete_fn: Callable[[str, List[Dict[str, str]]], Any],
        model_id: str = "qwen2.5:latest",
        min_confidence: float = 0.6,
    ):
        """
        Args:
            llm_complete_fn: Async-Funktion (prompt, messages) -> str
            model_id: Modell für Extraktion
            min_confidence: Mindest-Konfidenz für Übernahme
        """
        self._llm = llm_complete_fn
        self.model_id = model_id
        self.min_confidence = min_confidence

    async def extract(
        self,
        text: str,
        source: str = "llm_answer",
    ) -> List[KnowledgeEntry]:
        """
        Extrahiert Wissenselemente aus dem Text.

        Args:
            text: Roher Text (z.B. LLM-Antwort)
            source: Quell-Kennung

        Returns:
            Liste von KnowledgeEntry (nur confidence >= min_confidence)
        """
        if not text or len(text.strip()) < 50:
            return []

        prompt = EXTRACTION_PROMPT.format(text=text[:8000])
        messages = [{"role": "user", "content": prompt}]

        try:
            response = await self._llm(self.model_id, messages)
            return self._parse_response(response, source)
        except Exception as e:
            logger.warning("Knowledge-Extraktion fehlgeschlagen: %s", e)
            return []

    def _parse_response(self, response: str, source: str) -> List[KnowledgeEntry]:
        """Parst die LLM-Antwort in KnowledgeEntries."""
        entries: List[KnowledgeEntry] = []
        raw = (response or "").strip()

        # JSON-Block aus Antwort extrahieren
        match = re.search(r'\[[\s\S]*\]', raw)
        if match:
            raw = match.group(0)

        try:
            data = json.loads(raw)
            if not isinstance(data, list):
                return entries
            for item in data:
                if not isinstance(item, dict):
                    continue
                title = str(item.get("title", "")).strip()
                content = str(item.get("content", "")).strip()
                conf = float(item.get("confidence", 0.8))
                if title and content and conf >= self.min_confidence:
                    entries.append(
                        KnowledgeEntry(
                            title=title[:200],
                            content=content[:4000],
                            source=source,
                            confidence=conf,
                        )
                    )
        except json.JSONDecodeError:
            logger.debug("Kein gültiges JSON in Extraktion: %s", raw[:200])
        return entries

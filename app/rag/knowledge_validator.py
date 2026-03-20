"""
Knowledge Validator – prüft extrahierte Wissenselemente vor der Aufnahme.

Heuristik und optional LLM-basierte Validierung.
"""

import logging
import re
from typing import Any, Callable, List, Optional

from app.rag.knowledge_models import KnowledgeEntry

logger = logging.getLogger(__name__)

# Muster, die auf ungültige/triviale Einträge hindeuten
REJECT_PATTERNS = [
    r"^(ja|nein|ok|vielleicht|unbekannt)\s*$",
    r"^(ich\s+)?(weiß|kenne)\s+nicht",
    r"^(leider\s+)?(keine|kein)\s+(information|daten)",
    r"^(es\s+)?(hängt|kommt)\s+(davon|darauf)\s+an",
    r"^\.\.\.\s*$",
    r"^\[.*\]\s*$",  # Nur Markdown-Links
]

MIN_CONTENT_LENGTH = 30
MIN_TITLE_LENGTH = 3
MAX_DUPLICATE_SIMILARITY = 0.9  # Grobe Heuristik


class KnowledgeValidator:
    """
    Validiert KnowledgeEntries vor der Speicherung.
    """

    def __init__(
        self,
        min_confidence: float = 0.6,
        min_content_length: int = MIN_CONTENT_LENGTH,
        use_llm_validation: bool = False,
        llm_validate_fn: Optional[Callable[[str], Any]] = None,
    ):
        """
        Args:
            min_confidence: Mindest-Konfidenz
            min_content_length: Mindestlänge des Inhalts
            use_llm_validation: Optional LLM-basierte Prüfung
            llm_validate_fn: Async-Funktion (content) -> bool
        """
        self.min_confidence = min_confidence
        self.min_content_length = min_content_length
        self.use_llm_validation = use_llm_validation and llm_validate_fn
        self._llm_validate = llm_validate_fn

    def validate(self, entry: KnowledgeEntry) -> bool:
        """
        Prüft ein KnowledgeEntry (synchron, heuristisch).

        Returns:
            True wenn gültig
        """
        if entry.confidence < self.min_confidence:
            return False
        if len(entry.content.strip()) < self.min_content_length:
            return False
        if len(entry.title.strip()) < MIN_TITLE_LENGTH:
            return False

        content_lower = entry.content.lower().strip()
        for pat in REJECT_PATTERNS:
            if re.search(pat, content_lower, re.IGNORECASE):
                return False

        return True

    async def validate_async(self, entry: KnowledgeEntry) -> bool:
        """
        Vollständige Validierung inkl. optionaler LLM-Prüfung.
        """
        if not self.validate(entry):
            return False
        if self.use_llm_validation and self._llm_validate:
            try:
                return await self._llm_validate(entry.content)
            except Exception as e:
                logger.warning("LLM-Validierung fehlgeschlagen: %s", e)
                return True  # Bei Fehler: trotzdem übernehmen
        return True

    def filter_valid(self, entries: List[KnowledgeEntry]) -> List[KnowledgeEntry]:
        """Filtert nur gültige Einträge (synchron)."""
        return [e for e in entries if self.validate(e)]

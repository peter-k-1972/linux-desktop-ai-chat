"""
Knowledge-Entry-Modelle für Self-Improving RAG.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class KnowledgeEntry:
    """
    Ein extrahiertes Wissenselement für den Knowledge Store.

    Attributes:
        title: Kurzer Titel/Thema
        content: Der eigentliche Inhalt
        source: Herkunft (z.B. "llm_answer", "chat_123")
        confidence: Konfidenz 0.0–1.0
        timestamp: Zeitpunkt der Extraktion
    """

    title: str
    content: str
    source: str
    confidence: float = 1.0
    timestamp: Optional[datetime] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        self.confidence = max(0.0, min(1.0, self.confidence))

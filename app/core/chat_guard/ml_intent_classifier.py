"""
ML-/Embedding-basierte Intent-Klassifikation.

Nearest-Neighbor auf Intent-Beispielen.
Nutzt vorhandenen EmbeddingService (Ollama nomic-embed-text).
"""

import logging
from typing import Optional, Tuple

from app.core.chat_guard.intent_examples import INTENT_EXAMPLES
from app.core.chat_guard.intent_model import ChatIntent

logger = logging.getLogger(__name__)

# Confidence-Schwelle: darunter gilt ML als unsicher
ML_CONFIDENCE_THRESHOLD = 0.5


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine-Similarity zwischen zwei Vektoren. 1.0 = identisch."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(x * x for x in b) ** 0.5
    if na == 0 or nb == 0:
        return 0.0
    return max(-1.0, min(1.0, dot / (na * nb)))


class MLIntentClassifier:
    """
    Embedding-basierter Intent-Klassifikator.

    Nearest-Neighbor auf vordefinierten Beispielen.
    """

    def __init__(self, embedding_service=None):
        """
        Args:
            embedding_service: Optional. Wenn None, wird bei Bedarf erstellt.
        """
        self._embedding_service = embedding_service
        self._example_embeddings: list[tuple[list[float], ChatIntent]] = []
        self._initialized = False

    def _get_embedding_service(self):
        if self._embedding_service is not None:
            return self._embedding_service
        from app.rag.embedding_service import EmbeddingService
        return EmbeddingService()

    async def _ensure_embeddings(self) -> bool:
        """Lädt Beispiel-Embeddings. Gibt True wenn erfolgreich."""
        if self._initialized:
            return len(self._example_embeddings) > 0

        self._initialized = True
        try:
            svc = self._get_embedding_service()
            texts = [t for t, _ in INTENT_EXAMPLES]
            embeddings = await svc.embed_batch(texts)
            self._example_embeddings = [
                (emb, intent) for (emb, (_, intent)) in zip(embeddings, INTENT_EXAMPLES)
            ]
            return True
        except Exception as e:
            logger.warning("ML Intent: Embeddings konnten nicht geladen werden: %s", e)
            return False

    async def classify(self, text: str) -> Tuple[ChatIntent, float]:
        """
        Klassifiziert den Text per Nearest-Neighbor.

        Returns:
            (intent, confidence) – confidence 0.0–1.0
            Bei Fehler: (ChatIntent.CHAT, 0.0)
        """
        if not text or not text.strip():
            return ChatIntent.CHAT, 0.0

        ok = await self._ensure_embeddings()
        if not ok or not self._example_embeddings:
            return ChatIntent.CHAT, 0.0

        try:
            svc = self._get_embedding_service()
            query_emb = await svc.embed(text.strip())
        except Exception as e:
            logger.debug("ML Intent: Embedding fehlgeschlagen: %s", e)
            return ChatIntent.CHAT, 0.0

        best_intent = ChatIntent.CHAT
        best_sim = -1.0

        for ex_emb, ex_intent in self._example_embeddings:
            sim = _cosine_similarity(query_emb, ex_emb)
            if sim > best_sim:
                best_sim = sim
                best_intent = ex_intent

        # Cosine sim ist -1..1, wir normalisieren auf 0..1 für Confidence
        confidence = (best_sim + 1.0) / 2.0 if best_sim >= 0 else 0.0
        return best_intent, confidence

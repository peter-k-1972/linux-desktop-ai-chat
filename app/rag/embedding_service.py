"""
Embedding Service – erzeugt Vektor-Embeddings für Texte.

Primär: Ollama mit nomic-embed-text.
Optional vorbereitet: bge-m3.
"""

import logging
from typing import List, Optional

import aiohttp

logger = logging.getLogger(__name__)

DEFAULT_EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
BATCH_SIZE = 32  # Ollama verarbeitet einzelne Prompts; wir bündeln für Effizienz


class EmbeddingError(Exception):
    """Fehler bei der Embedding-Erzeugung."""

    pass


class EmbeddingService:
    """
    Erzeugt Embeddings über die Ollama-API.
    Batch-Verarbeitung und Fehlerbehandlung.
    """

    def __init__(
        self,
        model: str = DEFAULT_EMBEDDING_MODEL,
        base_url: str = "http://localhost:11434",
        batch_size: int = BATCH_SIZE,
    ):
        """
        Args:
            model: Ollama-Embedding-Modell (z.B. nomic-embed-text)
            base_url: Basis-URL der Ollama-Instanz
            batch_size: Max. Texte pro Batch (für sequentielle Verarbeitung)
        """
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.batch_size = batch_size

    async def embed(self, text: str) -> List[float]:
        """
        Erzeugt ein Embedding für einen einzelnen Text.

        Args:
            text: Der zu embeddende Text

        Returns:
            Embedding-Vektor als Liste von Floats

        Raises:
            EmbeddingError: Bei API-Fehlern
        """
        if not text or not text.strip():
            raise EmbeddingError("Leerer Text kann nicht embedded werden")

        result = await self._call_api(text.strip())
        return result

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Erzeugt Embeddings für mehrere Texte (Batch).
        Verarbeitet in Batches, um Timeouts zu vermeiden.

        Args:
            texts: Liste von Texten

        Returns:
            Liste von Embedding-Vektoren (gleiche Reihenfolge wie texts)
        """
        results: List[List[float]] = []
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i : i + self.batch_size]
            for text in batch:
                try:
                    emb = await self.embed(text)
                    results.append(emb)
                except EmbeddingError as e:
                    logger.warning("Embedding übersprungen: %s", e)
                    # Fallback: Null-Vektor gleicher Dimension (nomic: 768)
                    results.append([0.0] * 768)
        return results

    async def _call_api(self, prompt: str) -> List[float]:
        """Ruft die Ollama Embeddings-API auf."""
        url = f"{self.base_url}/api/embeddings"
        payload = {"model": self.model, "prompt": prompt}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=60)) as r:
                    if r.status != 200:
                        err_text = await r.text()
                        raise EmbeddingError(
                            f"Ollama API Fehler {r.status}: {err_text}"
                        )
                    data = await r.json()
                    embedding = data.get("embedding")
                    if not embedding:
                        raise EmbeddingError("Keine Embedding-Daten in Antwort")
                    return embedding
        except aiohttp.ClientError as e:
            raise EmbeddingError(f"Netzwerkfehler: {e}") from e

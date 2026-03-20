"""
Vector Store – persistente Speicherung von Embeddings.

Primär: ChromaDB.
Alternative vorbereitet: Qdrant.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.rag.models import Chunk

logger = logging.getLogger(__name__)


class VectorStoreError(Exception):
    """Fehler im Vector Store."""

    pass


class VectorStore:
    """
    Persistenter Vektor-Speicher auf Basis von ChromaDB.
    Speichert Chunk-Embeddings und Metadaten für Similarity Search.
    """

    def __init__(
        self,
        persist_directory: str,
        collection_name: str = "rag_chunks",
    ):
        """
        Args:
            persist_directory: Pfad für persistente Chroma-Daten
            collection_name: Name der Chroma-Collection
        """
        self.persist_directory = Path(persist_directory)
        self.collection_name = collection_name
        self._client = None
        self._collection = None

    def _ensure_client(self):
        """Initialisiert Chroma-Client und Collection lazy."""
        if self._collection is not None:
            return
        try:
            import chromadb
            from chromadb.config import Settings

            self.persist_directory.mkdir(parents=True, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=str(self.persist_directory),
                settings=Settings(anonymized_telemetry=False),
            )
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except ImportError as e:
            raise VectorStoreError(
                "chromadb nicht installiert. Bitte: pip install chromadb"
            ) from e

    def add_chunks(
        self,
        chunk_ids: List[str],
        embeddings: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        """
        Fügt Chunks mit Embeddings hinzu.

        Args:
            chunk_ids: Eindeutige IDs pro Chunk
            embeddings: Embedding-Vektoren
            documents: Chunk-Texte
            metadatas: Metadaten pro Chunk (müssen serialisierbar sein)
        """
        self._ensure_client()
        # Chroma akzeptiert nur primitive Metadaten
        clean_metadatas = [_sanitize_metadata(m) for m in metadatas]
        self._collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=clean_metadatas,
        )

    def query(
        self,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[str], List[Dict[str, Any]], List[float]]:
        """
        Führt eine Similarity-Suche durch.

        Args:
            query_embedding: Embedding der Suchanfrage
            n_results: Anzahl der Top-Ergebnisse
            where: Optionale Filter-Metadaten

        Returns:
            (ids, metadatas, distances, documents) – documents sind Chunk-Texte
        """
        self._ensure_client()
        kwargs: Dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ["documents", "metadatas", "distances"],
        }
        if where is not None:
            kwargs["where"] = where

        result = self._collection.query(**kwargs)
        ids = result["ids"][0] if result["ids"] else []
        metadatas = result["metadatas"][0] if result["metadatas"] else []
        distances = result["distances"][0] if result["distances"] else []
        documents = result["documents"][0] if result["documents"] else []

        # Chroma gibt bei cosine distance niedrigere Werte = ähnlicher
        return ids, metadatas, distances, documents

    def delete(self, ids: Optional[List[str]] = None, where: Optional[Dict] = None) -> None:
        """
        Löscht Einträge (z.B. für Re-Indexierung).

        Args:
            ids: Spezifische IDs zum Löschen
            where: Filter für Metadaten
        """
        self._ensure_client()
        if ids:
            self._collection.delete(ids=ids)
        elif where is not None:
            self._collection.delete(where=where)

    def count(self) -> int:
        """Anzahl der gespeicherten Chunks."""
        self._ensure_client()
        return self._collection.count()

    def delete_all(self) -> int:
        """Delete all chunks. Returns count of deleted items."""
        self._ensure_client()
        n = self._collection.count()
        if n == 0:
            return 0
        result = self._collection.get(include=[])
        ids = result.get("ids", [])
        if ids:
            self._collection.delete(ids=ids)
        return len(ids)


def _sanitize_metadata(m: Dict[str, Any]) -> Dict[str, Any]:
    """Chroma akzeptiert nur str, int, float, bool."""
    out = {}
    for k, v in m.items():
        if v is None:
            continue
        if isinstance(v, (str, int, float, bool)):
            out[k] = v
        else:
            out[k] = str(v)
    return out

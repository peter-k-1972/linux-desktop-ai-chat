"""
Retriever – sucht relevante Chunks für eine User-Query.

Nutzt Embedding-Service und Vector Store für Similarity Search.
"""

import logging
from typing import List, Optional

from app.rag.embedding_service import EmbeddingService
from app.rag.models import Chunk
from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)


class Retriever:
    """
    Sucht die relevantesten Chunks für eine User-Anfrage.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        embedding_service: EmbeddingService,
        top_k: int = 5,
    ):
        """
        Args:
            vector_store: Vektor-Datenbank
            embedding_service: Service für Query-Embeddings
            top_k: Anzahl der zurückgegebenen Chunks
        """
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.top_k = top_k

    async def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        where: Optional[dict] = None,
    ) -> List[Chunk]:
        """
        Sucht relevante Chunks für die Query.

        Args:
            query: User-Anfrage
            top_k: Override für Anzahl (optional)
            where: Optionale Metadaten-Filter

        Returns:
            Liste von Chunks, sortiert nach Relevanz
        """
        k = top_k or self.top_k
        if not query or not query.strip():
            return []

        try:
            query_embedding = await self.embedding_service.embed(query.strip())
        except Exception as e:
            logger.warning("Embedding-Fehler für Query: %s", e)
            return []

        try:
            ids, metadatas, distances, documents = self.vector_store.query(
                query_embedding=query_embedding,
                n_results=k,
                where=where,
            )
        except Exception as e:
            logger.warning("Vector-Store-Fehler: %s", e)
            try:
                from app.debug.agent_event import EventType
                from app.debug.emitter import emit_event

                emit_event(
                    EventType.RAG_RETRIEVAL_FAILED,
                    agent_name="RAG",
                    message=str(e),
                    metadata={"error": str(e), "source": "retriever"},
                )
            except Exception:
                pass
            return []

        chunks: List[Chunk] = []
        for i, doc_id in enumerate(ids):
            content = documents[i] if i < len(documents) else ""
            meta = metadatas[i] if i < len(metadatas) else {}
            doc_ref = meta.get("document_id", "")
            pos = meta.get("chunk_index", 0)
            chunks.append(
                Chunk(
                    id=doc_id,
                    document_id=doc_ref,
                    content=content,
                    metadata={**meta, "distance": distances[i] if i < len(distances) else None},
                    position=pos,
                )
            )
        return chunks

"""
Knowledge Space Manager – verwaltet getrennte Dokumentpools und Vektor-DBs.

Jeder Space hat eigenen Dokumentpool und eigene Vektordatenbank.
"""

import logging
from pathlib import Path
from typing import List, Optional

from app.rag.chunker import Chunker
from app.rag.document_loader import load_document, load_documents_from_directory
from app.rag.embedding_service import EmbeddingService
from app.rag.models import Chunk, Document
from app.rag.retriever import Retriever
from app.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

# Vordefinierte Knowledge Spaces
DEFAULT_SPACES = ["projects", "code", "documentation", "notes"]


class KnowledgeSpaceManager:
    """
    Verwaltet mehrere Knowledge Spaces mit je eigener Chroma-Collection.
    """

    def __init__(
        self,
        base_path: str,
        embedding_service: Optional[EmbeddingService] = None,
        chunk_size_tokens: int = 500,
        overlap_tokens: int = 50,
    ):
        """
        Args:
            base_path: Basisverzeichnis für persistente Daten (pro Space ein Unterordner)
            embedding_service: Gemeinsamer Embedding-Service
            chunk_size_tokens: Chunk-Größe
            overlap_tokens: Overlap
        """
        self.base_path = Path(base_path)
        self.embedding_service = embedding_service or EmbeddingService()
        self.chunker = Chunker(
            chunk_size_tokens=chunk_size_tokens,
            overlap_tokens=overlap_tokens,
        )
        self._stores: dict[str, VectorStore] = {}
        self._retrievers: dict[str, Retriever] = {}

    def _get_store(self, space: str) -> VectorStore:
        """Lazy-Initialisierung des Vector Stores pro Space."""
        if space not in self._stores:
            persist_dir = str(self.base_path / space)
            self._stores[space] = VectorStore(
                persist_directory=persist_dir,
                collection_name=f"rag_{space}",
            )
        return self._stores[space]

    def get_retriever(self, space: str, top_k: int = 5) -> Retriever:
        """Liefert den Retriever für einen Space."""
        if space not in self._retrievers:
            store = self._get_store(space)
            self._retrievers[space] = Retriever(
                vector_store=store,
                embedding_service=self.embedding_service,
                top_k=top_k,
            )
        return self._retrievers[space]

    async def index_document(self, space: str, path: str) -> int:
        """
        Indexiert ein einzelnes Dokument in einem Space.

        Returns:
            Anzahl der indexierten Chunks
        """
        doc = load_document(path)
        return await self._index_document(space, doc)

    async def index_directory(
        self,
        space: str,
        directory: str,
        recursive: bool = True,
    ) -> int:
        """
        Indexiert alle unterstützten Dokumente in einem Verzeichnis.

        Returns:
            Gesamtanzahl der indexierten Chunks
        """
        docs = load_documents_from_directory(directory, recursive=recursive)
        total = 0
        for doc in docs:
            total += await self._index_document(space, doc)
        return total

    async def _index_document(self, space: str, document: Document) -> int:
        """Indexiert ein Document in den Space."""
        chunks = self.chunker.chunk_document(document)
        if not chunks:
            return 0

        store = self._get_store(space)
        embeddings = await self.embedding_service.embed_batch([c.content for c in chunks])
        chunk_ids = [c.id for c in chunks]
        documents = [c.content for c in chunks]
        metadatas = [
            {
                "document_id": c.document_id,
                "chunk_index": c.position,
                "filename": document.metadata.get("filename", ""),
            }
            for c in chunks
        ]
        store.add_chunks(chunk_ids, embeddings, documents, metadatas)
        return len(chunks)

    def list_spaces(self) -> List[str]:
        """Listet alle Spaces mit persistierten Daten."""
        if not self.base_path.exists():
            return list(DEFAULT_SPACES)
        spaces = []
        for d in self.base_path.iterdir():
            if d.is_dir() and any(d.iterdir()):
                spaces.append(d.name)
        return sorted(spaces) if spaces else list(DEFAULT_SPACES)

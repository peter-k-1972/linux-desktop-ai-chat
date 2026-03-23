"""
Documentation search – semantic retrieval over the Chroma index built by
`tools/build_doc_embeddings.py` (collection `documentation`).

API: `search_docs(query, context=None)` → list of hits with title, snippet, file, score.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.rag.embedding_service import EmbeddingService
from app.rag.vector_store import VectorStore, VectorStoreError

logger = logging.getLogger(__name__)

COLLECTION_DOCUMENTATION = "documentation"
DEFAULT_CHROMA_REL = Path("data") / "chroma_documentation"
_DEFAULT_TOP_K = 10
_SNIPPET_DEFAULT = 280


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent


def _default_chroma_path() -> Path:
    return _project_root() / DEFAULT_CHROMA_REL


_WS = re.compile(r"\s+")


def _snippet(text: str, max_len: int) -> str:
    t = (text or "").strip()
    if not t:
        return ""
    one_line = _WS.sub(" ", t)
    if len(one_line) <= max_len:
        return one_line
    return one_line[: max_len - 1].rstrip() + "…"


def _distance_to_score(distance: float) -> float:
    """Higher is better; Chroma returns lower distance for better cosine matches."""
    d = float(distance)
    if d != d:  # NaN
        return 0.0
    return 1.0 / (1.0 + max(0.0, d))


@dataclass
class DocSearchHit:
    title: str
    snippet: str
    file: str
    score: float


class DocSearchService:
    """
    Semantic search in repo documentation vectors (Chroma collection `documentation`).
    """

    def __init__(
        self,
        chroma_path: Optional[Path | str] = None,
        collection_name: str = COLLECTION_DOCUMENTATION,
        embedding_service: Optional[EmbeddingService] = None,
        default_top_k: int = _DEFAULT_TOP_K,
    ):
        self._chroma_path = Path(chroma_path) if chroma_path else _default_chroma_path()
        self._collection_name = collection_name
        self._embedding_service = embedding_service or EmbeddingService()
        self._default_top_k = max(1, default_top_k)
        self._store: Optional[VectorStore] = None

    @property
    def chroma_path(self) -> Path:
        return self._chroma_path

    def _get_store(self) -> VectorStore:
        if self._store is None:
            self._store = VectorStore(
                persist_directory=str(self._chroma_path),
                collection_name=self._collection_name,
            )
        return self._store

    async def search_docs(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[DocSearchHit]:
        """
        Search documentation index.

        context (optional):
          - top_k: int — max results (default: service default)
          - where: dict — Chroma metadata filter
          - snippet_max: int — max snippet length (default: 280)
        """
        ctx = context or {}
        q = (query or "").strip()
        if not q:
            return []

        top_k = int(ctx.get("top_k", self._default_top_k))
        top_k = max(1, top_k)
        where = ctx.get("where")
        if where is not None and not isinstance(where, dict):
            where = None
        snippet_max = int(ctx.get("snippet_max", _SNIPPET_DEFAULT))
        snippet_max = max(40, snippet_max)

        try:
            query_embedding = await self._embedding_service.embed(q)
        except Exception as e:
            logger.warning("Doc search embedding failed: %s", e)
            return []

        try:
            store = self._get_store()
            ids, metadatas, distances, documents = store.query(
                query_embedding=query_embedding,
                n_results=top_k,
                where=where,
            )
        except VectorStoreError as e:
            logger.warning("Doc search vector store error: %s", e)
            return []
        except Exception as e:
            logger.warning("Doc search query failed: %s", e)
            return []

        hits: List[DocSearchHit] = []
        for i, _doc_id in enumerate(ids):
            meta = metadatas[i] if i < len(metadatas) else {}
            if not isinstance(meta, dict):
                meta = {}
            doc_text = documents[i] if i < len(documents) else ""
            dist = distances[i] if i < len(distances) else 0.0

            title = str(meta.get("title") or meta.get("section") or "Documentation").strip()
            file_path = str(meta.get("file_path") or "").strip()

            hits.append(
                DocSearchHit(
                    title=title,
                    snippet=_snippet(doc_text, snippet_max),
                    file=file_path,
                    score=_distance_to_score(dist),
                )
            )
        return hits


_doc_search_service: Optional[DocSearchService] = None


def get_doc_search_service() -> DocSearchService:
    global _doc_search_service
    if _doc_search_service is None:
        _doc_search_service = DocSearchService()
    return _doc_search_service


def set_doc_search_service(service: Optional[DocSearchService]) -> None:
    global _doc_search_service
    _doc_search_service = service


async def search_docs(query: str, context: Optional[Dict[str, Any]] = None) -> List[DocSearchHit]:
    """Module-level API: search documentation (uses shared DocSearchService)."""
    return await get_doc_search_service().search_docs(query, context)

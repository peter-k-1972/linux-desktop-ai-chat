"""
RAG Service – Fassade für die Chat-Integration.

Stellt eine einfache Schnittstelle bereit: augment_if_enabled(query) -> (augmented_text, was_used)
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

from app.debug.agent_event import EventType
from app.debug.emitter import emit_event
from app.rag.context_builder import ContextBuilder
from app.rag.embedding_service import EmbeddingService
from app.rag.knowledge_extractor import KnowledgeExtractor
from app.rag.knowledge_space import KnowledgeSpaceManager
from app.rag.knowledge_updater import KnowledgeUpdater
from app.rag.knowledge_validator import KnowledgeValidator
from app.rag.rag_pipeline import RAGPipeline

logger = logging.getLogger(__name__)


def get_default_rag_path() -> str:
    """Standardpfad für RAG-Daten (im Benutzerverzeichnis der App)."""
    from PySide6.QtCore import QStandardPaths
    data = QStandardPaths.writableLocation(QStandardPaths.AppDataLocation)
    return str(Path(data) / "rag_data")


class RAGService:
    """
    Fassade für RAG: Knowledge Spaces, Pipeline, Augmentierung.
    """

    def __init__(
        self,
        base_path: Optional[str] = None,
        default_space: str = "default",
    ):
        self.base_path = base_path or get_default_rag_path()
        self.default_space = default_space
        self._manager: Optional[KnowledgeSpaceManager] = None
        self._pipeline: Optional[RAGPipeline] = None

    def _ensure_manager(self) -> KnowledgeSpaceManager:
        if self._manager is None:
            self._manager = KnowledgeSpaceManager(
                base_path=self.base_path,
                embedding_service=EmbeddingService(),
            )
        return self._manager

    def get_pipeline(self, space: Optional[str] = None, top_k: int = 5) -> RAGPipeline:
        """Liefert die RAG-Pipeline für den angegebenen Space."""
        manager = self._ensure_manager()
        sp = space or self.default_space
        retriever = manager.get_retriever(sp, top_k=top_k)
        self._pipeline = RAGPipeline(
            retriever=retriever,
            context_builder=ContextBuilder(),
        )
        return self._pipeline

    async def augment_if_enabled(
        self,
        query: str,
        enabled: bool,
        space: Optional[str] = None,
        top_k: int = 5,
    ) -> Tuple[str, bool]:
        """
        Erweitert die Query mit RAG-Kontext, wenn RAG aktiviert ist.

        Returns:
            (text_for_llm, rag_was_used)
        """
        if not enabled or not query or not query.strip():
            return query, False

        try:
            pipeline = self.get_pipeline(space=space, top_k=top_k)
            return await pipeline.augment_prompt(query, top_k=top_k)
        except Exception as e:
            logger.warning("RAG-Augmentierung fehlgeschlagen: %s", e)
            emit_event(
                EventType.RAG_RETRIEVAL_FAILED,
                agent_name="RAG",
                message=str(e),
                metadata={"error": str(e), "query_preview": query[:100] if query else ""},
            )
            return query, False

    def get_manager(self) -> KnowledgeSpaceManager:
        """Zugriff auf den Knowledge-Space-Manager (z.B. für Indexierung)."""
        return self._ensure_manager()

    async def get_context(self, query: str, space: Optional[str] = None, top_k: int = 5) -> str:
        """
        Holt RAG-Kontext ohne Prompt-Augmentierung (für Research Agent).
        """
        try:
            pipeline = self.get_pipeline(space=space, top_k=top_k)
            return await pipeline.get_context(query, top_k=top_k)
        except Exception as e:
            logger.warning("RAG get_context fehlgeschlagen: %s", e)
            return ""

    def get_knowledge_updater(
        self,
        llm_complete_fn,
        self_improving_enabled: bool = True,
    ) -> Optional[KnowledgeUpdater]:
        """
        Erstellt einen KnowledgeUpdater für Self-Improving (optional).
        """
        if not self_improving_enabled:
            return None
        manager = self._ensure_manager()
        extractor = KnowledgeExtractor(llm_complete_fn)
        validator = KnowledgeValidator()
        return KnowledgeUpdater(manager, extractor, validator)

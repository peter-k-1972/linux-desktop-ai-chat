"""
Knowledge Updater – nimmt validierte Wissenselemente in den Knowledge Store auf.

Workflow: LLM Answer → Extraction → Validation → Vector DB Update
"""

import hashlib
import logging
from typing import List, Optional

from app.rag.knowledge_extractor import KnowledgeExtractor
from app.rag.knowledge_models import KnowledgeEntry
from app.rag.knowledge_space import KnowledgeSpaceManager
from app.rag.knowledge_validator import KnowledgeValidator
from app.rag.models import Document

logger = logging.getLogger(__name__)

SELF_IMPROVING_SPACE = "self_improving"


def _entry_to_document(entry: KnowledgeEntry, source_prefix: str = "si") -> Document:
    """Wandelt KnowledgeEntry in Document um."""
    raw = f"{entry.title}\n\n{entry.content}"
    doc_id = hashlib.sha256(
        f"{source_prefix}:{entry.source}:{entry.title}:{entry.content[:100]}".encode()
    ).hexdigest()[:32]
    return Document(
        id=doc_id,
        path=f"{source_prefix}://{entry.source}/{entry.title[:50]}",
        content=raw,
        metadata={
            "source": entry.source,
            "confidence": entry.confidence,
            "title": entry.title,
        },
        source_type="knowledge_entry",
    )


class KnowledgeUpdater:
    """
    Koordiniert Extraktion, Validierung und Speicherung.
    """

    def __init__(
        self,
        knowledge_space_manager: KnowledgeSpaceManager,
        extractor: KnowledgeExtractor,
        validator: KnowledgeValidator,
        target_space: str = SELF_IMPROVING_SPACE,
    ):
        self.manager = knowledge_space_manager
        self.extractor = extractor
        self.validator = validator
        self.target_space = target_space

    async def process_llm_answer(
        self,
        answer: str,
        source: str = "llm_answer",
        validate_async: bool = False,
    ) -> int:
        """
        Verarbeitet eine LLM-Antwort: extrahiert, validiert, speichert.

        Returns:
            Anzahl der neu aufgenommenen Einträge
        """
        entries = await self.extractor.extract(answer, source=source)
        if not entries:
            return 0

        valid: List[KnowledgeEntry] = []
        for e in entries:
            if validate_async:
                ok = await self.validator.validate_async(e)
            else:
                ok = self.validator.validate(e)
            if ok:
                valid.append(e)

        if not valid:
            return 0

        count = 0
        for entry in valid:
            try:
                doc = _entry_to_document(entry)
                n = await self.manager._index_document(self.target_space, doc)
                count += n
            except Exception as e:
                logger.warning("Knowledge-Update fehlgeschlagen für %s: %s", entry.title, e)
        return count

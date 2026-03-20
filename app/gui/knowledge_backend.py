"""
KnowledgeBackend – Kompatibilitätswrapper für KnowledgeService.

Delegiert an app.services. Neue Code sollte get_knowledge_service() nutzen.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from app.rag.models import Chunk


class KnowledgeBackend:
    """
    Deprecated. Delegiert an KnowledgeService.
    """

    def __init__(self, base_path: Optional[str] = None):
        from app.services.knowledge_service import get_knowledge_service, KnowledgeService
        self._svc = get_knowledge_service() if base_path is None else KnowledgeService(base_path)

    @property
    def base_path(self) -> Path:
        return self._svc.base_path

    def list_spaces(self) -> List[str]:
        return self._svc.list_spaces()

    def get_space_chunk_count(self, space: str) -> int:
        return self._svc.get_space_chunk_count(space)

    def list_sources(self, space: str) -> List[Dict[str, Any]]:
        return self._svc.list_sources(space)

    async def add_document(self, space: str, path: str) -> int:
        result = await self._svc.add_document(space, path)
        if not result.success:
            raise ValueError(result.error)
        return result.data or 0

    async def add_directory(self, space: str, directory: str, recursive: bool = True) -> int:
        result = await self._svc.add_directory(space, directory, recursive)
        if not result.success:
            raise ValueError(result.error)
        return result.data or 0

    async def retrieve(self, space: str, query: str, top_k: int = 5) -> List[Chunk]:
        result = await self._svc.retrieve(space, query, top_k)
        return result.data if result.success else []

    def get_overview(self) -> Dict[str, Any]:
        return self._svc.get_overview()


_backend: Optional[KnowledgeBackend] = None


def get_knowledge_backend() -> KnowledgeBackend:
    global _backend
    if _backend is None:
        _backend = KnowledgeBackend()
    return _backend


def set_knowledge_backend(backend: Optional[KnowledgeBackend]) -> None:
    global _backend
    _backend = backend

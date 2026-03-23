"""
KnowledgeService – Collections, Quellen, Retrieval.

Verantwortlich für:
- Knowledge Spaces / Collections
- Quellen registrieren
- Dokumente indexieren
- Retrieval ausführen

GUI spricht nur mit KnowledgeService, nicht mit RAG/Chroma direkt.
Projektbezogen: Space = project_{id} bei aktivem Projekt.

Collections: Flat logical groups of sources. Stored per project.
"""

import json
import logging
import shutil
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from app.rag.service import RAGService, get_default_rag_path
from app.rag.document_loader import SUPPORTED_EXTENSIONS
from app.rag.knowledge_space import DEFAULT_SPACES
from app.rag.models import Chunk
from app.services.result import ServiceResult

SOURCES_FILE = "sources.json"
COLLECTIONS_FILE = "collections.json"


class KnowledgeService:
    """
    Service für Knowledge / RAG: Spaces, Quellen, Indexierung, Retrieval.
    """

    def __init__(self, base_path: Optional[str] = None):
        self._base_path = Path(base_path or get_default_rag_path())
        self._rag = RAGService(base_path=str(self._base_path))
        self._manager = self._rag.get_manager()

    @property
    def base_path(self) -> Path:
        return self._base_path

    def list_spaces(self, project_id: Optional[int] = None) -> List[str]:
        """
        Listet verfügbare Spaces.
        project_id: bei aktivem Projekt nur project_{id}; sonst DEFAULT_SPACES + bestehende.
        """
        if project_id is not None:
            space = f"project_{project_id}"
            return [space]
        existing = self._manager.list_spaces()
        combined = list(dict.fromkeys(existing + DEFAULT_SPACES))
        return sorted(combined)

    def get_space_chunk_count(self, space: str) -> int:
        """Anzahl der Chunks in einem Space. 0 wenn leer oder Fehler."""
        try:
            store = self._manager._get_store(space)
            return store.count()
        except Exception:
            return 0

    def list_sources(self, space: str) -> List[Dict[str, Any]]:
        """Listet registrierte Quellen eines Spaces."""
        path = self._base_path / space / SOURCES_FILE
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            raw = data if isinstance(data, list) else []
            return [self._enrich_source(s) for s in raw]
        except Exception:
            return []

    def get_space_for_project(self, project_id: int) -> str:
        """Space-Name für ein Projekt."""
        return f"project_{project_id}"

    def remove_project_space(self, project_id: int) -> None:
        """
        Entfernt den gesamten RAG-Unterordner für ``project_{project_id}`` unter ``base_path``.

        Löscht nur Daten unter diesem Service-Pfad (Quellen-Metadaten, Index, Collections-JSON).
        Dateien außerhalb dieses Ordners (z. B. nur in sources.json referenzierte Pfade) werden nicht gelöscht.
        """
        space_dir = self._base_path / self.get_space_for_project(project_id)
        if space_dir.is_dir():
            shutil.rmtree(space_dir)
            logger.info("Knowledge-Raum entfernt: %s", space_dir)
        elif space_dir.exists():
            space_dir.unlink()
            logger.info("Knowledge-Raum-Datei entfernt: %s", space_dir)

    def list_sources_for_project(self, project_id: int) -> List[Dict[str, Any]]:
        """Quellen des Projekts (Space = project_{id})."""
        return self.list_sources(self.get_space_for_project(project_id))

    def get_project_chunk_count(self, project_id: int) -> int:
        """Chunk-Anzahl des Projekt-Spaces."""
        return self.get_space_chunk_count(self.get_space_for_project(project_id))

    # --- Collections (flat, per project) ---

    def _collections_path(self, project_id: int) -> Path:
        space = self.get_space_for_project(project_id)
        return self._base_path / space / COLLECTIONS_FILE

    def list_collections(self, project_id: int) -> List[Dict[str, Any]]:
        """List flat collections for project. Each: {id, name}."""
        path = self._collections_path(project_id)
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def create_collection(self, project_id: int, name: str) -> Dict[str, Any]:
        """Create a flat collection. Returns the new collection dict."""
        collections = self.list_collections(project_id)
        cid = f"col_{uuid.uuid4().hex[:12]}"
        coll = {"id": cid, "name": name.strip() or "Unnamed"}
        collections.append(coll)
        path = self._collections_path(project_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(collections, ensure_ascii=False, indent=2), encoding="utf-8")
        return coll

    def rename_collection(
        self, project_id: int, collection_id: str, new_name: str
    ) -> bool:
        """Rename a collection. Returns True on success."""
        collections = self.list_collections(project_id)
        for c in collections:
            if c.get("id") == collection_id:
                c["name"] = new_name.strip() or "Unnamed"
                path = self._collections_path(project_id)
                path.write_text(json.dumps(collections, ensure_ascii=False, indent=2), encoding="utf-8")
                return True
        return False

    def delete_collection(self, project_id: int, collection_id: str) -> bool:
        """Delete collection and unassign its sources. Returns True on success."""
        collections = self.list_collections(project_id)
        collections = [c for c in collections if c.get("id") != collection_id]
        if len(collections) == len(self.list_collections(project_id)):
            return False
        path = self._collections_path(project_id)
        path.write_text(json.dumps(collections, ensure_ascii=False, indent=2), encoding="utf-8")
        # Unassign sources
        space = self.get_space_for_project(project_id)
        sources = self._load_sources_raw(space)
        for s in sources:
            if s.get("collection_id") == collection_id:
                s.pop("collection_id", None)
        self._save_sources(space, sources)
        return True

    def assign_source_to_collection(
        self, project_id: int, source_path: str, collection_id: Optional[str]
    ) -> bool:
        """Assign source to collection. collection_id=None unassigns."""
        space = self.get_space_for_project(project_id)
        sources = self._load_sources_raw(space)
        path_str = str(Path(source_path).resolve())
        for s in sources:
            if s.get("path") == path_str:
                if collection_id:
                    s["collection_id"] = collection_id
                else:
                    s.pop("collection_id", None)
                self._save_sources(space, sources)
                return True
        return False

    def assign_sources_to_collection(
        self, project_id: int, source_paths: List[str], collection_id: Optional[str]
    ) -> int:
        """Assign multiple sources. Returns count of updated sources."""
        count = 0
        for p in source_paths:
            if self.assign_source_to_collection(project_id, p, collection_id):
                count += 1
        return count

    def _enrich_source(self, s: Dict[str, Any]) -> Dict[str, Any]:
        """Fügt type und status hinzu falls fehlend."""
        out = dict(s)
        if "type" not in out:
            p = Path(out.get("path", ""))
            if p.suffix:
                out["type"] = "datei"
            elif str(p) and p.name:
                out["type"] = "ordner"
            else:
                out["type"] = "quelle"
        if "status" not in out:
            out["status"] = "indexiert"
        return out

    def _save_sources(self, space: str, sources: List[Dict[str, Any]]) -> None:
        dir_path = self._base_path / space
        dir_path.mkdir(parents=True, exist_ok=True)
        path = dir_path / SOURCES_FILE
        path.write_text(json.dumps(sources, ensure_ascii=False, indent=2), encoding="utf-8")

    def _add_source_to_registry(
        self,
        space: str,
        path: str,
        name: str,
        project_id: Optional[int] = None,
    ) -> None:
        sources_raw = self._load_sources_raw(space)
        path_str = str(Path(path).resolve())
        if path_str not in {s.get("path", "") for s in sources_raw}:
            p = Path(path)
            entry: Dict[str, Any] = {
                "path": path_str,
                "name": name or p.name,
                "type": "ordner" if p.is_dir() else "datei",
                "status": "indexiert",
            }
            if project_id is not None:
                entry["project_id"] = project_id
            sources_raw.append(entry)
            self._save_sources(space, sources_raw)

    def _load_sources_raw(self, space: str) -> List[Dict[str, Any]]:
        """Lädt Quellen ohne Enrichment (für _save_sources)."""
        path = self._base_path / space / SOURCES_FILE
        if not path.exists():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    async def add_document(
        self,
        space: str,
        path: str,
        project_id: Optional[int] = None,
    ) -> ServiceResult[int]:
        """Indexiert ein Dokument. Returns: Anzahl der indexierten Chunks."""
        p = Path(path).resolve()
        if not p.exists():
            return ServiceResult.fail(f"Datei existiert nicht: {path}")
        if p.suffix.lower() not in SUPPORTED_EXTENSIONS:
            return ServiceResult.fail(
                f"Nicht unterstützt: {p.suffix}. Erlaubt: {', '.join(SUPPORTED_EXTENSIONS)}"
            )
        try:
            count = await self._manager.index_document(space, str(p))
            self._add_source_to_registry(space, str(p), p.name, project_id)
            return ServiceResult.ok(count)
        except Exception as e:
            return ServiceResult.fail(str(e))

    async def add_directory(
        self,
        space: str,
        directory: str,
        recursive: bool = True,
        project_id: Optional[int] = None,
    ) -> ServiceResult[int]:
        """Indexiert alle unterstützten Dokumente in einem Verzeichnis."""
        root = Path(directory).resolve()
        if not root.is_dir():
            return ServiceResult.fail(f"Verzeichnis existiert nicht: {directory}")
        try:
            total = await self._manager.index_directory(space, str(root), recursive=recursive)
            self._add_source_to_registry(space, str(root), root.name, project_id)
            return ServiceResult.ok(total)
        except Exception as e:
            return ServiceResult.fail(str(e))

    async def retrieve(
        self,
        space: str,
        query: str,
        top_k: int = 5,
    ) -> ServiceResult[List[Chunk]]:
        """Führt Retrieval für eine Query aus."""
        if not query or not query.strip():
            return ServiceResult.ok([])
        try:
            pipeline = self._rag.get_pipeline(space=space, top_k=top_k)
            _, chunks = await pipeline.get_context_and_chunks(query.strip(), top_k=top_k)
            return ServiceResult.ok(chunks)
        except Exception as e:
            return ServiceResult.fail(str(e))

    def get_embedding_model(self) -> str:
        """Embedding model name used for indexing."""
        try:
            return self._manager.embedding_service.model
        except Exception:
            from app.rag.embedding_service import DEFAULT_EMBEDDING_MODEL
            return DEFAULT_EMBEDDING_MODEL

    def get_index_stats(self, project_id: int) -> Dict[str, Any]:
        """
        Index statistics for technical visibility.
        Returns: embedding_model, chunk_count, index_size_bytes, source_count, last_update_ts
        """
        space = self.get_space_for_project(project_id)
        chunk_count = self.get_space_chunk_count(space)
        sources = self.list_sources_for_project(project_id)
        source_count = len(sources)

        # Index size: directory size of persist path
        space_path = self._base_path / space
        index_size = 0
        last_update: Optional[float] = None
        if space_path.exists():
            for f in space_path.rglob("*"):
                if f.is_file():
                    try:
                        st = f.stat()
                        index_size += st.st_size
                        if last_update is None or st.st_mtime > last_update:
                            last_update = st.st_mtime
                    except OSError:
                        pass

        return {
            "embedding_model": self.get_embedding_model(),
            "chunk_count": chunk_count,
            "index_size_bytes": index_size,
            "source_count": source_count,
            "last_update_ts": last_update,
        }

    def get_chunks_for_source(
        self, project_id: int, source_path: str, source_type: str
    ) -> List[Dict[str, Any]]:
        """
        Get chunks for a source (for debugging). Re-chunks on the fly using
        the same chunker config as indexing. Returns [{number, text, filename}, ...].
        """
        from app.rag.document_loader import (
            load_document,
            load_documents_from_directory,
            SUPPORTED_EXTENSIONS,
        )

        p = Path(source_path).resolve()
        chunks_out: List[Dict[str, Any]] = []
        chunker = self._manager.chunker

        if p.is_file():
            try:
                doc = load_document(str(p))
                rag_chunks = chunker.chunk_document(doc)
                for i, c in enumerate(rag_chunks):
                    chunks_out.append({
                        "number": i + 1,
                        "text": c.content,
                        "filename": doc.metadata.get("filename", p.name),
                    })
            except Exception:
                pass
        elif p.is_dir():
            try:
                docs = load_documents_from_directory(str(p), recursive=True)
                for doc in docs:
                    rag_chunks = chunker.chunk_document(doc)
                    fname = doc.metadata.get("filename", Path(doc.path).name)
                    for i, c in enumerate(rag_chunks):
                        chunks_out.append({
                            "number": len(chunks_out) + 1,
                            "text": c.content,
                            "filename": fname,
                        })
            except Exception:
                pass

        return chunks_out

    def clear_index(self, project_id: int) -> bool:
        """Clear all chunks from the project's index. Sources registry unchanged."""
        try:
            space = self.get_space_for_project(project_id)
            store = self._manager._get_store(space)
            store.delete_all()
            return True
        except Exception:
            return False

    def get_overview(self, project_id: Optional[int] = None) -> Dict[str, Any]:
        """Zusammenfassung: Spaces, Chunk-Zahlen, Quellenanzahl."""
        spaces = self.list_spaces(project_id)
        result: Dict[str, Any] = {
            "spaces": [],
            "total_chunks": 0,
            "total_sources": 0,
        }
        for space in spaces:
            chunk_count = self.get_space_chunk_count(space)
            sources = self.list_sources(space)
            result["spaces"].append({
                "name": space,
                "chunk_count": chunk_count,
                "source_count": len(sources),
            })
            result["total_chunks"] += chunk_count
            result["total_sources"] += len(sources)
        return result


_knowledge_service: Optional[KnowledgeService] = None


def get_knowledge_service() -> KnowledgeService:
    """Liefert den globalen KnowledgeService."""
    global _knowledge_service
    if _knowledge_service is None:
        _knowledge_service = KnowledgeService()
    return _knowledge_service


def set_knowledge_service(service: Optional[KnowledgeService]) -> None:
    """Setzt den KnowledgeService (für Tests)."""
    global _knowledge_service
    _knowledge_service = service

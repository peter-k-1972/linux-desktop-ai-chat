"""
KnowledgeWorkspace – Wissensarbeitsraum für RAG.

Projektbezogener Quellen-Explorer, Indexierung, Retrieval-Test.
"""

import asyncio
from pathlib import Path
from typing import List

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QFrame,
    QLabel,
)
from PySide6.QtCore import Qt, QTimer

from app.gui.shared import apply_workspace_layout
from app.gui.shared.base_operations_workspace import BaseOperationsWorkspace
from app.gui.domains.operations.knowledge.panels import (
    KnowledgeSourceExplorerPanel,
    KnowledgeOverviewPanel,
    RetrievalTestPanel,
)
from app.rag.models import Chunk


class KnowledgeWorkspace(BaseOperationsWorkspace):
    """Knowledge / RAG Arbeitsraum. Projektbezogener Quellen-Explorer."""

    def __init__(self, parent=None):
        super().__init__("knowledge", parent)
        self._current_source: str | None = None
        self._last_retrieval: List[Chunk] = []
        self._inspector_host = None
        self._indexing = False
        self._retrieving = False
        self._setup_ui()
        self._connect_signals()
        self._connect_project_context()
        QTimer.singleShot(0, self._defer_refresh)

    def _connect_project_context(self) -> None:
        try:
            from app.gui.events.project_events import subscribe_project_events
            subscribe_project_events(self._on_project_context_changed)
            QTimer.singleShot(0, self._defer_refresh)
        except Exception:
            pass

    def _on_project_context_changed(self, payload: dict) -> None:
        QTimer.singleShot(0, self._defer_refresh)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self._explorer = KnowledgeSourceExplorerPanel(self)
        splitter.addWidget(self._explorer)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        apply_workspace_layout(right_layout)
        title = QLabel("Knowledge / RAG")
        title.setObjectName("workspaceTitle")
        right_layout.addWidget(title)
        self._overview = KnowledgeOverviewPanel(self)
        self._retrieval = RetrievalTestPanel(self)
        right_layout.addWidget(self._overview)
        right_layout.addWidget(self._retrieval, 1)
        splitter.addWidget(right)

        splitter.setSizes([280, 400])
        layout.addWidget(splitter)

    def _connect_signals(self):
        self._explorer.add_source_requested.connect(self._on_add_source)
        self._explorer.source_selected.connect(self._on_source_selected)
        self._retrieval.retrieval_requested.connect(self._on_retrieval_requested)

    def _defer_refresh(self) -> None:
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._refresh_all())
        except RuntimeError:
            QTimer.singleShot(100, self._defer_refresh)

    def _get_active_project_id(self) -> int | None:
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            return get_project_context_manager().get_active_project_id()
        except Exception:
            return None

    def _get_current_space(self) -> str | None:
        return self._explorer.get_current_space()

    async def _refresh_all(self) -> None:
        project_id = self._get_active_project_id()
        self._explorer.refresh()
        self._overview.refresh(project_id)

    def _on_source_selected(self, path: str) -> None:
        self._current_source = path
        self._refresh_inspector()

    def _on_add_source(self, path: str) -> None:
        space = self._get_current_space()
        if not space:
            self._retrieval.set_status("Bitte zuerst ein Projekt auswählen.")
            return
        asyncio.create_task(self._run_add_source(path))

    async def _run_add_source(self, path: str) -> None:
        if self._indexing:
            return
        space = self._get_current_space()
        if not space:
            return
        self._indexing = True
        self._retrieval.set_status("Indexierung läuft…")
        try:
            from app.services.knowledge_service import get_knowledge_service
            svc = get_knowledge_service()
            p = Path(path)
            project_id = self._get_active_project_id()
            if p.is_file():
                result = await svc.add_document(space, path, project_id)
                count = result.data if result.success else 0
                if not result.success:
                    raise ValueError(result.error)
                self._retrieval.set_status(f"Indexiert: {count} Chunks")
            elif p.is_dir():
                result = await svc.add_directory(space, path, project_id=project_id)
                count = result.data if result.success else 0
                if not result.success:
                    raise ValueError(result.error)
                self._retrieval.set_status(f"Indexiert: {count} Chunks")
            else:
                self._retrieval.set_status("Ungültiger Pfad.")
                return
            self._explorer.refresh()
            self._overview.refresh(project_id)
            self._refresh_inspector()
        except ValueError as e:
            self._retrieval.set_status(f"Fehler: {e}")
        except Exception as e:
            self._retrieval.set_status(f"Fehler: {e!s}")
        finally:
            self._indexing = False

    def _on_retrieval_requested(self, query: str) -> None:
        space = self._get_current_space()
        if not space:
            self._retrieval.set_status("Bitte zuerst ein Projekt auswählen.")
            return
        asyncio.create_task(self._run_retrieval(query))

    async def _run_retrieval(self, query: str) -> None:
        space = self._get_current_space()
        if not space or self._retrieving:
            return
        self._retrieving = True
        self._retrieval.set_sending(True)
        self._retrieval.set_status("Suche…")
        try:
            from app.services.knowledge_service import get_knowledge_service
            result = await get_knowledge_service().retrieve(space, query, top_k=5)
            chunks = result.data if result.success else []
            if not result.success and result.error:
                self._retrieval.set_results("")
                self._retrieval.set_status(f"Fehler: {result.error}")
                self._refresh_inspector()
                return
            self._last_retrieval = chunks
            lines = []
            for i, c in enumerate(chunks, 1):
                source = c.metadata.get("filename", c.document_id)
                dist = c.metadata.get("distance")
                dist_str = f" (Score: {dist:.3f})" if dist is not None else ""
                lines.append(f"--- Treffer {i}: {source}{dist_str} ---")
                lines.append(c.content[:500] + ("…" if len(c.content) > 500 else ""))
                lines.append("")
            self._retrieval.set_results("\n".join(lines) if lines else "Keine Treffer.")
            self._retrieval.set_status(f"{len(chunks)} Treffer")
            self._refresh_inspector()
        except Exception as e:
            self._retrieval.set_results("")
            self._retrieval.set_status(f"Fehler: {e!s}")
        finally:
            self._retrieving = False
            self._retrieval.set_sending(False)

    def open_with_context(self, ctx: dict) -> None:
        """Öffnet eine Quelle aus Project-Hub-Kontext. ctx: {source_path: str}."""
        path = ctx.get("source_path")
        if path:
            QTimer.singleShot(50, lambda: self._explorer.select_source(path))

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        self._inspector_host = inspector_host
        self._inspector_content_token = content_token
        self._refresh_inspector()

    def _refresh_inspector(self) -> None:
        if not self._inspector_host:
            return
        from app.gui.inspector.knowledge_inspector import KnowledgeInspector
        project_name = None
        space = self._get_current_space()
        source_name = None
        source_type = None
        source_status = None
        if self._current_source:
            project_id = self._get_active_project_id()
            if project_id:
                try:
                    from app.services.knowledge_service import get_knowledge_service
                    svc = get_knowledge_service()
                    sources = svc.list_sources_for_project(project_id)
                    for s in sources:
                        if s.get("path") == self._current_source:
                            source_name = s.get("name", Path(self._current_source).name)
                            source_type = s.get("type", "quelle")
                            source_status = s.get("status", "—")
                            break
                except Exception:
                    pass
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            proj = get_project_context_manager().get_active_project()
            project_name = proj.get("name") if proj and isinstance(proj, dict) else None
        except Exception:
            pass
        content = KnowledgeInspector(
            space=space or "(keine)",
            source=self._current_source or "(keine)",
            source_name=source_name,
            source_type=source_type,
            source_status=source_status,
            chunk_count=len(self._last_retrieval),
            last_query=self._retrieval.get_query(),
            project_name=project_name,
        )
        token = getattr(self, "_inspector_content_token", None)
        self._inspector_host.set_content(content, content_token=token)

"""
IndexStatusPage – Technical visibility into the RAG index.

Shows: embedding model, chunk count, index size, source count, last update.
Actions: Rebuild index, Clear index, Re-embed all sources.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt, QTimer, Signal

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.widgets import EmptyStateWidget


def _format_size(bytes_val: int) -> str:
    """Format bytes for display."""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    if bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.1f} KB"
    return f"{bytes_val / (1024 * 1024):.1f} MB"


def _format_date(ts: Optional[float]) -> str:
    """Format timestamp for display."""
    if ts is None:
        return "—"
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError):
        return "—"


class IndexStatusPage(QFrame):
    """
    Index status page: stats and maintenance actions.
    """

    index_changed = Signal()  # Emitted when index is modified

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("indexStatusPage")
        self._project_id: Optional[int] = None
        self._busy = False
        self._setup_ui()
        self._connect_project_context()

    def _connect_project_context(self) -> None:
        try:
            from app.gui.events.project_events import subscribe_project_events
            subscribe_project_events(self._on_project_context_changed)
            from app.core.context.project_context_manager import get_project_context_manager
            self._project_id = get_project_context_manager().get_active_project_id()
            self._refresh_stats()
        except Exception:
            pass

    def _on_project_context_changed(self, payload: dict) -> None:
        self._project_id = payload.get("project_id")
        self._refresh_stats()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        title = QLabel("Index Status")
        title.setStyleSheet("font-size: 18px; font-weight: 600; color: #0f172a;")
        layout.addWidget(title)

        self._empty_widget = EmptyStateWidget(
            title="Kein Projekt ausgewählt",
            description="Wähle ein Projekt, um den Index-Status anzuzeigen.",
            icon=IconRegistry.PROJECTS,
            parent=self,
        )
        layout.addWidget(self._empty_widget)

        self._stats_frame = QFrame()
        stats_layout = QVBoxLayout(self._stats_frame)
        stats_layout.setSpacing(12)

        self._stat_labels = {}
        for key, label in [
            ("embedding_model", "Embedding model"),
            ("chunk_count", "Chunk count"),
            ("index_size", "Index size"),
            ("source_count", "Number of sources"),
            ("last_update", "Last update"),
        ]:
            row = QHBoxLayout()
            k = QLabel(f"{label}:")
            k.setStyleSheet("font-size: 12px; color: #64748b; min-width: 120px;")
            v = QLabel("—")
            v.setStyleSheet("font-size: 12px; color: #1f2937;")
            row.addWidget(k)
            row.addWidget(v, 1)
            stats_layout.addLayout(row)
            self._stat_labels[key] = v

        self._stats_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 16px;
            }
        """)
        layout.addWidget(self._stats_frame)
        self._stats_frame.hide()

        layout.addSpacing(8)

        actions_label = QLabel("Actions")
        actions_label.setStyleSheet("font-size: 14px; font-weight: 600; color: #334155;")
        layout.addWidget(actions_label)

        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(8)

        self._btn_rebuild = QPushButton("Rebuild Index")
        self._btn_rebuild.setIcon(IconManager.get(IconRegistry.REFRESH, size=16))
        self._btn_rebuild.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 10px 14px;
                font-size: 13px;
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background: #1d4ed8; }
            QPushButton:disabled { background: #cbd5e1; color: #94a3b8; }
        """)
        self._btn_rebuild.clicked.connect(self._on_rebuild)
        btn_layout.addWidget(self._btn_rebuild)

        self._btn_reembed = QPushButton("Re-embed All Sources")
        self._btn_reembed.setIcon(IconManager.get(IconRegistry.REFRESH, size=16))
        self._btn_reembed.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 10px 14px;
                font-size: 13px;
                background: #059669;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover { background: #047857; }
            QPushButton:disabled { background: #cbd5e1; color: #94a3b8; }
        """)
        self._btn_reembed.clicked.connect(self._on_reembed)
        btn_layout.addWidget(self._btn_reembed)

        self._btn_clear = QPushButton("Clear Index")
        self._btn_clear.setIcon(IconManager.get(IconRegistry.REMOVE, size=16))
        self._btn_clear.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 10px 14px;
                font-size: 13px;
                background: #fef2f2;
                color: #b91c1c;
                border: 1px solid #fecaca;
                border-radius: 8px;
            }
            QPushButton:hover { background: #fee2e2; }
            QPushButton:disabled { background: #f1f5f9; color: #94a3b8; }
        """)
        self._btn_clear.clicked.connect(self._on_clear)
        btn_layout.addWidget(self._btn_clear)

        layout.addLayout(btn_layout)

        self._status_label = QLabel("")
        self._status_label.setStyleSheet("font-size: 12px; color: #64748b;")
        layout.addWidget(self._status_label)
        layout.addStretch()

        self.setStyleSheet("""
            #indexStatusPage {
                background: #ffffff;
            }
        """)

    def _refresh_stats(self) -> None:
        """Refresh displayed stats from service."""
        if self._project_id is None:
            self._empty_widget.show()
            self._stats_frame.hide()
            self._set_buttons_enabled(False)
            return

        self._empty_widget.hide()
        self._stats_frame.show()
        self._set_buttons_enabled(True)

        try:
            from app.services.knowledge_service import get_knowledge_service
            svc = get_knowledge_service()
            stats = svc.get_index_stats(self._project_id)
        except Exception:
            stats = {}

        self._stat_labels["embedding_model"].setText(
            stats.get("embedding_model", "—")
        )
        self._stat_labels["chunk_count"].setText(
            str(stats.get("chunk_count", 0))
        )
        self._stat_labels["index_size"].setText(
            _format_size(stats.get("index_size_bytes", 0))
        )
        self._stat_labels["source_count"].setText(
            str(stats.get("source_count", 0))
        )
        self._stat_labels["last_update"].setText(
            _format_date(stats.get("last_update_ts"))
        )

    def _set_buttons_enabled(self, enabled: bool) -> None:
        """Enable/disable action buttons."""
        self._btn_rebuild.setEnabled(enabled and not self._busy)
        self._btn_reembed.setEnabled(enabled and not self._busy)
        self._btn_clear.setEnabled(enabled and not self._busy)

    def _set_busy(self, busy: bool) -> None:
        self._busy = busy
        self._set_buttons_enabled(self._project_id is not None)
        if busy:
            self._status_label.setText("Working…")
        else:
            self._status_label.setText("")

    def _on_rebuild(self) -> None:
        """Clear index and re-index all sources."""
        if self._project_id is None:
            return
        reply = QMessageBox.question(
            self,
            "Rebuild Index",
            "Clear the index and re-index all sources? This may take a while.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._defer_run(self._run_rebuild)

    def _on_reembed(self) -> None:
        """Re-embed all sources (same as rebuild)."""
        self._on_rebuild()

    def _on_clear(self) -> None:
        """Clear index only. Sources registry unchanged."""
        if self._project_id is None:
            return
        reply = QMessageBox.question(
            self,
            "Clear Index",
            "Remove all chunks from the index? Sources will remain; you can re-index later.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self._defer_run(self._run_clear)

    def _defer_run(self, coro_fn) -> None:
        """Run async task."""
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._run_with_busy(coro_fn))
        except RuntimeError:
            QTimer.singleShot(50, lambda: self._defer_run(coro_fn))

    async def _run_with_busy(self, coro_fn) -> None:
        self._set_busy(True)
        try:
            await coro_fn()
            self._refresh_stats()
            self.index_changed.emit()
        except Exception as e:
            self._status_label.setText(f"Error: {e!s}")
        finally:
            self._set_busy(False)

    async def _run_rebuild(self) -> None:
        """Clear and re-index all sources."""
        from app.services.knowledge_service import get_knowledge_service
        svc = get_knowledge_service()
        space = svc.get_space_for_project(self._project_id)
        sources = svc.list_sources_for_project(self._project_id)

        # Clear
        svc.clear_index(self._project_id)

        # Re-index each source
        total = 0
        for s in sources:
            path = s.get("path", "")
            stype = s.get("type", "")
            if not path or stype in ("url", "note"):
                continue
            p = Path(path)
            if p.is_file():
                result = await svc.add_document(space, path, self._project_id)
                if result.success:
                    total += result.data or 0
            elif p.is_dir():
                result = await svc.add_directory(space, path, project_id=self._project_id)
                if result.success:
                    total += result.data or 0

        self._status_label.setText(f"Rebuilt: {total} chunks indexed.")

    async def _run_clear(self) -> None:
        """Clear index only."""
        from app.services.knowledge_service import get_knowledge_service
        get_knowledge_service().clear_index(self._project_id)
        self._status_label.setText("Index cleared.")

    def refresh(self) -> None:
        """Reload stats from service."""
        self._refresh_stats()

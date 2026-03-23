"""
DocSearchPanel – semantische Dokumentationssuche (Chroma + doc_search_service).

Suchfeld, Trefferliste, Vorschau; Klick auf einen Treffer öffnet die Datei.
"""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from app.services.doc_search_service import DocSearchHit, DocSearchService


def _repo_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def _panel_frame_style() -> str:
    return (
        "QFrame#docSearchPanel { background: white; border: 1px solid #e5e7eb; "
        "border-radius: 10px; }"
    )


class DocSearchPanel(QFrame):
    """
    GUI für Dokumentationssuche über DocSearchService.

    Ein Klick auf einen Listeneintrag aktualisiert die Vorschau und öffnet die Quelldatei.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        doc_search_service: Optional["DocSearchService"] = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("docSearchPanel")
        self.setStyleSheet(_panel_frame_style())

        from app.services.doc_search_service import get_doc_search_service

        self._service = doc_search_service or get_doc_search_service()
        self._hits: List["DocSearchHit"] = []
        self._searching = False

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(10)

        title = QLabel("Semantische Repository-Dokumentation")
        title.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        root.addWidget(title)

        search_row = QHBoxLayout()
        search_row.setSpacing(8)
        self._query = QLineEdit(self)
        self._query.setPlaceholderText("Suchbegriff eingeben …")
        self._query.setClearButtonEnabled(True)
        self._query.returnPressed.connect(self._request_search)
        search_row.addWidget(self._query, 1)

        self._search_btn = QPushButton("Suchen", self)
        self._search_btn.setObjectName("docSearchButton")
        self._search_btn.setStyleSheet(
            """
            QPushButton#docSearchButton {
                background: #2563eb; color: white; border: none;
                border-radius: 6px; padding: 6px 14px; font-size: 12px;
            }
            QPushButton#docSearchButton:hover { background: #1d4ed8; }
            QPushButton#docSearchButton:disabled { background: #9ca3af; }
            """
        )
        self._search_btn.clicked.connect(self._request_search)
        search_row.addWidget(self._search_btn)
        root.addLayout(search_row)

        self._status = QLabel("")
        self._status.setStyleSheet("color: #6b7280; font-size: 12px;")
        self._status.setWordWrap(True)
        root.addWidget(self._status)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self._list = QListWidget(splitter)
        self._list.setObjectName("docSearchList")
        self._list.setSpacing(4)
        self._list.setAlternatingRowColors(True)
        self._list.setStyleSheet(
            "QListWidget { background: #fafafa; border: 1px solid #e5e7eb; border-radius: 6px; }"
        )
        self._list.itemClicked.connect(self._on_item_clicked)

        self._preview = QPlainTextEdit(splitter)
        self._preview.setObjectName("docSearchPreview")
        self._preview.setReadOnly(True)
        self._preview.setPlaceholderText("Vorschau des ausgewählten Treffers …")
        self._preview.setStyleSheet(
            "QPlainTextEdit { background: #ffffff; border: 1px solid #e5e7eb; "
            "border-radius: 6px; font-size: 12px; }"
        )

        splitter.addWidget(self._list)
        splitter.addWidget(self._preview)
        splitter.setSizes([320, 400])
        root.addWidget(splitter, 1)

        hint = QLabel("Hinweis: Index mit python3 tools/build_doc_index.py und tools/build_doc_embeddings.py erzeugen.")
        hint.setStyleSheet("color: #9ca3af; font-size: 11px;")
        hint.setWordWrap(True)
        root.addWidget(hint)

    def _request_search(self) -> None:
        q = self._query.text().strip()
        if not q:
            self._status.setText("Bitte einen Suchbegriff eingeben.")
            return
        self._defer_run_search(q)

    def _defer_run_search(self, query: str) -> None:
        try:
            asyncio.get_running_loop()
            asyncio.create_task(self._run_search(query))
        except RuntimeError:
            QTimer.singleShot(50, lambda: self._defer_run_search(query))

    async def _run_search(self, query: str) -> None:
        if self._searching:
            return
        self._searching = True
        self._search_btn.setEnabled(False)
        self._status.setText("Suche läuft …")
        self._list.clear()
        self._hits.clear()
        self._preview.clear()
        try:
            hits = await self._service.search_docs(query, {"top_k": 25})
            self._hits = list(hits)
            for i, h in enumerate(self._hits):
                item = QListWidgetItem()
                item.setData(Qt.ItemDataRole.UserRole, i)
                score_pct = min(100.0, max(0.0, h.score * 100.0))
                item.setText(f"{h.title}\n{h.file} · {score_pct:.0f}%")
                tip = f"{h.snippet}\n\n{h.file}"
                item.setToolTip(tip[:2000])
                self._list.addItem(item)
            if not self._hits:
                self._status.setText("Keine Treffer.")
                self._preview.setPlainText("")
            else:
                self._status.setText(f"{len(self._hits)} Treffer")
        except Exception as e:
            self._status.setText(f"Fehler: {e!s}")
        finally:
            self._searching = False
            self._search_btn.setEnabled(True)

    def _on_item_clicked(self, item: QListWidgetItem) -> None:
        idx = item.data(Qt.ItemDataRole.UserRole)
        if idx is None or not isinstance(idx, int):
            return
        if idx < 0 or idx >= len(self._hits):
            return
        hit = self._hits[idx]
        self._show_hit(hit)
        self._open_hit_file(hit.file)

    def _show_hit(self, hit: "DocSearchHit") -> None:
        score_pct = min(100.0, max(0.0, hit.score * 100.0))
        block = "\n".join(
            [
                f"Titel: {hit.title}",
                f"Datei: {hit.file}",
                f"Relevanz: {score_pct:.1f}%",
                "",
                hit.snippet or "(Kein Auszug)",
            ]
        )
        self._preview.setPlainText(block)

    def _open_hit_file(self, rel_path: str) -> None:
        rel = (rel_path or "").strip()
        if not rel:
            QMessageBox.warning(self, "Dokumentation", "Kein Dateipfad für diesen Treffer.")
            return
        full = (_repo_root() / rel).resolve()
        try:
            full.relative_to(_repo_root().resolve())
        except ValueError:
            QMessageBox.warning(
                self,
                "Dokumentation",
                f"Pfad liegt außerhalb des Projektroots:\n{full}",
            )
            return
        if not full.is_file():
            QMessageBox.warning(
                self,
                "Dokumentation",
                f"Datei nicht gefunden:\n{full}",
            )
            return
        QDesktopServices.openUrl(QUrl.fromLocalFile(str(full)))

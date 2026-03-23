"""
HelpPanel – Markdown-Hilfe für Seitenleiste oder Dialog.

Erwartet Inhalt als Markdown-Text (z. B. aus docs_manual, Pfad via manual_resolver).
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import unquote

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QDesktopServices, QTextCursor, QTextDocument
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.gui.components.markdown_widgets import MarkdownDocumentView

if TYPE_CHECKING:
    from app.help.manual_resolver import ManualHelpResolution


class HelpPanel(QWidget):
    """
    Scrollbares, kopierbares Hilfe-Panel mit optionaler Suche.

    Einbindung: in QDockWidget, QSplitter, QDialog oder beliebiges Layout.
    """

    link_requested = Signal(str)
    """Relativer oder unbekannter Link (wenn nicht unter manual_root auflösbar)."""

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        show_search: bool = True,
        manual_root: Path | None = None,
    ) -> None:
        super().__init__(parent)
        self._manual_root = Path(manual_root).resolve() if manual_root else None
        self._raw_markdown: str = ""

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(6)

        self._search_row = QWidget(self)
        search_layout = QHBoxLayout(self._search_row)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(8)

        self._search_label = QLabel("Suche:", self._search_row)
        search_layout.addWidget(self._search_label)

        self._search_input = QLineEdit(self._search_row)
        self._search_input.setPlaceholderText("Im Text suchen … (Enter / Weiter)")
        self._search_input.setClearButtonEnabled(True)
        self._search_input.returnPressed.connect(self._find_next)
        search_layout.addWidget(self._search_input, 1)

        self._search_next = QPushButton("Weiter", self._search_row)
        self._search_next.setToolTip("Nächstes Vorkommen (Enter im Suchfeld)")
        self._search_next.clicked.connect(self._find_next)
        search_layout.addWidget(self._search_next)

        root.addWidget(self._search_row)
        self._search_row.setVisible(show_search)

        self._browser = MarkdownDocumentView(self)
        self._browser.anchorClicked.connect(self._on_anchor_clicked)
        root.addWidget(self._browser, 1)

    def set_show_search(self, visible: bool) -> None:
        self._search_row.setVisible(visible)

    def set_manual_root(self, root: Path | None) -> None:
        """Basis für relative Markdown-Links (z. B. docs_manual_root())."""
        self._manual_root = Path(root).resolve() if root else None

    def clear(self) -> None:
        self._raw_markdown = ""
        self._browser.clear()

    def set_markdown(self, text: str) -> None:
        """Setzt Anzeige aus Markdown (zentrale Pipeline, identisch zum Chat)."""
        self._raw_markdown = text or ""
        self._browser.set_markdown(self._raw_markdown)

    def set_html(self, html: str) -> None:
        """Direktes HTML (ohne Markdown-Parsing)."""
        self._raw_markdown = ""
        self._browser.setHtml(html or "")

    def to_plain_text(self) -> str:
        """Aktueller Anzeigetext (nach HTML-Rendering)."""
        return self._browser.toPlainText()

    def markdown_source(self) -> str:
        """Zuletzt gesetztes Markdown (für Kopieren/Export durch Aufrufer)."""
        return self._raw_markdown

    def load_path(self, path: Path | str, *, encoding: str = "utf-8") -> bool:
        """Lädt eine Markdown-Datei. Rückgabe False bei Fehler."""
        p = Path(path)
        try:
            text = p.read_text(encoding=encoding)
        except OSError:
            return False
        self.set_markdown(text)
        return True

    def load_resolved_manual(self, resolution: ManualHelpResolution | None) -> bool:
        """
        Lädt die primäre Datei aus resolve_help() / ManualHelpResolution.

        Setzt manual_root automatisch auf docs_manual, wenn die Datei darunter liegt.
        """
        if resolution is None or not resolution.primary.is_file():
            return False
        from app.help.manual_resolver import docs_manual_root

        primary = resolution.primary.resolve()
        root = docs_manual_root().resolve()
        try:
            primary.relative_to(root)
            self.set_manual_root(root)
        except ValueError:
            self.set_manual_root(primary.parent)
        return self.load_path(primary)

    def _find_next(self) -> None:
        query = self._search_input.text().strip()
        if not query:
            return
        flags = QTextDocument.FindFlag(0)
        if not self._browser.find(query, flags):
            cur = self._browser.textCursor()
            cur.movePosition(QTextCursor.MoveOperation.Start)
            self._browser.setTextCursor(cur)
            self._browser.find(query, flags)

    def _on_anchor_clicked(self, url: QUrl) -> None:
        href = url.toString()
        if href.startswith(("http://", "https://")):
            QDesktopServices.openUrl(url)
            return

        if self._manual_root and href:
            path_part = unquote(href).strip().split("#")[0]
            if path_part:
                candidate = (self._manual_root / path_part.lstrip("/")).resolve()
                try:
                    candidate.relative_to(self._manual_root.resolve())
                except ValueError:
                    self.link_requested.emit(href)
                    return
                if candidate.is_dir():
                    readme = candidate / "README.md"
                    candidate = readme if readme.is_file() else candidate
                if candidate.is_file():
                    self.load_path(candidate)
                    return

        if href.startswith("#"):
            return

        self.link_requested.emit(href)

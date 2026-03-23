"""
Zentrale Markdown-Views: dieselbe Pipeline wie Hilfe & Chat, Styling getrennt vom Parsing.

- MarkdownMessageWidget: read-only QTextEdit (Chat-Blasen)
- MarkdownDocumentView: QTextBrowser (Hilfe, Dokumente)
- MarkdownView: generischer Container mit eingebettetem MarkdownDocumentView (Demo/Inspector)
"""

from __future__ import annotations

import math

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QTextOption
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QMenu,
    QSizePolicy,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.gui.shared.markdown.markdown_types import RenderTarget
from app.gui.shared.markdown_ui import apply_markdown_to_widget


def chat_context_menu_stylesheet() -> str:
    def _from_tokens(t: dict) -> str:
        bg = t.get("color_menu_bg") or t.get("color_bg_elevated") or t.get("color_bg_surface", "")
        fg = t.get("color_menu_fg") or t.get("color_fg_primary") or t.get("color_text", "")
        hover = t.get("color_menu_hover_bg") or t.get("color_interaction_hover") or t.get("color_bg_hover", "")
        return f"""
            QMenu {{ background-color: {bg}; color: {fg}; padding: 4px; }}
            QMenu::item:selected {{ background-color: {hover}; }}
        """

    try:
        from app.gui.themes import get_theme_manager

        return _from_tokens(get_theme_manager().get_tokens())
    except Exception:
        from app.gui.themes.registry import ThemeRegistry

        td = ThemeRegistry().get("light_default")
        if td:
            return _from_tokens(td.get_tokens_dict())
        return _from_tokens({})


class MarkdownMessageWidget(QTextEdit):
    """
    Chat-Nachrichtentext: zentrale Markdown-Pipeline, wachsende Höhe, kein Parser im Widget.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("markdownMessageContent")
        self.setReadOnly(True)
        self.setFrameShape(QFrame.Shape.NoFrame)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        self.setMinimumHeight(0)
        self.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.setWordWrapMode(QTextOption.WrapMode.WrapAtWordBoundaryOrAnywhere)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def set_markdown(
        self,
        text: str,
        *,
        promote_ascii: bool = True,
    ) -> None:
        apply_markdown_to_widget(
            self,
            text or "",
            target=RenderTarget.CHAT_BUBBLE,
            promote_ascii=promote_ascii,
        )
        self.updateGeometry()
        parent = self.parent()
        if parent is not None:
            parent.updateGeometry()

    def setPlainText(self, text: str) -> None:
        super().setPlainText(text)
        self.updateGeometry()

    def setHtml(self, html: str) -> None:
        super().setHtml(html or "")
        self.updateGeometry()

    def _wrap_width_for_height(self) -> int:
        vw = self.viewport().width()
        estimates: list[int] = []
        if vw >= 100:
            estimates.append(vw)
        parent = self.parent()
        if parent is not None and parent.width() >= 100:
            estimates.append(max(100, parent.width() - 96))
        if not estimates:
            estimates.append(400)
        w = min(estimates)
        return max(100, min(w, 700))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        w = max(1, self.viewport().width())
        self.document().setTextWidth(w)
        self.updateGeometry()
        parent = self.parent()
        if parent is not None:
            parent.updateGeometry()

    def sizeHint(self) -> QSize:
        doc = self.document()
        w = self._wrap_width_for_height()
        doc.setTextWidth(w)
        margin = int(doc.documentMargin())
        h = math.ceil(doc.size().height()) + 2 * margin + 6
        return QSize(-1, h)

    def minimumSizeHint(self) -> QSize:
        return self.sizeHint()

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        menu.setStyleSheet(chat_context_menu_stylesheet())
        menu.addAction("Kopieren").triggered.connect(self._on_copy)
        menu.addAction("Komplette Nachricht kopieren").triggered.connect(self._on_copy_full)
        menu.addSeparator()
        menu.addAction("Alles auswählen").triggered.connect(self.selectAll)
        menu.exec(event.globalPos())

    def _on_copy(self) -> None:
        from PySide6.QtWidgets import QApplication

        cursor = self.textCursor()
        text = (
            cursor.selectedText().replace("\u2029", "\n")
            if cursor.hasSelection()
            else self.toPlainText()
        )
        if text:
            QApplication.clipboard().setText(text)

    def _on_copy_full(self) -> None:
        from PySide6.QtWidgets import QApplication

        text = self.toPlainText()
        if text:
            QApplication.clipboard().setText(text)


class MarkdownDocumentView(QTextBrowser):
    """
    Hilfe / längere Dokumente: QTextBrowser + dieselbe Pipeline wie der Chat (RenderTarget.HELP_BROWSER).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("markdownDocumentView")
        self.setOpenExternalLinks(False)
        self.setLineWrapMode(QTextBrowser.LineWrapMode.WidgetWidth)
        self.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.TextSelectableByKeyboard
            | Qt.TextInteractionFlag.LinksAccessibleByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByKeyboard
        )

    def set_markdown(self, text: str, *, promote_ascii: bool = True) -> None:
        apply_markdown_to_widget(
            self,
            text or "",
            target=RenderTarget.HELP_BROWSER,
            promote_ascii=promote_ascii,
        )


class MarkdownView(QFrame):
    """
    Generischer Markdown-Block (z. B. Demo, Inspector): Titel optional + MarkdownDocumentView.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        title: str | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("markdownView")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)
        self._title: QLabel | None = None
        if title:
            self._title = QLabel(title)
            self._title.setStyleSheet("font-weight: 600; font-size: 13px;")
            layout.addWidget(self._title)
        self._body = MarkdownDocumentView(self)
        layout.addWidget(self._body, 1)

    def document_view(self) -> MarkdownDocumentView:
        return self._body

    def set_title(self, text: str) -> None:
        if self._title is None:
            self._title = QLabel(text)
            self._title.setStyleSheet("font-weight: 600; font-size: 13px;")
            self.layout().insertWidget(0, self._title)
        else:
            self._title.setText(text)
        self._title.setVisible(bool(text))

    def set_markdown(self, text: str, *, promote_ascii: bool = True) -> None:
        self._body.set_markdown(text, promote_ascii=promote_ascii)

    def set_html_direct(self, html: str) -> None:
        """Fertiges HTML (z. B. Hilfe-Topic mit Nachbearbeitung)."""
        self._body.setHtml(html or "")

"""
Zentrale Anwendung der Markdown-Pipeline auf QTextEdit / QTextBrowser.

Parsing/Rendering bleibt in app.gui.shared.markdown; hier nur Qt-Anbindung + Fallback.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from PySide6.QtGui import QFont

from app.gui.shared.markdown.markdown_types import RenderResult, RenderTarget

if TYPE_CHECKING:
    from PySide6.QtWidgets import QTextBrowser, QTextEdit


class _SupportsHtmlPlain(Protocol):
    def setHtml(self, html: str) -> None: ...
    def setPlainText(self, text: str) -> None: ...
    def toPlainText(self) -> str: ...
    def font(self) -> QFont: ...
    def setFont(self, font: QFont) -> None: ...


def apply_markdown_to_widget(
    widget: "QTextEdit | QTextBrowser",
    text: str,
    *,
    target: RenderTarget,
    promote_ascii: bool = True,
) -> RenderResult:
    """
    Setzt Inhalt über render_markdown → setHtml.

    Bei Fehler oder leerem Dokument bei nicht-leerem Input: Plaintext-Fallback
    (Monospace), damit ASCII/Code nicht zerstört werden.
    """
    from app.gui.shared.markdown import RenderOptions, render_markdown

    opts = RenderOptions(target=target, promote_ascii=promote_ascii)
    result = render_markdown(text or "", opts)
    plain_fallback = (result.plain_text or text or "").strip()
    try:
        widget.setHtml(result.html)
    except Exception:
        widget.setPlainText(result.plain_text or text or "")
        _apply_monospace_fallback_font(widget)
        return result

    # Sehr defensiv: Qt kann defektes HTML still „schlucken“
    try:
        if plain_fallback and len(widget.toPlainText()) == 0:
            raise ValueError("empty plain after setHtml")
    except Exception:
        widget.setPlainText(result.plain_text or text or "")
        _apply_monospace_fallback_font(widget)
        return result

    _clear_monospace_fallback_font(widget)
    return result


def _apply_monospace_fallback_font(widget: _SupportsHtmlPlain) -> None:
    f = QFont("DejaVu Sans Mono")
    f.setStyleHint(QFont.StyleHint.Monospace)
    f.setPointSize(max(9, widget.font().pointSize()))
    widget.setFont(f)


def _clear_monospace_fallback_font(widget: _SupportsHtmlPlain) -> None:
    """Zurück auf Standard-Schrift der Umgebung (Parent/Style)."""
    try:
        parent = getattr(widget, "parentWidget", lambda: None)()
        if parent is not None:
            widget.setFont(parent.font())
            return
    except Exception:
        pass
    widget.setFont(QFont())

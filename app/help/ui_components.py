"""
Definierte GUI-Anbindung fuer ``app.help``.

Nur diese schmale Widget-/Markdown-Schicht darf direkt in ``app.gui`` greifen.
"""

from app.gui.components.doc_search_panel import DocSearchPanel
from app.gui.components.markdown_widgets import MarkdownDocumentView
from app.gui.shared.markdown import markdown_to_html

__all__ = [
    "DocSearchPanel",
    "MarkdownDocumentView",
    "markdown_to_html",
]

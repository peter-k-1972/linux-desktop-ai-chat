"""
HelpWindow – Durchsuchbares Hilfefenster mit Kategorien und Navigation.
"""

import re
from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QSplitter,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QTextBrowser,
    QLabel,
    QComboBox,
    QWidget,
    QFrame,
    QPushButton,
    QScrollArea,
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QTextCharFormat, QBrush, QColor

from app.help.help_index import HelpIndex, HelpTopic, HELP_CATEGORIES
from app.resources.styles import get_theme_colors


def markdown_to_html(md: str) -> str:
    """Einfache Markdown-zu-HTML-Konvertierung für Anzeige."""
    html = md
    # Escapen
    html = html.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Code-Blöcke
    html = re.sub(r"```(\w*)\n(.*?)```", r'<pre><code class="\1">\2</code></pre>', html, flags=re.DOTALL)
    html = re.sub(r"`([^`]+)`", r"<code>\1</code>", html)
    # Headers
    for i in range(3, 0, -1):
        html = re.sub(rf"^#{i}\s+(.+)$", rf"<h{i}>\1</h{i}>", html, flags=re.MULTILINE)
    # Links [text](url)
    html = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', html)
    # Bold
    html = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", html)
    html = re.sub(r"__([^_]+)__", r"<b>\1</b>", html)
    # Lists
    html = re.sub(r"^- (.+)$", r"<li>\1</li>", html, flags=re.MULTILINE)
    html = re.sub(r"(<li>.*</li>\n?)+", r"<ul>\g<0></ul>", html)
    # Paragraphs
    html = re.sub(r"\n\n+", "</p><p>", html)
    html = f"<p>{html}</p>"
    html = html.replace("<p><h", "<h").replace("</h1></p>", "</h1>").replace("</h2></p>", "</h2>").replace("</h3></p>", "</h3>")
    html = html.replace("<p><ul>", "<ul>").replace("</ul></p>", "</ul>")
    html = html.replace("<p><pre>", "<pre>").replace("</pre></p>", "</pre>")
    return f'<div style="font-family: sans-serif; line-height: 1.5;">{html}</div>'


class HelpWindow(QDialog):
    """Hilfefenster mit Suchfeld, Kategorien, TOC und Dokumentanzeige."""

    def __init__(self, theme: str = "dark", parent=None, initial_topic_id: str | None = None):
        super().__init__(parent)
        self.theme = theme
        self.index = HelpIndex()
        self.setWindowTitle("Hilfe – Linux Desktop Chat")
        self.setMinimumSize(900, 600)
        self.resize(1000, 700)
        self.init_ui()
        self.apply_theme()
        self._populate_toc()
        if initial_topic_id and self.index.get_topic(initial_topic_id):
            self._show_topic(initial_topic_id)
        else:
            self._show_welcome()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)

        # Suchzeile
        search_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Durchsuchen… (Stichwörter, Tags)")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.textChanged.connect(self._on_search_changed)
        self.search_input.returnPressed.connect(self._search_and_show_first)
        search_row.addWidget(self.search_input)

        self.category_combo = QComboBox()
        self.category_combo.addItem("Alle Kategorien", None)
        for cid, cname in HELP_CATEGORIES:
            self.category_combo.addItem(cname, cid)
        self.category_combo.currentIndexChanged.connect(self._on_category_changed)
        search_row.addWidget(self.category_combo)
        layout.addLayout(search_row)

        # Splitter: TOC | Content
        splitter = QSplitter(Qt.Horizontal)

        # Linke Seite: TOC / Kategorien
        toc_widget = QWidget()
        toc_layout = QVBoxLayout(toc_widget)
        toc_layout.setContentsMargins(0, 0, 0, 0)
        toc_label = QLabel("Inhaltsverzeichnis")
        toc_label.setStyleSheet("font-weight: bold; font-size: 13px;")
        toc_layout.addWidget(toc_label)
        self.toc_list = QListWidget()
        self.toc_list.setMinimumWidth(220)
        self.toc_list.itemClicked.connect(self._on_toc_item_clicked)
        toc_layout.addWidget(self.toc_list)
        splitter.addWidget(toc_widget)

        # Rechte Seite: Dokument
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        self.doc_browser = QTextBrowser()
        self.doc_browser.setOpenExternalLinks(False)
        self.doc_browser.anchorClicked.connect(self._on_anchor_clicked)
        content_layout.addWidget(self.doc_browser)
        splitter.addWidget(content_widget)

        splitter.setSizes([250, 650])
        layout.addWidget(splitter)

        # Quick Guides + Guided Tours
        guide_row = QHBoxLayout()
        guide_row.addWidget(QLabel("Quick Guides:"))
        for label, topic_id in [
            ("Erste Schritte", "introduction"),
            ("Chat", "chat_overview"),
            ("Agenten", "agents_overview"),
            ("Prompts", "prompt_studio_overview"),
            ("RAG", "knowledge_overview"),
        ]:
            btn = QPushButton(label)
            btn.setFlat(True)
            btn.clicked.connect(lambda checked, tid=topic_id: self._show_topic(tid))
            guide_row.addWidget(btn)
        guide_row.addSpacing(20)
        guide_row.addWidget(QLabel("Guided Tours:"))
        for label, tour_id in [
            ("Tour: Erste Schritte", "getting_started"),
            ("Tour: Chat", "chat"),
            ("Tour: Agenten", "agents"),
            ("Tour: Prompts", "prompts"),
            ("Tour: Medien", "media"),
        ]:
            btn = QPushButton(label)
            btn.setFlat(True)
            btn.clicked.connect(lambda checked, tid=tour_id: self._start_tour(tid))
            guide_row.addWidget(btn)
        guide_row.addStretch()
        layout.addLayout(guide_row)

    def _populate_toc(self):
        """Befüllt das Inhaltsverzeichnis."""
        self.toc_list.clear()
        cat_filter = self.category_combo.currentData()
        topics = self.index.list_by_category(cat_filter)
        current_cat = None
        for t in topics:
            if t.category != current_cat:
                current_cat = t.category
                cat_item = QListWidgetItem(f"▸ {t.category_display}")
                cat_item.setData(Qt.UserRole, ("category", current_cat))
                cat_item.setFlags(Qt.ItemIsEnabled)
                self.toc_list.addItem(cat_item)
            item = QListWidgetItem(f"  {t.title}")
            item.setData(Qt.UserRole, ("topic", t.id))
            self.toc_list.addItem(item)

    def _on_category_changed(self):
        self._populate_toc()
        self._on_search_changed()

    def _on_search_changed(self):
        query = self.search_input.text().strip()
        if not query:
            self._populate_toc()
            return
        topics = self.index.search(query)
        self.toc_list.clear()
        for t in topics:
            item = QListWidgetItem(f"{t.category_display}: {t.title}")
            item.setData(Qt.UserRole, ("topic", t.id))
            self.toc_list.addItem(item)

    def _search_and_show_first(self):
        topics = self.index.search(self.search_input.text().strip())
        if topics:
            self._show_topic(topics[0].id)

    def _on_toc_item_clicked(self, item: QListWidgetItem):
        data = item.data(Qt.UserRole)
        if not data:
            return
        kind, value = data
        if kind == "topic":
            self._show_topic(value)

    def _on_anchor_clicked(self, url):
        """Interne Links: #topic_id oder topic_id"""
        url_str = url.toString() if hasattr(url, "toString") else str(url)
        if url_str.startswith("#"):
            self._show_topic(url_str[1:])
        elif url_str and not url_str.startswith("http") and "." not in url_str.split("/")[-1]:
            # Plain topic id like "chat_overview"
            self._show_topic(url_str.split("/")[-1].split("#")[0])

    def _show_topic(self, topic_id: str):
        topic = self.index.get_topic(topic_id)
        if not topic:
            self.doc_browser.setHtml("<p>Thema nicht gefunden.</p>")
            return
        html = markdown_to_html(topic.content)
        # Interne Links: [text](architecture.md) -> #architecture, [text](chat_overview) -> #chat_overview
        html = re.sub(r'href="([a-z0-9_]+)\.md"', r'href="#\1"', html)
        html = re.sub(r'href="([a-z0-9_]+)"', r'href="#\1"', html)
        # Related topics
        if getattr(topic, "related", None):
            related_html = '<div style="margin-top: 24px; padding: 12px; border-top: 1px solid #555; font-size: 13px;"><strong>Siehe auch:</strong> '
            links = []
            for rid in topic.related:
                rt = self.index.get_topic(rid)
                if rt:
                    links.append(f'<a href="#{rid}">{rt.title}</a>')
            if links:
                related_html += " · ".join(links) + "</div>"
                html += related_html
        self.doc_browser.setHtml(html)

    def _start_tour(self, tour_id: str):
        from app.help.guided_tour import GuidedTour
        dialog = GuidedTour.run(tour_id, theme=self.theme, parent=self)
        dialog.exec()

    def _show_welcome(self):
        welcome = """
# Willkommen in der Hilfe

Nutzen Sie die **Suchfunktion** oder das **Inhaltsverzeichnis**, um Themen zu finden.

## Quick Guides
- **Erste Schritte**: Schnellstart und Grundlagen
- **Chat verwenden**: Konversation, Modelle, Rollen
- **Agenten**: Spezialisierte Personas verwalten
- **Prompts**: Wiederverwendbare Prompts
- **RAG**: Kontext aus Dokumenten nutzen

## Kategorien
Wählen Sie eine Kategorie, um die Themen einzuschränken.
        """
        self.doc_browser.setHtml(markdown_to_html(welcome))

    def apply_theme(self):
        colors = get_theme_colors(self.theme)
        bg = colors.get("top_bar_bg", "#353535" if self.theme == "dark" else "#f5f5f5")
        fg = colors.get("fg", "#e8e8e8" if self.theme == "dark" else "#1a1a1a")
        border = colors.get("top_bar_border", "#505050" if self.theme == "dark" else "#cccccc")
        self.setStyleSheet(f"""
            QDialog {{ background-color: {bg}; color: {fg}; }}
            QLineEdit {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; padding: 8px; border-radius: 6px; }}
            QListWidget {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; border-radius: 6px; }}
            QTextBrowser {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; border-radius: 6px; padding: 12px; }}
            QPushButton {{ background: transparent; color: {fg}; }}
            QPushButton:hover {{ text-decoration: underline; }}
            QComboBox {{ background-color: {bg}; color: {fg}; border: 1px solid {border}; padding: 6px; border-radius: 6px; }}
        """)
        self.doc_browser.setStyleSheet(f"background-color: {bg}; color: {fg};")

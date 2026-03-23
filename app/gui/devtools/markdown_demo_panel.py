"""
Interne Markdown-Demo-Prüfstation: gleiche Pipeline wie Produktion (Chat/Hilfe).

Kein eigener Parser — nur UI, Sample-Laden und Aufruf von render_markdown / render_segments.
"""

from __future__ import annotations

from collections import Counter

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.gui.components.markdown_widgets import MarkdownDocumentView, MarkdownMessageWidget
from app.gui.devtools.markdown_demo_samples import (
    MARKDOWN_DEMO_SAMPLES,
    load_sample_text,
)
from app.gui.shared.markdown import RenderOptions, render_markdown, render_segments
from app.gui.shared.markdown.markdown_segment_types import AsciiBlockSegment, CodeBlockSegment
from app.gui.shared.markdown.markdown_types import RenderTarget


class MarkdownDemoPanel(QWidget):
    """
    Quelle links (Datei / bearbeitbar), Vorschau rechts: Hilfe- und Chat-Target nebeneinander.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._current_sample_id: str = MARKDOWN_DEMO_SAMPLES[0].sample_id
        self._setup_ui()
        self._wire_signals()
        self._select_first_sample()
        if not self._raw.toPlainText().strip():
            self._reload_from_disk()

    def _setup_ui(self) -> None:
        root = QHBoxLayout(self)
        root.setContentsMargins(12, 12, 12, 12)
        root.setSpacing(8)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        root.addWidget(splitter, 1)

        # --- Links: Auswahl + Quelle + Diagnose ---
        left = QWidget()
        left_l = QVBoxLayout(left)
        left_l.setContentsMargins(0, 0, 0, 0)
        left_l.setSpacing(8)

        banner = QLabel(
            "<b>Markdown-Prüfstation</b> (intern) — gleiche Pipeline wie Chat & Hilfe. "
            "Nicht für Endnutzer gedacht."
        )
        banner.setWordWrap(True)
        banner.setObjectName("markdownDemoBanner")
        left_l.addWidget(banner)

        left_l.addWidget(QLabel("Beispiel:"))
        self._sample_list = QListWidget()
        self._sample_list.setObjectName("markdownDemoSampleList")
        for s in MARKDOWN_DEMO_SAMPLES:
            it = QListWidgetItem(s.title)
            it.setData(Qt.ItemDataRole.UserRole, s.sample_id)
            self._sample_list.addItem(it)
        left_l.addWidget(self._sample_list, 1)

        self._edit_source = QCheckBox("Quelltext bearbeiten (lokale Änderungen)")
        left_l.addWidget(self._edit_source)

        self._raw = QPlainTextEdit()
        self._raw.setObjectName("markdownDemoRaw")
        self._raw.setReadOnly(True)
        self._raw.setPlaceholderText("Rohtext …")
        left_l.addWidget(self._raw, 2)

        btn_row = QHBoxLayout()
        self._btn_reload = QPushButton("Neu laden (Datei)")
        self._btn_reload.setToolTip("Verwirft lokale Änderungen und lädt die .md-Datei erneut.")
        self._btn_refresh = QPushButton("Rendering aktualisieren")
        self._btn_refresh.setToolTip("Wendet aktuellen Quelltext auf beide Vorschauen an.")
        btn_row.addWidget(self._btn_reload)
        btn_row.addWidget(self._btn_refresh)
        left_l.addLayout(btn_row)

        diag_box = QGroupBox("Render-Info (Pipeline)")
        diag_l = QVBoxLayout(diag_box)
        self._diag = QPlainTextEdit()
        self._diag.setReadOnly(True)
        self._diag.setMaximumHeight(140)
        self._diag.setPlaceholderText("Diagnose …")
        diag_l.addWidget(self._diag)
        left_l.addWidget(diag_box)

        splitter.addWidget(left)

        # --- Rechts: Vorschau Hilfe | Chat ---
        right = QWidget()
        right_l = QVBoxLayout(right)
        right_l.setContentsMargins(0, 0, 0, 0)
        tabs = QTabWidget()
        tabs.setObjectName("markdownDemoPreviewTabs")

        help_tab = QWidget()
        ht = QVBoxLayout(help_tab)
        ht.setContentsMargins(0, 0, 0, 0)
        self._help_preview = MarkdownDocumentView()
        self._help_preview.setObjectName("markdownDemoHelpPreview")
        ht.addWidget(self._help_preview)
        tabs.addTab(help_tab, "Vorschau (Hilfe)")

        chat_tab = QWidget()
        ct = QVBoxLayout(chat_tab)
        ct.setContentsMargins(0, 0, 0, 0)
        chat_row = QHBoxLayout()
        chat_row.addStretch(1)
        chat_inner = QFrame()
        chat_inner.setObjectName("markdownDemoChatFrame")
        chat_inner.setMaximumWidth(560)
        chat_inner_l = QVBoxLayout(chat_inner)
        chat_inner_l.setContentsMargins(8, 8, 8, 8)
        self._chat_preview = MarkdownMessageWidget()
        self._chat_preview.setObjectName("markdownDemoChatPreview")
        chat_inner_l.addWidget(self._chat_preview)
        chat_row.addWidget(chat_inner, 0, Qt.AlignmentFlag.AlignTop)
        chat_row.addStretch(1)
        ct.addLayout(chat_row)
        ct.addStretch(1)
        hint = QLabel(
            "Schmale Spalte simuliert Chat-Bubble — RenderTarget.CHAT_BUBBLE (Zeilenumbrüche wie im Chat)."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #64748b; font-size: 11px;")
        ct.addWidget(hint)
        tabs.addTab(chat_tab, "Vorschau (Chat)")

        right_l.addWidget(tabs, 1)
        splitter.addWidget(right)
        splitter.setSizes([340, 720])

    def _wire_signals(self) -> None:
        self._sample_list.currentItemChanged.connect(self._on_sample_changed)
        self._btn_reload.clicked.connect(self._reload_from_disk)
        self._btn_refresh.clicked.connect(self._refresh_previews)
        self._edit_source.toggled.connect(self._on_edit_toggled)

    def _on_edit_toggled(self, on: bool) -> None:
        self._raw.setReadOnly(not on)

    def _select_first_sample(self) -> None:
        self._sample_list.setCurrentRow(0)

    def _on_sample_changed(
        self, current: QListWidgetItem | None, _previous: QListWidgetItem | None
    ) -> None:
        if not current:
            return
        sid = current.data(Qt.ItemDataRole.UserRole)
        if sid:
            self._current_sample_id = sid
            self._reload_from_disk()

    def _reload_from_disk(self) -> None:
        text = load_sample_text(self._current_sample_id)
        self._raw.setPlainText(text)
        self._refresh_previews()

    def _refresh_previews(self) -> None:
        text = self._raw.toPlainText()
        self._help_preview.set_markdown(text)
        self._chat_preview.set_markdown(text)
        self._update_diagnostics(text)

    def _update_diagnostics(self, text: str) -> None:
        r_help = render_markdown(
            text or "",
            RenderOptions(target=RenderTarget.HELP_BROWSER, promote_ascii=True),
        )
        segs = render_segments(text or "", promote_ascii=True)
        kinds = Counter(s.kind for s in segs)
        n_code = sum(1 for s in segs if isinstance(s, CodeBlockSegment))
        n_ascii = sum(1 for s in segs if isinstance(s, AsciiBlockSegment))
        kind_lines = "\n".join(f"  {k}: {v}" for k, v in sorted(kinds.items()))
        self._diag.setPlainText(
            f"ContentProfile: {r_help.profile.name}\n"
            f"RenderMode: {r_help.mode.name}\n"
            f"Segmente (gesamt): {len(segs)}\n"
            f"  code_block: {n_code}\n"
            f"  ascii_block: {n_ascii}\n"
            f"Segmentarten:\n{kind_lines or '  —'}"
        )


class MarkdownDemoWorkspace(QWidget):
    """Runtime / Debug — Workspace-Eintrag für die Markdown-Prüfstation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("rd_markdown_demoWorkspace")
        self._inspector_host = None
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(MarkdownDemoPanel(self))

    @property
    def workspace_id(self) -> str:
        return "rd_markdown_demo"

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        self._inspector_host = inspector_host
        inspector_host.clear_content()

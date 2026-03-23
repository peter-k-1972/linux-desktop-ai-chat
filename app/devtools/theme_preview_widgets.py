"""
Komponenten-Vorschau für den Theme-Visualizer.

Farben ausschließlich über ThemeManager / ThemeTokenId — keine Demo-Palette.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMenu,
    QMessageBox,
    QPlainTextEdit,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QSlider,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QTextBrowser,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.gui.themes.canonical_token_ids import ThemeTokenId


class SupportsThemeColors(Protocol):
    """Minimale Schnittstelle für Token-Farben (ThemeManager oder eingebetteter Kontext)."""

    def color(self, token: str) -> str: ...


@dataclass
class PreviewFlags:
    show_disabled: bool = True
    show_focus: bool = True
    show_selection: bool = True
    debug_labels: bool = False
    token_names: bool = False


def _solid(fg: str, bg: str, border: str, radius: str = "6px", pad: str = "6px 10px") -> str:
    return (
        f"color: {fg}; background-color: {bg}; border: 1px solid {border}; "
        f"border-radius: {radius}; padding: {pad};"
    )


def _lbl(_colors: SupportsThemeColors, text: str, token_hint: str | None, flags: PreviewFlags) -> QLabel:
    w = QLabel(text)
    if flags.token_names and token_hint:
        w.setToolTip(token_hint)
    return w


class ThemeComponentPreview(QWidget):
    """Scroll-Inhalt: typische UI-Bausteine mit aktuellem Theme."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._root = QVBoxLayout(self)
        self._root.setSpacing(12)
        self._focus_line: QLineEdit | None = None
        self._selection_list: QListWidget | None = None

    def refresh(self, colors: SupportsThemeColors, flags: PreviewFlags) -> None:
        while self._root.count():
            item = self._root.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._focus_line = None
        self._selection_list = None

        t = colors.color
        bg_app = t(ThemeTokenId.BG_APP)
        surface = t(ThemeTokenId.BG_SURFACE)
        elevated = t(ThemeTokenId.BG_SURFACE_ELEVATED)
        overlay = t(ThemeTokenId.BG_OVERLAY)
        border = t(ThemeTokenId.BORDER_DEFAULT)
        subtle = t(ThemeTokenId.BORDER_SUBTLE)
        fg = t(ThemeTokenId.FG_PRIMARY)
        fg_sec = t(ThemeTokenId.FG_SECONDARY)
        fg_muted = t(ThemeTokenId.FG_MUTED)
        fg_dis = t(ThemeTokenId.FG_DISABLED)
        fg_link = t(ThemeTokenId.FG_LINK)
        fg_inv = t(ThemeTokenId.FG_INVERSE)

        self._root.addWidget(self._section_surfaces(colors, flags, bg_app, surface, elevated, overlay, border))
        self._root.addWidget(self._section_text(colors, flags, fg, fg_sec, fg_muted, fg_dis, fg_link, fg_inv))
        self._root.addWidget(self._section_buttons(colors, flags))
        self._root.addWidget(self._section_inputs(colors, flags))
        self._root.addWidget(self._section_nav_tabs(colors, flags))
        self._root.addWidget(self._section_tables_lists(colors, flags))
        self._root.addWidget(self._section_markdown_chat(colors, flags))
        self._root.addWidget(self._section_status(colors, flags))
        self._root.addWidget(self._section_misc(colors, flags, subtle))
        self._root.addStretch(1)

        if flags.show_focus and self._focus_line:
            self._focus_line.setFocus(Qt.FocusReason.OtherFocusReason)

        if flags.show_selection and self._selection_list:
            self._selection_list.setCurrentRow(0)

    def _section_surfaces(
        self,
        colors: SupportsThemeColors,
        flags: PreviewFlags,
        bg_app: str,
        surface: str,
        elevated: str,
        overlay: str,
        border: str,
    ) -> QGroupBox:
        box = QGroupBox("App-Flächen")
        lay = QVBoxLayout(box)
        if flags.debug_labels:
            lay.addWidget(_lbl(colors, "DEBUG: Surfaces", "ThemeTokenId.BG_*", flags))
        grid = QGridLayout()
        samples = [
            ("App", bg_app, ThemeTokenId.BG_APP),
            ("Surface / Card", surface, ThemeTokenId.BG_SURFACE),
            ("Elevated", elevated, ThemeTokenId.BG_SURFACE_ELEVATED),
            ("Overlay", overlay, ThemeTokenId.BG_OVERLAY),
        ]
        for i, (name, col, tid) in enumerate(samples):
            f = QFrame()
            f.setMinimumHeight(48)
            f.setStyleSheet(f"background-color: {col}; border: 1px solid {border}; border-radius: 6px;")
            if flags.token_names:
                f.setToolTip(tid)
            grid.addWidget(QLabel(name), i, 0)
            grid.addWidget(f, i, 1)
        lay.addLayout(grid)

        dlg = QFrame()
        dlg.setStyleSheet(
            f"QFrame {{ background-color: {surface}; border: 1px solid {border}; border-radius: 8px; padding: 8px; }}"
        )
        dl = QVBoxLayout(dlg)
        dl.addWidget(QLabel("Dialog-Karte (simuliert)"))
        dl.addWidget(QLabel("Inhalt mit Standard-Stylesheet"))
        lay.addWidget(dlg)
        return box

    def _section_text(
        self,
        colors: SupportsThemeColors,
        flags: PreviewFlags,
        fg: str,
        fg_sec: str,
        fg_muted: str,
        fg_dis: str,
        fg_link: str,
        fg_inv: str,
    ) -> QGroupBox:
        box = QGroupBox("Textbeispiele")
        lay = QVBoxLayout(box)
        p = QLabel("Primary Text")
        p.setStyleSheet(f"color: {fg}; background: transparent;")
        if flags.token_names:
            p.setToolTip(ThemeTokenId.FG_PRIMARY)
        lay.addWidget(p)
        s = QLabel("Secondary Text")
        s.setStyleSheet(f"color: {fg_sec};")
        if flags.token_names:
            s.setToolTip(ThemeTokenId.FG_SECONDARY)
        lay.addWidget(s)
        m = QLabel("Muted Text")
        m.setStyleSheet(f"color: {fg_muted};")
        if flags.token_names:
            m.setToolTip(ThemeTokenId.FG_MUTED)
        lay.addWidget(m)
        d = QLabel("Disabled Text")
        d.setStyleSheet(f"color: {fg_dis};")
        d.setEnabled(False)
        if flags.token_names:
            d.setToolTip(ThemeTokenId.FG_DISABLED)
        lay.addWidget(d)
        link = QLabel('<a href="#">Link Text</a>')
        link.setOpenExternalLinks(False)
        link.setStyleSheet(f"color: {fg_link};")
        if flags.token_names:
            link.setToolTip(ThemeTokenId.FG_LINK)
        lay.addWidget(link)
        inv_bg = colors.color(ThemeTokenId.STATE_ACCENT)
        inv = QLabel("Inverse on accent strip")
        inv.setStyleSheet(_solid(fg_inv, inv_bg, inv_bg))
        if flags.token_names:
            inv.setToolTip(f"{ThemeTokenId.FG_INVERSE} auf {ThemeTokenId.STATE_ACCENT}")
        lay.addWidget(inv)
        return box

    def _section_buttons(self, colors: SupportsThemeColors, flags: PreviewFlags) -> QGroupBox:
        box = QGroupBox("Buttons")
        lay = QVBoxLayout(box)
        t = colors.color
        bd = t(ThemeTokenId.BORDER_DEFAULT)

        row1 = QHBoxLayout()
        pri = QPushButton("Primary")
        pri.setStyleSheet(
            f"QPushButton {{ {_solid(t(ThemeTokenId.BUTTON_PRIMARY_FG), t(ThemeTokenId.BUTTON_PRIMARY_BG), bd)} }}\n"
            f"QPushButton:hover {{ background-color: {t(ThemeTokenId.BUTTON_PRIMARY_HOVER)}; }}"
        )
        if flags.token_names:
            pri.setToolTip(ThemeTokenId.BUTTON_PRIMARY_BG)
        row1.addWidget(pri)

        sec = QPushButton("Secondary")
        sec.setStyleSheet(
            f"QPushButton {{ {_solid(t(ThemeTokenId.BUTTON_SECONDARY_FG), t(ThemeTokenId.BUTTON_SECONDARY_BG), t(ThemeTokenId.BUTTON_SECONDARY_BORDER))} }}\n"
            f"QPushButton:hover {{ background-color: {t(ThemeTokenId.BUTTON_SECONDARY_HOVER)}; }}"
        )
        row1.addWidget(sec)

        ghost = QPushButton("Ghost")
        ghost.setStyleSheet(
            f"QPushButton {{ color: {t(ThemeTokenId.FG_PRIMARY)}; background: transparent; border: 1px dashed {bd}; "
            f"border-radius: 6px; padding: 6px 10px; }}"
        )
        row1.addWidget(ghost)
        lay.addLayout(row1)

        sim = QHBoxLayout()
        for label, bg_key in (
            ("Hover-Farbe", ThemeTokenId.BUTTON_PRIMARY_HOVER),
            ("Pressed-Farbe", ThemeTokenId.BUTTON_PRIMARY_PRESSED),
        ):
            b = QPushButton(label)
            b.setStyleSheet(_solid(t(ThemeTokenId.BUTTON_PRIMARY_FG), t(bg_key), bd))
            if flags.token_names:
                b.setToolTip(bg_key)
            sim.addWidget(b)
        lay.addLayout(sim)

        row2 = QHBoxLayout()
        dis = QPushButton("Disabled")
        dis.setEnabled(False)
        row2.addWidget(dis)
        if flags.show_focus:
            foc = QPushButton("Fokus testen")
            foc.setObjectName("themeVizFocusButton")
            row2.addWidget(foc)
        lay.addLayout(row2)
        return box

    def _section_inputs(self, colors: SupportsThemeColors, flags: PreviewFlags) -> QGroupBox:
        box = QGroupBox("Inputs")
        lay = QVBoxLayout(box)
        le = QLineEdit()
        le.setPlaceholderText("Search / LineEdit mit Placeholder")
        lay.addWidget(le)

        pte = QPlainTextEdit()
        pte.setPlainText("QPlainTextEdit\nzweite Zeile")
        pte.setMaximumHeight(72)
        lay.addWidget(pte)

        cb = QComboBox()
        cb.addItems(["ComboBox", "Eintrag B", "Eintrag C"])
        lay.addWidget(cb)

        if flags.show_disabled:
            le_d = QLineEdit("Disabled Input")
            le_d.setEnabled(False)
            lay.addWidget(le_d)

        if flags.show_focus:
            fe = QLineEdit("Fokus-Ziel — Tab")
            self._focus_line = fe
            lay.addWidget(fe)
        return box

    def _section_nav_tabs(self, colors: SupportsThemeColors, flags: PreviewFlags) -> QGroupBox:
        box = QGroupBox("Navigation & Tabs")
        lay = QVBoxLayout(box)
        t = colors.color

        side = QHBoxLayout()
        for label, bg, fg, tip in (
            ("Sidebar normal", t(ThemeTokenId.NAV_BG), t(ThemeTokenId.NAV_FG), ThemeTokenId.NAV_BG),
            ("Sidebar hover", t(ThemeTokenId.NAV_HOVER_BG), t(ThemeTokenId.NAV_FG), ThemeTokenId.NAV_HOVER_BG),
            ("Sidebar aktiv", t(ThemeTokenId.NAV_ACTIVE_BG), t(ThemeTokenId.NAV_ACTIVE_FG), ThemeTokenId.NAV_ACTIVE_BG),
        ):
            lab = QLabel(label)
            lab.setStyleSheet(_solid(fg, bg, t(ThemeTokenId.BORDER_SUBTLE)))
            if flags.token_names:
                lab.setToolTip(tip)
            side.addWidget(lab)
        lay.addLayout(side)

        tabs = QTabWidget()
        tabs.addTab(QLabel("Tab-Inhalt A"), "Tab A")
        tabs.addTab(QLabel("Tab-Inhalt B"), "Tab B")
        if flags.token_names:
            tabs.setToolTip(f"{ThemeTokenId.TAB_BG} / {ThemeTokenId.TAB_ACTIVE_BG}")
        lay.addWidget(tabs)
        return box

    def _section_tables_lists(self, colors: SupportsThemeColors, flags: PreviewFlags) -> QGroupBox:
        box = QGroupBox("Tabellen, Listen, Tree")
        lay = QVBoxLayout(box)

        tbl = QTableWidget(4, 3)
        tbl.setHorizontalHeaderLabels(["Spalte 1", "Spalte 2", "Spalte 3"])
        for r in range(4):
            for c in range(3):
                tbl.setItem(r, c, QTableWidgetItem(f"Zelle {r},{c}"))
        tbl.resizeColumnsToContents()
        tbl.setMaximumHeight(160)
        lay.addWidget(tbl)

        lw = QListWidget()
        for i in range(5):
            lw.addItem(QListWidgetItem(f"Listenzeile {i+1}"))
        lw.setMaximumHeight(100)
        if flags.show_selection:
            self._selection_list = lw
        lay.addWidget(lw)

        tw = QTreeWidget()
        tw.setHeaderLabels(["Baum", "Wert"])
        root = QTreeWidgetItem(["Wurzel", "1"])
        QTreeWidgetItem(root, ["Kind", "2"])
        tw.addTopLevelItem(root)
        tw.expandAll()
        tw.setMaximumHeight(110)
        lay.addWidget(tw)
        return box

    def _section_markdown_chat(self, colors: SupportsThemeColors, flags: PreviewFlags) -> QGroupBox:
        box = QGroupBox("Chat & Markdown (HTML-Vorschau)")
        lay = QVBoxLayout(box)
        t = colors.color

        bubbles = QHBoxLayout()
        for title, bg, fg, br in (
            ("User", t(ThemeTokenId.CHAT_USER_BG), t(ThemeTokenId.CHAT_USER_FG), t(ThemeTokenId.CHAT_USER_BORDER)),
            (
                "Assistant",
                t(ThemeTokenId.CHAT_ASSISTANT_BG),
                t(ThemeTokenId.CHAT_ASSISTANT_FG),
                t(ThemeTokenId.CHAT_ASSISTANT_BORDER),
            ),
            ("System", t(ThemeTokenId.CHAT_SYSTEM_BG), t(ThemeTokenId.CHAT_SYSTEM_FG), t(ThemeTokenId.BORDER_SUBTLE)),
        ):
            lab = QLabel(f"{title} Bubble")
            lab.setWordWrap(True)
            lab.setStyleSheet(_solid(fg, bg, br))
            bubbles.addWidget(lab)
        lay.addLayout(bubbles)

        body = t(ThemeTokenId.MARKDOWN_BODY)
        head = t(ThemeTokenId.MARKDOWN_HEADING)
        link = t(ThemeTokenId.MARKDOWN_LINK)
        quote = t(ThemeTokenId.MARKDOWN_QUOTE)
        qbd = t(ThemeTokenId.MARKDOWN_QUOTE_BORDER)
        icb = t(ThemeTokenId.MARKDOWN_INLINE_CODE_BG)
        icf = t(ThemeTokenId.MARKDOWN_INLINE_CODE_FG)
        cbb = t(ThemeTokenId.MARKDOWN_CODEBLOCK_BG)
        cbf = t(ThemeTokenId.MARKDOWN_CODEBLOCK_FG)
        thbd = t(ThemeTokenId.MARKDOWN_TABLE_BORDER)
        thh = t(ThemeTokenId.MARKDOWN_TABLE_HEADER_BG)
        surf = t(ThemeTokenId.BG_SURFACE)

        html = f"""
        <div style="background:{surf}; color:{body}; padding:8px; border-radius:6px;">
          <h3 style="color:{head}; margin:0 0 8px 0;">Überschrift</h3>
          <p>Body-Text mit <a style="color:{link};" href="#">Link</a>.</p>
          <blockquote style="border-left: 3px solid {qbd}; color:{quote}; margin:8px 0; padding-left:8px;">
            Zitatblock
          </blockquote>
          <p>Inline <code style="background:{icb}; color:{icf}; padding:2px 4px; border-radius:4px;">code</code></p>
          <pre style="background:{cbb}; color:{cbf}; padding:8px; border-radius:6px;">Codeblock\nZeile 2</pre>
          <table style="border-collapse:collapse; width:100%; margin-top:8px;">
            <tr style="background:{thh};"><th style="border:1px solid {thbd};">A</th><th style="border:1px solid {thbd};">B</th></tr>
            <tr><td style="border:1px solid {thbd};">1</td><td style="border:1px solid {thbd};">2</td></tr>
          </table>
        </div>
        """
        browser = QTextBrowser()
        browser.setHtml(html.strip())
        browser.setOpenExternalLinks(False)
        browser.setMaximumHeight(220)
        if flags.debug_labels:
            browser.setToolTip("Markdown-Tokens via HTML inline styles")
        lay.addWidget(browser)
        return box

    def _section_status(self, colors: SupportsThemeColors, flags: PreviewFlags) -> QGroupBox:
        box = QGroupBox("Status & Feedback")
        lay = QVBoxLayout(box)
        t = colors.color
        row = QHBoxLayout()
        for label, bg, fg in (
            ("Success", t(ThemeTokenId.BADGE_SUCCESS_BG), t(ThemeTokenId.BADGE_SUCCESS_FG)),
            ("Warning", t(ThemeTokenId.BADGE_WARNING_BG), t(ThemeTokenId.BADGE_WARNING_FG)),
            ("Error", t(ThemeTokenId.BADGE_ERROR_BG), t(ThemeTokenId.BADGE_ERROR_FG)),
            ("Info", t(ThemeTokenId.BADGE_INFO_BG), t(ThemeTokenId.BADGE_INFO_FG)),
        ):
            lab = QLabel(label)
            lab.setStyleSheet(_solid(fg, bg, t(ThemeTokenId.BORDER_SUBTLE), pad="4px 8px"))
            row.addWidget(lab)
        lay.addLayout(row)

        err_bg = t(ThemeTokenId.STATE_ERROR)
        msg = QLabel("Alert-Simulation: Aktion fehlgeschlagen.")
        msg.setStyleSheet(_solid(t(ThemeTokenId.FG_INVERSE), err_bg, err_bg))
        lay.addWidget(msg)

        dots = QHBoxLayout()
        for label, col, tip in (
            ("●", t(ThemeTokenId.STATE_SUCCESS), "success"),
            ("●", t(ThemeTokenId.STATE_WARNING), "warning"),
            ("●", t(ThemeTokenId.STATE_INFO), "info"),
        ):
            d = QLabel(label)
            d.setStyleSheet(f"color:{col}; font-size:18px;")
            d.setToolTip(tip)
            dots.addWidget(d)
        dots.addStretch(1)
        lay.addLayout(dots)
        return box

    def _section_misc(self, colors: SupportsThemeColors, flags: PreviewFlags, subtle: str) -> QGroupBox:
        box = QGroupBox("Spezial & Controls")
        lay = QVBoxLayout(box)

        tb = QPushButton("Menü")
        menu = QMenu(tb)
        menu.addAction("Eintrag 1")
        menu.addAction("Eintrag 2")
        tb.setMenu(menu)
        lay.addWidget(tb)

        tip_btn = QPushButton("Tooltip-Ziel")
        tip_btn.setToolTip("Beispiel-Tooltip-Text für QA")
        lay.addWidget(tip_btn)

        msg_btn = QPushButton("QMessageBox…")
        msg_btn.clicked.connect(
            lambda: QMessageBox.information(
                self.window(),
                "MessageBox-Vorschau",
                "System-Dialog mit aktuellem Qt-Style.",
            )
        )
        lay.addWidget(msg_btn)

        pb = QProgressBar()
        pb.setRange(0, 100)
        pb.setValue(62)
        lay.addWidget(pb)

        row = QHBoxLayout()
        row.addWidget(QCheckBox("Checkbox"))
        row.addWidget(QRadioButton("Radio"))
        s = QSlider(Qt.Orientation.Horizontal)
        s.setRange(0, 100)
        s.setValue(40)
        row.addWidget(s)
        lay.addLayout(row)

        if flags.debug_labels:
            lay.addWidget(QLabel(f"Border subtle: {subtle}"))
        return box

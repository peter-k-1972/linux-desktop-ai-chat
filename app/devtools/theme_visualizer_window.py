"""
Theme-Visualizer-Hauptfenster — QA/Dev, nutzt ThemeRegistry + Loader.

- Standalone (tools/theme_visualizer.py): globales Theme via ThemeManager.
- Eingebettet (GUI-Shell): Vorschau nur auf diesem Fenster; Shell-Theme unverändert.
"""

from __future__ import annotations

import re
from collections.abc import Callable

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication, QMouseEvent
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QScrollArea,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.devtools.theme_contrast import (
    DEFAULT_CONTRAST_PAIRS,
    ContrastLevel,
    contrast_hint_for_fg_on_bg,
    evaluate_pair,
    token_value,
)
from app.devtools.theme_preview_widgets import PreviewFlags, ThemeComponentPreview
from app.devtools.theme_token_groups import TOKEN_GROUPS
from app.gui.themes.canonical_token_ids import ThemeTokenId, flat_key
from app.gui.themes.definition import ThemeDefinition
from app.gui.themes.loader import load_stylesheet
from app.gui.themes.registry import ThemeRegistry


def _is_probable_color_hex(s: str) -> bool:
    s = s.strip()
    return bool(re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", s))


class _ManagerPreviewContext:
    """Globales Theme (Singleton ThemeManager)."""

    def __init__(self) -> None:
        from app.gui.themes import get_theme_manager

        self._mgr = get_theme_manager()

    def color(self, token: str) -> str:
        return self._mgr.color(token)

    def get_tokens(self) -> dict[str, str]:
        return self._mgr.get_tokens()

    def list_themes(self) -> list[tuple[str, str]]:
        return self._mgr.list_themes()

    def get_current_id(self) -> str:
        return self._mgr.get_current_id()

    def apply_theme_id(self, theme_id: str, window: QWidget | None) -> bool:
        return self._mgr.set_theme(theme_id)


class _EmbeddedPreviewContext:
    """Lokale Theme-Vorschau ohne ThemeManager.set_theme (eigenes Registry + Fenster-QSS)."""

    def __init__(self) -> None:
        self._registry = ThemeRegistry()
        self._theme_id = ""
        self._theme: ThemeDefinition | None = None
        self._sync_initial_from_app()

    def _sync_initial_from_app(self) -> None:
        from app.gui.themes import get_theme_manager

        mgr = get_theme_manager()
        tid = mgr.get_current_id()
        t = self._registry.get(tid) or self._registry.get("light_default")
        if t:
            self._theme_id = t.id
            self._theme = t

    def color(self, token: str) -> str:
        tokens = self.get_tokens()
        flat = flat_key(token) if "." in token else token
        return tokens.get(flat) or tokens.get(token, "")

    def get_tokens(self) -> dict[str, str]:
        if not self._theme:
            return {}
        return self._theme.get_tokens_dict()

    def list_themes(self) -> list[tuple[str, str]]:
        return self._registry.list_themes()

    def get_current_id(self) -> str:
        return self._theme_id

    def apply_theme_id(self, theme_id: str, window: QWidget | None) -> bool:
        t = self._registry.get(theme_id)
        if not t or window is None:
            return False
        self._theme_id = theme_id
        self._theme = t
        window.setStyleSheet(load_stylesheet(t))
        return True


class _TokenSwatchRow(QWidget):
    """Zeile mit Farbfeld; Klick kopiert und informiert den Inspektor."""

    pressed = Signal(str, str, str, str, str)  # canonical, flat, value, hint, theme_id

    def __init__(
        self,
        canonical: str,
        flat: str,
        value: str,
        missing: bool,
        hint: str,
        stripe_a: str,
        stripe_b: str,
        chip_border: str,
        error_fg: str,
        get_theme_id: Callable[[], str],
    ) -> None:
        super().__init__()
        self._canonical = canonical
        self._flat = flat
        self._value = value
        self._hint = hint
        self._missing = missing
        self._get_theme_id = get_theme_id

        hl = QHBoxLayout(self)
        hl.setContentsMargins(0, 2, 0, 2)

        self._chip = QFrame()
        self._chip.setFixedSize(36, 22)
        self._chip.setFrameShape(QFrame.Shape.Box)
        if missing:
            self._chip.setStyleSheet(
                f"background: repeating-linear-gradient(45deg,{stripe_a},{stripe_a} 4px,{stripe_b} 4px,{stripe_b} 8px);"
                f" border: 1px solid {chip_border};"
            )
            self._chip.setToolTip("Fehlend oder kein Hex — prüfe Theme / Spec-Ableitung")
        else:
            self._chip.setStyleSheet(f"background-color: {value}; border: 1px solid {chip_border};")

        self._name_lbl = QLabel(canonical)
        self._name_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._val_lbl = QLabel(value or "—")
        self._val_lbl.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self._hint_lbl = QLabel(hint)
        if missing:
            self._name_lbl.setStyleSheet(f"color: {error_fg}; font-weight: 600;")

        hl.addWidget(self._chip)
        hl.addWidget(self._name_lbl, 2)
        hl.addWidget(self._val_lbl, 1)
        hl.addWidget(self._hint_lbl, 1)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.pressed.emit(self._canonical, self._flat, self._value, self._hint, self._get_theme_id())
        super().mousePressEvent(event)


class ThemeVisualizerWindow(QWidget):
    """Dreispaltiges Dev-Tool: Steuerung | Tokens | Komponenten."""

    def __init__(self, parent: QWidget | None = None, embed_in_app: bool = False) -> None:
        super().__init__(parent)
        self._embed_in_app = embed_in_app
        self._ctx: _ManagerPreviewContext | _EmbeddedPreviewContext
        if embed_in_app:
            self._ctx = _EmbeddedPreviewContext()
        else:
            self._ctx = _ManagerPreviewContext()

        self.setObjectName("themeVisualizerRoot")
        self.setWindowTitle("Theme Visualizer (Dev)")
        self.resize(1400, 900)
        if embed_in_app:
            self.setWindowFlag(Qt.WindowType.Window, True)

        self._inspector = QPlainTextEdit()
        self._inspector.setReadOnly(True)
        self._token_scroll_inner = QWidget()
        self._token_layout = QVBoxLayout(self._token_scroll_inner)
        self._contrast_list = QListWidget()
        self._contrast_list.setObjectName("themeVisualizerContrastList")

        self._theme_combo = QComboBox()
        self._theme_combo.setObjectName("themeVisualizerThemeCombo")
        self._profile_combo = QComboBox()
        self._profile_combo.addItem("— (kein Farbprofil)", "")
        self._profile_combo.setEnabled(False)
        self._profile_combo.setToolTip("Reserviert für künftige color_profile_id")

        self._chk_disabled = QCheckBox("Disabled-Zustände")
        self._chk_disabled.setChecked(True)
        self._chk_focus = QCheckBox("Fokus-Zustände")
        self._chk_focus.setChecked(True)
        self._chk_selection = QCheckBox("Selektion")
        self._chk_selection.setChecked(True)
        self._chk_debug = QCheckBox("Debug-Labels")
        self._chk_token_names = QCheckBox("Token-Namen (Tooltips)")

        self._preview = ThemeComponentPreview()
        self._preview_scroll = QScrollArea()
        self._preview_scroll.setObjectName("themeVisualizerPreviewScroll")
        self._preview_scroll.setWidgetResizable(True)
        self._preview_scroll.setWidget(self._preview)

        self._build_layout()
        self._populate_theme_combo()
        self._sync_combo_to_context()
        self._wire_signals()

        tid = self._theme_combo.currentData()
        if isinstance(tid, str) and tid:
            self._ctx.apply_theme_id(tid, self)
        self.refresh_all()

    def _build_layout(self) -> None:
        main = QHBoxLayout(self)
        splitter = QSplitter(Qt.Orientation.Horizontal)
        main.addWidget(splitter)

        left = QWidget()
        left_l = QVBoxLayout(left)
        left_l.addWidget(QLabel("<b>Theme</b>"))
        left_l.addWidget(self._theme_combo)
        left_l.addWidget(QLabel("Farbprofil"))
        left_l.addWidget(self._profile_combo)

        row_btn = QHBoxLayout()
        self._btn_refresh = QPushButton("Aktualisieren")
        self._btn_reload = QPushButton("QSS neu anwenden")
        row_btn.addWidget(self._btn_refresh)
        row_btn.addWidget(self._btn_reload)
        left_l.addLayout(row_btn)

        self._btn_shot = QPushButton("Screenshot (Vorschau)…")
        left_l.addWidget(self._btn_shot)

        left_l.addWidget(QLabel("<b>QA-Optionen</b>"))
        for w in (
            self._chk_disabled,
            self._chk_focus,
            self._chk_selection,
            self._chk_debug,
            self._chk_token_names,
        ):
            left_l.addWidget(w)

        if self._embed_in_app:
            hint = QLabel(
                "<i>Eingebettet: Theme-Wechsel gilt nur für dieses Fenster; die Shell bleibt unverändert.</i>"
            )
            hint.setWordWrap(True)
            left_l.addWidget(hint)

        left_l.addWidget(QLabel("<b>Kontrast (Paare)</b>"))
        self._contrast_list.setMaximumHeight(220)
        left_l.addWidget(self._contrast_list)

        left_l.addWidget(QLabel("<b>Token-Inspektor</b>"))
        self._inspector.setMaximumHeight(120)
        self._inspector.setPlaceholderText("Klick auf eine Token-Zeile: Name, Wert, Kontrast …")
        left_l.addWidget(self._inspector)

        self._btn_copy = QPushButton("Inspektor in Zwischenablage")
        left_l.addWidget(self._btn_copy)
        left_l.addStretch(1)

        mid_scroll = QScrollArea()
        mid_scroll.setObjectName("themeVisualizerTokenScroll")
        mid_scroll.setWidgetResizable(True)
        mid_scroll.setWidget(self._token_scroll_inner)

        splitter.addWidget(left)
        splitter.addWidget(mid_scroll)
        splitter.addWidget(self._preview_scroll)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 1)
        splitter.setSizes([300, 520, 520])

    def _wire_signals(self) -> None:
        self._theme_combo.currentIndexChanged.connect(self._on_theme_changed)
        self._btn_refresh.clicked.connect(self.refresh_all)
        self._btn_reload.clicked.connect(self._reload_stylesheet)
        self._btn_shot.clicked.connect(self._export_screenshot)
        self._btn_copy.clicked.connect(self._copy_inspector)
        for c in (
            self._chk_disabled,
            self._chk_focus,
            self._chk_selection,
            self._chk_debug,
            self._chk_token_names,
        ):
            c.toggled.connect(self._on_flags_changed)

    def _on_flags_changed(self) -> None:
        self._preview.refresh(self._ctx, self._preview_flags())

    def _preview_flags(self) -> PreviewFlags:
        return PreviewFlags(
            show_disabled=self._chk_disabled.isChecked(),
            show_focus=self._chk_focus.isChecked(),
            show_selection=self._chk_selection.isChecked(),
            debug_labels=self._chk_debug.isChecked(),
            token_names=self._chk_token_names.isChecked(),
        )

    def _populate_theme_combo(self) -> None:
        self._theme_combo.blockSignals(True)
        self._theme_combo.clear()
        for tid, name in self._ctx.list_themes():
            self._theme_combo.addItem(f"{name} ({tid})", tid)
        self._theme_combo.blockSignals(False)

    def _sync_combo_to_context(self) -> None:
        tid = self._ctx.get_current_id()
        self._theme_combo.blockSignals(True)
        for i in range(self._theme_combo.count()):
            if self._theme_combo.itemData(i) == tid:
                self._theme_combo.setCurrentIndex(i)
                break
        self._theme_combo.blockSignals(False)

    def _on_theme_changed(self) -> None:
        tid = self._theme_combo.currentData()
        if isinstance(tid, str) and tid:
            self._ctx.apply_theme_id(tid, self)
            self.refresh_all()

    def _reload_stylesheet(self) -> None:
        tid = self._theme_combo.currentData()
        if isinstance(tid, str) and tid:
            self._ctx.apply_theme_id(tid, self)
        self.refresh_all()

    def apply_selected_theme(self) -> bool:
        """Öffentliche API für Tests: aktuelles Combo-Theme anwenden."""
        tid = self._theme_combo.currentData()
        if not isinstance(tid, str) or not tid:
            return False
        ok = self._ctx.apply_theme_id(tid, self)
        if ok:
            self.refresh_all()
        return ok

    def _export_screenshot(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Screenshot", "", "PNG (*.png)")
        if not path:
            return
        pix = self._preview_scroll.grab()
        if not pix.save(path, "PNG"):
            QMessageBox.warning(self, "Screenshot", "Speichern fehlgeschlagen.")

    def _copy_inspector(self) -> None:
        QGuiApplication.clipboard().setText(self._inspector.toPlainText())

    def refresh_all(self) -> None:
        self._rebuild_token_panel()
        self._rebuild_contrast_list()
        self._preview.refresh(self._ctx, self._preview_flags())

    def _theme_tokens(self) -> dict[str, str]:
        return self._ctx.get_tokens()

    def _rebuild_contrast_list(self) -> None:
        self._contrast_list.clear()
        tokens = self._theme_tokens()
        ok_c = QColor.fromString(self._ctx.color(ThemeTokenId.STATE_SUCCESS))
        warn_c = QColor.fromString(self._ctx.color(ThemeTokenId.STATE_WARNING))
        bad_c = QColor.fromString(self._ctx.color(ThemeTokenId.STATE_ERROR))
        for spec in DEFAULT_CONTRAST_PAIRS:
            ratio, level, extra = evaluate_pair(tokens, spec)
            fg = token_value(tokens, spec.fg_canonical)
            bg = token_value(tokens, spec.bg_canonical)
            if ratio is None:
                text = f"[{level.value}] {spec.label} — {extra}"
            else:
                text = f"[{level.value}] {spec.label} — {ratio:.2f}:1"
            item = QListWidgetItem(text)
            if level == ContrastLevel.OK:
                item.setForeground(ok_c)
            elif level == ContrastLevel.WARN:
                item.setForeground(warn_c)
            else:
                item.setForeground(bad_c)
            item.setToolTip(f"FG: {fg}\nBG: {bg}\nMin: {spec.minimum}:1")
            self._contrast_list.addItem(item)

    def _rebuild_token_panel(self) -> None:
        while self._token_layout.count():
            item = self._token_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        tokens = self._theme_tokens()
        surface = ThemeTokenId.BG_SURFACE
        stripe_a = self._ctx.color(ThemeTokenId.BORDER_STRONG)
        stripe_b = self._ctx.color(ThemeTokenId.BG_SURFACE_ALT)
        chip_border = self._ctx.color(ThemeTokenId.BORDER_DEFAULT)
        err_fg = self._ctx.color(ThemeTokenId.STATE_ERROR)
        get_tid = self._ctx.get_current_id

        for group in TOKEN_GROUPS:
            box = QFrame()
            box.setFrameShape(QFrame.Shape.StyledPanel)
            vl = QVBoxLayout(box)
            vl.addWidget(QLabel(f"<b>{group.title}</b>"))
            grid = QGridLayout()
            for row, cid in enumerate(group.token_ids):
                fk = flat_key(cid)
                raw = token_value(tokens, cid)
                missing = not raw or not _is_probable_color_hex(raw)
                hint = ""
                if not missing:
                    if cid.startswith("color.fg.") or "fg" in cid:
                        hint = contrast_hint_for_fg_on_bg(tokens, cid, surface, 4.5)
                    elif ".bg" in cid or "bg" in cid.split(".")[-1]:
                        hint = contrast_hint_for_fg_on_bg(tokens, ThemeTokenId.FG_PRIMARY, cid, 4.5)
                    else:
                        hint = "—"

                sw = _TokenSwatchRow(
                    cid,
                    fk,
                    raw,
                    missing,
                    hint,
                    stripe_a,
                    stripe_b,
                    chip_border,
                    err_fg,
                    get_tid,
                )
                sw.pressed.connect(self._on_swatch_pressed)
                grid.addWidget(sw, row, 0)
            vl.addLayout(grid)
            self._token_layout.addWidget(box)
        self._token_layout.addStretch(1)

    def _on_swatch_pressed(self, canonical: str, flat: str, value: str, hint: str, theme_id: str) -> None:
        mode = "eingebettet (nur dieses Fenster)" if self._embed_in_app else "global (ThemeManager)"
        self._inspector.setPlainText(
            f"Token (kanonisch): {canonical}\n"
            f"Flat-Key: {flat}\n"
            f"Wert: {value or '(leer)'}\n"
            f"Kontrast-Hinweis: {hint}\n"
            f"Aktives Vorschau-Theme: {theme_id}\n"
            f"Anwendungsmodus: {mode}\n"
            f"Quelle: built-in semantic profile / ThemeRegistry\n"
        )
        QGuiApplication.clipboard().setText(f"{canonical}\t{value}")

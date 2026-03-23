"""
PromptManagerPanel – Promptverwaltung als Studio-Panel.
Gestraffte UI: Kopfbereich, Aktionszeile, filterbare Liste, kompakte Metadaten, großer Inhaltsbereich.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPlainTextEdit,
    QPushButton,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QSplitter,
    QSizePolicy,
    QScrollArea,
    QFrame,
)
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from app.prompts import Prompt, PromptService, PROMPT_TYPES, PROMPT_CATEGORIES

from app.gui.shared.panel_constants import (
    _BUTTON_WIDTH_IF_FIT,
    _PROMPTS_PANEL_FIXED_WIDTH,
)


class PromptListWidget(QListWidget):
    """Filterbare Single-Selection-Liste der Prompts (radioähnlich)."""

    prompt_selected = Signal(object)

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.setObjectName("promptListWidget")
        self.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.itemSelectionChanged.connect(self._on_selection_changed)

    def _on_selection_changed(self):
        item = self.currentItem()
        if item and hasattr(item, "prompt"):
            self.prompt_selected.emit(item.prompt)

    def set_prompts(self, prompts: list):
        self.clear()
        for p in prompts:
            item = QListWidgetItem()
            item.prompt = p
            preview = (p.content[:60] + "…") if len(p.content) > 60 else (p.content or "")
            desc = (p.description[:40] + "…") if p.description and len(p.description) > 40 else (p.description or "")
            text = f"{p.title}  [{p.category}]"
            if desc:
                text += f"  – {desc}"
            item.setText(text)
            item.setToolTip(preview)
            self.addItem(item)


class PromptEditorWidget(QWidget):
    """Kompakter Bearbeitungsbereich: Titel, Kategorie+Typ nebeneinander, Beschreibung, Tags, großer Inhalt."""

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self._scope = "global"
        self._project_id: Optional[int] = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        # Titel (volle Breite)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Titel")
        layout.addWidget(self.title_edit)

        # Kategorie + Typ nebeneinander
        meta_row = QHBoxLayout()
        meta_row.setSpacing(12)
        self.category_combo = QComboBox()
        self.category_combo.addItems(PROMPT_CATEGORIES)
        self.type_combo = QComboBox()
        self.type_combo.addItems(PROMPT_TYPES)
        meta_row.addWidget(QLabel("Kategorie:"))
        meta_row.addWidget(self.category_combo, 1)
        meta_row.addWidget(QLabel("Typ:"))
        meta_row.addWidget(self.type_combo, 1)
        layout.addLayout(meta_row)

        # Beschreibung kompakt
        self.description_edit = QLineEdit()
        self.description_edit.setPlaceholderText("Beschreibung")
        layout.addWidget(self.description_edit)

        # Tags kompakt
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("Tags (kommagetrennt)")
        layout.addWidget(self.tags_edit)

        # Inhalt – möglichst groß
        layout.addWidget(QLabel("Inhalt:"))
        self.content_edit = QPlainTextEdit()
        self.content_edit.setPlaceholderText("Prompt-Text…")
        self.content_edit.setMinimumHeight(180)
        self.content_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.content_edit, 1)

    def load_prompt(self, prompt: Prompt):
        if not prompt:
            self.clear()
            return
        self.title_edit.setText(prompt.title)
        idx = self.category_combo.findText(prompt.category)
        if idx >= 0:
            self.category_combo.setCurrentIndex(idx)
        self.description_edit.setText(prompt.description)
        idx = self.type_combo.findText(prompt.prompt_type)
        if idx >= 0:
            self.type_combo.setCurrentIndex(idx)
        self.content_edit.setPlainText(prompt.content)
        self.tags_edit.setText(", ".join(prompt.tags))
        self._scope = getattr(prompt, "scope", "global") or "global"
        self._project_id = getattr(prompt, "project_id", None)

    def get_prompt(self, prompt_id=None) -> Prompt:
        tags_str = self.tags_edit.text().strip()
        tags = [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else []
        return Prompt(
            id=prompt_id,
            title=self.title_edit.text().strip(),
            category=self.category_combo.currentText(),
            description=self.description_edit.text().strip(),
            content=self.content_edit.toPlainText(),
            tags=tags,
            prompt_type=self.type_combo.currentText(),
            scope=self._scope,
            project_id=self._project_id,
            created_at=None,
            updated_at=None,
        )

    def clear(self):
        self.title_edit.clear()
        self.category_combo.setCurrentIndex(0)
        self.description_edit.clear()
        self.type_combo.setCurrentIndex(0)
        self.content_edit.clear()
        self.tags_edit.clear()
        self._scope = "global"
        self._project_id = None


class PromptPreviewWidget(QWidget):
    """Read-only Vorschau des ausgewählten Prompts."""

    def __init__(self, theme: str = "dark", parent=None):
        super().__init__(parent)
        self.theme = theme
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.preview_label = QLabel("Vorschau")
        self.preview_label.setObjectName("previewTitle")
        self.preview_text = QPlainTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMinimumHeight(60)
        layout.addWidget(self.preview_label)
        layout.addWidget(self.preview_text)

    def set_content(self, prompt: Prompt):
        if not prompt:
            self.preview_text.clear()
            self.preview_label.setText("Vorschau")
            return
        self.preview_label.setText(f"Vorschau: {prompt.title}")
        self.preview_text.setPlainText(prompt.content)


class PromptManagerPanel(QWidget):
    """
    Promptverwaltung: gestraffte UI mit filterbarer Liste, kompakten Metadaten und großem Inhaltsbereich.
    """

    prompt_apply_requested = Signal(object)
    prompt_as_system_requested = Signal(object)
    prompt_to_composer_requested = Signal(object)

    def __init__(
        self,
        prompt_service: PromptService = None,
        settings=None,
        theme: str = "dark",
        parent=None,
    ):
        super().__init__(parent)
        self.service = prompt_service or PromptService()
        self.settings = settings
        self.theme = theme
        self._current_prompt: Prompt = None
        self.init_ui()
        self._refresh_list()

    def init_ui(self):
        self.setObjectName("promptManagerPanel")
        self.setMinimumWidth(_PROMPTS_PANEL_FIXED_WIDTH())
        self.setMaximumWidth(_PROMPTS_PANEL_FIXED_WIDTH())

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # 1. Kopfbereich: Suchfeld + Kategorie-Filter nebeneinander, Backend-Anzeige
        head_row = QHBoxLayout()
        head_row.setSpacing(8)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Prompts durchsuchen…")
        self.search_edit.textChanged.connect(self._on_search_changed)
        head_row.addWidget(self.search_edit, 1)

        self.category_filter = QComboBox()
        self.category_filter.addItem("— Alle Kategorien —", None)
        for c in PROMPT_CATEGORIES:
            self.category_filter.addItem(c, c)
        self.category_filter.currentIndexChanged.connect(self._on_filter_changed)
        head_row.addWidget(self.category_filter, 0)
        main_layout.addLayout(head_row)

        self.backend_label = QLabel()
        self.backend_label.setStyleSheet("color: gray; font-size: 11px;")
        main_layout.addWidget(self.backend_label)
        self._update_backend_label()

        # 2. Aktionszeile
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)
        self.btn_new = QPushButton("Neu")
        self.btn_load = QPushButton("Laden")
        self.btn_save = QPushButton("Speichern")
        self.btn_delete = QPushButton("Löschen")
        self.btn_duplicate = QPushButton("Duplizieren")
        self.btn_new.clicked.connect(self._on_new)
        self.btn_load.clicked.connect(self._on_load)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_delete.clicked.connect(self._on_delete)
        self.btn_duplicate.clicked.connect(self._on_duplicate)
        btn_layout.addWidget(self.btn_new)
        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_save)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_duplicate)
        main_layout.addLayout(btn_layout)

        # 3. Prompt-Auswahlbereich (filterbare Liste)
        list_label = QLabel("Gespeicherte Prompts")
        list_label.setStyleSheet("font-weight: 600;")
        main_layout.addWidget(list_label)
        self.prompt_list = PromptListWidget(self.theme)
        self.prompt_list.setMinimumHeight(100)
        self.prompt_list.prompt_selected.connect(self._on_prompt_selected)
        main_layout.addWidget(self.prompt_list)

        # 4+5. Metadaten + Inhaltsbereich (Editor)
        self.editor = PromptEditorWidget(self.theme)
        main_layout.addWidget(self.editor, 1)

        # 6. Vorschau + Anwendungsaktionen
        preview_label = QLabel("Vorschau")
        preview_label.setStyleSheet("font-weight: 600;")
        main_layout.addWidget(preview_label)
        self.preview = PromptPreviewWidget(self.theme)
        main_layout.addWidget(self.preview)

        apply_layout = QHBoxLayout()
        apply_layout.setSpacing(8)
        self.btn_apply = QPushButton("In Chat übernehmen")
        self.btn_system = QPushButton("Als Systemprompt")
        self.btn_composer = QPushButton("In Composer einfügen")
        self.btn_apply.clicked.connect(self._on_apply)
        self.btn_system.clicked.connect(self._on_system)
        self.btn_composer.clicked.connect(self._on_composer)
        btn_width = _BUTTON_WIDTH_IF_FIT()
        if btn_width is not None:
            for btn in (self.btn_apply, self.btn_system, self.btn_composer):
                btn.setMinimumWidth(btn_width)
        apply_layout.addWidget(self.btn_apply)
        apply_layout.addWidget(self.btn_system)
        apply_layout.addWidget(self.btn_composer)
        main_layout.addLayout(apply_layout)

    def _update_backend_label(self):
        storage = getattr(self.settings, "prompt_storage_type", "database") if self.settings else "database"
        self.backend_label.setText("Speicher: Datenbank" if storage == "database" else "Speicher: Verzeichnis")

    def _on_search_changed(self, text: str):
        self._refresh_list()

    def _on_filter_changed(self):
        self._refresh_list()

    def _get_filter_params(self):
        search = self.search_edit.text().strip()
        category = self.category_filter.currentData()
        return search, category

    def _refresh_list(self, filter_text: str = None, category: str = None):
        if filter_text is None or category is None:
            filter_text, category = self._get_filter_params()
        try:
            prompts = self.service.list_all(filter_text, category)
            self.prompt_list.set_prompts(prompts)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Fehler",
                f"Prompts konnten nicht geladen werden: {e}",
            )

    def refresh_list(self):
        """Öffentliche Methode zum Aktualisieren der Liste (z.B. nach Backend-Wechsel)."""
        self._refresh_list()

    def _on_prompt_selected(self, prompt: Prompt):
        self._current_prompt = prompt
        self.editor.load_prompt(prompt)
        self.preview.set_content(prompt)

    def _get_effective_prompt_for_apply(self) -> Optional[Prompt]:
        """Liefert den aktuell sichtbaren Prompt-Inhalt (Editor oder ausgewählter)."""
        p = self.editor.get_prompt(self._current_prompt.id if self._current_prompt else None)
        if not p.content and not p.title:
            return self._current_prompt
        return p

    def _on_new(self):
        self._current_prompt = Prompt.empty()
        self.editor.load_prompt(self._current_prompt)
        self.preview.set_content(self._current_prompt)
        self.prompt_list.clearSelection()

    def _on_load(self):
        item = self.prompt_list.currentItem()
        if not item or not hasattr(item, "prompt"):
            QMessageBox.information(self, "Laden", "Bitte wählen Sie einen Prompt aus der Liste.")
            return
        self._on_prompt_selected(item.prompt)

    def _on_save(self):
        p = self.editor.get_prompt(self._current_prompt.id if self._current_prompt else None)
        if not p.title:
            QMessageBox.warning(self, "Speichern", "Bitte einen Titel eingeben.")
            return
        try:
            if p.id is None:
                created = self.service.create(p)
                if created:
                    self._current_prompt = created
                    self._refresh_list()
                    QMessageBox.information(self, "Speichern", "Prompt wurde erstellt.")
                else:
                    QMessageBox.warning(self, "Speichern", "Prompt konnte nicht erstellt werden.")
            else:
                if self.service.update(p):
                    self._current_prompt = p
                    self._refresh_list()
                    QMessageBox.information(self, "Speichern", "Prompt wurde aktualisiert.")
                else:
                    QMessageBox.warning(self, "Speichern", "Prompt konnte nicht aktualisiert werden.")
        except Exception as e:
            QMessageBox.critical(self, "Speichern", f"Fehler beim Speichern: {e}")

    def _on_delete(self):
        if not self._current_prompt or self._current_prompt.id is None:
            QMessageBox.information(self, "Löschen", "Bitte wählen Sie einen gespeicherten Prompt zum Löschen.")
            return
        confirm = getattr(self.settings, "prompt_confirm_delete", True) if self.settings else True
        if confirm:
            reply = QMessageBox.question(
                self,
                "Löschen",
                f"Prompt „{self._current_prompt.title}“ wirklich löschen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        try:
            if self.service.delete(self._current_prompt.id):
                self._current_prompt = None
                self.editor.clear()
                self.preview.set_content(None)
                self._refresh_list()
            else:
                QMessageBox.warning(self, "Löschen", "Prompt konnte nicht gelöscht werden.")
        except Exception as e:
            QMessageBox.critical(self, "Löschen", f"Fehler beim Löschen: {e}")

    def _on_duplicate(self):
        if not self._current_prompt or self._current_prompt.id is None:
            QMessageBox.information(self, "Duplizieren", "Bitte wählen Sie einen gespeicherten Prompt zum Duplizieren.")
            return
        try:
            created = self.service.duplicate(self._current_prompt)
            if created:
                self._current_prompt = created
                self.editor.load_prompt(created)
                self.preview.set_content(created)
                self._refresh_list()
                QMessageBox.information(self, "Duplizieren", "Kopie wurde erstellt.")
            else:
                QMessageBox.warning(self, "Duplizieren", "Kopie konnte nicht erstellt werden.")
        except Exception as e:
            QMessageBox.critical(self, "Duplizieren", f"Fehler beim Duplizieren: {e}")

    def _on_apply(self):
        p = self._get_effective_prompt_for_apply()
        if not p or not p.content:
            QMessageBox.information(self, "In Chat übernehmen", "Kein Prompt-Inhalt vorhanden.")
            return
        self.prompt_apply_requested.emit(p)

    def _on_system(self):
        p = self._get_effective_prompt_for_apply()
        if not p or not p.content:
            QMessageBox.information(self, "Als Systemprompt", "Kein Prompt-Inhalt vorhanden.")
            return
        self.prompt_as_system_requested.emit(p)

    def _on_composer(self):
        p = self._get_effective_prompt_for_apply()
        if not p or not p.content:
            QMessageBox.information(self, "In Composer einfügen", "Kein Prompt-Inhalt vorhanden.")
            return
        self.prompt_to_composer_requested.emit(p)

    def refresh_theme(self, theme: str):
        self.theme = theme
        self.prompt_list.theme = theme
        self._update_backend_label()


__all__ = [
    "PromptManagerPanel",
    "PromptListWidget",
    "PromptEditorWidget",
    "PromptPreviewWidget",
    "_PROMPTS_PANEL_FIXED_WIDTH",
]

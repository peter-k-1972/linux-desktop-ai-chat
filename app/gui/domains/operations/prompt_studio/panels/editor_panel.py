"""
PromptEditorPanel – Vollständiger Prompt-Editor.

Felder: Name, Beschreibung, Scope, Kategorie, Inhalt.
Speichern, Abbrechen. Dirty-State-Indikator.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QPushButton,
    QFormLayout,
    QScrollArea,
    QWidget,
)
from PySide6.QtCore import Signal, Qt

from app.prompts.prompt_models import Prompt, PROMPT_CATEGORIES


class PromptEditorPanel(QFrame):
    """Prompt-Editor: Name, Beschreibung, Scope, Kategorie, Inhalt."""

    prompt_saved = Signal(object)  # Prompt nach Speichern

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("promptEditorPanel")
        self.setMinimumHeight(200)
        self._current_prompt: Optional[Prompt] = None
        self._dirty = False
        self._setup_ui()
        self._update_buttons()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(16)

        header = QHBoxLayout()
        self._title_label = QLabel("Prompt Editor")
        self._title_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #1f2937;")
        header.addWidget(self._title_label)
        header.addStretch()
        self._dirty_indicator = QLabel("")
        self._dirty_indicator.setStyleSheet("color: #f59e0b; font-size: 12px;")
        header.addWidget(self._dirty_indicator)
        layout.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        form = QWidget()
        form_layout = QFormLayout(form)
        form_layout.setSpacing(12)

        self._name = QLineEdit()
        self._name.setPlaceholderText("Prompt-Name")
        self._name.textChanged.connect(self._mark_dirty)
        form_layout.addRow("Name:", self._name)

        self._description = QLineEdit()
        self._description.setPlaceholderText("Kurze Beschreibung (optional)")
        self._description.textChanged.connect(self._mark_dirty)
        form_layout.addRow("Beschreibung:", self._description)

        self._scope = QComboBox()
        self._scope.addItems(["project", "global"])
        self._scope.setItemText(0, "Projekt")
        self._scope.setItemText(1, "Global")
        self._scope.currentTextChanged.connect(self._mark_dirty)
        form_layout.addRow("Scope:", self._scope)

        self._category = QComboBox()
        self._category.addItems(PROMPT_CATEGORIES)
        self._category.setCurrentText("general")
        self._category.currentTextChanged.connect(self._mark_dirty)
        form_layout.addRow("Kategorie:", self._category)

        self._content = QTextEdit()
        self._content.setPlaceholderText("Prompt-Inhalt…")
        self._content.setMinimumHeight(120)
        self._content.textChanged.connect(self._mark_dirty)
        form_layout.addRow("Inhalt:", self._content)

        scroll.setWidget(form)
        layout.addWidget(scroll, 1)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_save = QPushButton("Speichern")
        self._btn_save.setObjectName("savePromptButton")
        self._btn_save.setStyleSheet("""
            #savePromptButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
            #savePromptButton:hover { background: #1d4ed8; }
            #savePromptButton:disabled {
                background: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self._btn_save.clicked.connect(self._on_save)
        self._btn_save.setEnabled(False)
        btn_row.addWidget(self._btn_save)
        layout.addLayout(btn_row)

        self.setStyleSheet("""
            #promptEditorPanel {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """)

    def _mark_dirty(self) -> None:
        self._dirty = True
        self._update_buttons()

    def _clear_dirty(self) -> None:
        self._dirty = False
        self._update_buttons()

    def _update_buttons(self) -> None:
        has_prompt = self._current_prompt is not None
        self._btn_save.setEnabled(has_prompt and self._dirty)
        if self._dirty and has_prompt:
            self._dirty_indicator.setText("• Ungespeichert")
        else:
            self._dirty_indicator.setText("")

    def load_prompt(self, prompt: Optional[Prompt]) -> None:
        """Lädt einen Prompt in den Editor."""
        self._current_prompt = prompt
        self._dirty = False

        if prompt is None:
            self._name.clear()
            self._description.clear()
            self._scope.setCurrentText("Global")
            self._category.setCurrentText("general")
            self._content.clear()
            self._title_label.setText("Prompt Editor")
            self._scope.setEnabled(False)
        else:
            self._name.setText(prompt.title or "")
            self._description.setText(prompt.description or "")
            scope_val = getattr(prompt, "scope", "global")
            self._scope.setCurrentText("Projekt" if scope_val == "project" else "Global")
            self._category.setCurrentText(prompt.category or "general")
            self._content.setPlainText(prompt.content or "")
            self._title_label.setText(f"Prompt: {prompt.title or 'Unbenannt'}")
            self._scope.setEnabled(True)

        self._update_buttons()

    def _on_save(self) -> None:
        if self._current_prompt is None:
            return
        title = (self._name.text() or "").strip()
        if not title:
            return
        scope_text = self._scope.currentText()
        scope = "project" if scope_text == "Projekt" else "global"

        try:
            from app.prompts.prompt_service import get_prompt_service
            from app.core.context.project_context_manager import get_project_context_manager

            svc = get_prompt_service()
            mgr = get_project_context_manager()
            project_id = mgr.get_active_project_id() if scope == "project" else None
            if scope == "project" and project_id is None:
                scope = "global"
                project_id = None

            updated = Prompt(
                id=self._current_prompt.id,
                title=title,
                category=self._category.currentText() or "general",
                description=(self._description.text() or "").strip(),
                content=self._content.toPlainText() or "",
                tags=getattr(self._current_prompt, "tags", []) or [],
                prompt_type=getattr(self._current_prompt, "prompt_type", "user"),
                scope=scope,
                project_id=project_id,
                created_at=self._current_prompt.created_at,
                updated_at=None,
            )
            if svc.update(updated):
                saved = svc.get(updated.id)
                if saved:
                    self._current_prompt = saved
                    self._clear_dirty()
                    self.prompt_saved.emit(saved)
        except Exception:
            pass

    def get_current_prompt(self) -> Optional[Prompt]:
        return self._current_prompt

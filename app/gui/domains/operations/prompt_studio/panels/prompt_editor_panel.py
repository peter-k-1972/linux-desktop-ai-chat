"""
PromptEditorPanel – Editor for prompt name and content.

Supports placeholder variables: {{input}}, {{context}}, {{topic}}.
Each save creates a new version entry.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QScrollArea,
    QWidget,
)
from PySide6.QtCore import Signal, Qt

from app.prompts.prompt_models import Prompt


# Supported placeholder variables
PLACEHOLDER_VARIABLES = ["{{input}}", "{{context}}", "{{topic}}"]
PLACEHOLDER_HINT = "Verwenden Sie {{input}}, {{context}} oder {{topic}} als Platzhalter."


class PromptEditorPanel(QFrame):
    """
    Prompt editor: name and content.

    - Placeholder support: {{input}}, {{context}}, {{topic}}
    - Each save creates a new version entry
    """

    prompt_saved = Signal(object)  # Prompt after save
    editor_state_changed = Signal(str, str)  # title, content (for preview panel)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("promptEditorPanel")
        self.setMinimumHeight(200)
        self._current_prompt: Optional[Prompt] = None
        self._dirty = False
        self._setup_ui()
        self._update_buttons()

    def _setup_ui(self) -> None:
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
        form_layout = QVBoxLayout(form)
        form_layout.setSpacing(12)

        # Name
        form_layout.addWidget(QLabel("Name:"))
        self._name = QLineEdit()
        self._name.setPlaceholderText("Prompt-Name")
        self._name.textChanged.connect(self._on_name_or_content_changed)
        form_layout.addWidget(self._name)

        # Content with placeholder support
        form_layout.addWidget(QLabel("Inhalt:"))
        self._content = QTextEdit()
        self._content.setPlaceholderText(
            "Prompt-Inhalt…\n\n" + PLACEHOLDER_HINT
        )
        self._content.setMinimumHeight(160)
        self._content.textChanged.connect(self._on_name_or_content_changed)
        form_layout.addWidget(self._content)

        # Placeholder buttons
        placeholder_row = QHBoxLayout()
        placeholder_row.addWidget(QLabel("Platzhalter einfügen:"))
        for var in PLACEHOLDER_VARIABLES:
            btn = QPushButton(var)
            btn.setObjectName("placeholderButton")
            btn.setStyleSheet("""
                #placeholderButton {
                    background: #f1f5f9;
                    color: #475569;
                    border: 1px solid #e2e8f0;
                    border-radius: 6px;
                    padding: 4px 10px;
                    font-size: 12px;
                }
                #placeholderButton:hover {
                    background: #e2e8f0;
                }
            """)
            btn.clicked.connect(lambda checked, v=var: self._insert_placeholder(v))
            placeholder_row.addWidget(btn)
        placeholder_row.addStretch()
        form_layout.addLayout(placeholder_row)

        scroll.setWidget(form)
        layout.addWidget(scroll, 1)

        # Save button
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self._btn_save = QPushButton("Speichern (neue Version)")
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

    def _insert_placeholder(self, placeholder: str) -> None:
        """Insert placeholder at cursor position in content."""
        cursor = self._content.textCursor()
        cursor.insertText(placeholder)
        self._on_name_or_content_changed()

    def _on_name_or_content_changed(self) -> None:
        self._mark_dirty()
        self._emit_editor_state()

    def _emit_editor_state(self) -> None:
        self.editor_state_changed.emit(
            (self._name.text() or "").strip(),
            self._content.toPlainText() or "",
        )

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
        """Load a prompt into the editor."""
        self._current_prompt = prompt
        self._dirty = False

        if prompt is None:
            self._name.clear()
            self._content.clear()
            self._title_label.setText("Prompt Editor")
        else:
            self._name.setText(prompt.title or "")
            self._content.setPlainText(prompt.content or "")
            self._title_label.setText(f"Prompt: {prompt.title or 'Unbenannt'}")

        self._update_buttons()
        self._emit_editor_state()

    def load_version_content(self, title: str, content: str) -> None:
        """
        Load version content into the editor without marking dirty.
        Used when switching between versions.
        """
        self._name.setText(title or "")
        self._content.setPlainText(content or "")
        self._dirty = False
        self._update_buttons()
        self._emit_editor_state()

    def _on_save(self) -> None:
        if self._current_prompt is None:
            return
        title = (self._name.text() or "").strip()
        if not title:
            return
        content = self._content.toPlainText() or ""

        try:
            from app.prompts.prompt_service import get_prompt_service
            svc = get_prompt_service()
            # Each save creates a new version entry
            saved = svc.save_version(self._current_prompt, title, content)
            if saved:
                self._current_prompt = saved
                self._clear_dirty()
                self.prompt_saved.emit(saved)
        except Exception:
            pass

    def get_current_prompt(self) -> Optional[Prompt]:
        return self._current_prompt

    def get_editor_title(self) -> str:
        return (self._name.text() or "").strip()

    def get_editor_content(self) -> str:
        return self._content.toPlainText() or ""

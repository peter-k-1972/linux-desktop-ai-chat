"""
TopicEditorDialog – Lightweight dialogs for topic CRUD.

- Create: simple name input
- Rename: inline / very lightweight
- Delete: requires confirmation; clarifies that chats move to Ungruppiert
"""

from typing import Optional

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt


class TopicCreateDialog(QDialog):
    """Lightweight dialog to create a new topic."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("topicCreateDialog")
        self.setWindowTitle("Neues Topic")
        self.setModal(True)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self._label = QLabel("Name des Topics:")
        self._label.setStyleSheet("font-size: 13px; color: #374151;")
        layout.addWidget(self._label)

        self._input = QLineEdit()
        self._input.setObjectName("topicNameInput")
        self._input.setPlaceholderText("z.B. API-Design, Bugfixes…")
        self._input.setStyleSheet("""
            #topicNameInput {
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
            }
            #topicNameInput:focus { border-color: #2563eb; }
        """)
        self._input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self._ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok_btn.setEnabled(False)
        layout.addWidget(buttons)

        self.setMinimumWidth(280)

    def _on_text_changed(self, text: str) -> None:
        self._ok_btn.setEnabled(bool((text or "").strip()))

    def get_name(self) -> str:
        return (self._input.text() or "").strip()


class TopicRenameDialog(QDialog):
    """Lightweight dialog to rename an existing topic."""

    def __init__(self, current_name: str, parent=None):
        super().__init__(parent)
        self.setObjectName("topicRenameDialog")
        self.setWindowTitle("Topic umbenennen")
        self.setModal(True)
        self._setup_ui(current_name)

    def _setup_ui(self, current_name: str) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        self._label = QLabel("Neuer Name:")
        self._label.setStyleSheet("font-size: 13px; color: #374151;")
        layout.addWidget(self._label)

        self._input = QLineEdit()
        self._input.setObjectName("topicRenameInput")
        self._input.setText(current_name or "")
        self._input.selectAll()
        self._input.setStyleSheet("""
            #topicRenameInput {
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 13px;
            }
            #topicRenameInput:focus { border-color: #2563eb; }
        """)
        self._input.textChanged.connect(self._on_text_changed)
        layout.addWidget(self._input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self._ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        self._ok_btn.setEnabled(bool((current_name or "").strip()))
        layout.addWidget(buttons)

        self.setMinimumWidth(280)

    def _on_text_changed(self, text: str) -> None:
        self._ok_btn.setEnabled(bool((text or "").strip()))

    def get_name(self) -> str:
        return (self._input.text() or "").strip()


class TopicDeleteConfirmDialog(QDialog):
    """
    Confirmation dialog for topic deletion.

    Clearly states that chats will move to Ungruppiert, not be deleted.
    """

    def __init__(self, topic_name: str, chat_count: int = 0, parent=None):
        super().__init__(parent)
        self.setObjectName("topicDeleteConfirmDialog")
        self.setWindowTitle("Topic löschen")
        self.setModal(True)
        self._setup_ui(topic_name, chat_count)

    def _setup_ui(self, topic_name: str, chat_count: int) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        self._warning = QLabel(
            f"Topic „{topic_name}“ wirklich löschen?"
        )
        self._warning.setStyleSheet("font-size: 14px; font-weight: 600; color: #1f2937;")
        self._warning.setWordWrap(True)
        layout.addWidget(self._warning)

        self._info = QLabel(
            "Die Chats werden nicht gelöscht. Sie werden in „Ungruppiert“ verschoben."
        )
        self._info.setStyleSheet("font-size: 12px; color: #64748b;")
        self._info.setWordWrap(True)
        layout.addWidget(self._info)

        if chat_count > 0:
            self._count = QLabel(f"{chat_count} Chat(s) werden zu Ungruppiert verschoben.")
            self._count.setStyleSheet("font-size: 12px; color: #475569;")
            layout.addWidget(self._count)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        # Use destructive label for Ok
        ok_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        ok_btn.setText("Löschen")
        ok_btn.setStyleSheet("""
            QPushButton {
                background: #dc2626;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 14px;
            }
            QPushButton:hover { background: #b91c1c; }
        """)
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setText("Abbrechen")
        layout.addWidget(buttons)

        self.setMinimumWidth(320)

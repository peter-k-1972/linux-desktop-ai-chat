"""
ProjectContextInspector – Inspector-Inhalt für Projekt-Kontext.

Zeigt Projektname, Beschreibung, Status, Inhaltszahlen.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
)


class ProjectContextInspector(QWidget):
    """Inspector-Widget für Projekt-Kontext."""

    def __init__(
        self,
        project_name: str = "(kein Projekt)",
        description: str = "—",
        status: str = "active",
        chat_count: int = 0,
        source_count: int = 0,
        prompt_count: int = 0,
        parent=None,
    ):
        super().__init__(parent)
        self.setObjectName("projectContextInspector")
        self._project_name = project_name
        self._description = description
        self._status = status
        self._chat_count = chat_count
        self._source_count = source_count
        self._prompt_count = prompt_count
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)

        # Projekt
        proj_group = QGroupBox("Projekt")
        proj_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        proj_layout = QVBoxLayout(proj_group)
        name_label = QLabel(self._project_name)
        name_label.setStyleSheet("color: #1f2937; font-size: 14px; font-weight: 500;")
        name_label.setWordWrap(True)
        proj_layout.addWidget(name_label)
        layout.addWidget(proj_group)

        # Beschreibung
        desc_group = QGroupBox("Beschreibung")
        desc_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        desc_layout = QVBoxLayout(desc_group)
        desc_label = QLabel(self._description)
        desc_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        desc_label.setWordWrap(True)
        desc_layout.addWidget(desc_label)
        layout.addWidget(desc_group)

        # Status
        status_group = QGroupBox("Status")
        status_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        status_layout = QVBoxLayout(status_group)
        status_label = QLabel(self._status)
        status_label.setStyleSheet("color: #22c55e; font-size: 12px;")
        status_layout.addWidget(status_label)
        layout.addWidget(status_group)

        # Inhalte
        content_group = QGroupBox("Inhalte")
        content_group.setStyleSheet("QGroupBox { font-weight: bold; color: #374151; }")
        content_layout = QVBoxLayout(content_group)
        content_label = QLabel(
            f"Chats: {self._chat_count} · Quellen: {self._source_count} · Prompts: {self._prompt_count}"
        )
        content_label.setStyleSheet("color: #6b7280; font-size: 12px;")
        content_layout.addWidget(content_label)
        layout.addWidget(content_group)

        layout.addStretch()

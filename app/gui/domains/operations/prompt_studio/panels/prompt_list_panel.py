"""
PromptListPanel – Prompts list with + New Prompt button.

Prompts represent reusable system prompts.
Selecting a prompt opens the prompt editor.
"""

from typing import Optional

from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QLineEdit,
    QScrollArea,
    QWidget,
    QMenu,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QAction

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.domains.operations.prompt_studio.panels.prompt_list_item import PromptListItem


class PromptListPanel(QFrame):
    """
    Prompts list panel for the Prompts page.

    - + New Prompt button
    - Search field
    - List of prompts (name, last updated, versions)
    - Selecting a prompt opens the editor (emits prompt_selected)
    """

    prompt_selected = Signal(object)  # Prompt
    new_prompt_requested = Signal()
    prompt_deleted = Signal(int)  # prompt_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("promptListPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(340)
        self._current_project_id: Optional[int] = None
        self._current_project_name: Optional[str] = None
        self._active_prompt_id: Optional[int] = None
        self._prompt_widgets: dict = {}
        self._setup_ui()
        self._connect_project_context()
        self._load_prompts()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Project header
        self._project_header = QFrame()
        self._project_header.setObjectName("promptListProjectHeader")
        header_layout = QVBoxLayout(self._project_header)
        header_layout.setContentsMargins(12, 10, 12, 10)
        self._project_label = QLabel("Bitte Projekt auswählen")
        self._project_label.setObjectName("promptListProjectLabel")
        self._project_label.setStyleSheet("""
            #promptListProjectLabel {
                font-size: 13px;
                font-weight: 600;
                color: #64748b;
            }
        """)
        self._project_label.setWordWrap(True)
        header_layout.addWidget(self._project_label)
        self._project_header.setStyleSheet("""
            #promptListProjectHeader {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self._project_header)

        # + New Prompt button
        self._btn_new = QPushButton("+ New Prompt")
        self._btn_new.setObjectName("newPromptButton")
        self._btn_new.setIcon(IconManager.get(IconRegistry.ADD, size=16))
        self._btn_new.setEnabled(False)
        self._btn_new.setStyleSheet("""
            #newPromptButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 12px;
                font-weight: 500;
            }
            #newPromptButton:hover { background: #1d4ed8; }
            #newPromptButton:disabled {
                background: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self._btn_new.clicked.connect(self._on_new_prompt)
        layout.addWidget(self._btn_new)

        # Search
        self._search = QLineEdit()
        self._search.setPlaceholderText("Prompts durchsuchen…")
        self._search.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QLineEdit:focus { border-color: #2563eb; }
        """)
        self._search.textChanged.connect(self._on_search_changed)
        layout.addWidget(self._search)

        # Scroll area with prompt list
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._list_content = QWidget()
        self._list_layout = QVBoxLayout(self._list_content)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(6)
        self._scroll.setWidget(self._list_content)
        layout.addWidget(self._scroll, 1)

        self._empty_label = QLabel("Keine Prompts.")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: #94a3b8; font-size: 13px; padding: 24px;")
        self._empty_label.hide()

        self.setStyleSheet("""
            #promptListPanel {
                background: #ffffff;
                border-right: 1px solid #e2e8f0;
            }
        """)

    def _connect_project_context(self) -> None:
        try:
            from app.gui.events.project_events import subscribe_project_events
            from app.core.context.project_context_manager import get_project_context_manager
            subscribe_project_events(self._on_project_context_changed)
            mgr = get_project_context_manager()
            pid = mgr.get_active_project_id()
            proj = mgr.get_active_project()
            self._on_project_changed(pid, proj)
        except Exception:
            pass

    def _on_project_context_changed(self, payload: dict) -> None:
        project_id = payload.get("project_id")
        if project_id is None:
            self._on_project_changed(None, None)
            return
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            project = get_project_context_manager().get_active_project()
            self._on_project_changed(project_id, project)
        except Exception:
            self._on_project_changed(None, None)

    def _on_project_changed(self, project_id: Optional[int], project: Optional[dict]) -> None:
        if project and isinstance(project, dict):
            self._current_project_id = project.get("project_id")
            self._current_project_name = project.get("name", "Projekt")
            self._project_label.setText(self._current_project_name)
            self._project_label.setStyleSheet("""
                #promptListProjectLabel {
                    font-size: 13px;
                    font-weight: 600;
                    color: #1f2937;
                }
            """)
            self._btn_new.setEnabled(True)
            self._search.show()
        else:
            self._current_project_id = None
            self._current_project_name = None
            self._project_label.setText("Bitte Projekt auswählen")
            self._project_label.setStyleSheet("""
                #promptListProjectLabel {
                    font-size: 13px;
                    font-weight: 600;
                    color: #64748b;
                }
            """)
            self._btn_new.setEnabled(False)
            self._search.show()
        self._load_prompts()

    def _load_prompts(self) -> None:
        """Load prompts: project prompts + global prompts, grouped."""
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._prompt_widgets.clear()

        filter_text = self._search.text().strip() if self._search.isVisible() else ""

        try:
            from app.prompts.prompt_service import get_prompt_service
            svc = get_prompt_service()

            project_prompts = []
            global_prompts = []

            if self._current_project_id is not None:
                project_prompts = svc.list_project_prompts(self._current_project_id, filter_text)
            global_prompts = svc.list_global_prompts(filter_text)

        except Exception:
            project_prompts = []
            global_prompts = []

        if not project_prompts and not global_prompts:
            self._empty_label.setParent(None)
            self._list_layout.addWidget(self._empty_label)
            if self._current_project_id is None:
                self._empty_label.setText("Bitte Projekt auswählen.")
            else:
                self._empty_label.setText("Keine Prompts. Klicken Sie auf + New Prompt.")
            self._empty_label.show()
            return

        self._empty_label.hide()

        if project_prompts:
            section = QLabel("Projekt-Prompts")
            section.setObjectName("promptListSection")
            section.setStyleSheet("""
                #promptListSection {
                    font-size: 11px;
                    font-weight: 600;
                    color: #64748b;
                    padding: 8px 0 4px 0;
                    margin-top: 4px;
                }
            """)
            self._list_layout.addWidget(section)
            for p in project_prompts:
                self._add_prompt_item(p)

        if global_prompts:
            section = QLabel("Globale Prompts")
            section.setObjectName("promptListSection")
            section.setStyleSheet("""
                #promptListSection {
                    font-size: 11px;
                    font-weight: 600;
                    color: #64748b;
                    padding: 8px 0 4px 0;
                    margin-top: 8px;
                }
            """)
            self._list_layout.addWidget(section)
            for p in global_prompts:
                self._add_prompt_item(p)

        self._list_layout.addStretch()

    def _add_prompt_item(self, prompt) -> None:
        pid = getattr(prompt, "id", None)
        active = pid == self._active_prompt_id
        version_count = None
        if pid is not None:
            try:
                from app.prompts.prompt_service import get_prompt_service
                version_count = get_prompt_service().count_versions(pid)
            except Exception:
                pass
        if version_count is None:
            version_count = 1  # New prompts have 1 version after first save
        item = PromptListItem(prompt, active, version_count, self)

        def _on_press(e, p=prompt):
            if e.button() == Qt.MouseButton.LeftButton:
                self._on_item_clicked(p)
            elif e.button() == Qt.MouseButton.RightButton:
                self._show_context_menu(item, e.pos(), p)

        item.mousePressEvent = _on_press
        if pid is not None:
            self._prompt_widgets[pid] = item
        self._list_layout.addWidget(item)

    def _show_context_menu(self, widget: QWidget, pos, prompt) -> None:
        menu = QMenu(self)
        action_delete = QAction("Löschen", self)
        action_delete.triggered.connect(lambda checked, p=prompt: self._on_delete_prompt(p))
        menu.addAction(action_delete)
        menu.exec(widget.mapToGlobal(pos))

    def _on_delete_prompt(self, prompt) -> None:
        pid = getattr(prompt, "id", None)
        if pid is None:
            return
        try:
            from app.prompts.prompt_service import get_prompt_service
            from PySide6.QtWidgets import QMessageBox
            if QMessageBox.question(
                self,
                "Prompt löschen",
                f"Prompt „{prompt.title}“ wirklich löschen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            ) != QMessageBox.StandardButton.Yes:
                return
            if get_prompt_service().delete(pid):
                self.prompt_deleted.emit(pid)
                self.refresh()
        except Exception:
            pass

    def _on_item_clicked(self, prompt) -> None:
        """Selecting a prompt opens the prompt editor."""
        pid = getattr(prompt, "id", None)
        for wid in self._prompt_widgets.values():
            wid.set_active(getattr(wid.prompt, "id", None) == pid)
        self._active_prompt_id = pid
        self.prompt_selected.emit(prompt)

    def _on_search_changed(self, text: str) -> None:
        self._load_prompts()

    def _on_new_prompt(self) -> None:
        self.new_prompt_requested.emit()

    def refresh(self) -> None:
        self._load_prompts()

    def set_active_prompt(self, prompt_id: Optional[int]) -> None:
        """Set the active prompt without reloading."""
        self._active_prompt_id = prompt_id
        for wid in self._prompt_widgets.values():
            wid.set_active(getattr(wid.prompt, "id", None) == prompt_id)

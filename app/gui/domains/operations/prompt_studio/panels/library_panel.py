"""
PromptLibraryPanel – Projektbezogener Prompt-Explorer.

Explorer-Struktur:
- Aktives Projekt (Header)
- Button: Neuer Prompt
- Suchfeld (optional)
- Projekt-Prompts (gruppiert)
- Globale Prompts (gruppiert)

Batch 2: optional ``prompt_studio_port`` → Presenter/Port/Adapter (gleiche Liste wie Slice 1).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

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
    QMessageBox,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QAction

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.shared import apply_header_layout, apply_sidebar_layout
from app.gui.widgets import EmptyStateWidget
from app.gui.domains.operations.prompt_studio.panels.prompt_list_item import PromptListItemWidget
from app.gui.domains.operations.prompt_studio.prompt_studio_library_sink import PromptStudioLibrarySink
from app.ui_application.presenters.prompt_studio_list_presenter import PromptStudioListPresenter
from app.ui_contracts.workspaces.prompt_studio_library import DeletePromptLibraryCommand
from app.ui_contracts.workspaces.prompt_studio_list import (
    LoadPromptStudioListCommand,
    PromptStudioListState,
)

if TYPE_CHECKING:
    from app.ui_application.ports.prompt_studio_port import PromptStudioPort


class PromptLibraryPanel(QFrame):
    """Projektbezogener Prompt-Explorer. Links im Prompt Studio."""

    prompt_selected = Signal(object)  # Prompt
    new_prompt_requested = Signal()
    prompt_deleted = Signal(int)  # prompt_id

    def __init__(self, parent=None, *, prompt_studio_port: Optional[PromptStudioPort] = None):
        super().__init__(parent)
        self.setObjectName("promptLibraryPanel")
        self.setMinimumWidth(260)
        self.setMaximumWidth(340)
        self._prompt_studio_port = prompt_studio_port
        self._library_sink: PromptStudioLibrarySink | None = None
        self._library_presenter: PromptStudioListPresenter | None = None
        self._current_project_id: Optional[int] = None
        self._current_project_name: Optional[str] = None
        self._active_prompt_id: Optional[int] = None
        self._prompt_widgets: dict = {}
        self._setup_ui()
        if prompt_studio_port is not None:
            self._library_sink = PromptStudioLibrarySink(self)
            self._library_presenter = PromptStudioListPresenter(self._library_sink, prompt_studio_port)
        self._connect_project_context()
        self.refresh()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        apply_sidebar_layout(layout)

        self._project_header = QFrame()
        self._project_header.setObjectName("promptExplorerProjectHeader")
        header_layout = QVBoxLayout(self._project_header)
        apply_header_layout(header_layout)
        self._project_label = QLabel("Bitte Projekt auswählen")
        self._project_label.setObjectName("promptExplorerProjectLabel")
        self._project_label.setStyleSheet("""
            #promptExplorerProjectLabel {
                font-size: 13px;
                font-weight: 600;
                color: #64748b;
            }
        """)
        self._project_label.setWordWrap(True)
        header_layout.addWidget(self._project_label)
        self._project_header.setStyleSheet("""
            #promptExplorerProjectHeader {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self._project_header)

        btn_row = QHBoxLayout()
        self._btn_new = QPushButton("Neuer Prompt")
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
        btn_row.addWidget(self._btn_new)
        layout.addLayout(btn_row)

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

        self._empty_widget = EmptyStateWidget(
            title="",
            description="",
            compact=True,
            parent=self,
        )
        self._empty_widget.hide()

        self.setStyleSheet("""
            #promptLibraryPanel {
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

    def _on_project_changed(self, project_id, project) -> None:
        if project and isinstance(project, dict):
            self._current_project_id = project.get("project_id")
            self._current_project_name = project.get("name", "Projekt")
            self._project_label.setText(self._current_project_name)
            self._project_label.setStyleSheet("""
                #promptExplorerProjectLabel {
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
                #promptExplorerProjectLabel {
                    font-size: 13px;
                    font-weight: 600;
                    color: #64748b;
                }
            """)
            self._btn_new.setEnabled(False)
            self._search.show()
        self.refresh()

    def _use_port_path(self) -> bool:
        return self._library_presenter is not None

    def apply_prompt_library_state(
        self,
        state: PromptStudioListState,
        prompt_models: tuple[Any, ...] = (),
    ) -> None:
        """Sink: Liste aus Contract-Zustand (Batch 2)."""
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._prompt_widgets.clear()

        if state.phase == "loading":
            self._empty_widget.set_content("Prompts werden geladen", "Bitte warten …")
            self._empty_widget.setParent(None)
            self._list_layout.addWidget(self._empty_widget)
            self._empty_widget.show()
            return

        if state.phase == "error":
            msg = state.error.message if state.error else "Fehler."
            self._empty_widget.set_content("Fehler", msg)
            self._empty_widget.setParent(None)
            self._list_layout.addWidget(self._empty_widget)
            self._empty_widget.show()
            return

        if state.phase == "empty":
            hint = state.empty_hint or "Keine Prompts."
            if self._current_project_id is None:
                self._empty_widget.set_content("Kein Projekt ausgewählt", hint)
            else:
                self._empty_widget.set_content("Keine Prompts", hint)
            self._empty_widget.setParent(None)
            self._list_layout.addWidget(self._empty_widget)
            self._empty_widget.show()
            return

        if len(state.rows) != len(prompt_models):
            self._empty_widget.set_content("Listenfehler", "Bitte erneut laden.")
            self._empty_widget.setParent(None)
            self._list_layout.addWidget(self._empty_widget)
            self._empty_widget.show()
            return

        self._empty_widget.hide()

        current_section: str | None = None
        first_header = True
        for row, p in zip(state.rows, prompt_models, strict=True):
            if current_section != row.list_section:
                current_section = row.list_section
                title = "Projekt-Prompts" if row.list_section == "project" else "Globale Prompts"
                section = QLabel(title)
                section.setObjectName("promptListSection")
                margin_top = "4px" if row.list_section == "project" and first_header else "8px"
                first_header = False
                section.setStyleSheet(f"""
                    #promptListSection {{
                        font-size: 11px;
                        font-weight: 600;
                        color: #64748b;
                        padding: 8px 0 4px 0;
                        margin-top: {margin_top};
                    }}
                """)
                self._list_layout.addWidget(section)
            self._add_prompt_item(p, version_count=row.version_count)

        self._list_layout.addStretch()

    def _load_prompts_legacy(self) -> None:
        """Lädt Prompts: Projekt-Prompts + Globale Prompts, gruppiert (Legacy)."""
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
            if self._current_project_id is None:
                self._empty_widget.set_content(
                    "Kein Projekt ausgewählt",
                    "Wähle ein Projekt, um Prompts anzuzeigen.",
                )
            else:
                self._empty_widget.set_content(
                    "Keine Prompts",
                    "Lege einen neuen Prompt an.",
                )
            self._empty_widget.setParent(None)
            self._list_layout.addWidget(self._empty_widget)
            self._empty_widget.show()
            return

        self._empty_widget.hide()

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

    def _version_count_from_service_legacy(self, pid: int) -> int:
        try:
            from app.prompts.prompt_service import get_prompt_service

            return max(1, int(get_prompt_service().count_versions(pid)))
        except Exception:
            return 1

    def _add_prompt_item(self, prompt, version_count: Optional[int] = None) -> None:
        pid = getattr(prompt, "id", None)
        active = pid == self._active_prompt_id
        if version_count is not None:
            vc = max(1, int(version_count))
        elif self._use_port_path():
            vc = 1
        elif pid is not None:
            vc = self._version_count_from_service_legacy(int(pid))
        else:
            vc = 1
        item = PromptListItemWidget(prompt, active, version_count=vc, parent=self)
        def _on_press(e, p=prompt):
            if e.button() == Qt.MouseButton.LeftButton:
                self._on_item_clicked(p)
            elif e.button() == Qt.MouseButton.RightButton:
                self._show_context_menu(item, e.pos(), p)
        item.mousePressEvent = _on_press
        if pid is not None:
            self._prompt_widgets[pid] = item
        self._list_layout.addWidget(item)

    def _show_context_menu(self, widget, pos, prompt) -> None:
        menu = QMenu(self)
        action_delete = QAction("Löschen", self)
        action_delete.triggered.connect(lambda checked, p=prompt: self._on_delete_prompt(p))
        menu.addAction(action_delete)
        menu.exec(widget.mapToGlobal(pos))

    def _on_delete_prompt(self, prompt) -> None:
        pid = getattr(prompt, "id", None)
        if pid is None:
            return
        if (
            QMessageBox.question(
                self,
                "Prompt löschen",
                f"Prompt „{prompt.title}“ wirklich löschen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        if self._use_port_path() and self._library_presenter is not None:
            ft = self._search.text().strip() if self._search.isVisible() else ""
            result = self._library_presenter.handle_delete_library_prompt(
                DeletePromptLibraryCommand(int(pid), self._current_project_id, ft),
            )
            if result.ok:
                self.prompt_deleted.emit(int(pid))
            elif result.error_message:
                QMessageBox.warning(self, "Prompt löschen", result.error_message)
            return
        self._on_delete_prompt_legacy(prompt)

    def _on_delete_prompt_legacy(self, prompt) -> None:
        pid = getattr(prompt, "id", None)
        if pid is None:
            return
        try:
            from app.prompts.prompt_service import get_prompt_service

            if get_prompt_service().delete(pid):
                self.prompt_deleted.emit(pid)
                self.refresh()
        except Exception:
            pass

    def _on_item_clicked(self, prompt) -> None:
        pid = getattr(prompt, "id", None)
        for wid in self._prompt_widgets.values():
            wid.set_active(getattr(wid.prompt, "id", None) == pid)
        self._active_prompt_id = pid
        self.prompt_selected.emit(prompt)

    def _on_search_changed(self, text: str) -> None:
        self.refresh()

    def _on_new_prompt(self) -> None:
        self.new_prompt_requested.emit()

    def refresh(self) -> None:
        if self._use_port_path() and self._library_presenter is not None:
            ft = self._search.text().strip() if self._search.isVisible() else ""
            self._library_presenter.handle_command(
                LoadPromptStudioListCommand(self._current_project_id, ft),
            )
        else:
            self._load_prompts_legacy()

    def set_active_prompt(self, prompt_id: int | None) -> None:
        """Setzt den aktiven Prompt ohne Neu laden."""
        self._active_prompt_id = prompt_id
        for wid in self._prompt_widgets.values():
            wid.set_active(getattr(wid.prompt, "id", None) == prompt_id)

"""
PromptStudioWorkspace – Prompt Studio with three-column layout.

Layout:
- Left: Navigation (Prompts, Templates, Test Lab, Settings)
- Center: Prompt editor / content
- Right: Prompt metadata and versions (inspector)

Reacts to project_context_changed to reload prompts belonging to the active project.
"""

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QMessageBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QSplitter,
    QStackedWidget,
)
from PySide6.QtCore import Qt

from app.gui.shared.base_operations_workspace import BaseOperationsWorkspace
from app.gui.domains.operations.prompt_studio.panels.prompt_navigation_panel import (
    PromptNavigationPanel,
    SECTION_PROMPTS,
    SECTION_TEMPLATES,
    SECTION_TEST_LAB,
)
from app.gui.domains.operations.prompt_studio.panels.prompt_list_panel import PromptListPanel
from app.gui.domains.operations.prompt_studio.panels.prompt_editor_panel import PromptEditorPanel
from app.gui.domains.operations.prompt_studio.panels import (
    PromptPreviewPanel,
    PromptTemplatesPanel,
    PromptTestLab,
)


class NewPromptDialog(QDialog):
    """Dialog to create a new prompt."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neuer Prompt")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        self._title = QLineEdit()
        self._title.setPlaceholderText("Prompt-Titel")
        layout.addRow("Titel:", self._title)
        self._content = QTextEdit()
        self._content.setPlaceholderText("Prompt-Inhalt…")
        self._content.setMaximumHeight(120)
        layout.addRow("Inhalt:", self._content)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_title(self) -> str:
        return (self._title.text() or "").strip()

    def get_content(self) -> str:
        return (self._content.toPlainText() or "").strip()


class PromptStudioWorkspace(BaseOperationsWorkspace):
    """Prompt Studio workspace with three-column layout and project integration."""

    def __init__(self, parent=None):
        super().__init__("prompt_studio", parent)
        self._navigation: PromptNavigationPanel | None = None
        self._list_panel: PromptListPanel | None = None
        self._editor: PromptEditorPanel | None = None
        self._inspector_host = None
        self._center_stack: QStackedWidget | None = None
        self._setup_ui()
        self._connect_signals()
        self._connect_project_context()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._navigation = PromptNavigationPanel(self)
        layout.addWidget(self._navigation)

        self._center_stack = QStackedWidget()
        self._center_stack.setObjectName("promptStudioCenter")
        self._center_stack.setStyleSheet("""
            #promptStudioCenter {
                background: #ffffff;
            }
        """)

        prompts_widget = QWidget()
        prompts_layout = QHBoxLayout(prompts_widget)
        prompts_layout.setContentsMargins(0, 0, 0, 0)
        prompts_layout.setSpacing(0)

        self._list_panel = PromptListPanel(self)
        prompts_layout.addWidget(self._list_panel)

        center_splitter = QSplitter(Qt.Orientation.Horizontal)
        self._editor = PromptEditorPanel(self)
        center_splitter.addWidget(self._editor)
        self._preview = PromptPreviewPanel(self)
        center_splitter.addWidget(self._preview)
        center_splitter.setStretchFactor(0, 2)
        center_splitter.setStretchFactor(1, 1)
        prompts_layout.addWidget(center_splitter, 1)

        self._center_stack.addWidget(prompts_widget)
        self._templates_panel = PromptTemplatesPanel(self)
        self._center_stack.addWidget(self._templates_panel)
        self._center_stack.addWidget(PromptTestLab(self))

        layout.addWidget(self._center_stack, 1)

        self._navigation.set_current(SECTION_PROMPTS)
        self._center_stack.setCurrentIndex(0)
        self._sync_preview_from_editor()

    def _on_editor_state_changed(self, title: str, body: str) -> None:
        if getattr(self, "_preview", None):
            self._preview.on_editor_state(title, body)

    def _sync_preview_from_editor(self) -> None:
        if self._editor and getattr(self, "_preview", None):
            self._preview.on_editor_state(
                self._editor.get_editor_title(),
                self._editor.get_editor_content(),
            )

    def _connect_signals(self) -> None:
        if self._navigation:
            self._navigation.section_selected.connect(self._on_section_selected)
        if self._list_panel:
            self._list_panel.new_prompt_requested.connect(self._on_new_prompt)
            self._list_panel.prompt_selected.connect(self._on_prompt_selected)
            self._list_panel.prompt_deleted.connect(self._on_prompt_deleted)
        if self._editor:
            self._editor.prompt_saved.connect(self._on_prompt_saved)
            self._editor.editor_state_changed.connect(self._on_editor_state_changed)
        if self._templates_panel:
            self._templates_panel.template_copied_to_prompt.connect(self._on_template_copied_to_prompt)

    def _connect_project_context(self) -> None:
        try:
            from app.gui.events.project_events import subscribe_project_events
            subscribe_project_events(self._on_project_context_changed)
        except Exception:
            pass

    def _on_project_context_changed(self, payload: dict) -> None:
        if self._list_panel:
            self._list_panel.refresh()
        if self._editor:
            self._editor.load_prompt(None)
        self._refresh_inspector(None)

    def _on_template_copied_to_prompt(self, prompt) -> None:
        self._navigation.set_current(SECTION_PROMPTS)
        self._center_stack.setCurrentIndex(0)
        if self._list_panel:
            self._list_panel.refresh()
            self._on_prompt_selected(prompt)

    def _on_section_selected(self, section_id: str) -> None:
        if section_id == SECTION_PROMPTS:
            self._center_stack.setCurrentIndex(0)
        elif section_id == SECTION_TEMPLATES:
            self._center_stack.setCurrentIndex(1)
        elif section_id == SECTION_TEST_LAB:
            self._center_stack.setCurrentIndex(2)

    def _on_prompt_selected(self, prompt) -> None:
        if self._editor:
            self._editor.load_prompt(prompt)
        if self._list_panel:
            pid = getattr(prompt, "id", None)
            self._list_panel.set_active_prompt(pid)
        self._refresh_inspector(prompt)

    def _on_prompt_saved(self, prompt) -> None:
        if self._list_panel:
            self._list_panel.refresh()
        self._refresh_inspector(prompt)

    def _on_prompt_deleted(self, prompt_id: int) -> None:
        if self._editor and self._editor.get_current_prompt():
            if getattr(self._editor.get_current_prompt(), "id", None) == prompt_id:
                self._editor.load_prompt(None)
        self._refresh_inspector(None)

    def _on_new_prompt(self) -> None:
        dlg = NewPromptDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        title = dlg.get_title()
        if not title:
            QMessageBox.warning(self, "Fehler", "Bitte einen Titel eingeben.")
            return
        try:
            from app.prompts import Prompt, get_prompt_service
            from app.core.context.project_context_manager import get_project_context_manager
            svc = get_prompt_service()
            mgr = get_project_context_manager()
            scope = "project" if mgr.get_active_project_id() else "global"
            project_id = mgr.get_active_project_id()
            prompt = Prompt(
                id=None,
                title=title,
                category="general",
                description="",
                content=dlg.get_content(),
                tags=[],
                prompt_type="user",
                scope=scope,
                project_id=project_id,
                created_at=None,
                updated_at=None,
            )
            created = svc.create(prompt)
            if created and self._list_panel:
                self._list_panel.refresh()
                self._on_prompt_selected(created)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Prompt konnte nicht angelegt werden: {e}")

    def open_with_context(self, ctx: dict) -> None:
        prompt_id = ctx.get("prompt_id")
        if prompt_id is not None and self._list_panel:
            try:
                from app.prompts.prompt_service import get_prompt_service
                prompt = get_prompt_service().get(prompt_id)
                if prompt:
                    self._list_panel.refresh()
                    self._on_prompt_selected(prompt)
            except Exception:
                pass

    def _refresh_inspector(self, prompt=None) -> None:
        if not self._inspector_host:
            return
        try:
            from app.gui.inspector.prompt_studio_inspector import PromptStudioInspector
            from app.core.context.project_context_manager import get_project_context_manager
            proj = get_project_context_manager().get_active_project()
            project_name = proj.get("name") if proj and isinstance(proj, dict) else None
        except Exception:
            project_name = None
        content = PromptStudioInspector(
            project_name=project_name,
            prompt=prompt,
            on_version_selected=self._on_version_selected,
        )
        self._inspector_host.set_content(content)

    def _on_version_selected(self, version_data: dict) -> None:
        if self._editor:
            title = version_data.get("title", "")
            content = version_data.get("content", "")
            self._editor.load_version_content(title, content)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        self._inspector_host = inspector_host
        try:
            from app.gui.inspector.prompt_studio_inspector import PromptStudioInspector
            from app.core.context.project_context_manager import get_project_context_manager
            proj = get_project_context_manager().get_active_project()
            project_name = proj.get("name") if proj and isinstance(proj, dict) else None
        except Exception:
            project_name = None
        prompt = self._editor.get_current_prompt() if self._editor else None
        content = PromptStudioInspector(
            project_name=project_name,
            prompt=prompt,
            on_version_selected=self._on_version_selected,
        )
        inspector_host.set_content(content, content_token=content_token)

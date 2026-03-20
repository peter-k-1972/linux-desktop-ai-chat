"""
ProjectsWorkspace – Arbeitscontainer für Projekte.

Projektliste, Anlegen, Auswahl, Overview. Aktives Projekt global sichtbar.
"""

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QSplitter,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QMessageBox,
)
from PySide6.QtCore import Qt
from app.gui.shared.base_operations_workspace import BaseOperationsWorkspace
from app.gui.domains.operations.projects.panels import ProjectListPanel, ProjectOverviewPanel


class NewProjectDialog(QDialog):
    """Dialog zum Anlegen eines neuen Projekts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neues Projekt")
        self.setMinimumWidth(400)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        self._name = QLineEdit()
        self._name.setPlaceholderText("z.B. Marketing-Kampagne Q2")
        layout.addRow("Name:", self._name)

        self._desc = QTextEdit()
        self._desc.setPlaceholderText("Optionale Beschreibung…")
        self._desc.setMaximumHeight(100)
        layout.addRow("Beschreibung:", self._desc)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_name(self) -> str:
        return (self._name.text() or "").strip()

    def get_description(self) -> str:
        return (self._desc.toPlainText() or "").strip()


class ProjectsWorkspace(BaseOperationsWorkspace):
    """Projekte-Arbeitsraum: Liste, Overview, aktives Projekt."""

    def __init__(self, parent=None):
        super().__init__("operations_projects", parent)
        self._inspector_host = None
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self._list_panel = ProjectListPanel(self)
        splitter.addWidget(self._list_panel)

        self._overview_panel = ProjectOverviewPanel(self)
        splitter.addWidget(self._overview_panel)

        splitter.setSizes([280, 400])
        layout.addWidget(splitter)

    def _connect_signals(self):
        self._list_panel.project_selected.connect(self._on_project_selected)
        self._list_panel.new_project_requested.connect(self._on_new_project)
        self._overview_panel.set_active_requested.connect(self._on_set_active)
        try:
            from app.core.context.active_project import get_active_project_context
            ctx = get_active_project_context()
            ctx.subscribe(self._on_active_project_changed)
            self._on_active_project_changed(ctx.active_project_id, ctx.active_project)
            self.destroyed.connect(lambda: ctx.unsubscribe(self._on_active_project_changed))
        except Exception:
            pass

    def _on_active_project_changed(self, project_id, project) -> None:
        """Synchronisiert Anzeige bei Projektwechsel (z.B. via TopBar Switcher)."""
        if project and isinstance(project, dict):
            self._list_panel.set_current(project.get("project_id"))
            self._overview_panel.set_project(project)
        else:
            self._list_panel.set_current(None)
            self._overview_panel.set_project(None)
        self._refresh_inspector()

    def _on_project_selected(self, project: dict | None) -> None:
        self._overview_panel.set_project(project)
        self._refresh_inspector()

    def _on_new_project(self) -> None:
        dlg = NewProjectDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        name = dlg.get_name()
        if not name:
            QMessageBox.warning(self, "Fehler", "Bitte einen Projektnamen eingeben.")
            return
        try:
            from app.services.project_service import get_project_service
            svc = get_project_service()
            desc = dlg.get_description()
            project_id = svc.create_project(name, desc)
            self._list_panel.refresh()
            proj = svc.get_project(project_id)
            if proj:
                self._list_panel.set_current(project_id)
                self._overview_panel.set_project(proj)
                self._on_set_active(proj)
            self._refresh_inspector()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Projekt konnte nicht angelegt werden: {e}")

    def _on_set_active(self, project: dict) -> None:
        """Set active project via ProjectContextManager (syncs to ActiveProjectContext)."""
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            pid = project.get("project_id")
            get_project_context_manager().set_active_project(pid)
            self._refresh_inspector()
        except Exception:
            pass

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Setzt den Inspector mit Projekt-Kontext."""
        self._inspector_host = inspector_host
        self._inspector_content_token = content_token
        self._refresh_inspector()

    def _refresh_inspector(self) -> None:
        if not self._inspector_host:
            return
        from app.gui.inspector.project_context_inspector import ProjectContextInspector

        proj = self._overview_panel.get_project()
        if proj:
            try:
                from app.services.project_service import get_project_service
                svc = get_project_service()
                chat_count = svc.count_chats_of_project(proj["project_id"])
                file_count = svc.count_files_of_project(proj["project_id"])
                prompt_count = svc.count_prompts_of_project(proj["project_id"])
            except Exception:
                chat_count = 0
                file_count = 0
                prompt_count = 0
            content = ProjectContextInspector(
                project_name=proj.get("name", ""),
                description=proj.get("description", "") or "—",
                status=proj.get("status", "active"),
                chat_count=chat_count,
                source_count=file_count,
                prompt_count=prompt_count,
            )
            token = getattr(self, "_inspector_content_token", None)
            self._inspector_host.set_content(content, content_token=token)
        else:
            self._inspector_host.clear_content()

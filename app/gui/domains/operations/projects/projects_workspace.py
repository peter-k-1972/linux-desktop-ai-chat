"""
ProjectsWorkspace – Arbeitscontainer für Projekte (Projektarchiv).

Dreispaltig: Projektliste · Übersicht · Projekt-Inspector. Aktives Projekt global sichtbar.
"""

from PySide6.QtWidgets import (
    QHBoxLayout,
    QSplitter,
    QDialog,
    QDialogButtonBox,
    QComboBox,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QMessageBox,
)
from PySide6.QtCore import Qt
from app.gui.shared.base_operations_workspace import BaseOperationsWorkspace
from app.gui.domains.operations.projects.panels import (
    ProjectInspectorPanel,
    ProjectListPanel,
    ProjectOverviewPanel,
)
from app.gui.domains.operations.projects.dialogs.project_edit_dialog import ProjectEditDialog
from app.projects.lifecycle import DEFAULT_LIFECYCLE_STATUS, lifecycle_combo_entries
from app.ui_application.adapters.service_projects_overview_command_adapter import (
    ServiceProjectsOverviewCommandAdapter,
)
from app.ui_application.adapters.service_projects_overview_read_adapter import (
    ServiceProjectsOverviewReadAdapter,
)


PROJECT_DELETE_INFORMATIVE_TEXT = (
    "• Chats bleiben erhalten; die Zuordnung zu diesem Projekt und die Themen dieses Projekts "
    "werden entfernt bzw. entkoppelt.\n"
    "• Prompts, Agenten und Workflows werden nicht verworfen: Sie werden global "
    "(ohne Projektzuordnung), damit keine Inhalte verloren gehen.\n"
    "• Knowledge: Der RAG-Unterordner dieses Projekts wird entfernt; referenzierte Dateien auf "
    "der Festplatte werden dabei nicht gelöscht.\n"
    "• Verknüpfungen in der Datenbank (z. B. project_files) werden aufgehoben.\n"
    "• War dieses Projekt aktiv, wird der aktive Projektkontext geleert (kein Ersatzprojekt)."
)


class NewProjectDialog(QDialog):
    """Dialog zum Anlegen eines neuen Projekts."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Neues Projekt")
        self.setMinimumWidth(440)
        self._setup_ui()

    def _setup_ui(self):
        layout = QFormLayout(self)
        self._name = QLineEdit()
        self._name.setPlaceholderText("z.B. Marketing-Kampagne Q2")
        layout.addRow("Name:", self._name)

        self._desc = QTextEdit()
        self._desc.setPlaceholderText("Optionale Beschreibung…")
        self._desc.setMaximumHeight(80)
        layout.addRow("Beschreibung:", self._desc)

        self._customer_name = QLineEdit()
        self._customer_name.setPlaceholderText("Kunde (optional)")
        layout.addRow("Kunde:", self._customer_name)

        self._external_reference = QLineEdit()
        layout.addRow("Externe Referenz:", self._external_reference)

        self._internal_code = QLineEdit()
        layout.addRow("Interner Code:", self._internal_code)

        self._lifecycle = QComboBox()
        for label, value in lifecycle_combo_entries():
            self._lifecycle.addItem(label, value)
        for i in range(self._lifecycle.count()):
            if self._lifecycle.itemData(i) == DEFAULT_LIFECYCLE_STATUS:
                self._lifecycle.setCurrentIndex(i)
                break
        layout.addRow("Projektphase:", self._lifecycle)

        self._planned_start = QLineEdit()
        self._planned_start.setPlaceholderText("YYYY-MM-DD")
        layout.addRow("Geplanter Start:", self._planned_start)

        self._planned_end = QLineEdit()
        self._planned_end.setPlaceholderText("YYYY-MM-DD")
        layout.addRow("Geplantes Ende:", self._planned_end)

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

    def get_customer_name(self) -> str:
        return (self._customer_name.text() or "").strip()

    def get_external_reference(self) -> str:
        return (self._external_reference.text() or "").strip()

    def get_internal_code(self) -> str:
        return (self._internal_code.text() or "").strip()

    def get_lifecycle_status(self) -> str:
        d = self._lifecycle.currentData()
        return str(d).strip().lower() if d is not None else DEFAULT_LIFECYCLE_STATUS

    def get_planned_start_date(self) -> str:
        return (self._planned_start.text() or "").strip()

    def get_planned_end_date(self) -> str:
        return (self._planned_end.text() or "").strip()


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
        self._projects_read_port = ServiceProjectsOverviewReadAdapter()
        self._projects_command_port = ServiceProjectsOverviewCommandAdapter()
        self._list_panel = ProjectListPanel(self, read_port=self._projects_read_port)
        splitter.addWidget(self._list_panel)

        self._overview_panel = ProjectOverviewPanel(
            self,
            read_port=self._projects_read_port,
            command_port=self._projects_command_port,
            host_callbacks=self,
        )
        splitter.addWidget(self._overview_panel)

        self._arch_inspector = ProjectInspectorPanel(self, read_port=self._projects_read_port)
        splitter.addWidget(self._arch_inspector)

        splitter.setSizes([300, 480, 280])
        layout.addWidget(splitter)

    def _connect_signals(self):
        self._list_panel.project_selected.connect(self._on_project_selected)
        self._list_panel.new_project_requested.connect(self._on_new_project)
        self._overview_panel.edit_project_requested.connect(self._on_edit_project)
        self._overview_panel.delete_project_requested.connect(self._on_delete_project)
        self._overview_panel.manage_milestones_requested.connect(self._on_manage_milestones)
        try:
            # ActiveProjectContext: nur Lesen/Subscribe; Schreiben erfolgt über PCM → Sync hierher.
            from app.core.context.active_project import get_active_project_context
            ctx = get_active_project_context()
            ctx.subscribe(self._on_active_project_changed)
            self._on_active_project_changed(ctx.active_project_id, ctx.active_project)
            self.destroyed.connect(lambda: ctx.unsubscribe(self._on_active_project_changed))
        except Exception:
            pass
        self._sync_arch_inspector()

    def _on_active_project_changed(self, project_id, project) -> None:
        """Synchronisiert Anzeige bei Projektwechsel (z.B. via TopBar Switcher)."""
        if project and isinstance(project, dict):
            self._list_panel.set_current(project.get("project_id"))
            self._overview_panel.set_project(project)
        else:
            self._list_panel.set_current(None)
            self._overview_panel.set_project(None)
        self._sync_arch_inspector()

    def _on_project_selected(self, project: object | None) -> None:
        if isinstance(project, dict) or project is None:
            resolved = project
        elif isinstance(project, int):
            try:
                from app.services.project_service import get_project_service

                resolved = get_project_service().get_project(project)
            except Exception:
                resolved = None
        else:
            resolved = None
        self._overview_panel.set_project(resolved)
        self._arch_inspector.set_project(resolved)

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
            project_id = svc.create_project(
                name,
                desc,
                customer_name=dlg.get_customer_name() or None,
                external_reference=dlg.get_external_reference() or None,
                internal_code=dlg.get_internal_code() or None,
                lifecycle_status=dlg.get_lifecycle_status(),
                planned_start_date=dlg.get_planned_start_date() or None,
                planned_end_date=dlg.get_planned_end_date() or None,
            )
            self._list_panel.refresh()
            proj = svc.get_project(project_id)
            if proj:
                self._list_panel.set_current(project_id)
                self._overview_panel.set_project(proj)
                self._on_set_active(proj)
            self._sync_arch_inspector()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Projekt konnte nicht angelegt werden: {e}")

    def _on_manage_milestones(self, project: dict) -> None:
        from app.gui.domains.operations.projects.dialogs.project_milestones_dialog import (
            ProjectMilestonesDialog,
        )

        dlg = ProjectMilestonesDialog(project, self)
        dlg.exec()
        try:
            from app.services.project_service import get_project_service
            from app.core.context.project_context_manager import get_project_context_manager

            pid = project.get("project_id")
            if pid is None:
                return
            svc = get_project_service()
            updated = svc.get_project(pid)
            if updated:
                self._overview_panel.set_project(updated)
                pcm = get_project_context_manager()
                if pcm.get_active_project_id() == pid:
                    pcm.set_active_project(pid)
            self._sync_arch_inspector()
        except Exception:
            pass

    def _on_set_active(self, project: dict) -> None:
        """Set active project via ProjectContextManager (syncs to ActiveProjectContext)."""
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            pid = project.get("project_id")
            get_project_context_manager().set_active_project(pid)
            self._sync_arch_inspector()
        except Exception:
            pass

    def on_project_selection_changed(self, payload) -> None:
        del payload
        self._sync_arch_inspector()

    def on_request_open_chat(self, project_id: int, chat_id: int | None = None) -> None:
        pending = {"chat_id": chat_id} if chat_id is not None else None
        self._open_project_area(project_id, "operations_chat", pending)

    def on_request_open_prompt_studio(self, project_id: int, prompt_id: int | None = None) -> None:
        pending = {"prompt_id": prompt_id} if prompt_id is not None else None
        self._open_project_area(project_id, "operations_prompt_studio", pending)

    def on_request_open_knowledge(self, project_id: int, source_path: str | None = None) -> None:
        pending = {"source_path": source_path} if source_path else None
        self._open_project_area(project_id, "operations_knowledge", pending)

    def on_request_open_workflows(self, project_id: int) -> None:
        self._open_project_area(
            project_id,
            "operations_workflows",
            {"workflow_ops_scope": "project"},
        )

    def on_request_open_agent_tasks(self, project_id: int) -> None:
        self._open_project_area(project_id, "operations_agent_tasks")

    def on_request_set_active_project(self, project_id: int | None) -> None:
        del project_id
        self._sync_arch_inspector()

    def _on_edit_project(self, project: dict) -> None:
        pid = project.get("project_id")
        if pid is None:
            return
        dlg = ProjectEditDialog(project, self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        (
            name,
            desc,
            status,
            clear_pol,
            pol_val,
            customer,
            ext_ref,
            int_code,
            lifecycle,
            pstart,
            pend,
            bamt,
            bcur,
            eff,
        ) = dlg.get_values()
        if not name:
            QMessageBox.warning(self, "Fehler", "Bitte einen Projektnamen eingeben.")
            return
        try:
            from app.services.project_service import get_project_service
            from app.core.context.project_context_manager import get_project_context_manager

            svc = get_project_service()
            svc.update_project(
                pid,
                name=name,
                description=desc,
                status=status,
                default_context_policy=pol_val,
                clear_default_context_policy=clear_pol,
                customer_name=customer,
                external_reference=ext_ref,
                internal_code=int_code,
                lifecycle_status=lifecycle,
                planned_start_date=pstart or None,
                planned_end_date=pend or None,
                budget_amount=bamt if bamt.strip() else None,
                budget_currency=bcur if bcur.strip() else None,
                estimated_effort_hours=eff if eff.strip() else None,
            )
            self._list_panel.set_current(pid)
            self._list_panel.refresh()
            pcm = get_project_context_manager()
            if pcm.get_active_project_id() == pid:
                pcm.set_active_project(pid)
            updated = svc.get_project(pid)
            if updated:
                self._overview_panel.set_project(updated)
                self._list_panel.set_current(pid)
            self._sync_arch_inspector()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Projekt konnte nicht gespeichert werden: {e}")

    def _on_delete_project(self, project: dict) -> None:
        pid = project.get("project_id")
        if pid is None:
            return
        name = (project.get("name") or "Projekt").strip()
        box = QMessageBox(self)
        box.setIcon(QMessageBox.Icon.Warning)
        box.setWindowTitle("Projekt löschen")
        box.setText(f"Projekt „{name}“ wirklich löschen?")
        box.setInformativeText(PROJECT_DELETE_INFORMATIVE_TEXT)
        box.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        box.setDefaultButton(QMessageBox.StandardButton.No)
        if box.exec() != QMessageBox.StandardButton.Yes:
            return
        try:
            from app.services.project_service import get_project_service

            get_project_service().delete_project(pid)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Projekt konnte nicht gelöscht werden: {e}")
            return

        self._list_panel.set_current(None)
        self._list_panel.refresh()
        op = self._overview_panel.get_project()
        if op and op.get("project_id") == pid:
            self._overview_panel.set_project(None)
        self._sync_arch_inspector()

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        """Globaler App-Inspector: leer lassen; Kontext sitzt in der rechten Archiv-Spalte."""
        self._inspector_host = inspector_host
        if self._inspector_host:
            self._inspector_host.clear_content()

    def _sync_arch_inspector(self) -> None:
        proj = self._overview_panel.get_project()
        self._arch_inspector.set_project(proj)

    def _open_project_area(
        self,
        project_id: int,
        workspace_id: str,
        pending_context: dict | None = None,
    ) -> None:
        self._activate_project_context(project_id)
        if pending_context:
            try:
                from app.gui.domains.operations.operations_context import set_pending_context

                set_pending_context(pending_context)
            except Exception:
                pass
        host = self._find_workspace_host()
        if host is None:
            return
        from app.gui.navigation.nav_areas import NavArea

        host.show_area(NavArea.OPERATIONS, workspace_id)

    def _activate_project_context(self, project_id: int) -> None:
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            mgr = get_project_context_manager()
            if mgr.get_active_project_id() != project_id:
                mgr.set_active_project(project_id)
        except Exception:
            pass

    def _find_workspace_host(self):
        p = self
        while p:
            if hasattr(p, "show_area") and hasattr(p, "_area_to_index"):
                return p
            p = p.parent() if hasattr(p, "parent") else None
        return None

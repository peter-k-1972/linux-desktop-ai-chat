"""
PromptTemplatesPanel – Reusable prompt patterns.

Templates are prompts with prompt_type=template.
- Create template
- Edit template
- Copy template into a new prompt
- Templates may include placeholder variables ({{input}}, {{context}}, {{topic}})

Batch 2: optional ``prompt_studio_port`` → Presenter/Port/Adapter für die Listen-Lesepfad.
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
    QTextEdit,
    QScrollArea,
    QWidget,
    QMenu,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QMessageBox,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QAction

from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry
from app.gui.domains.operations.prompt_studio.prompt_snapshot_ui import prompt_from_snapshot
from app.gui.domains.operations.prompt_studio.prompt_studio_templates_sink import PromptStudioTemplatesSink
from app.prompts.prompt_models import Prompt
from app.ui_application.presenters.prompt_studio_templates_presenter import PromptStudioTemplatesPresenter
from app.ui_contracts.workspaces.prompt_studio_templates import (
    CopyPromptTemplateCommand,
    CreatePromptTemplateCommand,
    DeletePromptTemplateCommand,
    LoadPromptTemplatesCommand,
    PromptTemplatesState,
    UpdatePromptTemplateCommand,
)

if TYPE_CHECKING:
    from app.ui_application.ports.prompt_studio_port import PromptStudioPort

PLACEHOLDER_HINT = "Platzhalter: {{input}}, {{context}}, {{topic}}"


class TemplateEditDialog(QDialog):
    """Dialog to create or edit a template."""

    def __init__(self, parent=None, template: Optional[Prompt] = None):
        super().__init__(parent)
        self._template = template
        self.setWindowTitle("Template bearbeiten" if template else "Neues Template")
        self.setMinimumWidth(480)
        self.setMinimumHeight(320)
        self._setup_ui()
        if template:
            self._title.setText(template.title or "")
            self._description.setText(template.description or "")
            self._content.setPlainText(template.content or "")

    def _setup_ui(self) -> None:
        layout = QFormLayout(self)
        self._title = QLineEdit()
        self._title.setPlaceholderText("Template-Name")
        layout.addRow("Name:", self._title)

        self._description = QLineEdit()
        self._description.setPlaceholderText("Kurze Beschreibung (optional)")
        layout.addRow("Beschreibung:", self._description)

        layout.addRow(QLabel("Inhalt:"))
        self._content = QTextEdit()
        self._content.setPlaceholderText(f"Template-Inhalt…\n\n{PLACEHOLDER_HINT}")
        self._content.setMinimumHeight(160)
        layout.addRow(self._content)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def get_title(self) -> str:
        return (self._title.text() or "").strip()

    def get_description(self) -> str:
        return (self._description.text() or "").strip()

    def get_content(self) -> str:
        return (self._content.toPlainText() or "").strip()


class TemplateItemWidget(QFrame):
    """Single template entry: title, description, Copy button."""

    copy_clicked = Signal(object)  # template

    def __init__(self, template: Prompt, parent=None):
        super().__init__(parent)
        self.template = template
        self.setObjectName("templateItem")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        row = QHBoxLayout()
        title = QLabel(self.template.title or "Unbenannt")
        title.setStyleSheet("font-weight: 600; font-size: 13px; color: #1f2937;")
        title.setWordWrap(True)
        row.addWidget(title, 1)

        copy_btn = QPushButton("Als Prompt kopieren")
        copy_btn.setObjectName("copyTemplateButton")
        copy_btn.setStyleSheet("""
            #copyTemplateButton {
                background: #f1f5f9;
                color: #475569;
                border: 1px solid #e2e8f0;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 11px;
            }
            #copyTemplateButton:hover { background: #e2e8f0; }
        """)
        copy_btn.clicked.connect(lambda: self.copy_clicked.emit(self.template))
        row.addWidget(copy_btn)
        layout.addLayout(row)

        desc = (self.template.description or "").strip()
        if desc:
            desc_label = QLabel(desc[:80] + "…" if len(desc) > 80 else desc)
            desc_label.setStyleSheet("font-size: 11px; color: #64748b;")
            desc_label.setWordWrap(True)
            layout.addWidget(desc_label)

        self.setStyleSheet("""
            #templateItem {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
            }
            #templateItem:hover {
                background: #f9fafb;
                border-color: #d1d5db;
            }
        """)


class PromptTemplatesPanel(QFrame):
    """
    Templates panel – reusable prompt patterns.

    - Create template
    - Edit template
    - Copy template into a new prompt
    - Templates may include {{input}}, {{context}}, {{topic}}
    """

    template_copied_to_prompt = Signal(object)  # New Prompt created from template

    def __init__(self, parent=None, *, prompt_studio_port: Optional[PromptStudioPort] = None):
        super().__init__(parent)
        self.setObjectName("promptTemplatesPanel")
        self._current_project_id: Optional[int] = None
        self._template_widgets: dict = {}
        self._templates_sink: PromptStudioTemplatesSink | None = None
        self._templates_presenter: PromptStudioTemplatesPresenter | None = None
        if prompt_studio_port is not None:
            self._templates_sink = PromptStudioTemplatesSink(self)
            self._templates_presenter = PromptStudioTemplatesPresenter(
                self._templates_sink,
                prompt_studio_port,
            )
        self._setup_ui()
        self._connect_project_context()
        self.refresh()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Templates")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #1f2937;")
        layout.addWidget(title)

        subtitle = QLabel("Wiederverwendbare Prompt-Muster. Platzhalter: {{input}}, {{context}}, {{topic}}")
        subtitle.setStyleSheet("font-size: 12px; color: #64748b;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        # Create button
        self._btn_create = QPushButton("+ Template erstellen")
        self._btn_create.setObjectName("createTemplateButton")
        self._btn_create.setIcon(IconManager.get(IconRegistry.ADD, size=16))
        self._btn_create.setStyleSheet("""
            #createTemplateButton {
                background: #2563eb;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: 500;
            }
            #createTemplateButton:hover { background: #1d4ed8; }
            #createTemplateButton:disabled {
                background: #cbd5e1;
                color: #94a3b8;
            }
        """)
        self._btn_create.clicked.connect(self._on_create)
        layout.addWidget(self._btn_create)

        # Search
        self._search = QLineEdit()
        self._search.setPlaceholderText("Templates durchsuchen…")
        self._search.setStyleSheet("""
            QLineEdit {
                padding: 8px 12px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QLineEdit:focus { border-color: #2563eb; }
        """)
        self._search.textChanged.connect(self.refresh)
        layout.addWidget(self._search)

        # Template list
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scroll.setStyleSheet("QScrollArea { background: transparent; border: none; }")

        self._list_content = QWidget()
        self._list_layout = QVBoxLayout(self._list_content)
        self._list_layout.setContentsMargins(0, 0, 0, 0)
        self._list_layout.setSpacing(8)
        self._scroll.setWidget(self._list_content)
        layout.addWidget(self._scroll, 1)

        self._empty_label = QLabel("Keine Templates. Erstellen Sie ein neues Template.")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.setStyleSheet("color: #94a3b8; font-size: 13px; padding: 32px;")
        self._empty_label.hide()

        self.setStyleSheet("""
            #promptTemplatesPanel {
                background: #ffffff;
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
        self._current_project_id = project.get("project_id") if project and isinstance(project, dict) else None
        self._btn_create.setEnabled(self._current_project_id is not None)
        self.refresh()

    def _use_port_path(self) -> bool:
        return self._templates_presenter is not None

    def _scope_and_project_for_mutations(self) -> tuple[str, Optional[int]]:
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            mgr = get_project_context_manager()
            pid = mgr.get_active_project_id()
            if pid is not None:
                return "project", pid
        except Exception:
            pass
        return "global", None

    def _templates_refresh_filter_text(self) -> str:
        return self._search.text().strip()

    def apply_prompt_templates_state(
        self,
        state: PromptTemplatesState,
        template_models: tuple[Any, ...] = (),
    ) -> None:
        """Sink: Template-Liste aus Contract-Zustand (Batch 2)."""
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._template_widgets.clear()

        if state.phase == "loading":
            self._empty_label.setParent(None)
            self._list_layout.addWidget(self._empty_label)
            self._empty_label.setText("Templates werden geladen …")
            self._empty_label.show()
            return

        if state.phase == "error":
            self._empty_label.setParent(None)
            self._list_layout.addWidget(self._empty_label)
            msg = state.error.message if state.error else "Fehler."
            self._empty_label.setText(msg)
            self._empty_label.show()
            return

        if state.phase == "empty":
            self._empty_label.setParent(None)
            self._list_layout.addWidget(self._empty_label)
            self._empty_label.setText(state.empty_hint or "Keine Templates.")
            self._empty_label.show()
            return

        if len(state.rows) != len(template_models):
            self._empty_label.setParent(None)
            self._list_layout.addWidget(self._empty_label)
            self._empty_label.setText("Listenfehler — bitte erneut laden.")
            self._empty_label.show()
            return

        self._empty_label.hide()
        for t in template_models:
            self._add_template_item(t)
        self._list_layout.addStretch()

    def _load_templates_legacy(self) -> None:
        """Load templates (project + global) — Legacy."""
        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self._template_widgets.clear()

        filter_text = self._search.text().strip()
        try:
            from app.prompts.prompt_service import get_prompt_service
            templates = get_prompt_service().list_templates(
                project_id=self._current_project_id,
                filter_text=filter_text,
            )
        except Exception:
            templates = []

        if not templates:
            self._empty_label.setParent(None)
            self._list_layout.addWidget(self._empty_label)
            self._empty_label.setText("Keine Templates." + (" Erstellen Sie ein neues." if self._current_project_id else " Projekt auswählen."))
            self._empty_label.show()
            return

        self._empty_label.hide()
        for t in templates:
            self._add_template_item(t)
        self._list_layout.addStretch()

    def _add_template_item(self, template: Prompt) -> None:
        item = TemplateItemWidget(template, self)
        item.copy_clicked.connect(self._on_copy_to_prompt)

        def _on_press(e, t=template):
            if e.button() == Qt.MouseButton.LeftButton:
                self._on_edit(t)
            elif e.button() == Qt.MouseButton.RightButton:
                self._show_context_menu(item, e.pos(), t)

        item.mousePressEvent = _on_press
        tid = getattr(template, "id", None)
        if tid is not None:
            self._template_widgets[tid] = item
        self._list_layout.addWidget(item)

    def _show_context_menu(self, widget: QWidget, pos, template: Prompt) -> None:
        menu = QMenu(self)
        action_edit = QAction("Bearbeiten", self)
        action_edit.triggered.connect(lambda checked, t=template: self._on_edit(t))
        menu.addAction(action_edit)
        action_copy = QAction("Als neuen Prompt kopieren", self)
        action_copy.triggered.connect(lambda checked, t=template: self._on_copy_to_prompt(t))
        menu.addAction(action_copy)
        action_delete = QAction("Löschen", self)
        action_delete.triggered.connect(lambda checked, t=template: self._on_delete(t))
        menu.addAction(action_delete)
        menu.exec(widget.mapToGlobal(pos))

    def _on_create(self) -> None:
        dlg = TemplateEditDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        title = dlg.get_title()
        if not title:
            QMessageBox.warning(self, "Fehler", "Bitte einen Namen eingeben.")
            return
        if self._use_port_path() and self._templates_presenter is not None:
            scope, project_id = self._scope_and_project_for_mutations()
            cmd = CreatePromptTemplateCommand(
                title=title,
                description=dlg.get_description(),
                content=dlg.get_content(),
                scope=scope,
                project_id=project_id,
            )
            result = self._templates_presenter.handle_create_template(
                cmd,
                refresh_project_id=self._current_project_id,
                refresh_filter_text=self._templates_refresh_filter_text(),
            )
            if not result.ok:
                QMessageBox.critical(
                    self,
                    "Fehler",
                    result.error_message or "Template konnte nicht erstellt werden.",
                )
            return
        self._on_create_legacy(title, dlg.get_description(), dlg.get_content())

    def _on_create_legacy(self, title: str, description: str, content: str) -> None:
        try:
            from app.prompts import Prompt, get_prompt_service
            from app.core.context.project_context_manager import get_project_context_manager

            svc = get_prompt_service()
            mgr = get_project_context_manager()
            scope = "project" if mgr.get_active_project_id() else "global"
            project_id = mgr.get_active_project_id()
            template = Prompt(
                id=None,
                title=title,
                category="general",
                description=description,
                content=content,
                tags=[],
                prompt_type="template",
                scope=scope,
                project_id=project_id,
                created_at=None,
                updated_at=None,
            )
            created = svc.create(template)
            if created:
                self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Template konnte nicht erstellt werden: {e}")

    def _on_edit(self, template: Prompt) -> None:
        dlg = TemplateEditDialog(self, template)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        title = dlg.get_title()
        if not title:
            QMessageBox.warning(self, "Fehler", "Bitte einen Namen eingeben.")
            return
        tid = getattr(template, "id", None)
        if tid is None:
            return
        if self._use_port_path() and self._templates_presenter is not None:
            cmd = UpdatePromptTemplateCommand(
                template_id=int(tid),
                title=title,
                description=dlg.get_description(),
                content=dlg.get_content(),
            )
            result = self._templates_presenter.handle_update_template(
                cmd,
                refresh_project_id=self._current_project_id,
                refresh_filter_text=self._templates_refresh_filter_text(),
            )
            if not result.ok:
                QMessageBox.critical(
                    self,
                    "Fehler",
                    result.error_message or "Template konnte nicht gespeichert werden.",
                )
            return
        self._on_edit_legacy(template, title, dlg.get_description(), dlg.get_content())

    def _on_edit_legacy(
        self,
        template: Prompt,
        title: str,
        description: str,
        content: str,
    ) -> None:
        try:
            from app.prompts.prompt_service import get_prompt_service

            svc = get_prompt_service()
            updated = Prompt(
                id=template.id,
                title=title,
                category=template.category,
                description=description,
                content=content,
                tags=getattr(template, "tags", []) or [],
                prompt_type="template",
                scope=getattr(template, "scope", "global"),
                project_id=getattr(template, "project_id", None),
                created_at=template.created_at,
                updated_at=None,
            )
            if svc.update(updated):
                self.refresh()
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Template konnte nicht gespeichert werden: {e}")

    def _on_copy_to_prompt(self, template: Prompt) -> None:
        """Copy template into a new prompt (prompt_type=user)."""
        tid = getattr(template, "id", None)
        if tid is None:
            return
        if self._use_port_path() and self._templates_presenter is not None:
            scope, project_id = self._scope_and_project_for_mutations()
            cmd = CopyPromptTemplateCommand(source_template_id=int(tid), scope=scope, project_id=project_id)
            result = self._templates_presenter.handle_copy_template_to_prompt(cmd)
            if result.ok and result.snapshot is not None:
                self.template_copied_to_prompt.emit(prompt_from_snapshot(result.snapshot))
            elif not result.ok:
                QMessageBox.critical(
                    self,
                    "Fehler",
                    result.error_message or "Prompt konnte nicht erstellt werden.",
                )
            return
        self._on_copy_to_prompt_legacy(template)

    def _on_copy_to_prompt_legacy(self, template: Prompt) -> None:
        try:
            from app.prompts import Prompt, get_prompt_service
            from app.core.context.project_context_manager import get_project_context_manager

            svc = get_prompt_service()
            mgr = get_project_context_manager()
            scope = "project" if mgr.get_active_project_id() else "global"
            project_id = mgr.get_active_project_id()
            new_prompt = Prompt(
                id=None,
                title=f"Von Template: {template.title or 'Unbenannt'}",
                category=template.category,
                description=template.description or "",
                content=template.content or "",
                tags=list(getattr(template, "tags", []) or []),
                prompt_type="user",
                scope=scope,
                project_id=project_id,
                created_at=None,
                updated_at=None,
            )
            created = svc.create(new_prompt)
            if created:
                self.template_copied_to_prompt.emit(created)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", f"Prompt konnte nicht erstellt werden: {e}")

    def _on_delete(self, template: Prompt) -> None:
        tid = getattr(template, "id", None)
        if tid is None:
            return
        if (
            QMessageBox.question(
                self,
                "Template löschen",
                f"Template „{template.title}“ wirklich löschen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            != QMessageBox.StandardButton.Yes
        ):
            return
        if self._use_port_path() and self._templates_presenter is not None:
            result = self._templates_presenter.handle_delete_template(
                DeletePromptTemplateCommand(int(tid)),
                refresh_project_id=self._current_project_id,
                refresh_filter_text=self._templates_refresh_filter_text(),
            )
            if not result.ok and result.error_message:
                QMessageBox.warning(self, "Template löschen", result.error_message)
            return
        self._on_delete_legacy(int(tid))

    def _on_delete_legacy(self, template_id: int) -> None:
        try:
            from app.prompts.prompt_service import get_prompt_service

            if get_prompt_service().delete(template_id):
                self.refresh()
        except Exception:
            pass

    def refresh(self) -> None:
        if self._use_port_path() and self._templates_presenter is not None:
            ft = self._search.text().strip()
            self._templates_presenter.handle_command(
                LoadPromptTemplatesCommand(self._current_project_id, ft),
            )
        else:
            self._load_templates_legacy()

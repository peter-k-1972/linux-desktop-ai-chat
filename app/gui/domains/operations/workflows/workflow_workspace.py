"""
WorkflowsWorkspace – Prozessdiagramm (Planungstafel): Liste, Canvas, Inspector, Run-Historie.

Layout: links Workflow-Liste, Mitte Canvas & Metadaten, rechts Knoten-Inspector,
unten Run-Historie (und Register „Geplant“).
"""

from __future__ import annotations

import copy
import logging
import sqlite3
from typing import Callable, Optional

from PySide6.QtCore import QObject, QRunnable, QThreadPool, QTimer, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QMessageBox,
    QSplitter,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from app.gui.domains.operations.workflows.dialogs.schedule_edit_dialog import ScheduleEditDialog
from app.gui.domains.operations.workflows.dialogs.workflow_create_dialog import WorkflowCreateDialog
from app.gui.domains.operations.workflows.dialogs.workflow_duplicate_dialog import WorkflowDuplicateDialog
from app.gui.domains.operations.workflows.dialogs.workflow_input_dialog import WorkflowInputDialog
from app.gui.domains.operations.workflows.panels.workflow_editor_panel import WorkflowEditorPanel
from app.gui.domains.operations.workflows.panels.workflow_inspector_panel import WorkflowInspectorPanel
from app.gui.domains.operations.workflows.panels.workflow_list_panel import WorkflowListPanel
from app.gui.domains.operations.workflows.panels.workflow_run_panel import WorkflowRunPanel
from app.gui.domains.operations.workflows.panels.workflow_schedule_panel import WorkflowSchedulePanel
from app.gui.domains.operations.workflows.run_status_mapper import (
    canvas_status_by_node_id,
    find_node_run_for_node,
)
from app.gui.shared.base_operations_workspace import BaseOperationsWorkspace
from app.services.schedule_service import ScheduleNotFoundError, get_schedule_service
from app.services.workflow_service import (
    IncompleteHistoricalRunError,
    RunNotFoundError,
    WorkflowNotFoundError,
    WorkflowValidationError,
    get_workflow_service,
)

_log = logging.getLogger(__name__)
from app.workflows.models.definition import WorkflowDefinition, WorkflowEdge, WorkflowNode
from app.workflows.serialization.json_io import definition_to_json


def _clone_definition(d: WorkflowDefinition) -> WorkflowDefinition:
    return WorkflowDefinition.from_dict(copy.deepcopy(d.to_dict()))


def _is_missing_workflow_table(exc: Exception) -> bool:
    """Headless/isolierte Tests: leere DB ohne Workflow-Schema nicht modal blockieren."""
    if not isinstance(exc, sqlite3.OperationalError):
        return False
    msg = str(exc).lower()
    return "no such table" in msg and (
        "workflows" in msg or "workflow_runs" in msg or "workflow_node_runs" in msg
    )


class _ScheduleRunSignals(QObject):
    finished = Signal(object)


class _ScheduleRunNowRunnable(QRunnable):
    def __init__(self, schedule_id: str, signals: _ScheduleRunSignals) -> None:
        super().__init__()
        self._schedule_id = schedule_id
        self._signals = signals

    def run(self) -> None:
        from app.services.schedule_service import get_schedule_service

        try:
            rid = get_schedule_service().run_now(self._schedule_id)
            self._signals.finished.emit(rid)
        except Exception as exc:
            self._signals.finished.emit(exc)


class WorkflowsWorkspace(BaseOperationsWorkspace):
    """Liste, Prozessdiagramm (Canvas), eingebetteter Inspector, Run-Historie."""

    def __init__(self, parent=None):
        super().__init__("workflows", parent)
        self._svc = get_workflow_service()
        self._inspector_host = None
        self._inspector_token: int | None = None
        self._working: Optional[WorkflowDefinition] = None
        self._loaded_id: Optional[str] = None
        self._dirty = False

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._list_panel = WorkflowListPanel(self)
        self._editor = WorkflowEditorPanel(self, planning_board=True)
        self._run_panel = WorkflowRunPanel(self)
        self._schedule_panel = WorkflowSchedulePanel(self)
        self._schedule_panel.set_last_run_resolver(
            lambda sid: get_schedule_service().get_last_run_id(sid)
        )
        self._run_tabs = QTabWidget()
        self._run_tabs.setObjectName("workflowRunsTabs")
        self._run_tabs.addTab(self._run_panel, "Run-Historie")
        self._run_tabs.addTab(self._schedule_panel, "Geplant")
        self._sched_pool = QThreadPool.globalInstance()
        self._sched_sig = _ScheduleRunSignals(self)
        self._sched_sig.finished.connect(self._on_schedule_run_now_done)

        self._inspector_panel = WorkflowInspectorPanel(
            on_apply=self._on_inspector_apply,
            node_types=[
                "start",
                "end",
                "noop",
                "prompt_build",
                "agent",
                "tool_call",
                "context_load",
                "chain_delegate",
            ],
            parent=self,
        )
        self._inspector_panel.setMinimumWidth(260)
        self._inspector_panel.setMaximumWidth(440)
        self._inspector_panel.apply_requested.connect(self._refresh_inspector_after_apply)

        center_col = QWidget()
        cv = QVBoxLayout(center_col)
        cv.setContentsMargins(0, 0, 0, 0)
        cv.setSpacing(0)
        split_v = QSplitter(Qt.Orientation.Vertical)
        split_v.addWidget(self._editor)
        split_v.addWidget(self._run_tabs)
        split_v.setStretchFactor(0, 4)
        split_v.setStretchFactor(1, 1)
        cv.addWidget(split_v)

        split_h = QSplitter(Qt.Orientation.Horizontal)
        split_h.addWidget(self._list_panel)
        split_h.addWidget(center_col)
        split_h.addWidget(self._inspector_panel)
        split_h.setStretchFactor(0, 0)
        split_h.setStretchFactor(1, 1)
        split_h.setStretchFactor(2, 0)
        self._list_panel.setMinimumWidth(240)
        self._list_panel.setMaximumWidth(400)
        root.addWidget(split_h)
        split_h.setSizes([280, 720, 300])
        split_v.setSizes([480, 220])

        self._project_event_handler = self._on_project_context_changed
        try:
            from app.gui.events.project_events import subscribe_project_events

            subscribe_project_events(self._project_event_handler)
            self.destroyed.connect(self._unsubscribe_project_events)
        except Exception:
            pass

        self._connect_signals()
        QTimer.singleShot(0, self._refresh_list)
        QTimer.singleShot(0, self._refresh_schedules)

    def _unsubscribe_project_events(self) -> None:
        try:
            from app.gui.events.project_events import unsubscribe_project_events

            unsubscribe_project_events(self._project_event_handler)
        except Exception:
            pass

    def _on_project_context_changed(self, _payload: dict) -> None:
        """Liste neu laden; Editor/Dirty bleiben unangetastet."""
        self._refresh_list()
        self._refresh_runs()
        self._refresh_schedules()

    def open_with_context(self, ctx: dict) -> None:
        """
        Pending-Kontext nach ``OperationsScreen.show_workspace`` (O4, R1).

        - ``workflow_ops_scope == "project"``: Run-Liste auf aktives Projekt, Refresh.
        - ``workflow_ops_run_id``: Fokus auf einen Run (z. B. aus Incident-UI).
          Mit ``workflow_ops_workflow_id`` und ohne Dirty-State wird der Workflow
          geladen und die Run-Liste gefiltert; sonst Modus „Alle Runs“ + Auswahl.
        - ``workflow_ops_select_workflow_id``: Definition laden (R2 Deep Link), wenn nicht dirty.
        """
        if not ctx:
            return
        run_id = (ctx.get("workflow_ops_run_id") or "").strip()
        wf_for_run = (ctx.get("workflow_ops_workflow_id") or "").strip()
        if run_id:
            if wf_for_run and not self._dirty:
                self._load_workflow_id(wf_for_run)
            else:
                self._run_panel.set_run_list_scope(WorkflowRunPanel.RUN_SCOPE_ALL, silent=True)
                self._refresh_runs()
            self._run_panel.select_run_by_id(run_id)
            return
        if ctx.get("workflow_ops_scope") == "project":
            self._run_panel.set_run_list_scope(WorkflowRunPanel.RUN_SCOPE_PROJECT, silent=True)
            self._refresh_runs()
        select_wf = (ctx.get("workflow_ops_select_workflow_id") or "").strip()
        if select_wf and not self._dirty:
            self._refresh_list()
            self._load_workflow_id(select_wf)

    def _project_label_fn(self) -> Callable[[Optional[int]], str]:
        names: dict[int, str] = {}
        try:
            from app.services.project_service import get_project_service

            for p in get_project_service().list_projects():
                pid = p.get("project_id")
                if pid is None:
                    continue
                names[int(pid)] = (p.get("name") or "").strip() or f"Projekt {pid}"
        except Exception:
            pass

        def label(pid: Optional[int]) -> str:
            if pid is None:
                return "Global"
            return names.get(pid, f"Projekt #{pid}")

        return label

    def _connect_signals(self) -> None:
        self._list_panel.selection_workflow_id_changed.connect(self._on_list_selection)
        self._list_panel.refresh_requested.connect(self._refresh_list)
        self._list_panel.new_requested.connect(self._on_new_workflow)
        self._list_panel.delete_requested.connect(self._on_delete_workflow)
        self._list_panel.duplicate_requested.connect(self._on_duplicate_workflow)

        self._editor.content_modified.connect(self._mark_dirty)
        self._editor.node_selection_changed.connect(self._on_node_selection)
        self._editor.save_requested.connect(self._on_save)
        self._editor.validate_requested.connect(self._on_validate_only)
        self._editor.test_run_requested.connect(self._on_test_run)
        self._editor.reload_requested.connect(self._on_reload)
        self._editor.export_json_requested.connect(self._on_export_json)

        self._run_panel.refresh_requested.connect(self._refresh_runs)
        self._run_panel.test_run_requested.connect(self._on_test_run)
        self._run_panel.rerun_requested.connect(self._on_rerun)
        self._run_panel.scope_or_filter_changed.connect(self._refresh_runs)
        self._run_panel.run_selection_changed.connect(self._on_run_panel_run_changed)
        self._run_panel.node_run_selection_changed.connect(self._on_run_panel_node_run_changed)
        self._run_panel.jump_to_node_requested.connect(self._editor.select_node_by_id)

        self._schedule_panel.refresh_requested.connect(self._refresh_schedules)
        self._schedule_panel.new_requested.connect(self._on_schedule_new)
        self._schedule_panel.edit_requested.connect(self._on_schedule_edit)
        self._schedule_panel.delete_requested.connect(self._on_schedule_delete)
        self._schedule_panel.toggle_enabled_requested.connect(self._on_schedule_toggle)
        self._schedule_panel.run_now_requested.connect(self._on_schedule_run_now)
        self._schedule_panel.jump_to_run_requested.connect(self._on_schedule_jump_run)

    def _refresh_schedules(self) -> None:
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            scope_pid = get_project_context_manager().get_active_project_id()
            rows = get_schedule_service().list_schedules(
                project_scope_id=scope_pid,
                include_global=True,
            )
            self._schedule_panel.set_schedules(rows)
        except Exception as e:
            _log.warning("Schedules konnten nicht geladen werden: %s", e)

    @Slot(object)
    def _on_schedule_run_now_done(self, payload: object) -> None:
        if isinstance(payload, Exception):
            QMessageBox.critical(self, "Schedule", str(payload))
            return
        rid = str(payload)
        QMessageBox.information(self, "Schedule", f"Run abgeschlossen: {rid}")
        self._refresh_runs()
        self._run_panel.select_run_by_id(rid)
        self._refresh_schedules()

    def _on_schedule_run_now(self, schedule_id: str) -> None:
        self._sched_pool.start(_ScheduleRunNowRunnable(schedule_id, self._sched_sig))

    def _on_schedule_jump_run(self, run_id: str) -> None:
        self._run_panel.set_run_list_scope(WorkflowRunPanel.RUN_SCOPE_ALL, silent=True)
        self._refresh_runs()
        self._run_panel.select_run_by_id(run_id)

    def _on_schedule_new(self) -> None:
        dlg = ScheduleEditDialog(self, default_workflow_id=self._loaded_id or "")
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        data = dlg.get_result()
        try:
            get_schedule_service().create_schedule(
                workflow_id=data["workflow_id"],
                initial_input_json=data["initial_input_json"],
                next_run_at=data["next_run_at"],
                rule_json=data["rule_json"],
                enabled=data["enabled"],
            )
        except Exception as e:
            QMessageBox.critical(self, "Schedule", str(e))
            return
        self._refresh_schedules()

    def _on_schedule_edit(self, schedule_id: str) -> None:
        try:
            sch = get_schedule_service().get_schedule(schedule_id)
        except ScheduleNotFoundError:
            QMessageBox.warning(self, "Schedule", "Eintrag nicht gefunden.")
            self._refresh_schedules()
            return
        dlg = ScheduleEditDialog(self, schedule=sch)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        data = dlg.get_result()
        try:
            get_schedule_service().update_schedule(
                schedule_id,
                workflow_id=data["workflow_id"],
                initial_input_json=data["initial_input_json"],
                next_run_at=data["next_run_at"],
                rule_json=data["rule_json"],
                enabled=data["enabled"],
            )
        except Exception as e:
            QMessageBox.critical(self, "Schedule", str(e))
            return
        self._refresh_schedules()

    def _on_schedule_delete(self, schedule_id: str) -> None:
        r = QMessageBox.question(
            self,
            "Schedule löschen",
            f"Schedule {schedule_id!r} wirklich löschen?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if r != QMessageBox.StandardButton.Yes:
            return
        get_schedule_service().delete_schedule(schedule_id)
        self._refresh_schedules()

    def _on_schedule_toggle(self, schedule_id: str, enabled: bool) -> None:
        try:
            get_schedule_service().update_schedule(schedule_id, enabled=enabled)
        except Exception as e:
            QMessageBox.warning(self, "Schedule", str(e))
            return
        self._refresh_schedules()

    def _mark_dirty(self) -> None:
        self._dirty = True

    def _clear_dirty(self) -> None:
        self._dirty = False

    def _confirm_discard(self, title: str, text: str) -> bool:
        """True = verwerfen und fortfahren, False = abbrechen."""
        if not self._dirty:
            return True
        m = QMessageBox(self)
        m.setIcon(QMessageBox.Icon.Question)
        m.setWindowTitle(title)
        m.setText(text)
        save_btn = m.addButton("Speichern", QMessageBox.ButtonRole.AcceptRole)
        discard_btn = m.addButton("Verwerfen", QMessageBox.ButtonRole.DestructiveRole)
        cancel_btn = m.addButton("Abbrechen", QMessageBox.ButtonRole.RejectRole)
        m.exec()
        clicked = m.clickedButton()
        if clicked == cancel_btn:
            return False
        if clicked == save_btn:
            if not self._on_save():
                return False
        else:
            self._clear_dirty()
        return True

    def _on_list_selection(self, workflow_id: object) -> None:
        wid = workflow_id if isinstance(workflow_id, str) else None
        if wid is None:
            if not self._confirm_discard(
                "Ungespeicherte Änderungen",
                "Änderungen am aktuellen Workflow speichern?",
            ):
                if self._loaded_id:
                    self._list_panel.select_workflow_id(self._loaded_id)
                return
            self._working = None
            self._loaded_id = None
            self._editor.set_definition(None)
            self._editor.set_run_node_status_overlay(None)
            self._run_panel.set_workflow_id(None)
            self._run_panel.set_jump_context_workflow_id(None)
            self._refresh_inspector_empty()
            self._clear_dirty()
            self._refresh_runs()
            return

        if wid == self._loaded_id and not self._dirty:
            return

        if not self._confirm_discard(
            "Ungespeicherte Änderungen",
            "Änderungen speichern, bevor ein anderer Workflow geladen wird?",
        ):
            if self._loaded_id:
                self._list_panel.select_workflow_id(self._loaded_id)
            return

        self._load_workflow_id(wid)

    def _load_workflow_id(self, wid: str) -> None:
        try:
            raw = self._svc.load_workflow(wid)
        except WorkflowNotFoundError:
            QMessageBox.warning(self, "Workflow", f"Workflow {wid!r} nicht gefunden.")
            self._refresh_list()
            return
        self._working = _clone_definition(raw)
        self._loaded_id = wid
        auto_filled = self._editor.set_definition(self._working)
        self._run_panel.set_workflow_id(wid)
        self._run_panel.set_jump_context_workflow_id(wid)
        self._refresh_runs()
        if auto_filled == 0:
            self._clear_dirty()
        self._list_panel.select_workflow_id(wid)
        self._on_node_selection(self._editor.selected_node_id())

    def _refresh_list(self) -> None:
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            scope_pid = get_project_context_manager().get_active_project_id()
            items = self._svc.list_workflows(
                project_scope_id=scope_pid,
                include_global=True,
            )
        except Exception as e:
            if _is_missing_workflow_table(e):
                _log.warning("Workflow-Liste ohne Schema geladen; zeige leere Liste: %s", e)
                scope_pid = None
                items = []
            else:
                QMessageBox.critical(self, "Fehler", f"Liste konnte nicht geladen werden:\n{e}")
                return
        if scope_pid is None:
            hint = "Kein aktives Projekt: alle Workflows."
        else:
            hint = "Aktives Projekt und globale Workflows (Projektzuordnung „Global“)."
        self._list_panel.set_filter_hint(hint)
        self._list_panel.set_workflows(
            items,
            project_label=self._project_label_fn(),
            reselect_id=self._loaded_id,
        )

    def _refresh_runs(self) -> None:
        from app.gui.domains.operations.workflows.panels.workflow_run_panel import WorkflowRunPanel

        scope = self._run_panel.run_list_scope()
        st = self._run_panel.status_filter_value()
        try:
            if scope == WorkflowRunPanel.RUN_SCOPE_WORKFLOW:
                if not self._loaded_id:
                    self._run_panel.set_run_summaries(
                        [],
                        scope_caption="Modus: Dieser Workflow — kein Workflow geladen.",
                        empty_hint="Bitte einen Workflow in der Liste auswählen.",
                    )
                    return
                caption = f"Modus: Dieser Workflow (ID {self._loaded_id})."
                sums = self._svc.list_run_summaries(workflow_id=self._loaded_id, status=st)
            elif scope == WorkflowRunPanel.RUN_SCOPE_PROJECT:
                try:
                    from app.core.context.project_context_manager import get_project_context_manager

                    pid = get_project_context_manager().get_active_project_id()
                except Exception:
                    pid = None
                if pid is None:
                    self._run_panel.set_run_summaries(
                        [],
                        scope_caption="Modus: Aktives Projekt — kein Projekt aktiv.",
                        empty_hint="Aktivieren Sie ein Projekt (z. B. über Projekte oder die TopBar).",
                    )
                    return
                caption = (
                    f"Modus: Aktives Projekt (project_id={pid}). "
                    "Nur Runs von Workflows mit dieser Projektzuordnung (nicht globale Workflows)."
                )
                sums = self._svc.list_run_summaries(project_id=pid, status=st)
            else:
                caption = "Modus: Alle Runs — alle Workflows inkl. globaler Definitionen."
                sums = self._svc.list_run_summaries(status=st)
            self._run_panel.set_run_summaries(
                sums,
                scope_caption=caption,
                empty_hint="Keine Runs für die aktuelle Filterkombination."
                if len(sums) == 0
                else "",
            )
        except Exception as e:
            if _is_missing_workflow_table(e):
                _log.warning("Workflow-Runs ohne Schema geladen; zeige leere Liste: %s", e)
                self._run_panel.set_run_summaries(
                    [],
                    scope_caption="Modus: Runs derzeit nicht verfuegbar.",
                    empty_hint="Workflow-Run-Tabellen sind noch nicht initialisiert.",
                )
                return
            QMessageBox.warning(self, "Runs", f"Runs konnten nicht geladen werden:\n{e}")

    def _on_new_workflow(self) -> None:
        if not self._confirm_discard(
            "Neuer Workflow",
            "Aktuelle Änderungen vor dem Anlegen speichern?",
        ):
            return
        dlg = WorkflowCreateDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        wid = dlg.workflow_id()
        name = dlg.workflow_name()
        if not wid:
            QMessageBox.warning(self, "Fehler", "Bitte eine Workflow-ID eingeben.")
            return
        if not name:
            name = wid
        try:
            self._svc.load_workflow(wid)
            exists = True
        except WorkflowNotFoundError:
            exists = False
        if exists:
            r = QMessageBox.question(
                self,
                "Workflow existiert",
                f"Die ID {wid!r} existiert bereits. Überschreiben?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if r != QMessageBox.StandardButton.Yes:
                return
        try:
            from app.core.context.project_context_manager import get_project_context_manager

            active_pid = get_project_context_manager().get_active_project_id()
        except Exception:
            active_pid = None
        wf = WorkflowDefinition(
            workflow_id=wid,
            name=name,
            description=dlg.description(),
            nodes=[
                WorkflowNode("start", "start", title="Start"),
                WorkflowNode("end", "end", title="End"),
            ],
            edges=[WorkflowEdge("e1", "start", "end")],
            project_id=active_pid,
        )
        try:
            vr = self._svc.save_workflow(wf)
            msg = "Gespeichert."
            if not vr.is_valid:
                msg += "\n\nValidierung: " + "\n".join(vr.errors[:8])
                if vr.warnings:
                    msg += "\n\nWarnungen:\n" + "\n".join(vr.warnings[:5])
            QMessageBox.information(self, "Workflow", msg)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))
            return
        self._refresh_list()
        self._load_workflow_id(wid)

    def _on_delete_workflow(self) -> None:
        wid = self._list_panel.current_workflow_id()
        if not wid:
            QMessageBox.information(self, "Löschen", "Bitte einen Workflow auswählen.")
            return
        r = QMessageBox.question(
            self,
            "Workflow löschen",
            f"Workflow {wid!r} wirklich löschen (inkl. Runs)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if r != QMessageBox.StandardButton.Yes:
            return
        try:
            self._svc.delete_workflow(wid)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))
            return
        if self._loaded_id == wid:
            self._working = None
            self._loaded_id = None
            self._editor.set_definition(None)
            self._run_panel.set_workflow_id(None)
            self._run_panel.set_jump_context_workflow_id(None)
            self._refresh_inspector_empty()
            self._clear_dirty()
            self._refresh_runs()
        self._refresh_list()

    def _on_duplicate_workflow(self) -> None:
        wid = self._list_panel.current_workflow_id()
        if not wid:
            QMessageBox.information(self, "Duplizieren", "Bitte einen Workflow auswählen.")
            return
        try:
            src = self._svc.load_workflow(wid)
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))
            return
        dlg = WorkflowDuplicateDialog(wid, f"{src.name} (Kopie)", self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        new_id = dlg.new_workflow_id()
        if not new_id:
            QMessageBox.warning(self, "Fehler", "Bitte eine neue Workflow-ID eingeben.")
            return
        try:
            self._svc.duplicate_workflow(wid, new_id, dlg.new_name())
        except ValueError as e:
            QMessageBox.warning(self, "Duplizieren", str(e))
            return
        except Exception as e:
            QMessageBox.critical(self, "Fehler", str(e))
            return
        self._refresh_list()
        if not self._confirm_discard(
            "Duplikat geöffnet",
            "Aktuelle Änderungen vor dem Öffnen des Duplikats speichern?",
        ):
            self._list_panel.select_workflow_id(wid)
            return
        self._load_workflow_id(new_id)

    def _on_save(self) -> bool:
        if not self._working:
            QMessageBox.information(self, "Speichern", "Kein Workflow geladen.")
            return False
        try:
            vr = self._svc.save_workflow(self._working)
        except Exception as e:
            QMessageBox.critical(self, "Speichern", str(e))
            return False
        self._editor.refresh_header_labels()
        lines = []
        if vr.is_valid:
            lines.append("Workflow ist valide und gespeichert.")
        else:
            lines.append("Gespeichert mit Validierungsfehlern:")
            lines.extend(vr.errors)
        if vr.warnings:
            lines.append("")
            lines.append("Warnungen:")
            lines.extend(vr.warnings)
        QMessageBox.information(self, "Validierung / Speichern", "\n".join(lines))
        self._clear_dirty()
        self._refresh_list()
        if self._loaded_id:
            self._working = _clone_definition(self._svc.load_workflow(self._loaded_id))
            self._editor.set_definition(self._working)
        return True

    def _on_validate_only(self) -> None:
        if not self._working:
            return
        vr = self._svc.validate_workflow(self._working)
        lines = []
        if vr.is_valid:
            lines.append("Valid: keine strukturellen Fehler.")
        else:
            lines.append("Ungültig:")
            lines.extend(vr.errors)
        if vr.warnings:
            lines.append("")
            lines.append("Warnungen:")
            lines.extend(vr.warnings)
        QMessageBox.information(self, "Validierung", "\n".join(lines))

    def _on_reload(self) -> None:
        if not self._loaded_id:
            self._editor.set_definition(None)
            self._clear_dirty()
            return
        if self._dirty:
            r = QMessageBox.question(
                self,
                "Verwerfen",
                "Alle ungespeicherten Änderungen verwerfen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if r != QMessageBox.StandardButton.Yes:
                return
        self._load_workflow_id(self._loaded_id)

    def _on_export_json(self) -> None:
        if not self._working:
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Workflow als JSON",
            f"{self._working.workflow_id}.json",
            "JSON (*.json)",
        )
        if not path:
            return
        try:
            text = definition_to_json(self._working, indent=2)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
        except OSError as e:
            QMessageBox.critical(self, "Export", str(e))

    def _on_test_run(self) -> None:
        if not self._loaded_id or not self._working:
            QMessageBox.information(self, "Test-Run", "Bitte zuerst einen Workflow laden.")
            return
        vr = self._svc.validate_workflow(self._working)
        if not vr.is_valid:
            QMessageBox.warning(
                self,
                "Test-Run",
                "Workflow ist ungültig:\n" + "\n".join(vr.errors[:12]),
            )
            return
        if self._dirty:
            r = QMessageBox.question(
                self,
                "Test-Run",
                "Ungespeicherte Änderungen – vor dem Run speichern?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            )
            if r == QMessageBox.StandardButton.Cancel:
                return
            if r == QMessageBox.StandardButton.Yes and not self._on_save():
                return
        dlg = WorkflowInputDialog(self)
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            run = self._svc.start_run(self._loaded_id, dlg.get_input())
        except WorkflowValidationError as e:
            QMessageBox.warning(self, "Test-Run", "Validierung:\n" + "\n".join(e.errors))
            return
        except Exception as e:
            QMessageBox.critical(self, "Test-Run", str(e))
            return
        QMessageBox.information(
            self,
            "Test-Run",
            f"Run {run.run_id} abgeschlossen mit Status {run.status.value}.",
        )
        self._refresh_runs()
        self._run_panel.select_run_by_id(run.run_id)

    def _on_rerun(self) -> None:
        run = self._run_panel.current_run()
        if not run:
            return
        if not (run.workflow_id or "").strip():
            QMessageBox.warning(
                self,
                "Re-Run",
                "Für diesen Lauf fehlt eine gültige Workflow-ID; ein erneuter Start ist nicht möglich.",
            )
            return
        r = QMessageBox.question(
            self,
            "Re-Run",
            "Es wird ein neuer Run gestartet; bestehende Einträge in der Historie bleiben unverändert.\n\n"
            "Externe Nebenwirkungen (z. B. Tool-Aufrufe) können erneut ausgelöst werden.\n\n"
            "Fortfahren?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.Yes,
        )
        if r != QMessageBox.StandardButton.Yes:
            return
        dlg = WorkflowInputDialog(
            self,
            window_title="Re-Run – Eingabe (JSON)",
            initial_input=dict(run.initial_input or {}),
        )
        if dlg.exec() != QDialog.DialogCode.Accepted:
            return
        try:
            new_run = self._svc.start_run_from_previous(run.run_id, dlg.get_input())
        except RunNotFoundError:
            QMessageBox.warning(self, "Re-Run", "Der ausgewählte Lauf wurde nicht gefunden.")
            self._refresh_runs()
            return
        except IncompleteHistoricalRunError as e:
            QMessageBox.warning(self, "Re-Run", str(e))
            return
        except WorkflowValidationError as e:
            QMessageBox.warning(self, "Re-Run", "Validierung:\n" + "\n".join(e.errors))
            return
        except WorkflowNotFoundError:
            QMessageBox.warning(
                self,
                "Re-Run",
                f"Workflow {run.workflow_id!r} ist nicht mehr vorhanden.",
            )
            return
        except Exception as e:
            QMessageBox.critical(self, "Re-Run", str(e))
            return
        QMessageBox.information(
            self,
            "Re-Run",
            f"Neuer Run {new_run.run_id} abgeschlossen mit Status {new_run.status.value}.",
        )
        self._refresh_runs()
        self._run_panel.select_run_by_id(new_run.run_id)

    def _on_run_panel_run_changed(self, run_id: object) -> None:
        rid = run_id if isinstance(run_id, str) else None
        if rid:
            try:
                run = self._svc.get_run(rid)
                self._run_panel.set_full_run_detail(run)
            except RunNotFoundError:
                self._run_panel.clear_full_run_detail()
                rid = None
            except Exception as e:
                _log.warning("Run-Detail: get_run(%r) fehlgeschlagen: %s", rid, e)
                self._run_panel.clear_full_run_detail()
                rid = None
        else:
            self._run_panel.clear_full_run_detail()
        self._sync_canvas_run_overlay(rid)
        sid = self._editor.selected_node_id()
        self._apply_inspector_run_excerpt(sid if isinstance(sid, str) else None)
        self._run_panel.sync_node_run_selection_to_node_id(sid if isinstance(sid, str) else None)

    def _on_run_panel_node_run_changed(self, node_id: object) -> None:
        run = self._run_panel.current_run()
        if run and self._loaded_id and run.workflow_id != self._loaded_id:
            self._inspector_panel.set_run_node_context(None)
            return
        nid = node_id if isinstance(node_id, str) else None
        if nid:
            self._editor.select_node_by_id(nid)
        else:
            sid = self._editor.selected_node_id()
            self._apply_inspector_run_excerpt(sid if isinstance(sid, str) else None)

    def _sync_canvas_run_overlay(self, run_id: Optional[str]) -> None:
        if not self._working:
            self._editor.set_run_node_status_overlay(None)
            return
        nids = [n.node_id for n in self._working.nodes]
        if not run_id:
            self._editor.set_run_node_status_overlay(None)
            return
        run = self._run_panel.current_run()
        if run is None or run.run_id != run_id:
            try:
                run = self._svc.get_run(run_id)
            except RunNotFoundError:
                self._editor.set_run_node_status_overlay(None)
                return
            except Exception as e:
                _log.warning("Run-Overlay: get_run(%r) fehlgeschlagen: %s", run_id, e)
                self._editor.set_run_node_status_overlay(None)
                return
        if not self._loaded_id or run.workflow_id != self._loaded_id:
            self._editor.set_run_node_status_overlay(None)
            return
        self._editor.set_run_node_status_overlay(canvas_status_by_node_id(nids, run.node_runs))

    def _apply_inspector_run_excerpt(self, node_id: Optional[str]) -> None:
        if not node_id or not self._working:
            self._inspector_panel.set_run_node_context(None)
            return
        run = self._run_panel.current_run()
        if not run or not self._loaded_id or run.workflow_id != self._loaded_id:
            self._inspector_panel.set_run_node_context(None)
            return
        self._inspector_panel.set_run_node_context(find_node_run_for_node(run.node_runs, node_id))

    def _on_node_selection(self, node_id: object) -> None:
        nid = node_id if isinstance(node_id, str) else None
        if not self._working or not nid:
            self._inspector_panel.clear()
            self._run_panel.sync_node_run_selection_to_node_id(None)
            return
        node = next((n for n in self._working.nodes if n.node_id == nid), None)
        if node is None:
            self._inspector_panel.clear()
            self._run_panel.sync_node_run_selection_to_node_id(None)
            return
        self._inspector_panel.show_node(node)
        self._apply_inspector_run_excerpt(nid)
        self._run_panel.sync_node_run_selection_to_node_id(nid)

    def _on_inspector_apply(
        self,
        *,
        old_node_id: str,
        new_node_id: str,
        node_type: str,
        title: str,
        description: str,
        is_enabled: bool,
        config: dict,
    ) -> Optional[str]:
        return self._editor.apply_inspector_to_model(
            old_node_id,
            new_node_id,
            node_type,
            title,
            description,
            is_enabled,
            config,
        )

    def _refresh_inspector_empty(self) -> None:
        self._inspector_panel.clear()

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        self._inspector_host = inspector_host
        self._inspector_token = content_token
        if self._inspector_host:
            self._inspector_host.clear_content()
        self._on_node_selection(self._editor.selected_node_id())

    def _refresh_inspector_after_apply(self) -> None:
        nid = self._editor.selected_node_id()
        self._on_node_selection(nid)

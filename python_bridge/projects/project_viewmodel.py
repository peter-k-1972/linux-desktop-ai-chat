"""
QML-Kontextobjekt ``projectStudio``: Projekt-War-Room (Liste, Übersicht, Inspector).

Selection and ``set_active_project`` stay aligned with ProjectContextManager via
:class:`QmlProjectWarRoomPort` (same path as the PySide6 Projects workspace).

Properties: projects, selectedProjectId, selectedProject (Name), chats, workflows,
           agents, files, description, contextRules, defaultContextMode,
           authorityActiveProjectId, selectionMatchesAuthority.
Slots: selectProject, createProject, deleteProject, reload
"""

from __future__ import annotations

import json
import logging
from typing import Any

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.gui.events.project_events import subscribe_project_events, unsubscribe_project_events
from app.projects.models import (
    format_context_rules_narrative,
    format_default_context_policy_caption,
)
from app.ui_application.adapters.service_qml_project_war_room_adapter import ServiceQmlProjectWarRoomAdapter
from app.ui_application.ports.qml_project_war_room_port import QmlProjectWarRoomPort

from python_bridge.projects.project_row_models import (
    ProjectAgentRowModel,
    ProjectChatRowModel,
    ProjectFileRowModel,
    ProjectSummaryListModel,
    ProjectWorkflowRowModel,
)

logger = logging.getLogger(__name__)


def _str_or_dash(v: Any) -> str:
    if v is None:
        return ""
    s = str(v).strip()
    return s if s else ""


class ProjectViewModel(QObject):
    projectsChanged = Signal()
    selectedProjectIdChanged = Signal()
    descriptionChanged = Signal()
    contextRulesChanged = Signal()
    defaultContextModeChanged = Signal()
    selectedProjectChanged = Signal()
    lastErrorChanged = Signal()
    authorityActiveProjectIdChanged = Signal()
    selectionMatchesAuthorityChanged = Signal()

    def __init__(
        self,
        port: QmlProjectWarRoomPort | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._port: QmlProjectWarRoomPort = port or ServiceQmlProjectWarRoomAdapter()
        self._projects = ProjectSummaryListModel(self)
        self._chats = ProjectChatRowModel(self)
        self._workflows = ProjectWorkflowRowModel(self)
        self._agents = ProjectAgentRowModel(self)
        self._files = ProjectFileRowModel(self)
        self._selected_id: int | None = None
        self._description = ""
        self._context_rules = ""
        self._default_context_mode = ""
        self._selected_name = ""
        self._last_error = ""
        self._authority_active_id: int | None = None
        self._selection_matches_authority = True
        self._project_event_handler = self._on_project_context_changed
        subscribe_project_events(self._project_event_handler)
        self.reload()

    def dispose(self) -> None:
        """Detach global project listeners (tests / teardown)."""
        try:
            unsubscribe_project_events(self._project_event_handler)
        except Exception:
            pass

    # --- models ---
    def _get_projects(self) -> ProjectSummaryListModel:
        return self._projects

    projects = Property(QObject, _get_projects, notify=projectsChanged)

    def _get_chats(self) -> ProjectChatRowModel:
        return self._chats

    chats = Property(QObject, _get_chats, constant=True)

    def _get_workflows(self) -> ProjectWorkflowRowModel:
        return self._workflows

    workflows = Property(QObject, _get_workflows, constant=True)

    def _get_agents(self) -> ProjectAgentRowModel:
        return self._agents

    agents = Property(QObject, _get_agents, constant=True)

    def _get_files(self) -> ProjectFileRowModel:
        return self._files

    files = Property(QObject, _get_files, constant=True)

    def _get_sel(self) -> int:
        return int(self._selected_id) if self._selected_id is not None else -1

    selectedProjectId = Property(int, _get_sel, notify=selectedProjectIdChanged)

    def _get_desc(self) -> str:
        return self._description

    description = Property(str, _get_desc, notify=descriptionChanged)

    def _get_ctx(self) -> str:
        return self._context_rules

    contextRules = Property(str, _get_ctx, notify=contextRulesChanged)

    def _get_mode(self) -> str:
        return self._default_context_mode

    defaultContextMode = Property(str, _get_mode, notify=defaultContextModeChanged)

    def _get_sel_project(self) -> str:
        return self._selected_name

    selectedProject = Property(str, _get_sel_project, notify=selectedProjectChanged)

    def _get_err(self) -> str:
        return self._last_error

    lastError = Property(str, _get_err, notify=lastErrorChanged)

    def _get_authority_id(self) -> int:
        return int(self._authority_active_id) if self._authority_active_id is not None else -1

    authorityActiveProjectId = Property(int, _get_authority_id, notify=authorityActiveProjectIdChanged)

    def _get_sel_matches(self) -> bool:
        return self._selection_matches_authority

    selectionMatchesAuthority = Property(bool, _get_sel_matches, notify=selectionMatchesAuthorityChanged)

    def _refresh_authority_snapshot(self) -> None:
        try:
            aid = self._port.get_active_project_id()
        except Exception:
            aid = None
        aid_i = int(aid) if aid is not None else None
        if self._authority_active_id != aid_i:
            self._authority_active_id = aid_i
            self.authorityActiveProjectIdChanged.emit()
        sel = self._selected_id
        match = sel is None and aid_i is None or (sel is not None and aid_i is not None and sel == aid_i)
        if self._selection_matches_authority != match:
            self._selection_matches_authority = match
            self.selectionMatchesAuthorityChanged.emit()

    def _on_project_context_changed(self, payload: dict[str, Any]) -> None:
        pid = payload.get("project_id")
        if pid is None:
            if self._selected_id is not None:
                self._selected_id = None
                self.selectedProjectIdChanged.emit()
                self._projects.set_selected(None)
                self._clear_detail_models()
            self._refresh_authority_snapshot()
            return
        try:
            pid_i = int(pid)
        except (TypeError, ValueError):
            self._refresh_authority_snapshot()
            return
        if self._selected_id == pid_i:
            self._refresh_authority_snapshot()
            return
        ids = self._projects.project_ids()
        if pid_i not in ids:
            self.reload()
            return
        self._selected_id = pid_i
        self.selectedProjectIdChanged.emit()
        self._projects.set_selected(pid_i)
        self._load_detail(pid_i)
        self._refresh_authority_snapshot()

    def _clear_detail_models(self) -> None:
        self._chats.set_rows([])
        self._workflows.set_rows([])
        self._agents.set_rows([])
        self._files.set_rows([])
        self._set_inspector(None)

    def _set_inspector(self, project: dict | None) -> None:
        desc = _str_or_dash((project or {}).get("description")) or "—"
        rules = format_context_rules_narrative(project)
        mode = format_default_context_policy_caption(project)
        name = _str_or_dash((project or {}).get("name")) or ""
        if self._description != desc:
            self._description = desc
            self.descriptionChanged.emit()
        if self._context_rules != rules:
            self._context_rules = rules
            self.contextRulesChanged.emit()
        if self._default_context_mode != mode:
            self._default_context_mode = mode
            self.defaultContextModeChanged.emit()
        if self._selected_name != name:
            self._selected_name = name
            self.selectedProjectChanged.emit()

    def _build_project_rows(self, rows: list[dict]) -> list[dict[str, object]]:
        out: list[dict[str, object]] = []
        for p in rows:
            pid = p.get("project_id")
            if pid is None:
                continue
            try:
                snap = self._port.get_project_monitoring_snapshot(int(pid))
            except Exception:
                snap = {}
            msg7 = int(snap.get("message_count_7d") or 0)
            last_at = snap.get("last_activity_at") or ""
            last_s = (str(last_at)[:19] if last_at else "—").replace("T", " ")
            activity = f"{msg7} Nachr. · 7d · zuletzt {last_s}"
            life = _str_or_dash(p.get("lifecycle_status")) or "—"
            st = _str_or_dash(p.get("status")) or "—"
            status_line = f"{life} · {st}"
            out.append(
                {
                    "projectId": int(pid),
                    "name": _str_or_dash(p.get("name")) or f"Projekt {pid}",
                    "activity": activity,
                    "status": status_line,
                }
            )
        return out

    def _load_detail(self, project_id: int) -> None:
        proj = None
        try:
            proj = self._port.get_project(project_id)
        except Exception as exc:
            logger.debug("get_project failed: %s", exc)
        self._set_inspector(proj)

        chat_rows: list[dict[str, object]] = []
        try:
            raw = self._port.get_recent_chats_of_project(project_id, 8)
        except Exception:
            raw = []
        for c in raw:
            cid = c.get("id")
            title = _str_or_dash(c.get("title")) or f"Chat {cid}"
            la = c.get("last_activity") or c.get("created_at") or ""
            sub = f"zuletzt {str(la)[:19]}".replace("T", " ") if la else "—"
            chat_rows.append({"chatId": int(cid), "title": title, "subline": sub})
        self._chats.set_rows(chat_rows)

        wf_rows: list[dict[str, object]] = []
        try:
            defs = self._port.list_workflows_for_project(project_id, limit=24)
            for d in defs:
                wf_rows.append(
                    {
                        "workflowId": d.workflow_id,
                        "name": d.name or d.workflow_id,
                        "subline": f"v{d.version} · {getattr(d.status, 'value', d.status)}",
                    }
                )
        except Exception as exc:
            logger.debug("list_workflows: %s", exc)
        self._workflows.set_rows(wf_rows)

        ag_rows: list[dict[str, object]] = []
        try:
            profiles = self._port.list_active_agents_for_project(project_id)
            for a in profiles:
                nm = _str_or_dash(a.display_name) or _str_or_dash(a.name) or (a.id or "")
                dept = _str_or_dash(a.department) or "—"
                ag_rows.append(
                    {
                        "agentId": a.id or "",
                        "name": nm,
                        "subline": f"{a.status} · {dept}",
                    }
                )
        except Exception as exc:
            logger.debug("list_agents_for_project: %s", exc)
        self._agents.set_rows(ag_rows)

        file_rows: list[dict[str, object]] = []
        try:
            fl = self._port.list_files_of_project(project_id, limit=30)
            for f in fl:
                fid = f.get("id")
                name = _str_or_dash(f.get("name")) or f"Datei {fid}"
                path = _str_or_dash(f.get("path"))
                if len(path) > 56:
                    path = path[:24] + "…" + path[-24:]
                file_rows.append({"fileId": int(fid), "name": name, "subline": path or "—"})
        except Exception as exc:
            logger.debug("list_files_of_project: %s", exc)
        self._files.set_rows(file_rows)

    @Slot()
    def reload(self) -> None:
        self._last_error = ""
        self.lastErrorChanged.emit()
        try:
            plist = self._port.list_projects("")
        except Exception as exc:
            self._last_error = str(exc)
            self.lastErrorChanged.emit()
            plist = []
        rows = self._build_project_rows(plist) if plist else []
        sel = self._selected_id
        if sel is not None and not any(r["projectId"] == sel for r in rows):
            sel = None
            self._selected_id = None
            self.selectedProjectIdChanged.emit()
            self._clear_detail_models()
        self._projects.set_rows(rows, sel)
        self.projectsChanged.emit()
        self._apply_authority_after_reload()
        if self._selected_id is not None:
            self._load_detail(int(self._selected_id))
        else:
            self._clear_detail_models()
        self._refresh_authority_snapshot()

    def _apply_authority_after_reload(self) -> None:
        """Prefer ProjectContextManager when (re)loading the list."""
        try:
            aid = self._port.get_active_project_id()
        except Exception:
            aid = None
        if aid is None:
            return
        try:
            aid_i = int(aid)
        except (TypeError, ValueError):
            return
        ids = self._projects.project_ids()
        if aid_i not in ids:
            return
        self._selected_id = aid_i
        self.selectedProjectIdChanged.emit()
        self._projects.set_selected(aid_i)
        self._load_detail(aid_i)

    @Slot(int)
    def selectProject(self, project_id: int) -> None:
        if project_id < 0:
            if self._selected_id is not None:
                self._selected_id = None
                self.selectedProjectIdChanged.emit()
                self._projects.set_selected(None)
                self._clear_detail_models()
            try:
                self._port.clear_active_project()
            except Exception as exc:
                logger.debug("clear_active_project: %s", exc)
            self._refresh_authority_snapshot()
            return
        self._selected_id = int(project_id)
        self.selectedProjectIdChanged.emit()
        self._projects.set_selected(self._selected_id)
        try:
            self._port.set_active_project(project_id=self._selected_id)
        except Exception as exc:
            logger.debug("set_active_project: %s", exc)
        self._load_detail(self._selected_id)
        self._refresh_authority_snapshot()

    @Slot(str, str)
    def createProject(self, name: str, description: str = "") -> None:
        nm = (name or "").strip()
        if not nm:
            self._last_error = "Name fehlt."
            self.lastErrorChanged.emit()
            return
        try:
            pid = self._port.create_project(nm, description or "")
            self.reload()
            self.selectProject(int(pid))
        except Exception as exc:
            self._last_error = str(exc)
            self.lastErrorChanged.emit()

    @Slot(int)
    def deleteProject(self, project_id: int) -> None:
        if project_id < 0:
            return
        try:
            self._port.delete_project(int(project_id))
        except Exception as exc:
            self._last_error = str(exc)
            self.lastErrorChanged.emit()
            return
        if self._selected_id == int(project_id):
            self._selected_id = None
            self.selectedProjectIdChanged.emit()
            self._clear_detail_models()
        self.reload()
        self._refresh_authority_snapshot()

    @Slot(QObject)
    def shellNavigateToOperationsChat(self, shell: QObject | None) -> None:
        """Delegates to ``shell.requestRouteChange`` — no routing logic in QML."""
        if shell is None:
            return
        from app.core.navigation.nav_areas import NavArea

        shell.requestRouteChange(NavArea.OPERATIONS, "operations_chat")

    @Slot(QObject)
    def shellNavigateToOperationsWorkflowsProjectScope(self, shell: QObject | None) -> None:
        """Workflow list scoped to active project (``workflow_ops_scope`` = project)."""
        if shell is None:
            return
        from app.core.navigation.nav_areas import NavArea

        ctx = json.dumps({"workflow_ops_scope": "project"}, separators=(",", ":"), sort_keys=True)
        shell.requestRouteChangeWithContextJson(NavArea.OPERATIONS, "operations_workflows", ctx)

    @Slot(QObject, int)
    def shellNavigateToOperationsChatWithChatId(self, shell: QObject | None, chat_id: int) -> None:
        if shell is None or chat_id < 0:
            return
        from app.core.navigation.nav_areas import NavArea

        ctx = json.dumps({"chat_id": int(chat_id)}, separators=(",", ":"), sort_keys=True)
        shell.requestRouteChangeWithContextJson(NavArea.OPERATIONS, "operations_chat", ctx)

    @Slot(QObject, str)
    def shellNavigateToOperationsWorkflowWithId(self, shell: QObject | None, workflow_id: str) -> None:
        if shell is None:
            return
        from app.core.navigation.nav_areas import NavArea

        wid = (workflow_id or "").strip()
        if not wid:
            shell.requestRouteChange(NavArea.OPERATIONS, "operations_workflows")
            return
        ctx = json.dumps(
            {"workflow_ops_select_workflow_id": wid},
            separators=(",", ":"),
            sort_keys=True,
        )
        shell.requestRouteChangeWithContextJson(NavArea.OPERATIONS, "operations_workflows", ctx)

    @Slot(QObject, str)
    def shellNavigateToAgentTasksWithAgentId(self, shell: QObject | None, agent_id: str) -> None:
        if shell is None:
            return
        from app.core.navigation.nav_areas import NavArea

        raw = (agent_id or "").strip()
        if not raw:
            shell.requestRouteChange(NavArea.OPERATIONS, "operations_agent_tasks")
            return
        ctx = json.dumps(
            {"agent_ops_subtab": "betrieb", "agent_ops_focus_agent_id": raw},
            separators=(",", ":"),
            sort_keys=True,
        )
        shell.requestRouteChangeWithContextJson(NavArea.OPERATIONS, "operations_agent_tasks", ctx)


def build_project_viewmodel(
    port: QmlProjectWarRoomPort | None = None,
    parent: QObject | None = None,
) -> ProjectViewModel:
    return ProjectViewModel(port=port, parent=parent)

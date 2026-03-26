"""
QML-Kontextobjekt für die Agents-Domäne (``agentStudio``).

Properties: agents, selectedAgent, tasks (+ activityFeed für den Schreibtisch)
Slots: selectAgent, dispatchTask
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime

from PySide6.QtCore import Property, QObject, Signal, Slot

from app.agents.agent_profile import AgentProfile
from app.ui_application.adapters.service_qml_agent_roster_adapter import ServiceQmlAgentRosterAdapter
from app.ui_application.ports.qml_agent_roster_port import QmlAgentRosterPort

from python_bridge.agents.agent_models import ActivityFeedListModel, AgentRosterListModel, AgentTaskListModel

logger = logging.getLogger(__name__)


def _status_label(status: str) -> str:
    s = (status or "").lower()
    if s == "active":
        return "Bereit"
    if s == "inactive":
        return "Inaktiv"
    if s == "archived":
        return "Archiviert"
    return status or "—"


def _format_skills(p: AgentProfile) -> str:
    caps = [x for x in (p.capabilities or []) if (x or "").strip()]
    tools = [x for x in (p.tools or []) if (x or "").strip()]
    lines: list[str] = []
    if caps:
        lines.append("Fähigkeiten: " + ", ".join(caps))
    if tools:
        lines.append("Werkzeuge: " + ", ".join(tools))
    return "\n".join(lines) if lines else "—"


def _format_context(p: AgentProfile) -> str:
    parts: list[str] = []
    if (p.short_description or "").strip():
        parts.append(p.short_description.strip())
    ks = [x for x in (p.knowledge_spaces or []) if (x or "").strip()]
    if ks:
        parts.append("Wissensräume: " + ", ".join(ks))
    sp = (p.system_prompt or "").strip()
    if sp:
        excerpt = sp[:400] + ("…" if len(sp) > 400 else "")
        parts.append("Systemkontext (Auszug):\n" + excerpt)
    return "\n\n".join(parts) if parts else "—"


def _format_configuration(p: AgentProfile) -> str:
    lines: list[str] = []
    if p.assigned_model_role:
        lines.append(f"Modell-Rolle: {p.assigned_model_role}")
    if p.fallback_model:
        lines.append(f"Fallback-Modell: {p.fallback_model}")
    if p.memory_config:
        lines.append(f"Speicher: {p.memory_config}")
    if p.limits_config:
        lines.append(f"Limits: {p.limits_config}")
    lines.append(f"Cloud erlaubt: {'ja' if p.cloud_allowed else 'nein'}")
    lines.append(f"Sichtbar im Chat: {'ja' if p.visibility_in_chat else 'nein'}")
    lines.append(f"Priorität: {p.priority}")
    if p.department:
        lines.append(f"Abteilung: {p.department}")
    return "\n".join(lines)


class _SelectedAgentSurface(QObject):
    agentIdChanged = Signal()
    nameChanged = Signal()
    roleChanged = Signal()
    modelChanged = Signal()
    statusChanged = Signal()
    skillsTextChanged = Signal()
    contextTextChanged = Signal()
    configurationTextChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._agent_id: str = ""
        self._name: str = ""
        self._role: str = ""
        self._model: str = ""
        self._status: str = ""
        self._skills: str = ""
        self._context: str = ""
        self._configuration: str = ""

    def _get_id(self) -> str:
        return self._agent_id

    agentId = Property(str, _get_id, notify=agentIdChanged)

    def _get_name(self) -> str:
        return self._name

    name = Property(str, _get_name, notify=nameChanged)

    def _get_role(self) -> str:
        return self._role

    role = Property(str, _get_role, notify=roleChanged)

    def _get_model(self) -> str:
        return self._model

    model = Property(str, _get_model, notify=modelChanged)

    def _get_status(self) -> str:
        return self._status

    status = Property(str, _get_status, notify=statusChanged)

    def _get_skills(self) -> str:
        return self._skills

    skillsText = Property(str, _get_skills, notify=skillsTextChanged)

    def _get_context(self) -> str:
        return self._context

    contextText = Property(str, _get_context, notify=contextTextChanged)

    def _get_configuration(self) -> str:
        return self._configuration

    configurationText = Property(str, _get_configuration, notify=configurationTextChanged)

    def clear(self) -> None:
        self.apply(None)

    def apply(self, profile: AgentProfile | None) -> None:
        if profile is None or not profile.id:
            self._agent_id = ""
            self._name = ""
            self._role = ""
            self._model = ""
            self._status = ""
            self._skills = ""
            self._context = ""
            self._configuration = ""
        else:
            self._agent_id = profile.id
            self._name = profile.effective_display_name
            self._role = (profile.role or "").strip() or "—"
            self._model = (profile.assigned_model or "").strip() or "—"
            self._status = _status_label(profile.status)
            self._skills = _format_skills(profile)
            self._context = _format_context(profile)
            self._configuration = _format_configuration(profile)
        self.agentIdChanged.emit()
        self.nameChanged.emit()
        self.roleChanged.emit()
        self.modelChanged.emit()
        self.statusChanged.emit()
        self.skillsTextChanged.emit()
        self.contextTextChanged.emit()
        self.configurationTextChanged.emit()


class AgentViewModel(QObject):
    agentsChanged = Signal()
    selectedAgentChanged = Signal()
    tasksChanged = Signal()
    activityFeedChanged = Signal()

    def __init__(
        self,
        port: QmlAgentRosterPort | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._port: QmlAgentRosterPort = port or ServiceQmlAgentRosterAdapter()
        self._roster = AgentRosterListModel(self)
        self._tasks = AgentTaskListModel(self)
        self._activities = ActivityFeedListModel(self)
        self._selected = _SelectedAgentSurface(self)
        self._selected_id: str | None = None
        self._task_rows: list[dict[str, str]] = []
        self._activity_rows: list[dict[str, str]] = []
        self.reload_roster()

    def _get_roster(self) -> AgentRosterListModel:
        return self._roster

    agents = Property(QObject, _get_roster, notify=agentsChanged)

    def _get_selected(self) -> _SelectedAgentSurface:
        return self._selected

    selectedAgent = Property(QObject, _get_selected, notify=selectedAgentChanged)

    def _get_tasks(self) -> AgentTaskListModel:
        return self._tasks

    tasks = Property(QObject, _get_tasks, notify=tasksChanged)

    def _get_activities(self) -> ActivityFeedListModel:
        return self._activities

    activityFeed = Property(QObject, _get_activities, notify=activityFeedChanged)

    @Slot()
    def reload_roster(self) -> None:
        try:
            self._port.refresh_registry()
            profiles = self._port.list_all_profiles()
        except Exception:
            logger.exception("reload_roster")
            profiles = []
        sid = self._selected_id
        rows: list[dict[str, object]] = []
        for p in profiles:
            if not p.id:
                continue
            rows.append(
                {
                    "agentId": p.id,
                    "name": p.effective_display_name,
                    "role": (p.role or "").strip() or "—",
                    "assignedModel": (p.assigned_model or "").strip() or "—",
                    "status": _status_label(p.status),
                }
            )
        self._roster.set_agents(rows, sid)
        self.agentsChanged.emit()
        if sid:
            try:
                prof = self._port.get_profile(sid)
            except Exception:
                prof = None
            if prof:
                self._selected.apply(prof)
            else:
                self._selected.clear()
                self._selected_id = None
                self._roster.update_selection(None)

    def _push_activity(self, message: str) -> None:
        now = datetime.now().strftime("%H:%M")
        self._activity_rows.insert(0, {"message": message, "timeLabel": now})
        self._activity_rows = self._activity_rows[:50]
        self._activities.set_rows(list(self._activity_rows))
        self.activityFeedChanged.emit()

    def _sync_task_model(self) -> None:
        self._tasks.set_rows(list(self._task_rows))
        self.tasksChanged.emit()

    @Slot(str)
    def selectAgent(self, agent_id: str) -> None:  # noqa: N802
        aid = (agent_id or "").strip()
        if not aid:
            self._selected_id = None
            self._selected.clear()
            self._roster.update_selection(None)
            self.selectedAgentChanged.emit()
            return
        try:
            p = self._port.get_profile(aid)
        except Exception:
            logger.exception("selectAgent")
            p = None
        if p is None:
            return
        self._selected_id = aid
        self._selected.apply(p)
        self._roster.update_selection(aid)
        self.selectedAgentChanged.emit()

    @Slot(str)
    def dispatchTask(self, description: str) -> None:  # noqa: N802
        text = (description or "").strip()
        if not text:
            return
        if not self._selected_id:
            self._push_activity("Kein Agent gewählt — Auftrag verworfen.")
            return
        try:
            p = self._port.get_profile(self._selected_id)
        except Exception:
            p = None
        label = p.effective_display_name if p else self._selected_id
        tid = str(uuid.uuid4())[:8]
        now = datetime.now().strftime("%H:%M")
        self._task_rows.insert(
            0,
            {
                "taskId": tid,
                "title": text,
                "state": "Ausstehend",
                "agentLabel": label,
                "timeLabel": now,
            },
        )
        self._task_rows = self._task_rows[:40]
        self._sync_task_model()
        self._push_activity(f"Auftrag an {label}: {text}")

    @Slot(str)
    def applyShellPendingContextJson(self, json_str: str) -> None:
        """Subset of ``operations_context`` (``agent_ops_focus_agent_id``)."""
        raw = (json_str or "").strip()
        if not raw:
            return
        try:
            ctx = json.loads(raw)
        except json.JSONDecodeError:
            return
        if not isinstance(ctx, dict):
            return
        aid = (ctx.get("agent_ops_focus_agent_id") or "").strip()
        if aid:
            self.selectAgent(aid)


def build_agent_viewmodel() -> AgentViewModel:
    return AgentViewModel()

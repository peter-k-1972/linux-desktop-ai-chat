"""
AgentTasksWorkspace – R2 Betriebs-Sicht + bestehende Aufgaben.

AgentRegistryPanel, AgentOperationsDetailPanel (read-only), Task-Panels unverändert nutzbar.
"""

import asyncio

from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QGridLayout,
    QLabel,
    QTabWidget,
    QSplitter,
)
from PySide6.QtCore import Qt, QTimer

from app.gui.shared import apply_workspace_layout
from app.gui.shared.layout_constants import CARD_SPACING
from app.gui.shared.base_operations_workspace import BaseOperationsWorkspace
from app.gui.domains.operations.agent_tasks.panels import (
    AgentRegistryPanel,
    AgentTaskPanel,
    ActiveAgentsPanel,
    AgentSummaryPanel,
    AgentResultPanel,
)
from app.gui.domains.operations.agent_tasks.panels.agent_operations_detail_panel import (
    AgentOperationsDetailPanel,
)


class AgentTasksWorkspace(BaseOperationsWorkspace):
    """Agent Tasks: Tab „Betrieb“ (read-only) + Tab „Aufgaben“ (bestehend)."""

    def __init__(self, parent=None):
        super().__init__("agent_tasks", parent)
        self._inspector_host = None
        self._sending = False
        self._summaries_by_id: dict = {}
        self._last_project_id: int | None = None
        self._setup_ui()
        self._connect_signals()
        QTimer.singleShot(0, self._defer_init)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        apply_workspace_layout(layout)

        title = QLabel("Agent Tasks")
        title.setObjectName("workspaceTitle")
        layout.addWidget(title)

        self._tabs = QTabWidget()
        self._tabs.setObjectName("agentTasksTabs")

        self._betrieb = QWidget()
        betrieb_layout = QHBoxLayout(self._betrieb)
        betrieb_layout.setContentsMargins(0, 8, 0, 0)
        betrieb_layout.setSpacing(8)
        split = QSplitter(Qt.Orientation.Horizontal)
        self._registry = AgentRegistryPanel(self._betrieb)
        self._ops_detail = AgentOperationsDetailPanel(self._betrieb)
        split.addWidget(self._registry)
        split.addWidget(self._ops_detail)
        split.setStretchFactor(0, 1)
        split.setStretchFactor(1, 2)
        betrieb_layout.addWidget(split)
        self._tabs.addTab(self._betrieb, "Betrieb")

        self._tasks = QWidget()
        tasks_layout = QVBoxLayout(self._tasks)
        tasks_layout.setContentsMargins(0, 8, 0, 0)
        grid = QGridLayout()
        grid.setSpacing(CARD_SPACING)
        self._task_panel = AgentTaskPanel(self._tasks)
        self._active_panel = ActiveAgentsPanel(self._tasks)
        self._summary = AgentSummaryPanel(self._tasks)
        self._result_panel = AgentResultPanel(self._tasks)
        grid.addWidget(self._task_panel, 0, 0)
        grid.addWidget(self._active_panel, 0, 1)
        grid.addWidget(self._summary, 1, 0)
        grid.addWidget(self._result_panel, 1, 1)
        tasks_layout.addLayout(grid)
        self._tabs.addTab(self._tasks, "Aufgaben")

        layout.addWidget(self._tabs, 1)

    def _connect_signals(self):
        self._registry.agent_selected.connect(self._on_agent_selected)
        self._task_panel.task_requested.connect(self._on_task_requested)
        try:
            from app.gui.events.project_events import subscribe_project_events

            subscribe_project_events(self._on_project_context_changed)
        except Exception:
            pass

    def open_with_context(self, ctx: dict) -> None:
        """R2: Tab und Agent-Fokus aus Pending-Kontext."""
        if not ctx:
            return
        sub = (ctx.get("agent_ops_subtab") or "").strip().lower()
        if sub == "tasks":
            self._tabs.setCurrentIndex(1)
        else:
            self._tabs.setCurrentIndex(0)
        aid = (ctx.get("agent_ops_focus_agent_id") or "").strip()
        if aid:
            self._refresh_agents()
            self._registry.select_agent_by_id(aid)

    def _on_project_context_changed(self, payload: dict) -> None:
        self._refresh_agents()

    def _defer_init(self) -> None:
        try:
            from app.agents.seed_agents import ensure_seed_agents

            ensure_seed_agents()
        except Exception:
            pass
        try:
            from app.debug.debug_store import get_debug_store

            get_debug_store()
        except Exception:
            pass
        self._refresh_agents()

    def _refresh_agents(self) -> None:
        try:
            from app.core.context.project_context_manager import get_project_context_manager
            from app.services.agent_service import get_agent_service
            from app.services.agent_operations_read_service import get_agent_operations_read_service

            project_id = get_project_context_manager().get_active_project_id()
            self._last_project_id = project_id
            service = get_agent_service()
            agents = service.list_agents_for_project(project_id) if project_id is not None else []
            summaries = []
            if project_id is not None:
                try:
                    summaries = get_agent_operations_read_service().list_summaries(project_id)
                except Exception:
                    summaries = []
            self._summaries_by_id = {s.agent_id: s for s in summaries if s.agent_id}
            self._registry.refresh(project_id=project_id, summaries_by_id=self._summaries_by_id)
            self._task_panel.set_agents(agents)
        except Exception:
            self._last_project_id = None
            self._registry.refresh(project_id=None)

    def _on_agent_selected(self, profile) -> None:
        self._summary.set_agent(profile)
        if profile and profile.id:
            self._task_panel.set_selected_agent(profile.id)
            s = self._summaries_by_id.get(profile.id)
            if s is None and self._last_project_id is not None:
                try:
                    from app.services.agent_operations_read_service import get_agent_operations_read_service

                    s = get_agent_operations_read_service().get_summary(
                        profile.id, self._last_project_id
                    )
                except Exception:
                    s = None
            self._ops_detail.set_summary(s)
        else:
            self._ops_detail.set_summary(None)

    def _on_task_requested(self, agent_id: str, prompt: str) -> None:
        if self._sending:
            return
        asyncio.create_task(self._run_task(agent_id, prompt))

    async def _run_task(self, agent_id: str, prompt: str) -> None:
        if self._sending:
            return
        self._sending = True
        self._task_panel.set_sending(True)
        try:
            from app.services.agent_service import get_agent_service

            result = await get_agent_service().start_agent_task(agent_id, prompt)
            self._result_panel.set_result(result)
            self._refresh_inspector(result)
        except asyncio.CancelledError:
            self._result_panel.set_result(None)
        except Exception as e:
            from app.agents.agent_task_runner import AgentTaskResult

            self._result_panel.set_result(
                AgentTaskResult(
                    task_id="",
                    agent_id=agent_id,
                    agent_name="",
                    prompt=prompt,
                    response="",
                    model="",
                    success=False,
                    error=str(e),
                )
            )
        finally:
            self._sending = False
            self._task_panel.set_sending(False)
            self._refresh_inspector(None)

    def _refresh_inspector(self, result) -> None:
        if not self._inspector_host:
            return
        from app.gui.inspector.agent_tasks_inspector import AgentTasksInspector

        content = AgentTasksInspector(last_result=result, sending=self._sending)
        token = getattr(self, "_inspector_content_token", None)
        self._inspector_host.set_content(content, content_token=token)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        self._inspector_host = inspector_host
        self._inspector_content_token = content_token
        self._refresh_inspector(None)

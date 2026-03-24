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
from app.gui.domains.operations.agent_tasks.agent_tasks_runtime_sink import AgentTasksRuntimeSink
from app.gui.domains.operations.agent_tasks.agent_tasks_selection_sink import AgentTasksSelectionSink
from app.gui.domains.operations.agent_tasks.agent_tasks_task_panel_sink import AgentTasksTaskPanelSink
from app.ui_application.adapters.service_agent_tasks_registry_adapter import ServiceAgentTasksRegistryAdapter
from app.ui_application.adapters.service_agent_tasks_runtime_adapter import ServiceAgentTasksRuntimeAdapter
from app.ui_application.presenters.agent_tasks_runtime_presenter import AgentTasksRuntimePresenter
from app.ui_application.presenters.agent_tasks_selection_presenter import AgentTasksSelectionPresenter
from app.ui_application.presenters.agent_tasks_task_panel_presenter import AgentTasksTaskPanelPresenter
from app.ui_contracts.workspaces.agent_tasks_inspector import LoadAgentTasksInspectorCommand
from app.ui_contracts.workspaces.agent_tasks_registry import LoadAgentTaskSelectionCommand
from app.ui_contracts.workspaces.agent_tasks_runtime import StartAgentTaskCommand
from app.ui_contracts.workspaces.agent_tasks_task_panel import LoadAgentTaskPanelCommand


class AgentTasksWorkspace(BaseOperationsWorkspace):
    """Agent Tasks: Tab „Betrieb“ (read-only) + Tab „Aufgaben“ (bestehend)."""

    def __init__(self, parent=None):
        super().__init__("agent_tasks", parent)
        self._inspector_host = None
        self._inspector_content_token: int | None = None
        self._inspector_focus_agent_id: str = ""
        self._sending = False
        self._last_project_id: int | None = None
        self._inspector_sink = None
        self._inspector_presenter = None
        self._registry_adapter = ServiceAgentTasksRegistryAdapter()
        self._runtime_adapter = ServiceAgentTasksRuntimeAdapter()
        self._runtime_sink: AgentTasksRuntimeSink | None = None
        self._runtime_presenter: AgentTasksRuntimePresenter | None = None
        self._selection_sink: AgentTasksSelectionSink | None = None
        self._selection_presenter: AgentTasksSelectionPresenter | None = None
        self._task_panel_sink: AgentTasksTaskPanelSink | None = None
        self._task_panel_presenter: AgentTasksTaskPanelPresenter | None = None
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
        self._registry = AgentRegistryPanel(
            self._betrieb,
            agent_tasks_registry_port=self._registry_adapter,
        )
        self._ops_detail = AgentOperationsDetailPanel(self._betrieb)
        split.addWidget(self._registry)
        split.addWidget(self._ops_detail)
        split.setStretchFactor(0, 1)
        split.setStretchFactor(1, 2)
        betrieb_layout.addWidget(split)
        self._selection_sink = AgentTasksSelectionSink(self._ops_detail)
        self._selection_presenter = AgentTasksSelectionPresenter(
            self._selection_sink,
            self._registry_adapter,
        )
        self._tabs.addTab(self._betrieb, "Betrieb")

        self._tasks = QWidget()
        tasks_layout = QVBoxLayout(self._tasks)
        tasks_layout.setContentsMargins(0, 8, 0, 0)
        grid = QGridLayout()
        grid.setSpacing(CARD_SPACING)
        self._task_panel = AgentTaskPanel(self._tasks)
        self._task_panel_sink = AgentTasksTaskPanelSink(self._task_panel)
        self._task_panel_presenter = AgentTasksTaskPanelPresenter(
            self._task_panel_sink,
            self._registry_adapter,
        )
        self._active_panel = ActiveAgentsPanel(self._tasks)
        self._summary = AgentSummaryPanel(self._tasks)
        self._result_panel = AgentResultPanel(self._tasks)
        self._runtime_sink = AgentTasksRuntimeSink(self._result_panel)
        self._runtime_presenter = AgentTasksRuntimePresenter(
            self._runtime_sink,
            self._runtime_adapter,
        )
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

            project_id = get_project_context_manager().get_active_project_id()
            self._last_project_id = project_id
            self._registry.refresh(project_id=project_id)
            snap = self._registry_adapter.last_registry_snapshot
            self._task_panel.set_agents(list(snap.agents) if snap else [])
            self._refresh_task_panel_read()
        except Exception:
            self._last_project_id = None
            self._registry.refresh(project_id=None)
            self._refresh_task_panel_read()

    def _refresh_task_panel_read(self) -> None:
        if self._task_panel_presenter is None:
            return
        aid = (self._inspector_focus_agent_id or "").strip()
        self._task_panel_presenter.handle_command(
            LoadAgentTaskPanelCommand(aid, self._last_project_id),
        )

    def _on_agent_selected(self, profile) -> None:
        self._inspector_focus_agent_id = (
            str(profile.id).strip() if profile and getattr(profile, "id", None) else ""
        )
        self._summary.set_agent(profile)
        if profile and profile.id:
            self._task_panel.set_selected_agent(profile.id)
        aid = ""
        if profile and getattr(profile, "id", None):
            aid = str(profile.id).strip()
        if self._selection_presenter is not None:
            self._selection_presenter.handle_command(
                LoadAgentTaskSelectionCommand(aid, self._last_project_id)
            )
        else:
            self._apply_ops_detail_legacy(profile)
        self._refresh_task_panel_read()

    def _apply_ops_detail_legacy(self, profile) -> None:
        """Legacy: direkter Read-Service, wenn Registry ohne Port (Tests/ältere Verdrahtung)."""
        self._ops_detail.set_read_error(None)
        if profile and profile.id:
            leg_snap = self._registry_adapter.last_registry_snapshot
            summaries = leg_snap.summaries_by_id if leg_snap else {}
            s = summaries.get(profile.id)
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
            if self._runtime_presenter is not None:
                await self._runtime_presenter.handle_start_task_async(
                    StartAgentTaskCommand(agent_id=agent_id, prompt=prompt),
                )
            else:
                await self._run_task_legacy(agent_id, prompt)
        finally:
            self._sending = False
            self._task_panel.set_sending(False)
            self._refresh_inspector(None)

    async def _run_task_legacy(self, agent_id: str, prompt: str) -> None:
        """Legacy: direkter Agent-Service-Start."""
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
                ),
            )

    def _inspector_task_sections(self, result) -> tuple[str, str, str]:
        """Task-Anteil für Inspector (gleiche Textlogik wie Legacy-Widget)."""
        if self._sending and result is None:
            status = "Wird gesendet…"
        elif result is not None:
            if result.success:
                status = f"Abgeschlossen: {result.agent_name}"
            else:
                status = f"Fehler: {result.error or 'Unbekannt'}"
        else:
            status = "Bereit"
        if result is None:
            ctx = "Aktiver Task, Delegationen."
        else:
            p = (result.prompt or "")[:80]
            if len(result.prompt or "") > 80:
                p += "…"
            ctx = f"Agent: {result.agent_name}\nPrompt: {p}"
        if result is None or not result.model:
            tool = "Modell wird bei Task-Ausführung angezeigt."
        else:
            tool = f"Modell: {result.model}\nDauer: {result.duration_sec:.1f}s"
        return status, ctx, tool

    def _refresh_inspector(self, result) -> None:
        if not self._inspector_host:
            return
        if (
            self._registry.uses_port_driven_registry()
            and self._inspector_presenter is not None
        ):
            t1, t2, t3 = self._inspector_task_sections(result)
            self._inspector_presenter.handle_command(
                LoadAgentTasksInspectorCommand(
                    agent_id=self._inspector_focus_agent_id,
                    project_id=self._last_project_id,
                    sending=self._sending,
                    task_section_1=t1,
                    task_section_2=t2,
                    task_section_3=t3,
                ),
            )
        else:
            self._refresh_inspector_legacy(result)

    def _refresh_inspector_legacy(self, result) -> None:
        if not self._inspector_host:
            return
        from app.gui.inspector.agent_tasks_inspector import AgentTasksInspector

        content = AgentTasksInspector(last_result=result, sending=self._sending)
        self._inspector_host.set_content(content, content_token=self._inspector_content_token)

    def setup_inspector(self, inspector_host, content_token: int | None = None) -> None:
        from app.gui.domains.operations.agent_tasks.agent_tasks_inspector_sink import (
            AgentTasksInspectorSink,
        )
        from app.ui_application.presenters.agent_tasks_inspector_presenter import (
            AgentTasksInspectorPresenter,
        )

        self._inspector_host = inspector_host
        self._inspector_content_token = content_token
        self._inspector_sink = AgentTasksInspectorSink(
            inspector_host,
            content_token=content_token,
        )
        self._inspector_presenter = AgentTasksInspectorPresenter(
            self._inspector_sink,
            self._registry_adapter,
        )
        self._refresh_inspector(None)

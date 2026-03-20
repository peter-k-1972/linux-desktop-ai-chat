"""
Execution Engine – führt Tasks über Agenten aus.

Workflow: task -> agent.run(task) -> result -> task.completed

Vorbereitet für Parallelisierung (asyncio.gather).
"""

import asyncio
import logging
from typing import Any, Callable, Dict, List, Optional

from app.agents.agent_base import BaseAgent, ProfileAgent
from app.debug.emitter import emit_event
from app.debug.agent_event import EventType
from app.agents.agent_factory import AgentFactory, get_agent_factory
from app.agents.agent_profile import AgentProfile
from app.agents.delegation_engine import DelegationEngine
from app.agents.task import Task, TaskStatus
from app.agents.task_graph import TaskGraph

logger = logging.getLogger(__name__)


# Typ für die Chat-Funktion, die ein Agent ausführt (injiziert von ChatWidget)
TaskRunnerFn = Callable[[str, str, Dict[str, Any]], Any]


class ExecutionEngine:
    """
    Führt Tasks über Agenten aus.

    Erwartet eine run_fn, die (agent_id, prompt, context) -> str ausführt.
    Diese wird vom ChatWidget bereitgestellt (run_chat mit Agent).
    """

    def __init__(
        self,
        run_fn: Optional[TaskRunnerFn] = None,
        factory: Optional[AgentFactory] = None,
        delegation_engine: Optional[DelegationEngine] = None,
    ):
        """
        Args:
            run_fn: Async (agent_id, prompt, context) -> str. Führt den Agent aus.
            factory: AgentFactory für ProfileAgent-Erstellung
            delegation_engine: Für assign_agent vor der Ausführung
        """
        self._run_fn = run_fn
        self._factory = factory or get_agent_factory()
        self._delegation = delegation_engine or DelegationEngine()

    def set_run_fn(self, run_fn: TaskRunnerFn) -> None:
        """Setzt die Run-Funktion (z.B. vom ChatWidget)."""
        self._run_fn = run_fn

    async def run_task(
        self,
        task: Task,
        graph: TaskGraph,
        run_fn: Optional[TaskRunnerFn] = None,
    ) -> str:
        """
        Führt einen einzelnen Task aus.

        1. Delegation: assign_agent, mark_running
        2. Ausführung via run_fn oder Agent
        3. mark_completed / mark_failed

        Returns:
            Task-Output oder Fehlermeldung
        """
        fn = run_fn or self._run_fn

        # Agent zuweisen
        agent_name = ""
        profile = self._delegation.dispatch_task(task, graph)
        if not profile:
            graph.mark_failed(task.id, "Kein passender Agent gefunden")
            emit_event(
                EventType.TASK_FAILED,
                agent_name="",
                task_id=task.id,
                message="Kein passender Agent gefunden",
                metadata={"error": "Kein passender Agent gefunden"},
            )
            return "Fehler: Kein passender Agent gefunden"

        agent_name = profile.effective_display_name or profile.id or profile.slug or ""
        emit_event(
            EventType.AGENT_SELECTED,
            agent_name=agent_name,
            task_id=task.id,
            message=f"Agent {agent_name} zugewiesen",
        )
        emit_event(
            EventType.TASK_STARTED,
            agent_name=agent_name,
            task_id=task.id,
            message=task.description[:80],
        )

        prompt = task.input.get("prompt", task.description) or task.description
        context = {
            "task_id": task.id,
            "original_prompt": task.input.get("original_prompt", ""),
            "tool_hint": task.tool_hint,
        }

        try:
            if fn:
                result = await fn(profile.id or profile.slug, prompt, context)
            else:
                # Fallback: Agent direkt ausführen (ProfileAgent braucht injizierte run_fn)
                agent = self._factory.create_from_profile(profile)
                result = await self._run_agent_fallback(agent, prompt, context)
            result_str = str(result) if result is not None else ""
            graph.mark_completed(task.id, result_str)
            emit_event(
                EventType.TASK_COMPLETED,
                agent_name=agent_name,
                task_id=task.id,
                message="Abgeschlossen",
                metadata={"agent_id": profile.id or profile.slug},
            )
            return result_str
        except Exception as e:
            logger.exception("Task %s fehlgeschlagen: %s", task.id[:8], e)
            graph.mark_failed(task.id, str(e))
            emit_event(
                EventType.TASK_FAILED,
                agent_name=agent_name,
                task_id=task.id,
                message=str(e),
                metadata={"error": str(e), "agent_id": profile.id or profile.slug},
            )
            return f"Fehler: {e}"

    async def _run_agent_fallback(
        self,
        agent: BaseAgent,
        prompt: str,
        context: Dict[str, Any],
    ) -> str:
        """
        Fallback wenn keine run_fn: ProfileAgent.run() wirft NotImplementedError.
        Hier geben wir einen Platzhalter zurück, da die echte Ausführung
        über ChatWidget.run_chat mit Agent erfolgen muss.
        """
        if isinstance(agent, ProfileAgent):
            raise NotImplementedError(
                "ExecutionEngine benötigt run_fn vom ChatWidget. "
                "ProfileAgent.run() erfordert injizierte Chat-Funktion."
            )
        return await agent.run(prompt, context)

    async def run_graph(
        self,
        graph: TaskGraph,
        run_fn: Optional[TaskRunnerFn] = None,
        on_task_progress: Optional[Callable[[Task, str], None]] = None,
    ) -> str:
        """
        Führt den gesamten Task-Graphen aus.

        Führt Tasks in Reihenfolge der Dependencies aus.
        Vorbereitet für Parallelisierung: get_next_tasks kann mehrere liefern.

        Args:
            graph: TaskGraph mit allen Tasks
            run_fn: Optionale Override-Run-Funktion
            on_task_progress: Callback (task, status) für UI-Updates

        Returns:
            Zusammengefasstes Ergebnis (z.B. letzter Output oder Konkatenation)
        """
        results: List[str] = []
        fn = run_fn or self._run_fn

        if not fn:
            return "Fehler: Keine Run-Funktion konfiguriert (Chat-Integration erforderlich)"

        while not graph.is_complete():
            next_tasks = graph.get_next_tasks(limit=1)  # Sequentiell; für parallel: limit erhöhen
            if not next_tasks:
                # Keine bereiten Tasks, aber Graph nicht komplett -> Deadlock?
                pending = [t for t in graph.get_all_tasks() if t.is_pending]
                if pending:
                    for t in pending:
                        graph.mark_failed(t.id, "Blockiert: Dependencies nicht erfüllt")
                break

            for task in next_tasks:
                if on_task_progress:
                    on_task_progress(task, "running")
                output = await self.run_task(task, graph, run_fn=fn)
                results.append(output)
                if on_task_progress:
                    on_task_progress(task, "completed")

        return "\n\n---\n\n".join(results) if results else "Keine Tasks ausgeführt."

    async def run_graph_parallel(
        self,
        graph: TaskGraph,
        run_fn: Optional[TaskRunnerFn] = None,
        max_concurrent: int = 3,
        on_task_progress: Optional[Callable[[Task, str], None]] = None,
    ) -> str:
        """
        Führt den Task-Graphen mit paralleler Ausführung aus.

        Führt bis zu max_concurrent bereite Tasks gleichzeitig aus.
        """
        results: List[str] = []
        fn = run_fn or self._run_fn

        if not fn:
            return "Fehler: Keine Run-Funktion konfiguriert"

        while not graph.is_complete():
            next_tasks = graph.get_next_tasks(limit=max_concurrent)
            if not next_tasks:
                pending = [t for t in graph.get_all_tasks() if t.is_pending]
                if pending:
                    for t in pending:
                        graph.mark_failed(t.id, "Blockiert: Dependencies nicht erfüllt")
                break

            async def run_one(t: Task) -> str:
                if on_task_progress:
                    on_task_progress(t, "running")
                out = await self.run_task(t, graph, run_fn=fn)
                if on_task_progress:
                    on_task_progress(t, "completed")
                return out

            outputs = await asyncio.gather(*[run_one(t) for t in next_tasks])
            results.extend(outputs)

        return "\n\n---\n\n".join(results) if results else "Keine Tasks ausgeführt."

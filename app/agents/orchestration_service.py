"""
Orchestration Service – Fassade für die Agenten-Orchestrierung.

Verbindet Task Planner, Delegation Engine und Execution Engine.
Bereitgestellt für Chat-Integration.
"""

import logging
from typing import Any, Callable, Optional

from app.agents.execution_engine import ExecutionEngine
from app.debug.emitter import emit_event
from app.debug.agent_event import EventType
from app.agents.task_planner import TaskPlanner
from app.core.llm.llm_complete import complete

logger = logging.getLogger(__name__)

# Typ für Chat-Funktion (orchestrator.chat)
ChatFn = Callable[..., Any]


def create_orchestration_service(
    chat_fn: ChatFn,
    llm_complete_fn: Optional[Callable] = None,
    planner_model: str = "qwen2.5:latest",
) -> "OrchestrationService":
    """
    Erstellt einen OrchestrationService mit gebundenen Abhängigkeiten.

    Args:
        chat_fn: orchestrator.chat (async generator)
        llm_complete_fn: Optional. Wenn None, wird complete(chat_fn, ...) genutzt.
        planner_model: Modell für Task Planner
    """
    if llm_complete_fn is None:

        async def _llm(model_id: str, messages: list):
            return await complete(chat_fn, model_id, messages)

        llm_complete_fn = _llm

    planner = TaskPlanner(llm_complete_fn=llm_complete_fn, model_id=planner_model)
    execution = ExecutionEngine()
    return OrchestrationService(planner=planner, execution=execution)


class OrchestrationService:
    """
    Zentrale Fassade für die Agenten-Orchestrierung.

    Flow: plan() -> TaskGraph, dann run() mit run_fn vom ChatWidget.
    """

    def __init__(
        self,
        planner: Optional[TaskPlanner] = None,
        execution: Optional[ExecutionEngine] = None,
    ):
        self.planner = planner or TaskPlanner()
        self.execution = execution or ExecutionEngine()

    async def plan(self, user_prompt: str):
        """Erzeugt einen Task-Graphen aus dem User-Prompt."""
        graph = await self.planner.plan(user_prompt)
        for task in graph.get_all_tasks():
            emit_event(
                EventType.TASK_CREATED,
                agent_name="TaskPlanner",
                task_id=task.id,
                message=task.description[:80],
                metadata={"description": task.description},
            )
        return graph

    async def run(
        self,
        graph,
        run_fn: Callable[[str, str, dict], Any],
        on_task_progress: Optional[Callable] = None,
    ) -> str:
        """
        Führt den Task-Graphen aus.

        Args:
            graph: TaskGraph von plan()
            run_fn: (agent_id, prompt, context) -> str (vom ChatWidget)
            on_task_progress: Optional (task, status) für UI-Updates

        Returns:
            Zusammengefasstes Ergebnis
        """
        self.execution.set_run_fn(run_fn)
        return await self.execution.run_graph(graph, on_task_progress=on_task_progress)

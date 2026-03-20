"""
Delegation Engine – verteilt Tasks an Agenten.

Verbindet Task Graph, Agent Router und Execution Engine.
"""

import logging
from typing import Any, Callable, Optional

from app.agents.agent_profile import AgentProfile
from app.agents.agent_router import AgentRouter
from app.agents.task import Task, TaskStatus
from app.agents.task_graph import TaskGraph

logger = logging.getLogger(__name__)


class DelegationEngine:
    """
    Delegiert Tasks an Agenten.

    - assign_agent: Weist einem Task einen Agenten zu
    - dispatch_task: Bereitet Task für Ausführung vor (assign + mark running)
    """

    def __init__(self, router: Optional[AgentRouter] = None):
        self._router = router or AgentRouter()

    def assign_agent(self, task: Task) -> Optional[AgentProfile]:
        """
        Weist einem Task einen Agenten zu.

        Nutzt den Agent Router für die Auswahl.
        Setzt task.assigned_agent auf die Agent-ID.

        Returns:
            Zugewiesenes AgentProfile oder None
        """
        profile = self._router.route(task)
        if profile:
            task.assigned_agent = profile.id or profile.slug
            task.touch()
            logger.debug("Task %s -> Agent %s", task.id[:8], profile.effective_display_name)
        return profile

    def dispatch_task(
        self,
        task: Task,
        graph: TaskGraph,
    ) -> Optional[AgentProfile]:
        """
        Bereitet einen Task für die Ausführung vor.

        1. assign_agent
        2. graph.mark_running(task.id)

        Returns:
            AgentProfile wenn erfolgreich zugewiesen, sonst None
        """
        profile = self.assign_agent(task)
        if profile:
            graph.mark_running(task.id)
        return profile

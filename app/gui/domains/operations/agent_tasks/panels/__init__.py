"""Agent Tasks Panels."""

from app.gui.domains.operations.agent_tasks.panels.agent_registry_panel import AgentRegistryPanel
from app.gui.domains.operations.agent_tasks.panels.agent_task_panel import AgentTaskPanel
from app.gui.domains.operations.agent_tasks.panels.active_agents_panel import ActiveAgentsPanel
from app.gui.domains.operations.agent_tasks.panels.agent_summary_panel import AgentSummaryPanel
from app.gui.domains.operations.agent_tasks.panels.result_panel import AgentResultPanel
from app.gui.domains.operations.agent_tasks.panels.agent_operations_detail_panel import (
    AgentOperationsDetailPanel,
)

__all__ = [
    "AgentRegistryPanel",
    "AgentTaskPanel",
    "ActiveAgentsPanel",
    "AgentSummaryPanel",
    "AgentResultPanel",
    "AgentOperationsDetailPanel",
]

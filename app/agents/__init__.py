"""
Agenten-Subsystem – Planner, Research, Critic, ProfileAgent, HR-Verwaltung.

Modulare Agent-Architektur ohne LangChain.
Orchestrierung: Task Planner, Delegation Engine, Execution Engine.
"""

from app.agents.agent_base import BaseAgent, ProfileAgent
from app.agents.agent_profile import AgentProfile, AgentStatus
from app.agents.agent_registry import get_agent_registry, AgentRegistry
from app.agents.agent_service import get_agent_service, AgentService
from app.agents.departments import Department, all_departments
from app.agents.planner import Planner
from app.agents.critic import CriticAgent
from app.agents.research_agent import ResearchAgent
from app.agents.task import Task, TaskStatus
from app.agents.task_graph import TaskGraph
from app.agents.task_planner import TaskPlanner
from app.agents.agent_router import AgentRouter
from app.agents.delegation_engine import DelegationEngine
from app.agents.execution_engine import ExecutionEngine
from app.agents.capabilities import all_capabilities, CAPABILITIES

__all__ = [
    "BaseAgent",
    "ProfileAgent",
    "AgentProfile",
    "AgentStatus",
    "AgentRegistry",
    "AgentService",
    "get_agent_registry",
    "get_agent_service",
    "Department",
    "all_departments",
    "Planner",
    "CriticAgent",
    "ResearchAgent",
    "Task",
    "TaskStatus",
    "TaskGraph",
    "TaskPlanner",
    "AgentRouter",
    "DelegationEngine",
    "ExecutionEngine",
    "all_capabilities",
    "CAPABILITIES",
]

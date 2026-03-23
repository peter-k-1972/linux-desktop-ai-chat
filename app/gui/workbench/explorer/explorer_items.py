"""
Structured explorer identifiers for the Workbench tree.

``ExplorerItemRef`` travels over Qt item roles and signals so context menus, favorites,
and data-backed trees can share one contract without touching domain services yet.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ExplorerSection(str, Enum):
    """Top-level Workbench regions (matches the visual tree)."""

    FAVORITES = "favorites"
    RECENT = "recent"
    WORKSPACE = "workspace"
    TASKS = "tasks"
    PROJECTS = "projects"
    LIBRARY = "library"
    RUNTIME = "runtime"
    SYSTEM = "system"


class ExplorerNodeKind:
    """Leaf and folder kinds; extend when wiring real domain providers."""

    FOLDER = "folder"

    # Projects / project children
    PROJECT_OVERVIEW = "project_overview"
    PROJECT_AGENTS = "project_agents"
    PROJECT_WORKFLOWS = "project_workflows"
    PROJECT_CHAINS = "project_chains"
    PROJECT_FILES = "project_files"
    PROJECT_DATASETS = "project_datasets"
    PROJECT_RUNS = "project_runs"

    # Library
    LIB_MODELS = "lib_models"
    LIB_PROMPTS = "lib_prompts"
    LIB_TOOLS = "lib_tools"
    LIB_TEMPLATES = "lib_templates"
    LIB_KNOWLEDGE = "lib_knowledge"

    # Runtime
    RT_SESSIONS = "rt_sessions"
    RT_AGENT_RUNS = "rt_agent_runs"
    RT_WORKFLOW_RUNS = "rt_workflow_runs"
    RT_BACKGROUND = "rt_background"
    RT_LOGS = "rt_logs"

    # System
    SYS_SETTINGS = "sys_settings"
    SYS_PROVIDERS = "sys_providers"
    SYS_DEBUG = "sys_debug"
    SYS_HEALTH = "sys_health"

    # User workflows (task-first entry points)
    WF_TEST_AGENT = "wf_test_agent"
    WF_KNOWLEDGE_BASE = "wf_knowledge_base"
    WF_BUILD_WORKFLOW = "wf_build_workflow"
    WF_PROMPT_DEV = "wf_prompt_dev"
    WF_MODEL_COMPARE = "wf_model_compare"

    # Legacy / demo opens (still routed to existing canvas placeholders)
    AGENT = "agent"
    WORKFLOW = "workflow"
    FILE = "file"
    CHAT = "chat"


@dataclass(frozen=True, slots=True)
class ExplorerItemRef:
    """
    Immutable handle for the selected or activated explorer row.

    ``path_labels`` is the human-readable trail (e.g. ("Projects", "Project A", "Agents")).
    """

    section: ExplorerSection
    kind: str
    payload: str | None
    path_labels: tuple[str, ...]

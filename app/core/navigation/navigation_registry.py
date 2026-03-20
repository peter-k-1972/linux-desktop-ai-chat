"""
Navigation Registry – single source of truth for all navigable entities.

Defines: id, title, area, workspace, description, help_topic_id, feature_ref.
Used by: Sidebar, Command Palette, Workspace Graph, Help Context.
"""

from dataclasses import dataclass, field
from typing import Optional

from app.core.navigation.nav_areas import NavArea
from app.core.navigation.icon_ids import (
    ACTIVITY,
    ADVANCED,
    AGENT_ACTIVITY,
    AGENTS,
    APPEARANCE,
    CHAT,
    COVERAGE_MAP,
    DATA_STORES,
    DASHBOARD,
    EVENTBUS,
    GAP_ANALYSIS,
    GEAR,
    INCIDENTS,
    KNOWLEDGE,
    LOGS,
    LLM_CALLS,
    METRICS,
    MODELS,
    PROMPT_STUDIO,
    PROJECTS,
    PROVIDERS,
    REPLAY_LAB,
    SHIELD,
    SYSTEM,
    SYSTEM_GRAPH,
    TEST_INVENTORY,
    TOOLS,
)


@dataclass
class NavEntry:
    """A navigable entity (workspace or area)."""

    id: str
    title: str
    area: str
    workspace: Optional[str]
    description: str = ""
    help_topic_id: Optional[str] = None
    feature_ref: Optional[str] = None
    icon: str = ""

    @property
    def nav_key(self) -> str:
        """Unique key for selection (workspace_id or area_id)."""
        return self.workspace or self.area


@dataclass
class NavSectionDef:
    """Section definition for grouped navigation."""

    id: str
    title: str
    entry_ids: list[str]
    default_expanded: bool = True


# All navigable entries. id = nav_key (workspace_id or area_id).
_ENTRIES: dict[str, NavEntry] = {}
_SECTIONS: list[NavSectionDef] = []


def _build_registry() -> None:
    """Build the registry from canonical definitions."""
    global _ENTRIES, _SECTIONS
    entries_list = [
        # PROJECT section
        NavEntry("project_hub", "Projektübersicht", NavArea.PROJECT_HUB, None,
                 "Übersicht über aktive Projekte und deren Status", icon=PROJECTS),
        NavEntry("command_center", "Systemübersicht", NavArea.COMMAND_CENTER, None,
                 "Übersicht über System-Status, QA und Aktivitäten", icon=DASHBOARD),
        NavEntry("operations_projects", "Projekte", NavArea.OPERATIONS, "operations_projects",
                 "Projekte verwalten, anlegen und aktiv setzen", "projects_overview", "Projects",
                 icon=PROJECTS),
        # WORKSPACE section
        NavEntry("operations_chat", "Chat", NavArea.OPERATIONS, "operations_chat",
                 "Conversations with local/cloud LLMs", "chat_overview", "Chat", icon=CHAT),
        NavEntry("operations_knowledge", "Knowledge", NavArea.OPERATIONS, "operations_knowledge",
                 "RAG: context from indexed documents", "knowledge_overview", "Knowledge",
                 icon=KNOWLEDGE),
        NavEntry("operations_prompt_studio", "Prompt Studio", NavArea.OPERATIONS, "operations_prompt_studio",
                 "Reusable prompts and templates", "prompt_studio_overview", "Prompt Studio",
                 icon=PROMPT_STUDIO),
        NavEntry("operations_agent_tasks", "Agent Tasks", NavArea.OPERATIONS, "operations_agent_tasks",
                 "Specialized personas (Code, Research, Media)", "agents_overview", "Agent Tasks",
                 icon=AGENTS),
        # SYSTEM section
        NavEntry("cc_models", "Models", NavArea.CONTROL_CENTER, "cc_models",
                 "Model configuration", "cc_models", "Models", icon=MODELS),
        NavEntry("cc_providers", "Providers", NavArea.CONTROL_CENTER, "cc_providers",
                 "Provider configuration", "cc_providers", "Providers", icon=PROVIDERS),
        NavEntry("cc_agents", "Agents", NavArea.CONTROL_CENTER, "cc_agents",
                 "Agent profiles", "control_center_agents", "Agents", icon=AGENTS),
        NavEntry("cc_tools", "Tools", NavArea.CONTROL_CENTER, "cc_tools",
                 "Tools registry", "cc_tools", "Tools", icon=TOOLS),
        NavEntry("cc_data_stores", "Data Stores", NavArea.CONTROL_CENTER, "cc_data_stores",
                 "Data store configuration", "cc_data_stores", "Data Stores", icon=DATA_STORES),
        # OBSERVABILITY section
        NavEntry("rd_introspection", "Introspection", NavArea.RUNTIME_DEBUG, "rd_introspection",
                 "Live diagnostics: navigation, UI, runtime, services", icon=SYSTEM),
        NavEntry("rd_qa_cockpit", "QA Cockpit", NavArea.RUNTIME_DEBUG, "rd_qa_cockpit",
                 "QA health: test inventory, coverage, risk, gaps, incidents, stability", icon=SHIELD),
        NavEntry("rd_qa_observability", "QA Observability", NavArea.RUNTIME_DEBUG, "rd_qa_observability",
                 "QA health: coverage, risk radar, incidents, tests, stability", icon=SHIELD),
        NavEntry("rd_eventbus", "Runtime", NavArea.RUNTIME_DEBUG, "rd_eventbus",
                 "EventBus monitoring", icon=EVENTBUS),
        NavEntry("rd_logs", "Logs", NavArea.RUNTIME_DEBUG, "rd_logs",
                 "Log viewer", "runtime_overview", icon=LOGS),
        NavEntry("rd_llm_calls", "LLM Calls", NavArea.RUNTIME_DEBUG, "rd_llm_calls",
                 "LLM call traces", icon=LLM_CALLS),
        NavEntry("rd_agent_activity", "Agent Activity", NavArea.RUNTIME_DEBUG, "rd_agent_activity",
                 "Agent execution monitoring", icon=AGENT_ACTIVITY),
        NavEntry("rd_metrics", "Metrics", NavArea.RUNTIME_DEBUG, "rd_metrics",
                 "Metrics dashboard", icon=METRICS),
        NavEntry("rd_system_graph", "System Graph", NavArea.RUNTIME_DEBUG, "rd_system_graph",
                 "System graph view", icon=SYSTEM_GRAPH),
        # Area-only (for command palette "Open X" without specific workspace)
        NavEntry("qa_governance", "QA & Governance", NavArea.QA_GOVERNANCE, None,
                 "Test inventory, coverage, incidents, replay", icon=SHIELD),
        NavEntry("runtime_debug", "Runtime / Debug", NavArea.RUNTIME_DEBUG, None,
                 "EventBus, logs, metrics, LLM calls", icon=ACTIVITY),
        NavEntry("settings", "Settings", NavArea.SETTINGS, None,
                 "Application, appearance, models, data", icon=GEAR),
        # QUALITY section
        NavEntry("qa_test_inventory", "Test Inventory", NavArea.QA_GOVERNANCE, "qa_test_inventory",
                 "Test inventory", "qa_overview", "Test Inventory", icon=TEST_INVENTORY),
        NavEntry("qa_coverage_map", "Coverage", NavArea.QA_GOVERNANCE, "qa_coverage_map",
                 "Coverage map", feature_ref="Coverage Map", icon=COVERAGE_MAP),
        NavEntry("qa_incidents", "Incidents", NavArea.QA_GOVERNANCE, "qa_incidents",
                 "Incident tracking", feature_ref="Incidents", icon=INCIDENTS),
        NavEntry("qa_replay_lab", "Replay", NavArea.QA_GOVERNANCE, "qa_replay_lab",
                 "Replay lab", feature_ref="Replay Lab", icon=REPLAY_LAB),
        NavEntry("qa_gap_analysis", "Gaps", NavArea.QA_GOVERNANCE, "qa_gap_analysis",
                 "Gap analysis", feature_ref="Gap Analysis", icon=GAP_ANALYSIS),
        # SETTINGS section
        NavEntry("settings_application", "Application", NavArea.SETTINGS, "settings_application",
                 "Application settings", icon=SYSTEM),
        NavEntry("settings_appearance", "Appearance", NavArea.SETTINGS, "settings_appearance",
                 "Appearance and theme", "settings_overview", icon=APPEARANCE),
        NavEntry("settings_ai_models", "AI / Models", NavArea.SETTINGS, "settings_ai_models",
                 "AI model settings", icon=MODELS),
        NavEntry("settings_data", "Data", NavArea.SETTINGS, "settings_data",
                 "Data settings", icon=DATA_STORES),
        NavEntry("settings_privacy", "Privacy", NavArea.SETTINGS, "settings_privacy",
                 "Privacy settings", icon=SHIELD),
        NavEntry("settings_advanced", "Advanced", NavArea.SETTINGS, "settings_advanced",
                 "Advanced settings", icon=ADVANCED),
        NavEntry("settings_project", "Project", NavArea.SETTINGS, "settings_project",
                 "Project settings", icon=PROJECTS),
        NavEntry("settings_workspace", "Workspace", NavArea.SETTINGS, "settings_workspace",
                 "Workspace settings", icon=GEAR),
    ]

    _ENTRIES = {e.id: e for e in entries_list}

    _SECTIONS = [
        NavSectionDef("project", "PROJECT",
                      ["project_hub", "command_center", "operations_projects"], True),
        NavSectionDef("workspace", "WORKSPACE",
                      ["operations_chat", "operations_knowledge", "operations_prompt_studio", "operations_agent_tasks"], True),
        NavSectionDef("system", "SYSTEM",
                      ["cc_models", "cc_providers", "cc_agents", "cc_tools", "cc_data_stores"], True),
        NavSectionDef("observability", "OBSERVABILITY",
                      ["rd_introspection", "rd_qa_cockpit", "rd_qa_observability", "rd_eventbus", "rd_logs", "rd_llm_calls", "rd_agent_activity", "rd_metrics", "rd_system_graph"], False),
        NavSectionDef("quality", "QUALITY",
                      ["qa_test_inventory", "qa_coverage_map", "qa_incidents", "qa_replay_lab", "qa_gap_analysis"], False),
        NavSectionDef("settings", "SETTINGS",
                      ["settings_application", "settings_appearance", "settings_ai_models", "settings_data",
                       "settings_privacy", "settings_advanced", "settings_project", "settings_workspace"], False),
    ]


def get_all_entries() -> dict[str, NavEntry]:
    """All navigation entries by id."""
    if not _ENTRIES:
        _build_registry()
    return _ENTRIES


def get_entry(entry_id: str) -> Optional[NavEntry]:
    """Get entry by id."""
    return get_all_entries().get(entry_id)


def get_sidebar_sections() -> list[NavSectionDef]:
    """Sidebar sections with entry ids."""
    if not _SECTIONS:
        _build_registry()
    return _SECTIONS

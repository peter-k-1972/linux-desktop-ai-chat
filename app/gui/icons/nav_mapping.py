"""
NavMapping – Zuordnung von Nav-IDs zu Icon-Namen.

Zentrale Mapping-Tabelle für Navigation und Domain-Navs.
"""

from app.gui.icons.registry import IconRegistry
from app.gui.navigation.nav_areas import NavArea


# Hauptnavigation: area_id -> icon_name
NAV_AREA_ICONS: dict[str, str] = {
    NavArea.COMMAND_CENTER: IconRegistry.DASHBOARD,
    NavArea.OPERATIONS: IconRegistry.CHAT,
    NavArea.CONTROL_CENTER: IconRegistry.CONTROL,
    NavArea.QA_GOVERNANCE: IconRegistry.SHIELD,
    NavArea.RUNTIME_DEBUG: IconRegistry.ACTIVITY,
    NavArea.SETTINGS: IconRegistry.GEAR,
}

# Control Center: workspace_id -> icon_name
CC_WORKSPACE_ICONS: dict[str, str] = {
    "cc_models": IconRegistry.MODELS,
    "cc_providers": IconRegistry.PROVIDERS,
    "cc_agents": IconRegistry.AGENTS,
    "cc_tools": IconRegistry.TOOLS,
    "cc_data_stores": IconRegistry.DATA_STORES,
}

# Operations: workspace_id -> icon_name
OPS_WORKSPACE_ICONS: dict[str, str] = {
    "operations_projects": IconRegistry.PROJECTS,
    "operations_chat": IconRegistry.CHAT,
    "operations_agent_tasks": IconRegistry.AGENTS,
    "operations_knowledge": IconRegistry.KNOWLEDGE,
    "operations_prompt_studio": IconRegistry.PROMPT_STUDIO,
}

# QA & Governance: workspace_id -> icon_name
QA_WORKSPACE_ICONS: dict[str, str] = {
    "qa_test_inventory": IconRegistry.TEST_INVENTORY,
    "qa_coverage_map": IconRegistry.COVERAGE_MAP,
    "qa_gap_analysis": IconRegistry.GAP_ANALYSIS,
    "qa_incidents": IconRegistry.INCIDENTS,
    "qa_replay_lab": IconRegistry.REPLAY_LAB,
}

# Runtime / Debug: workspace_id -> icon_name
RD_WORKSPACE_ICONS: dict[str, str] = {
    "rd_introspection": IconRegistry.SYSTEM,
    "rd_qa_cockpit": IconRegistry.SHIELD,
    "rd_qa_observability": IconRegistry.SHIELD,
    "rd_eventbus": IconRegistry.EVENTBUS,
    "rd_logs": IconRegistry.LOGS,
    "rd_metrics": IconRegistry.METRICS,
    "rd_llm_calls": IconRegistry.LLM_CALLS,
    "rd_agent_activity": IconRegistry.AGENT_ACTIVITY,
    "rd_system_graph": IconRegistry.SYSTEM_GRAPH,
}

# Settings: workspace_id -> icon_name
SETTINGS_WORKSPACE_ICONS: dict[str, str] = {
    "settings_appearance": IconRegistry.APPEARANCE,
    "settings_system": IconRegistry.SYSTEM,
    "settings_models": IconRegistry.MODELS,
    "settings_agents": IconRegistry.AGENTS,
    "settings_advanced": IconRegistry.ADVANCED,
}


def get_nav_area_icon(area_id: str) -> str | None:
    """Icon-Name für einen Hauptbereich."""
    return NAV_AREA_ICONS.get(area_id)


def get_workspace_icon(workspace_id: str) -> str | None:
    """Icon-Name für einen Workspace (alle Domains)."""
    for mapping in (
        CC_WORKSPACE_ICONS,
        OPS_WORKSPACE_ICONS,
        QA_WORKSPACE_ICONS,
        RD_WORKSPACE_ICONS,
        SETTINGS_WORKSPACE_ICONS,
    ):
        if workspace_id in mapping:
            return mapping[workspace_id]
    return None

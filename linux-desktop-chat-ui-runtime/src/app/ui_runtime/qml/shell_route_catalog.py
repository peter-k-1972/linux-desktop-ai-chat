"""
Qt-free routing vocabulary for the QML shell (Welle 1).

Aligns top-level areas with :class:`app.core.navigation.nav_areas.NavArea` and
Operations sub-workspaces with ``OperationsScreen`` (app/gui/domains/operations/operations_screen.py).

No services, no presenters — pure resolution tables for ShellPresenter.
"""

from __future__ import annotations

from app.core.navigation.nav_areas import NavArea

# Mirrors operations_screen.py workspace registration order / IDs.
OPERATIONS_WORKSPACE_ORDER: tuple[str, ...] = (
    "operations_projects",
    "operations_chat",
    "operations_knowledge",
    "operations_prompt_studio",
    "operations_workflows",
    "operations_deployment",
    "operations_audit_incidents",
    "operations_agent_tasks",
)

OPERATIONS_WORKSPACE_LABELS: dict[str, str] = {
    "operations_projects": "Projekte",
    "operations_chat": "Chat",
    "operations_knowledge": "Knowledge / RAG",
    "operations_prompt_studio": "Prompt Studio",
    "operations_workflows": "Workflows",
    "operations_deployment": "Deployment",
    "operations_audit_incidents": "Audit / Incidents",
    "operations_agent_tasks": "Agent Tasks",
}

# Relative to repository qml/ root. None => use defer surface (shell/DeferStage.qml).
OPERATIONS_WORKSPACE_STAGE: dict[str, str | None] = {
    "operations_projects": "domains/projects/ProjectStage.qml",
    "operations_chat": "domains/chat/ChatStage.qml",
    "operations_knowledge": None,
    "operations_prompt_studio": "domains/prompts/PromptStage.qml",
    "operations_workflows": "domains/workflows/WorkflowStage.qml",
    "operations_deployment": "domains/deployment/DeploymentStage.qml",
    "operations_audit_incidents": "domains/operations/OperationsReadStage.qml",
    "operations_agent_tasks": "domains/agents/AgentStage.qml",
}

DEFER_STAGE_RELATIVE: str = "shell/DeferStage.qml"

SETTINGS_STAGE_RELATIVE: str = "domains/settings/SettingsStage.qml"

# Default matches OperationsNav initial selection in OperationsScreen.
DEFAULT_OPERATIONS_WORKSPACE: str = "operations_projects"

# Legacy flat domain IDs (pre–NavArea rail) -> (area_id, workspace_id).
LEGACY_FLAT_TO_ROUTE: dict[str, tuple[str, str]] = {
    "chat": (NavArea.OPERATIONS, "operations_chat"),
    "projects": (NavArea.OPERATIONS, "operations_projects"),
    "prompt_studio": (NavArea.OPERATIONS, "operations_prompt_studio"),
    "workflows": (NavArea.OPERATIONS, "operations_workflows"),
    "agent_tasks": (NavArea.OPERATIONS, "operations_agent_tasks"),
    "deployment": (NavArea.OPERATIONS, "operations_deployment"),
    "settings": (NavArea.SETTINGS, ""),
}


def top_area_entries() -> list[tuple[str, str]]:
    """(area_id, label) for primary shell navigation — same order as NavArea.all_areas."""
    return list(NavArea.all_areas())


def default_route() -> tuple[str, str]:
    """Initial shell route: Operations hub, projects workspace (widget default)."""
    return (NavArea.OPERATIONS, DEFAULT_OPERATIONS_WORKSPACE)


def is_valid_top_area(area_id: str) -> bool:
    return area_id in {a for a, _ in NavArea.all_areas()}


def is_valid_operations_workspace(workspace_id: str) -> bool:
    return workspace_id in OPERATIONS_WORKSPACE_ORDER


def operations_workspace_entries() -> list[tuple[str, str]]:
    return [(w, OPERATIONS_WORKSPACE_LABELS[w]) for w in OPERATIONS_WORKSPACE_ORDER]


def map_legacy_flat_domain(flat_id: str) -> tuple[str, str] | None:
    """Map pre-Welle-1 domain string to (area, workspace)."""
    return LEGACY_FLAT_TO_ROUTE.get(flat_id)


def legacy_surface_key(area_id: str, workspace_id: str) -> str:
    """
    Stable string for backward-compatible bindings (e.g. activeDomain).

    Operations workspaces map to their historical flat id where one existed; else workspace_id.
    Non-operations areas use area_id.
    """
    if area_id == NavArea.OPERATIONS and workspace_id:
        for flat, (a, w) in LEGACY_FLAT_TO_ROUTE.items():
            if a == area_id and w == workspace_id:
                return flat
        return workspace_id
    if area_id == NavArea.SETTINGS:
        return "settings"
    return area_id


def resolve_stage_relative_path(area_id: str, workspace_id: str) -> tuple[str, str]:
    """
    Returns (relative_path_under_qml_root, defer_reason).

    defer_reason is empty when a product stage path is returned; otherwise a short token for QML.
    """
    if area_id == NavArea.OPERATIONS:
        if not workspace_id or not is_valid_operations_workspace(workspace_id):
            return (DEFER_STAGE_RELATIVE, "invalid_operations_workspace")
        rel = OPERATIONS_WORKSPACE_STAGE.get(workspace_id)
        if rel is None:
            return (DEFER_STAGE_RELATIVE, f"unbound:{workspace_id}")
        return (rel, "")
    if area_id == NavArea.SETTINGS:
        return (SETTINGS_STAGE_RELATIVE, "")
    # Command center, control center, QA, runtime debug: no QML product surface in Welle 1.
    if is_valid_top_area(area_id):
        return (DEFER_STAGE_RELATIVE, f"unbound_area:{area_id}")
    return (DEFER_STAGE_RELATIVE, "invalid_top_area")


def default_workspace_for_area(area_id: str) -> str:
    if area_id == NavArea.OPERATIONS:
        return DEFAULT_OPERATIONS_WORKSPACE
    return ""


def normalize_route(area_id: str, workspace_id: str | None) -> tuple[str, str]:
    """Fill default workspace for Operations when empty."""
    ws = (workspace_id or "").strip()
    if area_id == NavArea.OPERATIONS and not ws:
        ws = default_workspace_for_area(area_id)
    return (area_id, ws)

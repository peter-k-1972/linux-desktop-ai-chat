"""
Top-level domain IDs and stage QML paths for the QML shell (Slice 0/1).

No business rules — routing vocabulary only.
"""

from __future__ import annotations

DEFAULT_DOMAIN = "chat"

_DOMAIN_ORDER: tuple[str, ...] = (
    "chat",
    "projects",
    "prompt_studio",
    "workflows",
    "agent_tasks",
    "deployment",
    "settings",
)

# Human-readable labels for the navigation rail (UI copy only).
_DOMAIN_LABELS: dict[str, str] = {
    "chat": "Chat",
    "projects": "Projekte",
    "prompt_studio": "Prompt Studio",
    "workflows": "Workflows",
    "agent_tasks": "Agenten",
    "deployment": "Deployment",
    "settings": "Settings",
}

# Relative to repository qml/ root.
_STAGE_QML_PATH: dict[str, str] = {
    "chat": "domains/chat/ChatStage.qml",
    "projects": "domains/projects/ProjectStage.qml",
    "prompt_studio": "domains/prompts/PromptStage.qml",
    "workflows": "domains/workflows/WorkflowStage.qml",
    "agent_tasks": "domains/agents/AgentStage.qml",
    "deployment": "domains/deployment/DeploymentStage.qml",
    "settings": "domains/settings/SettingsStage.qml",
}


def default_domain() -> str:
    return DEFAULT_DOMAIN


def is_valid_domain(domain_id: str) -> bool:
    return domain_id in _STAGE_QML_PATH


def stage_relative_path(domain_id: str) -> str | None:
    return _STAGE_QML_PATH.get(domain_id)


def domain_entries() -> list[tuple[str, str]]:
    return [(d, _DOMAIN_LABELS[d]) for d in _DOMAIN_ORDER]


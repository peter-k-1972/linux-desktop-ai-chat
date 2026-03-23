"""
Zentrale Zuordnung: semantische Registry-Namen → Taxonomie unter ``resources/icons/``.

- :func:`get_resource_svg_path` — absoluter Pfad zur SVG-Datei
- :func:`get_icon` — :class:`QIcon` (via :class:`IconManager`, ``state`` + optional ``color_token``)
- :func:`get_icon_for_object` / :func:`get_icon_for_action` — Domänen-Helfer
- :func:`get_icon_for_nav` — ``workspace_id`` oder ``NavArea``-ID → Icon
- :func:`get_icon_for_status` — Status-Glyphe (success, warning, …)

Siehe docs/design/ICON_MAPPING.md, ICON_STYLE_GUIDE.md.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from app.utils.paths import get_resource_icons_root

if TYPE_CHECKING:
    from PySide6.QtGui import QIcon

# Registry-ID → (Unterordner in resources/icons, Dateiname)
REGISTRY_TO_RESOURCE: dict[str, tuple[str, str]] = {
    # navigation
    "dashboard": ("navigation", "dashboard.svg"),
    "chat": ("navigation", "chat.svg"),
    "control": ("navigation", "control.svg"),
    "shield": ("navigation", "shield.svg"),
    "activity": ("navigation", "activity.svg"),
    "gear": ("navigation", "gear.svg"),
    # objects
    "agents": ("objects", "agents.svg"),
    "models": ("objects", "models.svg"),
    "providers": ("objects", "providers.svg"),
    "tools": ("objects", "tools.svg"),
    "data_stores": ("objects", "data_stores.svg"),
    "knowledge": ("objects", "knowledge.svg"),
    "prompt_studio": ("objects", "prompt_studio.svg"),
    "projects": ("objects", "projects.svg"),
    "test_inventory": ("objects", "test_inventory.svg"),
    "coverage_map": ("objects", "coverage_map.svg"),
    "gap_analysis": ("objects", "gap_analysis.svg"),
    "incidents": ("objects", "incidents.svg"),
    "replay_lab": ("objects", "replay_lab.svg"),
    "appearance": ("objects", "appearance.svg"),
    "system": ("objects", "system.svg"),
    "advanced": ("objects", "advanced.svg"),
    # monitoring
    "eventbus": ("monitoring", "eventbus.svg"),
    "logs": ("monitoring", "logs.svg"),
    "metrics": ("monitoring", "metrics.svg"),
    "llm_calls": ("monitoring", "llm_calls.svg"),
    "agent_activity": ("monitoring", "agent_activity.svg"),
    "system_graph": ("monitoring", "system_graph.svg"),
    "qa_runtime": ("monitoring", "qa_runtime.svg"),
    # actions
    "add": ("actions", "add.svg"),
    "remove": ("actions", "remove.svg"),
    "edit": ("actions", "edit.svg"),
    "refresh": ("actions", "refresh.svg"),
    "search": ("actions", "search.svg"),
    "filter": ("actions", "filter.svg"),
    "run": ("actions", "run.svg"),
    "stop": ("actions", "stop.svg"),
    "save": ("actions", "save.svg"),
    "deploy": ("actions", "deploy.svg"),
    "pin": ("actions", "pin.svg"),
    "open": ("actions", "open.svg"),
    "link_out": ("actions", "link_out.svg"),
    # ai
    "sparkles": ("ai", "sparkles.svg"),
    # workflow (optional Registry-IDs)
    "graph": ("workflow", "graph.svg"),
    "pipeline": ("workflow", "pipeline.svg"),
    # data (optional Registry-IDs)
    "dataset": ("data", "dataset.svg"),
    "folder": ("data", "folder.svg"),
    # states
    "success": ("states", "success.svg"),
    "warning": ("states", "warning.svg"),
    "error": ("states", "error.svg"),
    "running": ("states", "running.svg"),
    "idle": ("states", "idle.svg"),
    "paused": ("states", "paused.svg"),
    # system (Hilfe, Meta)
    "help": ("system", "help.svg"),
    "info": ("system", "info.svg"),
    "send": ("system", "send.svg"),
}

OBJECT_TYPE_TO_REGISTRY: dict[str, str] = {
    "agent": "agents",
    "agents": "agents",
    "model": "models",
    "models": "models",
    "provider": "providers",
    "providers": "providers",
    "tool": "tools",
    "tools": "tools",
    "dataset": "data_stores",
    "data_store": "data_stores",
    "data_stores": "data_stores",
    "knowledge": "knowledge",
    "collection": "knowledge",
    "prompt": "prompt_studio",
    "prompt_studio": "prompt_studio",
    "project": "projects",
    "projects": "projects",
    "workflow": "system_graph",
    "workflows": "system_graph",
    "deployment": "deploy",
    "deploy": "deploy",
    "incident": "incidents",
    "incidents": "incidents",
    "test": "test_inventory",
    "coverage": "coverage_map",
    "gap": "gap_analysis",
    "replay": "replay_lab",
    "llm": "llm_calls",
    "metric": "metrics",
    "log": "logs",
    "event": "eventbus",
    "folder": "folder",
    "graph": "graph",
    "pipeline": "pipeline",
}

_ACTION_TO_REGISTRY: dict[str, str] = {
    "create": "add",
    "add": "add",
    "new": "add",
    "delete": "remove",
    "remove": "remove",
    "edit": "edit",
    "rename": "edit",
    "save": "save",
    "refresh": "refresh",
    "reload": "refresh",
    "search": "search",
    "find": "search",
    "open": "open",
    "filter": "filter",
    "run": "run",
    "execute": "run",
    "play": "run",
    "stop": "stop",
    "cancel": "stop",
    "deploy": "deploy",
    "publish": "deploy",
    "help": "help",
    "send": "send",
    "pin": "pin",
    "link_out": "link_out",
    "external_link": "link_out",
    "open_external": "link_out",
}

_STATUS_REGISTRY_IDS: frozenset[str] = frozenset(
    {"success", "warning", "error", "running", "idle", "paused"}
)


def get_resource_svg_path(registry_name: str) -> Path | None:
    """Absoluter Pfad unter ``resources/icons/``, wenn vorhanden."""
    tup = REGISTRY_TO_RESOURCE.get(registry_name)
    if not tup:
        return None
    folder, filename = tup
    p = get_resource_icons_root() / folder / filename
    return p if p.is_file() else None


def get_icon(
    name: str,
    *,
    size: int | None = None,
    state: str = "default",
    color: str | None = None,
    color_token: str | None = None,
) -> "QIcon":
    from app.gui.icons.manager import IconManager

    return IconManager.get(
        name,
        size=size,
        state=state,
        color=color,
        color_token=color_token,
    )


def get_icon_for_object(
    obj_type: str,
    *,
    state: str = "default",
    size: int | None = None,
    color: str | None = None,
    color_token: str | None = None,
) -> "QIcon":
    key = (obj_type or "").strip().lower()
    reg = OBJECT_TYPE_TO_REGISTRY.get(key, "projects")
    return get_icon(
        reg,
        size=size,
        state=state,
        color=color,
        color_token=color_token,
    )


def get_icon_for_action(
    action: str,
    *,
    state: str = "default",
    size: int | None = None,
    color: str | None = None,
    color_token: str | None = None,
) -> "QIcon":
    key = (action or "").strip().lower()
    reg = _ACTION_TO_REGISTRY.get(key, "add")
    return get_icon(
        reg,
        size=size,
        state=state,
        color=color,
        color_token=color_token,
    )


def get_icon_for_nav(
    nav_id: str,
    *,
    state: str = "default",
    size: int | None = None,
    color: str | None = None,
    color_token: str | None = None,
) -> "QIcon":
    """
    Löst eine Navigations-ID auf: zuerst Workspace, sonst Hauptbereich (NavArea).

    ``nav_id`` ist typischerweise ``workspace_id`` (z. B. ``operations_chat``) oder
    ``area_id`` (z. B. ``nav_operations``).
    """
    from app.gui.icons.nav_mapping import get_nav_area_icon, get_workspace_icon

    nid = (nav_id or "").strip()
    name = get_workspace_icon(nid) or get_nav_area_icon(nid)
    if not name:
        return get_icon(
            "projects",
            state=state,
            size=size,
            color=color,
            color_token=color_token,
        )
    return get_icon(
        name,
        state=state,
        size=size,
        color=color,
        color_token=color_token,
    )


def get_icon_for_status(
    status: str,
    *,
    state: str | None = None,
    size: int | None = None,
    color: str | None = None,
    color_token: str | None = None,
) -> "QIcon":
    """
    Status-Glyphe aus ``states/*`` (success, warning, error, running, idle, paused).

    ``state`` steuert die Token-Tönung; wenn ``None``, wird ``default`` verwendet.
    """
    key = (status or "").strip().lower()
    reg = key if key in _STATUS_REGISTRY_IDS else "info"
    eff_state = state if state is not None else "default"
    return get_icon(
        reg,
        state=eff_state,
        size=size,
        color=color,
        color_token=color_token,
    )


def list_resource_backed_names() -> list[str]:
    root = get_resource_icons_root()
    out: list[str] = []
    for name, (folder, filename) in REGISTRY_TO_RESOURCE.items():
        if (root / folder / filename).is_file():
            out.append(name)
    return sorted(out)

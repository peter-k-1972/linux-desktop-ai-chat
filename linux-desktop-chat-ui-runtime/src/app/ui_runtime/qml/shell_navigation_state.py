"""
Deprecated flat domain routing (pre–Welle 1).

Prefer :mod:`app.ui_runtime.qml.shell_route_catalog` and :class:`ShellPresenter` /
:class:`ShellBridgeFacade` for navigation.
"""

from __future__ import annotations

from app.ui_runtime.qml.shell_route_catalog import (
    LEGACY_FLAT_TO_ROUTE,
    default_route,
    legacy_surface_key,
    map_legacy_flat_domain,
)

__all__ = [
    "LEGACY_FLAT_TO_ROUTE",
    "default_route",
    "legacy_surface_key",
    "map_legacy_flat_domain",
    "domain_entries",
    "default_domain",
    "is_valid_domain",
    "stage_relative_path",
]


def default_domain() -> str:
    """Legacy key for the default startup route (Operations → projects)."""
    a, w = default_route()
    return legacy_surface_key(a, w)


def domain_entries() -> list[tuple[str, str]]:
    """Flat (id, label) pairs for legacy tooling — not used by the Welle 1 rail."""
    labels = {
        "chat": "Chat",
        "projects": "Projekte",
        "prompt_studio": "Prompt Studio",
        "workflows": "Workflows",
        "agent_tasks": "Agenten",
        "deployment": "Deployment",
        "settings": "Settings",
    }
    return [(k, labels[k]) for k in labels]


def is_valid_domain(domain_id: str) -> bool:
    return domain_id in LEGACY_FLAT_TO_ROUTE or domain_id == "settings"


def stage_relative_path(domain_id: str) -> str | None:
    """Best-effort stage path for a legacy flat id only."""
    mapped = map_legacy_flat_domain(domain_id)
    if mapped is None:
        return None
    from app.ui_runtime.qml.shell_route_catalog import resolve_stage_relative_path

    rel, _ = resolve_stage_relative_path(mapped[0], mapped[1])
    return rel

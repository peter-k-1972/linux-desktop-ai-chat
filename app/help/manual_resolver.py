"""
Resolve docs_manual paths from current GUI / context.

All help text lives under docs_manual/; this module only returns file paths.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def docs_manual_root() -> Path:
    return project_root() / "docs_manual"


@dataclass(frozen=True)
class ManualHelpContext:
    """Input for resolve_help (workspace-centric navigation state)."""

    workspace_id: str = ""
    area_id: str = ""
    panel: str | None = None
    context_mode: str | None = None
    feature: str | None = None


@dataclass(frozen=True)
class ManualHelpResolution:
    """Result: primary doc plus optional related paths (existing files only)."""

    primary: Path
    related: tuple[Path, ...] = ()
    match_key: str = ""


def _module(name: str) -> Path:
    return docs_manual_root() / "modules" / name / "README.md"


def _workflow(name: str) -> Path:
    return docs_manual_root() / "workflows" / f"{name}.md"


def _root_doc(name: str) -> Path:
    return docs_manual_root() / name


# Optional feature hint -> module folder name under docs_manual/modules/
_FEATURE_MODULE: Mapping[str, str] = {
    "chat": "chat",
    "context": "context",
    "settings": "settings",
    "providers": "providers",
    "agents": "agents",
    "rag": "rag",
    "chains": "chains",
    "prompts": "prompts",
    "gui": "gui",
}


# Workspace id -> primary relative target: ("module", name) | ("workflow", name) | ("root", filename)
_WORKSPACE_MAP: Mapping[str, tuple[str, str]] = {
    "operations_chat": ("module", "chat"),
    "operations_projects": ("module", "gui"),
    "operations_knowledge": ("module", "rag"),
    "operations_prompt_studio": ("module", "prompts"),
    "operations_agent_tasks": ("module", "agents"),
    "cc_models": ("module", "providers"),
    "cc_providers": ("module", "providers"),
    "cc_agents": ("module", "agents"),
    "cc_tools": ("module", "chains"),
    "cc_data_stores": ("module", "rag"),
    "qa_test_inventory": ("root", "architecture.md"),
    "qa_coverage_map": ("root", "architecture.md"),
    "qa_gap_analysis": ("root", "architecture.md"),
    "qa_incidents": ("root", "architecture.md"),
    "qa_replay_lab": ("root", "architecture.md"),
    "rd_introspection": ("root", "architecture.md"),
    "rd_qa_cockpit": ("root", "architecture.md"),
    "rd_qa_observability": ("root", "architecture.md"),
    "rd_eventbus": ("root", "architecture.md"),
    "rd_logs": ("root", "architecture.md"),
    "rd_metrics": ("root", "architecture.md"),
    "rd_llm_calls": ("root", "architecture.md"),
    "rd_agent_activity": ("module", "agents"),
    "rd_system_graph": ("root", "architecture.md"),
}


_SETTINGS_CATEGORY_MAP: Mapping[str, tuple[str, str]] = {
    "settings_ai_models": ("module", "providers"),
    "settings_data": ("module", "rag"),
    "settings_workspace": ("module", "settings"),
    "settings_project": ("module", "settings"),
    "settings_application": ("module", "settings"),
    "settings_appearance": ("module", "settings"),
    "settings_privacy": ("module", "settings"),
    "settings_advanced": ("module", "settings"),
}


def _resolve_target(kind: str, name: str) -> Path:
    if kind == "module":
        return _module(name)
    if kind == "workflow":
        return _workflow(name)
    return _root_doc(name)


def _existing(path: Path) -> Path | None:
    return path if path.is_file() else None


def _chat_primary_and_related(ctx: ManualHelpContext) -> tuple[Path, tuple[Path, ...]]:
    """
    Chat workspace: if context injection is active (not off), prioritize context module;
    always surface chat + workflow as related when useful.
    """
    chat_p = _module("chat")
    ctx_p = _module("context")
    wf = _workflow("chat_usage")
    mode = (ctx.context_mode or "").strip().lower()
    active = mode not in ("", "off")
    if active and _existing(ctx_p):
        related = [p for p in (chat_p, wf) if _existing(p)]
        return ctx_p, tuple(related)
    related = [p for p in (ctx_p, wf) if _existing(p)]
    return chat_p, tuple(related)


def _pick_primary_path(ctx: ManualHelpContext) -> tuple[Path, str, list[Path]]:
    related: list[Path] = []

    if ctx.feature:
        key = ctx.feature.strip().lower()
        mod = _FEATURE_MODULE.get(key)
        if mod:
            p = _module(mod)
            return p, f"feature:{key}", related

    ws = (ctx.workspace_id or "").strip()
    area = (ctx.area_id or "").strip()

    if ws.startswith("settings_") or ws in _SETTINGS_CATEGORY_MAP:
        mapped = _SETTINGS_CATEGORY_MAP.get(ws)
        if mapped:
            p = _resolve_target(mapped[0], mapped[1])
            return p, f"settings:{ws}", related
        p = _module("settings")
        return p, f"settings:{ws or 'default'}", related

    if ws == "operations_chat":
        primary, rel = _chat_primary_and_related(ctx)
        return primary, "workspace:operations_chat", list(rel)

    if ws in _WORKSPACE_MAP:
        kind, name = _WORKSPACE_MAP[ws]
        p = _resolve_target(kind, name)
        if ws == "operations_agent_tasks" and _existing(_workflow("agent_usage")):
            related.append(_workflow("agent_usage"))
        if ws in ("cc_models", "cc_providers") and _existing(_workflow("settings_usage")):
            related.append(_workflow("settings_usage"))
        return p, f"workspace:{ws}", related

    if ws == "command_center" or area == "command_center":
        readme = _root_doc("README.md")
        return readme, "workspace:command_center", related

    if area == "settings":
        p = _module("settings")
        return p, "area:settings", related

    if area == "operations" and not ws.startswith("operations_"):
        readme = _root_doc("README.md")
        return readme, "area:operations", related

    if area == "control_center" and not ws.startswith("cc_"):
        p = _module("providers")
        return p, "area:control_center", related

    if area == "qa_governance" and not ws.startswith("qa_"):
        p = _root_doc("architecture.md")
        return p, "area:qa_governance", related

    if area == "runtime_debug" and not ws.startswith("rd_"):
        p = _root_doc("architecture.md")
        return p, "area:runtime_debug", related

    readme = _root_doc("README.md")
    return readme, "default", related


def resolve_help(context: ManualHelpContext | None = None) -> ManualHelpResolution | None:
    """
    Map navigation context to a docs_manual file.

    Returns None only if docs_manual is missing; otherwise prefers README.md as fallback.
    """
    ctx = context or ManualHelpContext()
    root = docs_manual_root()
    if not root.is_dir():
        return None

    primary, key, related_list = _pick_primary_path(ctx)
    if not _existing(primary):
        fallback = _root_doc("README.md")
        primary = fallback if _existing(fallback) else primary
        key = f"{key}|fallback_readme"

    related: list[Path] = []
    seen = {primary.resolve()}
    for p in related_list:
        rp = p.resolve()
        if rp in seen:
            continue
        if _existing(p):
            related.append(p)
            seen.add(rp)

    return ManualHelpResolution(
        primary=primary,
        related=tuple(related),
        match_key=key,
    )


def manual_context_from_workspace_host(workspace_host) -> ManualHelpContext:
    """Build ManualHelpContext from WorkspaceHost (and live chat context mode if available)."""
    ws = ""
    area = ""
    try:
        ws = workspace_host.get_current_workspace_id() or ""
    except Exception:
        ws = ""
    try:
        area = getattr(workspace_host, "_current_area_id", "") or ""
    except Exception:
        area = ""

    mode: str | None = None
    try:
        from app.services.infrastructure import get_infrastructure

        s = get_infrastructure().settings
        mode = getattr(s, "chat_context_mode", None)
    except Exception:
        mode = None

    return ManualHelpContext(workspace_id=ws, area_id=area, context_mode=mode)


def show_contextual_help(
    workspace_host=None,
    *,
    theme: str = "dark",
    parent=None,
) -> None:
    """
    Open HelpWindow: docs_manual via resolve_help when possible, else legacy HelpIndex topic.
    """
    from PySide6.QtWidgets import QApplication

    from app.core.navigation.help_topic_resolver import resolve_help_topic_with_title
    from app.help.help_window import HelpWindow

    parent = parent or QApplication.activeWindow()

    if workspace_host is not None:
        ctx = manual_context_from_workspace_host(workspace_host)
    else:
        ctx = ManualHelpContext()

    resolved = resolve_help(ctx)
    if resolved is not None and resolved.primary.is_file():
        HelpWindow(
            theme=theme,
            parent=parent,
            initial_manual_path=resolved.primary,
        ).exec()
        return

    ws_id = ""
    if workspace_host is not None:
        try:
            ws_id = workspace_host.get_current_workspace_id()
        except Exception:
            ws_id = ""
        area_id = getattr(workspace_host, "_current_area_id", "") or ""
    else:
        area_id = ""

    pair = None
    if ws_id:
        pair = resolve_help_topic_with_title(ws_id)
    if not pair and area_id:
        pair = resolve_help_topic_with_title(area_id)
    initial = pair[0] if pair else None
    HelpWindow(theme=theme, parent=parent, initial_topic_id=initial).exec()


__all__ = [
    "ManualHelpContext",
    "ManualHelpResolution",
    "docs_manual_root",
    "manual_context_from_workspace_host",
    "project_root",
    "resolve_help",
    "show_contextual_help",
]

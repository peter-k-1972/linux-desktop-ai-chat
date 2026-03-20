"""
Palette Command Loader – registriert Command-Palette-Befehle.

Verschoben von app/core/feature_registry_loader (Layer-Bruch core→gui entfernt).
Nutzt app.core.command_registry und app.core.navigation; GUI-Imports nur hier.
"""

import re
from pathlib import Path

from app.core.command_registry import (
    CATEGORY_COMMAND,
    CATEGORY_HELP,
    CATEGORY_SETTING,
    CATEGORY_WORKSPACE,
    CommandRegistry,
    PaletteCommand,
)
from app.core.navigation.navigation_registry import get_all_entries


def _workspace_to_nav() -> dict[str, tuple[str, str | None]]:
    """Workspace/area id -> (area_id, workspace_id for show_area) from registry."""
    result = {}
    for entry in get_all_entries().values():
        result[entry.id] = (entry.area, entry.workspace)
    return result


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent.parent.parent


def _parse_feature_registry() -> list[tuple[str, str, str]]:
    """Parse FEATURE_REGISTRY.md. Returns [(display_name, workspace_id, help_id), ...]."""
    path = _project_root() / "docs" / "FEATURE_REGISTRY.md"
    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8")
    result = []
    current_feature = ""
    current_workspace = ""
    current_help = ""

    for line in text.splitlines():
        m = re.match(r"^### (.+)$", line)
        if m:
            if current_feature and current_workspace:
                result.append((current_feature, current_workspace, current_help))
            current_feature = m.group(1).strip()
            current_workspace = ""
            current_help = ""
            continue
        m = re.match(r"^\|\s*Workspace\s*\|\s*`([^`]+)`\s*\|", line)
        if m:
            current_workspace = m.group(1).strip()
            continue
        m = re.match(r"^\|\s*Help\s*\|\s*`([^`]+)`\s*\|", line)
        if m:
            current_help = m.group(1).strip()
            continue

    if current_feature and current_workspace:
        result.append((current_feature, current_workspace, current_help))

    return result


def load_feature_commands(workspace_host) -> None:
    """Load feature registry and register Open X commands."""
    from app.gui.icons.registry import IconRegistry

    features = _parse_feature_registry()
    _icons = {
        "operations_chat": IconRegistry.CHAT,
        "operations_knowledge": IconRegistry.KNOWLEDGE,
        "operations_prompt_studio": IconRegistry.PROMPT_STUDIO,
        "operations_agent_tasks": IconRegistry.AGENTS,
        "operations_projects": IconRegistry.PROJECTS,
        "cc_models": IconRegistry.MODELS,
        "cc_providers": IconRegistry.PROVIDERS,
        "cc_agents": IconRegistry.AGENTS,
        "cc_tools": IconRegistry.TOOLS,
        "cc_data_stores": IconRegistry.DATA_STORES,
    }

    def _icon_for_workspace(ws_id: str) -> str:
        return _icons.get(ws_id) or (
            IconRegistry.SHIELD if ws_id.startswith("qa_") else
            IconRegistry.ACTIVITY if ws_id.startswith("rd_") else
            IconRegistry.GEAR if ws_id.startswith("settings_") else ""
        )

    workspace_to_nav = _workspace_to_nav()
    for display_name, workspace_id, help_id in features:
        nav = workspace_to_nav.get(workspace_id)
        if not nav:
            continue
        area_id, ws_id = nav
        ws_id = ws_id or None

        cmd_id = f"feature.open.{workspace_id}"
        if cmd_id in [c.id for c in CommandRegistry.all_commands()]:
            continue

        def _make_callback(area, ws):
            return lambda: workspace_host.show_area(area, ws)

        CommandRegistry.register(PaletteCommand(
            id=cmd_id,
            title=f"Open {display_name}",
            description=f"Navigate to {display_name}",
            icon=_icon_for_workspace(workspace_id),
            category=CATEGORY_WORKSPACE if not workspace_id.startswith("settings_") else CATEGORY_SETTING,
            keywords=f"{display_name} {workspace_id} {help_id}",
            callback=_make_callback(area_id, ws_id),
        ))


def load_help_commands(workspace_host=None) -> None:
    """Register Help commands from HelpIndex."""
    from app.gui.icons.registry import IconRegistry
    from app.help.help_index import HelpIndex

    def _open_help():
        from PySide6.QtWidgets import QApplication
        from app.gui.themes import get_theme_manager
        from app.help.help_window import HelpWindow
        mgr = get_theme_manager()
        theme_id = mgr.get_current_id()
        theme = "dark" if "dark" in theme_id else "light"
        parent = QApplication.activeWindow()
        win = HelpWindow(theme=theme, parent=parent)
        win.exec()

    CommandRegistry.register(PaletteCommand(
        id="help.open",
        title="Open Help",
        description="Open help center",
        icon=IconRegistry.SEARCH,
        category=CATEGORY_HELP,
        callback=_open_help,
    ))

    if workspace_host:

        def _open_context_help():
            from PySide6.QtWidgets import QApplication
            from app.gui.themes import get_theme_manager
            from app.help.help_window import HelpWindow
            from app.core.navigation.help_topic_resolver import resolve_help_topic_with_title
            ws_id = workspace_host.get_current_workspace_id()
            resolved = resolve_help_topic_with_title(ws_id) or resolve_help_topic_with_title(workspace_host._current_area_id)
            mgr = get_theme_manager()
            theme_id = mgr.get_current_id()
            theme = "dark" if "dark" in theme_id else "light"
            parent = QApplication.activeWindow()
            initial = resolved[0] if resolved else None
            win = HelpWindow(theme=theme, parent=parent, initial_topic_id=initial)
            win.exec()

        CommandRegistry.register(PaletteCommand(
            id="help.context",
            title="Context Help",
            description="Help for current workspace",
            icon=IconRegistry.SEARCH,
            category=CATEGORY_HELP,
            callback=_open_context_help,
        ))

    index = HelpIndex()
    topics = index.list_by_category()
    for topic in topics[:50]:
        cmd_id = f"help.open.{topic.id}"
        if any(c.id == cmd_id for c in CommandRegistry.all_commands()):
            continue

        def _make_callback(tid):
            def _open():
                from PySide6.QtWidgets import QApplication
                from app.gui.themes import get_theme_manager
                from app.help.help_window import HelpWindow
                mgr = get_theme_manager()
                theme_id = mgr.get_current_id()
                theme = "dark" if "dark" in theme_id else "light"
                parent = QApplication.activeWindow()
                win = HelpWindow(theme=theme, parent=parent, initial_topic_id=tid)
                win.exec()
            return _open

        CommandRegistry.register(PaletteCommand(
            id=cmd_id,
            title=f"Help: {topic.title}",
            description=f"Open help article",
            icon=IconRegistry.SEARCH,
            category=CATEGORY_HELP,
            keywords=f"{topic.title} {topic.id} {' '.join(topic.tags)}",
            callback=_make_callback(topic.id),
        ))


def load_system_commands() -> None:
    """Register system commands (Rebuild maps, QA, Reload)."""
    from app.gui.icons.registry import IconRegistry

    root = _project_root()

    def _rebuild_system_map():
        import subprocess
        subprocess.run(["python3", str(root / "tools" / "generate_system_map.py")], cwd=str(root))

    def _rebuild_trace_map():
        import subprocess
        subprocess.run(["python3", str(root / "tools" / "generate_trace_map.py")], cwd=str(root))

    def _rebuild_feature_registry():
        import subprocess
        subprocess.run(["python3", str(root / "tools" / "generate_feature_registry.py")], cwd=str(root))

    def _reload_providers():
        try:
            from app.services.infrastructure import get_infrastructure
            infra = get_infrastructure()
            if hasattr(infra, "reload_providers"):
                infra.reload_providers()
        except Exception:
            pass

    CommandRegistry.register(PaletteCommand(
        id="cmd.rebuild_system_map",
        title="Rebuild System Map",
        description="Regenerate docs/SYSTEM_MAP.md",
        icon=IconRegistry.REFRESH,
        category=CATEGORY_COMMAND,
        callback=_rebuild_system_map,
    ))
    CommandRegistry.register(PaletteCommand(
        id="cmd.rebuild_trace_map",
        title="Rebuild Trace Map",
        description="Regenerate docs/TRACE_MAP.md",
        icon=IconRegistry.REFRESH,
        category=CATEGORY_COMMAND,
        callback=_rebuild_trace_map,
    ))
    CommandRegistry.register(PaletteCommand(
        id="cmd.rebuild_feature_registry",
        title="Rebuild Feature Registry",
        description="Regenerate docs/FEATURE_REGISTRY.md",
        icon=IconRegistry.REFRESH,
        category=CATEGORY_COMMAND,
        callback=_rebuild_feature_registry,
    ))
    CommandRegistry.register(PaletteCommand(
        id="cmd.reload_providers",
        title="Reload Providers",
        description="Reload Ollama providers",
        icon=IconRegistry.REFRESH,
        category=CATEGORY_COMMAND,
        callback=_reload_providers,
    ))

    def _run_qa_sweep():
        import subprocess
        subprocess.run(
            ["python3", str(root / "scripts" / "qa" / "run_feedback_loop.py")],
            cwd=str(root),
        )

    CommandRegistry.register(PaletteCommand(
        id="cmd.run_qa_sweep",
        title="Run QA Sweep",
        description="Run feedback loop (scripts/qa/run_feedback_loop.py)",
        icon=IconRegistry.SHIELD,
        category=CATEGORY_COMMAND,
        callback=_run_qa_sweep,
    ))


def load_area_commands(workspace_host) -> None:
    """Register area-level navigation from registry (area-only entries)."""
    area_ids = {"command_center", "project_hub", "qa_governance", "runtime_debug", "settings"}
    for entry in get_all_entries().values():
        if entry.id not in area_ids or entry.workspace:
            continue
        cmd_id = f"nav.area.{entry.area}"
        if any(c.id == cmd_id for c in CommandRegistry.all_commands()):
            continue

        def _make_cb(area, ws):
            return lambda: workspace_host.show_area(area, ws)

        CommandRegistry.register(PaletteCommand(
            id=cmd_id,
            title=f"Open {entry.title}",
            description=f"Navigate to {entry.title}",
            icon=entry.icon or "",
            category=CATEGORY_WORKSPACE,
            callback=_make_cb(entry.area, entry.workspace),
        ))


def load_workspace_graph_command(workspace_host) -> None:
    """Register Open Workspace Graph command."""
    from app.gui.icons.registry import IconRegistry
    from app.gui.navigation.workspace_graph import WorkspaceGraphDialog

    def _open_graph():
        from PySide6.QtWidgets import QApplication
        parent = QApplication.activeWindow()
        dlg = WorkspaceGraphDialog(workspace_host, parent=parent)
        dlg.exec()

    CommandRegistry.register(PaletteCommand(
        id="nav.workspace_graph",
        title="Open Workspace Graph",
        description="Visual map of workspaces and areas",
        icon=IconRegistry.SYSTEM_GRAPH,
        category=CATEGORY_WORKSPACE,
        keywords="map system overview navigation",
        callback=_open_graph,
    ))


def load_all_palette_commands(workspace_host) -> None:
    """Load all commands: area nav, features, help, system, workspace graph."""
    load_area_commands(workspace_host)
    load_workspace_graph_command(workspace_host)
    load_feature_commands(workspace_host)
    load_help_commands(workspace_host)
    load_system_commands()

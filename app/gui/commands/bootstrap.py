"""
Command Bootstrap – Registrierung der Standard-Commands.

Wird von MainWindow aufgerufen. Registriert Navigation, System, Search.

Navigation-Commands (id ``nav.*``): bei gesetzter FeatureRegistry nur wenn die ID in
``collect_active_gui_command_ids`` liegt (Edition → Features → Descriptor.commands).
"""

from __future__ import annotations

from typing import FrozenSet, Optional

from app.gui.commands.model import Command
from app.gui.commands.registry import CommandRegistry
from app.gui.icons.registry import IconRegistry
from app.gui.navigation.nav_areas import NavArea


def _register_nav_command(
    workspace_host,
    allowed: Optional[FrozenSet[str]],
    cmd: Command,
) -> None:
    if allowed is not None and cmd.id not in allowed:
        return
    CommandRegistry.register(cmd)


def _maybe_register_theme_visualizer_nav_command(
    workspace_host,
    allowed: Optional[FrozenSet[str]],
) -> None:
    from app.gui.devtools.devtools_visibility import is_theme_visualizer_available

    if not is_theme_visualizer_available():
        return
    if allowed is not None and "nav.rd_theme_visualizer" not in allowed:
        return
    CommandRegistry.register(Command(
        id="nav.rd_theme_visualizer",
        title="Theme Visualizer (Runtime)",
        description="Runtime / Debug – QA-Theme-Tool (eigenes Fenster)",
        icon=IconRegistry.APPEARANCE,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.RUNTIME_DEBUG, "rd_theme_visualizer"),
    ))


def register_commands(workspace_host) -> None:
    """
    Registriert alle Standard-Commands.
    workspace_host: WorkspaceHost für Navigation.
    """
    from app.features import collect_active_gui_command_ids, get_feature_registry

    fr = get_feature_registry()
    allowed: Optional[frozenset[str]] = (
        collect_active_gui_command_ids(fr) if fr is not None else None
    )

    # --- Navigation (Hauptbereiche) ---
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.dashboard",
        title="Kommandozentrale öffnen",
        description="Systemübersicht und Status",
        icon=IconRegistry.DASHBOARD,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.COMMAND_CENTER),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.projects",
        title="Projekte öffnen",
        description="Operations – Projekte verwalten",
        icon=IconRegistry.PROJECTS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.OPERATIONS, "operations_projects"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.chat",
        title="Chat öffnen",
        description="Operations – Chat",
        icon=IconRegistry.CHAT,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.OPERATIONS, "operations_chat"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.knowledge",
        title="Knowledge öffnen",
        description="Operations – Knowledge / RAG",
        icon=IconRegistry.KNOWLEDGE,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.OPERATIONS, "operations_knowledge"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.prompt_studio",
        title="Prompt Studio öffnen",
        description="Operations – Prompt Studio",
        icon=IconRegistry.PROMPT_STUDIO,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.OPERATIONS, "operations_prompt_studio"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.workflows",
        title="Workflows öffnen",
        description="Operations – gespeicherte DAGs (Editor, Runs, Canvas)",
        icon=IconRegistry.SYSTEM_GRAPH,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.OPERATIONS, "operations_workflows"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.agent_tasks",
        title="Agent Tasks öffnen",
        description="Operations – Agent Tasks",
        icon=IconRegistry.AGENTS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.OPERATIONS, "operations_agent_tasks"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.control_center",
        title="Control Center öffnen",
        description="Systemkonfiguration",
        icon=IconRegistry.CONTROL,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.CONTROL_CENTER),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.cc_models",
        title="Models öffnen",
        description="Control Center – Models",
        icon=IconRegistry.MODELS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.CONTROL_CENTER, "cc_models"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.cc_providers",
        title="Providers öffnen",
        description="Control Center – Providers",
        icon=IconRegistry.PROVIDERS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.CONTROL_CENTER, "cc_providers"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.cc_agents",
        title="Agents öffnen",
        description="Control Center – Agents",
        icon=IconRegistry.AGENTS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.CONTROL_CENTER, "cc_agents"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.cc_tools",
        title="Tools öffnen",
        description="Control Center – Tools",
        icon=IconRegistry.TOOLS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.CONTROL_CENTER, "cc_tools"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.cc_data_stores",
        title="Data Stores öffnen",
        description="Control Center – Data Stores",
        icon=IconRegistry.DATA_STORES,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.CONTROL_CENTER, "cc_data_stores"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.qa_governance",
        title="QA & Governance öffnen",
        description="Test- und Qualitätsübersicht",
        icon=IconRegistry.SHIELD,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.QA_GOVERNANCE),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.runtime_debug",
        title="Runtime / Debug öffnen",
        description="Laufzeit- und Debug-Ansicht",
        icon=IconRegistry.ACTIVITY,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.RUNTIME_DEBUG),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.rd_qa_cockpit",
        title="QA Cockpit öffnen",
        description="Runtime – QA Health: Test Inventory, Coverage, Risk, Gaps, Incidents, Stability",
        icon=IconRegistry.SHIELD,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.RUNTIME_DEBUG, "rd_qa_cockpit"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.rd_qa_observability",
        title="QA Observability öffnen",
        description="Runtime – QA Health: Coverage, Risk, Incidents, Tests",
        icon=IconRegistry.SHIELD,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.RUNTIME_DEBUG, "rd_qa_observability"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.rd_system_graph",
        title="System Graph öffnen",
        description="Runtime – System Graph",
        icon=IconRegistry.SYSTEM_GRAPH,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.RUNTIME_DEBUG, "rd_system_graph"),
    ))
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.rd_markdown_demo",
        title="Markdown-Demo öffnen",
        description="Runtime – zentrale Markdown-Pipeline visuell prüfen (Hilfe/Chat/ASCII)",
        icon=IconRegistry.LOGS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.RUNTIME_DEBUG, "rd_markdown_demo"),
    ))
    _maybe_register_theme_visualizer_nav_command(workspace_host, allowed)
    _register_nav_command(workspace_host, allowed, Command(
        id="nav.settings",
        title="Einstellungen öffnen",
        description="Systemeinstellungen",
        icon=IconRegistry.GEAR,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.SETTINGS),
    ))

    # --- System ---
    CommandRegistry.register(Command(
        id="system.help",
        title="Hilfe öffnen",
        description="Handbuch passend zum aktuellen Bereich (docs_manual)",
        icon=IconRegistry.SEARCH,
        category="system",
        callback=lambda: _open_help(workspace_host),
    ))
    CommandRegistry.register(Command(
        id="system.help_context",
        title="Kontexthilfe anzeigen",
        description="Handbuch passend zum aktuellen Workspace",
        icon=IconRegistry.SEARCH,
        category="system",
        callback=lambda: _open_context_help(workspace_host),
    ))
    CommandRegistry.register(Command(
        id="system.switch_theme",
        title="Theme wechseln",
        description="Light/Dark umschalten",
        icon=IconRegistry.GEAR,
        category="system",
        callback=_switch_theme,
    ))
    CommandRegistry.register(Command(
        id="system.reload_theme",
        title="Theme neu laden",
        description="Aktuelles Theme neu laden",
        icon=IconRegistry.REFRESH,
        category="system",
        callback=_reload_theme,
    ))


def _open_context_help(workspace_host) -> None:
    """Öffnet docs_manual passend zum Workspace; Fallback: Hilfe-Index."""
    _open_help(workspace_host)


def _open_help(workspace_host) -> None:
    """Öffnet kontextbezogenes Handbuch (docs_manual) oder Legacy-Hilfe."""
    try:
        from app.gui.themes import get_theme_manager
        from app.gui.themes.theme_id_utils import theme_id_to_legacy_light_dark
        from app.help.manual_resolver import show_contextual_help

        mgr = get_theme_manager()
        theme_id = mgr.get_current_id()
        theme = theme_id_to_legacy_light_dark(theme_id)
        show_contextual_help(workspace_host, theme=theme, parent=None)
    except Exception:
        pass


def _switch_theme() -> None:
    """Wechselt zwischen Light und Dark."""
    try:
        from app.gui.themes import get_theme_manager
        mgr = get_theme_manager()
        current = mgr.get_current_id()
        themes = [t[0] for t in mgr.list_themes()]
        idx = themes.index(current) if current in themes else 0
        next_id = themes[(idx + 1) % len(themes)]
        mgr.set_theme(next_id)
    except Exception:
        pass


def _reload_theme() -> None:
    """Lädt das aktuelle Theme neu."""
    try:
        from app.gui.themes import get_theme_manager
        from app.gui.icons import IconManager
        mgr = get_theme_manager()
        current = mgr.get_current_id()
        mgr.set_theme(current)
        IconManager.clear_cache()
    except Exception:
        pass

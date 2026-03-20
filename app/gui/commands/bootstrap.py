"""
Command Bootstrap – Registrierung der Standard-Commands.

Wird von MainWindow aufgerufen. Registriert Navigation, System, Search.
"""

from app.gui.commands.model import Command
from app.gui.commands.registry import CommandRegistry
from app.gui.icons.registry import IconRegistry
from app.gui.navigation.nav_areas import NavArea


def register_commands(workspace_host) -> None:
    """
    Registriert alle Standard-Commands.
    workspace_host: WorkspaceHost für Navigation.
    """

    # --- Navigation (Hauptbereiche) ---
    CommandRegistry.register(Command(
        id="nav.dashboard",
        title="Kommandozentrale öffnen",
        description="Systemübersicht und Status",
        icon=IconRegistry.DASHBOARD,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.COMMAND_CENTER),
    ))
    CommandRegistry.register(Command(
        id="nav.projects",
        title="Projekte öffnen",
        description="Operations – Projekte verwalten",
        icon=IconRegistry.PROJECTS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.OPERATIONS, "operations_projects"),
    ))
    CommandRegistry.register(Command(
        id="nav.chat",
        title="Chat öffnen",
        description="Operations – Chat",
        icon=IconRegistry.CHAT,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.OPERATIONS, "operations_chat"),
    ))
    CommandRegistry.register(Command(
        id="nav.knowledge",
        title="Knowledge öffnen",
        description="Operations – Knowledge / RAG",
        icon=IconRegistry.KNOWLEDGE,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.OPERATIONS, "operations_knowledge"),
    ))
    CommandRegistry.register(Command(
        id="nav.prompt_studio",
        title="Prompt Studio öffnen",
        description="Operations – Prompt Studio",
        icon=IconRegistry.PROMPT_STUDIO,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.OPERATIONS, "operations_prompt_studio"),
    ))
    CommandRegistry.register(Command(
        id="nav.agent_tasks",
        title="Agent Tasks öffnen",
        description="Operations – Agent Tasks",
        icon=IconRegistry.AGENTS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.OPERATIONS, "operations_agent_tasks"),
    ))
    CommandRegistry.register(Command(
        id="nav.control_center",
        title="Control Center öffnen",
        description="Systemkonfiguration",
        icon=IconRegistry.CONTROL,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.CONTROL_CENTER),
    ))
    CommandRegistry.register(Command(
        id="nav.cc_models",
        title="Models öffnen",
        description="Control Center – Models",
        icon=IconRegistry.MODELS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.CONTROL_CENTER, "cc_models"),
    ))
    CommandRegistry.register(Command(
        id="nav.cc_providers",
        title="Providers öffnen",
        description="Control Center – Providers",
        icon=IconRegistry.PROVIDERS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.CONTROL_CENTER, "cc_providers"),
    ))
    CommandRegistry.register(Command(
        id="nav.cc_agents",
        title="Agents öffnen",
        description="Control Center – Agents",
        icon=IconRegistry.AGENTS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.CONTROL_CENTER, "cc_agents"),
    ))
    CommandRegistry.register(Command(
        id="nav.cc_tools",
        title="Tools öffnen",
        description="Control Center – Tools",
        icon=IconRegistry.TOOLS,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.CONTROL_CENTER, "cc_tools"),
    ))
    CommandRegistry.register(Command(
        id="nav.cc_data_stores",
        title="Data Stores öffnen",
        description="Control Center – Data Stores",
        icon=IconRegistry.DATA_STORES,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.CONTROL_CENTER, "cc_data_stores"),
    ))
    CommandRegistry.register(Command(
        id="nav.qa_governance",
        title="QA & Governance öffnen",
        description="Test- und Qualitätsübersicht",
        icon=IconRegistry.SHIELD,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.QA_GOVERNANCE),
    ))
    CommandRegistry.register(Command(
        id="nav.runtime_debug",
        title="Runtime / Debug öffnen",
        description="Laufzeit- und Debug-Ansicht",
        icon=IconRegistry.ACTIVITY,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.RUNTIME_DEBUG),
    ))
    CommandRegistry.register(Command(
        id="nav.rd_qa_cockpit",
        title="QA Cockpit öffnen",
        description="Runtime – QA Health: Test Inventory, Coverage, Risk, Gaps, Incidents, Stability",
        icon=IconRegistry.SHIELD,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.RUNTIME_DEBUG, "rd_qa_cockpit"),
    ))
    CommandRegistry.register(Command(
        id="nav.rd_qa_observability",
        title="QA Observability öffnen",
        description="Runtime – QA Health: Coverage, Risk, Incidents, Tests",
        icon=IconRegistry.SHIELD,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.RUNTIME_DEBUG, "rd_qa_observability"),
    ))
    CommandRegistry.register(Command(
        id="nav.rd_system_graph",
        title="System Graph öffnen",
        description="Runtime – System Graph",
        icon=IconRegistry.SYSTEM_GRAPH,
        category="navigation",
        callback=lambda: workspace_host.show_area(NavArea.RUNTIME_DEBUG, "rd_system_graph"),
    ))
    CommandRegistry.register(Command(
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
        description="Dokumentation und Hilfethemen",
        icon=IconRegistry.SEARCH,
        category="system",
        callback=_open_help,
    ))
    CommandRegistry.register(Command(
        id="system.help_context",
        title="Kontexthilfe anzeigen",
        description="Hilfe für aktuellen Workspace",
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
    """Öffnet Hilfe mit dem Thema des aktuellen Workspaces."""
    try:
        from PySide6.QtWidgets import QApplication
        from app.gui.themes import get_theme_manager
        from app.help.help_window import HelpWindow
        from app.help.help_index import HelpIndex
        workspace_id = workspace_host.get_current_workspace_id()
        index = HelpIndex()
        topic = index.get_topic_by_workspace(workspace_id)
        if not topic:
            topic = index.get_topic_by_workspace(workspace_host._current_area_id)
        mgr = get_theme_manager()
        theme_id = mgr.get_current_id()
        theme = "dark" if "dark" in theme_id else "light"
        parent = QApplication.activeWindow()
        initial_topic = topic.id if topic else None
        win = HelpWindow(theme=theme, parent=parent, initial_topic_id=initial_topic)
        win.exec()
    except Exception:
        pass


def _open_help() -> None:
    """Öffnet das Hilfefenster."""
    try:
        from PySide6.QtWidgets import QApplication
        from app.gui.themes import get_theme_manager
        from app.help.help_window import HelpWindow
        mgr = get_theme_manager()
        theme_id = mgr.get_current_id()
        theme = "dark" if "dark" in theme_id else "light"
        parent = QApplication.activeWindow()
        win = HelpWindow(theme=theme, parent=parent)
        win.exec()
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

"""
Architektur-Guard-Konfiguration.

Zentrale Definition der erlaubten/verbotenen Strukturen.
Änderungen nur nach Architektur-Review.
"""

from pathlib import Path

# Projekt-Root (parent von tests/)
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
APP_ROOT = PROJECT_ROOT / "app"
# Kanonischer Pfad für Architektur-Dokumentation (docs/04_architecture).
# Siehe docs/04_architecture/DOCS_ARCHITECTURE_PATH_DECISION.md
DOCS_ARCH = PROJECT_ROOT / "docs" / "04_architecture"

# --- 1. App-Root: Erlaubte Dateien ---
# Nur diese Dateien dürfen direkt im app/ Root liegen.
# Subpackages (Verzeichnisse) sind separat erlaubt.
ALLOWED_APP_ROOT_FILES = frozenset({
    "__init__.py",
    "__main__.py",
    "main.py",
    "resources.qrc",
    "resources_rc.py",
})

# Während Refactoring temporär erlaubt (Phase D: entfernen)
# Siehe docs/architecture/APP_MOVE_MATRIX.md
TEMPORARILY_ALLOWED_ROOT_FILES = frozenset({
    "db.py",
    "ollama_client.py",
    "critic.py",
})

# --- 2. Ziel-Packages (Import-Guard-Set; vollständige Landkarte inkl. erweiterter Segmente:
#     docs/architecture/PACKAGE_MAP.md, app/packaging/landmarks.py EXTENDED_APP_TOP_PACKAGES) ---
TARGET_PACKAGES = frozenset({
    "core",
    "gui",
    "agents",
    "rag",
    "prompts",
    "providers",
    "services",
    "debug",
    "metrics",
    "tools",
    "utils",
    "pipelines",
    "ui_contracts",
    "ui_application",
    "ui_runtime",
    "ui_themes",
    "features",
})

# --- 3. Verbotene Parallelstrukturen ---
# ui/ wurde in gui migriert; darf nicht neu erstellt werden.
FORBIDDEN_PARALLEL_PACKAGES = frozenset({
    "ui",  # Migriert nach gui; Neuaufbau verboten.
})

# --- 4. Verbotene Import-Richtungen (source_package -> darf nicht importieren) ---
# Format: (source_top_package, forbidden_top_package)
# source = Modul innerhalb app.<source>.*
# forbidden = app.<forbidden>.*
FORBIDDEN_IMPORT_RULES = frozenset({
    # features: Kern ohne statischen app.gui-Import (Integrations-Registrare unter gui/registration/)
    ("features", "gui"),
    # core: editions- und feature-blind (Phase-2-Feature-Registrar)
    ("core", "features"),
    # core darf NICHT importieren:
    ("core", "gui"),
    ("core", "agents"),
    ("core", "rag"),
    ("core", "prompts"),
    ("core", "providers"),
    ("core", "services"),
    ("core", "debug"),
    ("core", "metrics"),
    ("core", "ui"),
    # utils darf NICHT importieren (außer stdlib):
    ("utils", "core"),
    ("utils", "gui"),
    ("utils", "agents"),
    ("utils", "rag"),
    ("utils", "prompts"),
    ("utils", "providers"),
    ("utils", "services"),
    ("utils", "debug"),
    ("utils", "metrics"),
    ("utils", "tools"),
    ("utils", "ui"),
    # providers darf NICHT importieren:
    ("providers", "gui"),
    ("providers", "agents"),
    ("providers", "rag"),
    ("providers", "prompts"),
    ("providers", "services"),
    ("providers", "debug"),
    ("providers", "metrics"),
    ("providers", "agents"),
    ("providers", "ui"),
    ("agents", "ui"),
    ("rag", "ui"),
    ("prompts", "ui"),
    ("services", "ui"),
    ("services", "gui"),  # Service Governance: services darf gui nicht importieren
    ("gui", "providers"),  # Service Governance: gui nutzt services, nicht direkt providers
    ("_root", "providers"),  # main.py Legacy – Ausnahme dokumentiert
    # tools darf NICHT importieren:
    ("tools", "gui"),
    ("tools", "agents"),
    ("tools", "rag"),
    ("tools", "prompts"),
    ("tools", "providers"),
    ("tools", "services"),
    ("tools", "debug"),
    ("tools", "metrics"),
    ("tools", "ui"),
    # metrics darf NICHT importieren:
    ("metrics", "gui"),
    ("metrics", "agents"),
    ("metrics", "rag"),
    ("metrics", "prompts"),
    ("metrics", "providers"),
    ("metrics", "services"),
    ("metrics", "debug"),
    ("metrics", "ui"),
    # pipelines darf NICHT importieren:
    ("pipelines", "gui"),
    ("pipelines", "providers"),
    ("pipelines", "services"),
    ("pipelines", "agents"),
    ("pipelines", "rag"),
    ("pipelines", "prompts"),
    ("pipelines", "core"),
    ("pipelines", "debug"),
    ("pipelines", "metrics"),
    ("pipelines", "tools"),
    # ui_contracts — strikt Qt-frei, keine Fach-/Persistenz-Schicht:
    ("ui_contracts", "gui"),
    ("ui_contracts", "features"),
    ("ui_contracts", "services"),
    ("ui_contracts", "rag"),
    ("ui_contracts", "workflows"),
    ("ui_contracts", "agents"),
    # ui_themes — nur Assets; kein Service-/GUI-Import in Python-Dateien:
    ("ui_themes", "gui"),
    ("ui_themes", "services"),
    # ui_runtime — Theme-Loader ohne Service-Kopplung (Anbindung erfolgt außen):
    ("ui_runtime", "services"),
    # debug darf NICHT importieren:
    ("debug", "gui"),
    ("debug", "agents"),
    ("debug", "rag"),
    ("debug", "prompts"),
    ("debug", "providers"),
    ("debug", "services"),
    ("debug", "ui"),
})

# --- 5. Root-Legacy-Module (sollen nicht von Feature-Packages importiert werden) ---
# Feature-Packages: core, agents, rag, prompts, providers, tools, metrics, debug
ROOT_LEGACY_MODULES = frozenset({
    "chat_widget",
    "sidebar_widget",
    "project_chat_list_widget",
    "message_widget",
    "file_explorer_widget",
})

# --- 6. Zentrale Navigation (einzige produktive Implementierung) ---
# Haupt-Navigation: Sidebar, Command Palette, Workspace-Graph
CENTRAL_NAVIGATION_PATH = APP_ROOT / "gui" / "navigation"

# --- 11. GUI Governance (Screen, Navigation, Commands) ---
# Siehe docs/architecture/GUI_GOVERNANCE_POLICY.md
# Mapping: area_id -> set of valid workspace_ids (None = area-only)
GUI_SCREEN_WORKSPACE_MAP = {
    "command_center": frozenset(),
    "operations": frozenset({
        "operations_projects", "operations_chat", "operations_knowledge",
        "operations_prompt_studio", "operations_workflows", "operations_agent_tasks",
        "operations_deployment", "operations_audit_incidents",
    }),
    "control_center": frozenset({
        "cc_models", "cc_providers", "cc_agents", "cc_tools", "cc_data_stores",
    }),
    "runtime_debug": frozenset({
        "rd_introspection", "rd_qa_cockpit", "rd_qa_observability",
        "rd_markdown_demo", "rd_theme_visualizer",
        "rd_eventbus", "rd_logs", "rd_metrics", "rd_llm_calls",
        "rd_agent_activity", "rd_system_graph",
    }),
    "qa_governance": frozenset({
        "qa_test_inventory", "qa_coverage_map", "qa_gap_analysis",
        "qa_incidents", "qa_replay_lab",
    }),
    "settings": frozenset({
        "settings_application", "settings_appearance", "settings_ai_models",
        "settings_data", "settings_privacy", "settings_advanced",
        "settings_project", "settings_workspace",
    }),
}

# --- 10. GUI Domain Dependency Guards ---
# Siehe docs/architecture/GUI_DOMAIN_DEPENDENCY_POLICY.md
# Format: (source_domain, target_domain) – source darf target nicht importieren
FORBIDDEN_GUI_DOMAIN_PAIRS = frozenset({
    ("settings", "operations.chat"),
    ("settings", "operations.prompt_studio"),
    ("settings", "control_center"),
    ("settings", "runtime_debug"),
    ("settings", "dashboard"),
    ("settings", "qa_governance"),
    ("settings", "command_center"),
    ("dashboard", "operations.chat"),
    ("qa_governance", "operations.chat"),
    ("command_center", "operations.chat"),
    ("operations.chat", "settings"),
    ("operations.chat", "runtime_debug"),
})

# Bekannte Ausnahmen (DISCOURAGE – dokumentiert, Follow-up geplant)
# Format: (source_file_pattern, target_domain) – pattern in rel_path
# model_settings_panel: behoben (2026-03-16) – _PROMPTS_PANEL_FIXED_WIDTH nach shared
KNOWN_GUI_DOMAIN_EXCEPTIONS = frozenset({
    ("domains/operations/chat/panels/chat_side_panel.py", "settings"),
    ("domains/operations/chat/panels/chat_side_panel.py", "runtime_debug"),
})

# --- 7. Bekannte Import-Ausnahmen (zu beheben) ---
# (source_file_pattern, forbidden_dst) - wenn source_file_pattern in Pfad, wird Verletzung ignoriert
# Bei Behebung: Eintrag entfernen.
KNOWN_IMPORT_EXCEPTIONS = frozenset({
    ("core/llm/llm_complete.py", "debug"),            # Optional: emit_event für Debug-Monitor
    ("core/context/project_context_manager.py", "services"),   # ProjectService für Projekt-Load
    # Entkopplung: docs/architecture/FEATURE_SYSTEM.md (ProjectContextEvent-Port)
    ("core/context/project_context_manager.py", "gui"),   # emit_project_context_changed (gui.events)
    ("core/models/orchestrator.py", "providers"),     # Orchestrierung: Provider-Zuordnung (arch. Entscheidung)
    ("metrics/metrics_collector.py", "debug"),         # Emitter/EventBus für Metriken
    # Service Governance – dokumentierte Ausnahmen
    ("main.py", "providers"),                         # Legacy MainWindow
    ("gui/domains/settings/settings_dialog.py", "providers"),  # Legacy Settings-Dialog
    ("ollama_client.py", "providers"),                # Root re-export von app.providers.ollama_client
})

# --- 8. Erlaubte ui-Importeure (Übergangsphase) ---
# Nur diese Module dürfen app.ui importieren. Ziel: ui → gui Migration.
# Format: Pfad-Pattern (str) – Datei ist erlaubt, wenn rel_path.startswith(pattern) oder pattern in rel_path
ALLOWED_UI_IMPORTER_PATTERNS = frozenset({
    "main.py",                    # Legacy
    "gui/",                       # gui (inkl. gui/legacy) importiert ui während Übergang
    "core/context/project_context_manager.py",  # emit_project_context_changed
})

# --- 12. Service Governance ---
# Siehe docs/architecture/SERVICE_GOVERNANCE_POLICY.md
# services darf NICHT gui importieren (außer dokumentierte Ausnahme)
FORBIDDEN_SERVICE_IMPORT_GUI = True
# gui darf NICHT providers importieren (außer dokumentierte Ausnahmen)
FORBIDDEN_GUI_IMPORT_PROVIDERS = True

# Bekannte Ausnahmen: (source_file_pattern, target) – pattern in rel_path
# Bei Behebung: Eintrag entfernen.
# services/infrastructure.py -> gui: BEHOBEN (2026-03-16) Dependency Inversion.
KNOWN_SERVICE_GUI_EXCEPTIONS = frozenset()
# settings_dialog: BEHOBEN (2026-03-16) – nutzt ModelService/ProviderService
KNOWN_GUI_PROVIDER_EXCEPTIONS = frozenset({
    ("main.py", "providers"),           # Legacy MainWindow
})

# Zentrale Service-Module (app/services/*.py, ohne __init__ und result)
CANONICAL_SERVICE_MODULES = frozenset({
    "agent_service",
    "chat_service",
    "infrastructure",
    "knowledge_service",
    "model_service",
    "pipeline_service",
    "project_service",
    "provider_service",
    "qa_governance_service",
    "topic_service",
})

# --- 12b. Root-Entrypoint Governance ---
# Siehe docs/04_architecture/ROOT_ENTRYPOINT_POLICY.md
# Erlaubte .py und .sh Dateien im Projekt-Root (keine neuen Startskripte ohne Review)
ALLOWED_PROJECT_ROOT_ENTRYPOINT_SCRIPTS = frozenset({
    "main.py",
    "run_gui_shell.py",
    "run_workbench_demo.py",
    "start.sh",
    "install-desktop.sh",
})

# --- 13. Startup Governance ---
# Siehe docs/architecture/STARTUP_GOVERNANCE_POLICY.md
# Kanonische GUI-Einstiegspunkte (müssen init_infrastructure mit QSettings aufrufen)
CANONICAL_GUI_ENTRY_POINTS = frozenset({
    "run_gui_shell.py",           # Standard-GUI
    "app/main.py",                # Legacy-GUI (app.main.main)
})
# Jeder Einstiegspunkt muss diese Strings in main() enthalten (Bootstrap-Contract)
REQUIRED_BOOTSTRAP_PATTERNS = frozenset({
    "init_infrastructure",
    "create_qsettings_backend",
})

# --- 14. Registry Governance ---
# Siehe docs/architecture/REGISTRY_GOVERNANCE_POLICY.md
# Gültige Provider-Strings in ModelRegistry (ModelEntry.provider)
KNOWN_MODEL_PROVIDER_STRINGS = frozenset({"local", "ollama_cloud"})

# --- 15. Provider-Orchestrator Governance ---
# Siehe docs/architecture/PROVIDER_ORCHESTRATOR_GOVERNANCE_POLICY.md
# Erlaubte Dateien für provider="local" / provider="ollama_cloud" (Hardcoding-Guard)
ALLOWED_PROVIDER_STRING_FILES = frozenset({
    "app/core/models/registry.py",
    "app/providers/local_ollama_provider.py",
    "app/providers/cloud_ollama_provider.py",
    "tests/architecture/arch_guard_config.py",
    "tests/architecture/test_registry_governance_guards.py",
    "tests/architecture/test_provider_orchestrator_governance_guards.py",
})

# --- 16. EventBus Governance ---
# Siehe docs/architecture/EVENTBUS_GOVERNANCE_POLICY.md
# Erlaubte Module für emit_event-Import (app.debug.emitter)
ALLOWED_EMIT_EVENT_IMPORTERS = frozenset({
    "app/agents/",
    "app/rag/",
    "app/core/llm/llm_complete.py",
    "app/gui/legacy/chat_widget.py",
})
# Erlaubte Module für EventBus/get_event_bus-Import (app.debug.event_bus)
ALLOWED_EVENTBUS_DIRECT_IMPORTERS = frozenset({
    "app/debug/",
    "app/agents/agent_task_runner.py",
    "app/metrics/metrics_collector.py",
})
# Top-Packages, die app.debug (EventBus, emit_event) NICHT importieren dürfen
FORBIDDEN_EVENTBUS_IMPORTER_PACKAGES = frozenset({"providers", "prompts", "tools", "utils"})

# --- 17. Architecture Drift Radar ---
# Siehe docs/architecture/ARCHITECTURE_DRIFT_RADAR_POLICY.md
DRIFT_RADAR_SCRIPT = PROJECT_ROOT / "scripts" / "architecture" / "architecture_drift_radar.py"
DRIFT_RADAR_JSON = DOCS_ARCH / "ARCHITECTURE_DRIFT_RADAR.json"
DRIFT_RADAR_STATUS = DOCS_ARCH / "ARCHITECTURE_DRIFT_RADAR_STATUS.md"
EXPECTED_DRIFT_CATEGORIES = frozenset({
    "layer_drift", "startup_drift", "registry_drift", "provider_drift",
    "event_drift", "entrypoint_drift", "hardcoding_drift", "gui_domain_drift",
    "feature_drift",
})
EXPECTED_GOVERNANCE_DOMAINS = frozenset({
    "app_package", "gui", "services", "startup", "registry",
    "provider", "eventbus", "feature",
})

# --- 9. Globale vs. Domain-Navigation ---
# Globale Navigation: nur in gui/navigation/
GLOBAL_NAVIGATION_CLASSES = frozenset({"NavigationSidebar", "CommandPalette"})
# Erlaubte Klassen in gui/navigation/ (Daten, Helper, Dialoge)
ALLOWED_IN_GUI_NAVIGATION = frozenset({
    "NavigationSidebar", "CommandPalette", "NavItem", "NavSection",
    "NavSectionWidget", "WorkspaceGraphDialog",
})

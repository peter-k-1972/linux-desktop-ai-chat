# App Target Package Architecture

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Status:** Zielarchitektur – keine Umsetzung  
**Referenz:** docs/architecture/APP_PACKAGE_ARCHITECTURE_ASSESSMENT.md, docs/04_architecture/GUI_REPOSITORY_ARCHITECTURE.md

**Architektur-Guard-Tests:** `tests/architecture/test_app_package_guards.py` – prüft Root-Dateien, Import-Richtungen, Navigation, Feature-Package-Isolation.

---

## 1. Zielstruktur

```
app/
├── __init__.py
├── main.py
├── core/
├── gui/
├── agents/
├── rag/
├── prompts/
├── providers/
├── services/
├── debug/
├── metrics/
├── tools/
└── utils/
```

---

## 2. Package-Verantwortlichkeiten

### 2.1 `app` (Root)

| Verantwortung | Inhalt |
|--------------|--------|
| Package-Marker | `__init__.py` |
| Einstiegspunkt | `main.py` – delegiert an `run_gui_shell` (Standard) oder Legacy-GUI |
| Keine Fachlogik | Root enthält nur Einstieg; alle Module in Subpackages |

### 2.2 `app.core`

| Verantwortung | Inhalt |
|--------------|--------|
| **Konfiguration** | AppSettings, Theme-Pfade, Defaults |
| **Datenbank** | DatabaseManager, Schema, Migrationen |
| **Modell-Logik** | ModelRegistry, ModelRoles, ModelRouter, ModelOrchestrator, EscalationManager |
| **Navigation (Daten)** | NavArea, NavigationRegistry, FeatureRegistry, HelpTopicResolver, TraceMapLoader |
| **Command Registry** | Palette-Commands, Kategorien, Bereichs-Mapping |
| **Projekt-Kontext** | ActiveProjectContext, ProjectContextManager |
| **Chat-Commands** | Slash-Command-Parsing (parse_slash_command) |
| **LLM-Aufrufe** | Completion, Output-Pipeline, Retry-Policy, Response-Cleaner |

**Regel:** Keine PySide6-Imports. Keine GUI-Abhängigkeiten. Core ist testbar ohne Qt.

### 2.3 `app.gui`

| Verantwortung | Inhalt |
|--------------|--------|
| **Shell** | MainWindow, Docking, TopBar, Layout-Konstanten |
| **Navigation (UI)** | Sidebar, Command Palette, Breadcrumbs, Workspace-Graph |
| **Domains** | Operations, Control Center, QA Governance, Runtime Debug, Settings, Dashboard, Project Hub |
| **Workspaces** | WorkspaceHost, ScreenRegistry, Domain-Workspaces |
| **Inspector** | InspectorHost, kontextabhängige Panels |
| **Monitors** | Bottom-Panel (Logs, Events, Metrics, Agent Activity, LLM Trace) |
| **Themes** | Theme Loader, Manager, Registry, Tokens |
| **Icons** | IconManager, IconRegistry, NavMapping |
| **Help** | HelpWindow, HelpIndex, DocGenerator, GuidedTour, TooltipHelper |
| **Resources** | Styles, QSS, Theme-Farben |
| **Widgets** | EmptyStateWidget, wiederverwendbare UI-Bausteine |
| **Legacy** | ChatWidget, SidebarWidget, etc. in `gui/legacy/` (bis Legacy-GUI abgeschaltet) |
| **Backends** | ChatBackend, KnowledgeBackend |

**Regel:** GUI importiert nur core, agents, rag, prompts, providers, services, debug, metrics, tools, utils. Keine zirkulären Imports.

### 2.4 `app.agents`

| Verantwortung | Inhalt |
|--------------|--------|
| Agent-Profile | AgentProfile, ModelRole-Mapping |
| Registry & Repository | AgentRegistry, AgentRepository |
| Services | AgentService, ResearchService, OrchestrationService |
| Execution | AgentTaskRunner, ExecutionEngine, TaskPlanner, TaskGraph |
| Spezialisierte Agenten | CriticAgent, ResearchAgent, SeedAgents |
| Routing & Delegation | AgentRouter, DelegationEngine |

### 2.5 `app.rag`

| Verantwortung | Inhalt |
|--------------|--------|
| RAG Service | Service-API, Retriever, Context-Builder |
| Embedding | EmbeddingService, VectorStore |
| Dokumente | DocumentLoader, Chunker, KnowledgeExtractor |
| Validierung | KnowledgeValidator, KnowledgeUpdater |

### 2.6 `app.prompts`

| Verantwortung | Inhalt |
|--------------|--------|
| Storage | PromptRepository, StorageBackend |
| Service | PromptService, PromptModels |

### 2.7 `app.providers`

| Verantwortung | Inhalt |
|--------------|--------|
| Ollama Client | Low-Level API (OllamaClient) |
| Provider | BaseProvider, LocalOllamaProvider, CloudOllamaProvider |

### 2.8 `app.services`

| Verantwortung | Inhalt |
|--------------|--------|
| Chat | ChatService |
| Knowledge | KnowledgeService |
| Agent | AgentService (Facade zu app.agents) |
| Project | ProjectService |
| Topic | TopicService |
| Model | ModelService |
| Provider | ProviderService |
| QA Governance | QaGovernanceService |
| Infrastruktur | Infrastructure (DB, Settings, Ollama-Bootstrap) |

### 2.9 `app.debug`

| Verantwortung | Inhalt |
|--------------|--------|
| EventBus | EventBus, Emitter, AgentEvent |
| Debug Store | DebugStore |
| QA Cockpit | QaCockpitPanel, QaArtifactLoader |
| Runtime | GuiLogBuffer (von runtime/) |

### 2.10 `app.metrics`

| Verantwortung | Inhalt |
|--------------|--------|
| Collector | MetricsCollector, MetricsStore, MetricsService |
| Agent-Metriken | AgentMetrics |

### 2.11 `app.tools`

| Verantwortung | Inhalt |
|--------------|--------|
| FileSystem | FileSystemTools |
| Web Search | WebSearch (DuckDuckGo) |

### 2.12 `app.utils`

| Verantwortung | Inhalt |
|--------------|--------|
| Pfade | Paths (Icons, Themes, etc.) |
| Datum/Zeit | DateTimeUtils |
| Umgebung | EnvLoader |

---

## 3. Abhängigkeitsregeln

### 3.1 Erlaubte Abhängigkeiten

| Von | Darf importieren |
|-----|------------------|
| `core` | utils |
| `gui` | core, agents, rag, prompts, providers, services, debug, metrics, tools, utils |
| `agents` | core, providers, prompts, rag, utils |
| `rag` | core, providers, utils |
| `prompts` | core, utils |
| `providers` | core, utils |
| `services` | core, agents, rag, prompts, providers, debug, metrics, utils |
| `debug` | core, utils |
| `metrics` | utils |
| `tools` | utils |
| `utils` | – |

### 3.2 Verbotene Abhängigkeiten

| Von | Darf NICHT importieren |
|-----|-------------------------|
| `core` | gui, agents, rag, prompts, providers, services, debug, metrics |
| `utils` | Alle anderen app-Packages |
| `providers` | gui, agents, rag, prompts, services, debug, metrics |
| `tools` | gui, agents, rag, prompts, providers, services, debug, metrics |
| `metrics` | gui, agents, rag, prompts, providers, services, debug |
| `debug` | gui, agents, rag, prompts, providers, services |

### 3.3 Sonderfälle

- **core → gui.icons:** Aktuell importiert `core.navigation.navigation_registry` `gui.icons.registry`. **Zu beheben:** Icon-IDs als Strings; Registry-Injection oder Verschiebung der Icon-Zuordnung nach gui.
- **gui → services:** Erlaubt; GUI nutzt Services für Daten.
- **services → agents:** Erlaubt; AgentService fasst app.agents zusammen.

---

## 4. Zentrale Navigation unter `app/gui/navigation/`

### 4.1 Kandidaten (bereits vorhanden)

| Datei | Rolle |
|-------|-------|
| `nav_areas.py` | Re-Export von `core.navigation.nav_areas.NavArea` |
| `sidebar.py` | NavigationSidebar – linke Haupt-Sidebar |
| `sidebar_config.py` | NavItem, NavSection, get_sidebar_sections (delegiert an core) |
| `command_palette.py` | CommandPalette – VSCode-Style Befehlspalette |
| `workspace_graph.py` | WorkspaceGraphDialog – klickbare Systemkarte |
| `workspace_graph_resolver.py` | Metadata für Workspace-Graph |

### 4.2 Domain-spezifische Navigation (aus ui → gui)

| Aktuell | Ziel | Typ |
|---------|------|-----|
| `ui/settings/settings_navigation.py` | `gui/domains/settings/navigation.py` | Links-Nav für Settings |
| `ui/chat/chat_navigation_panel.py` | `gui/domains/operations/chat/navigation_panel.py` | Links-Nav für Chats |
| `ui/knowledge/knowledge_navigation_panel.py` | `gui/domains/operations/knowledge/navigation_panel.py` | Links-Nav für Knowledge |
| `ui/agents/agent_navigation_panel.py` | `gui/domains/control_center/agents/navigation_panel.py` oder in gui/domains/operations/agent_tasks | Links-Nav für Agents |
| `ui/prompts/prompt_navigation_panel.py` | `gui/domains/operations/prompt_studio/navigation_panel.py` | Links-Nav für Prompt Studio |

**Konvention:** Domain-spezifische Navigation liegt in der Domain; zentrale Navigation (Sidebar, Palette, Graph) in `gui/navigation/`.

---

## 5. Pages, Widgets, Dialogs, MainWindow-Komposition

### 5.1 Pages (Full-Screen-Views)

| Komponente | Ort | Beschreibung |
|------------|-----|--------------|
| DashboardScreen | gui/domains/dashboard/ | Kommandozentrale |
| OperationsScreen | gui/domains/operations/ | Tab-Host für Chat, Agent Tasks, Knowledge, Prompt Studio, Projects |
| ControlCenterScreen | gui/domains/control_center/ | Tab-Host für Models, Providers, Agents, Tools, Data Stores |
| QaGovernanceScreen | gui/domains/qa_governance/ | Tab-Host für Test Inventory, Coverage, Gaps, Incidents, Replay |
| RuntimeDebugScreen | gui/domains/runtime_debug/ | Tab-Host für EventBus, Logs, Metrics, LLM Calls, Agent Activity |
| SettingsScreen | gui/domains/settings/ | Full-Page Settings |
| ProjectHubScreen | gui/domains/project_hub/ | Projekt-Übersicht |

### 5.2 Widgets (Wiederverwendbare Bausteine)

| Komponente | Ort | Beschreibung |
|------------|-----|--------------|
| EmptyStateWidget | gui/widgets/ | Platzhalter für leere Zustände |
| ProjectSwitcherButton | gui/project_switcher/ | Projekt-Wechsel in TopBar |
| ChatHeaderWidget | gui/domains/operations/chat/ | Chat-Header mit Modell-Auswahl |
| ChatComposerWidget | gui/domains/operations/chat/ | Eingabefeld für Nachrichten |
| ChatMessageWidget | gui/domains/operations/chat/ | Einzelne Nachricht |
| SourceListItem / SourceListItemWidget | gui/domains/operations/knowledge/ | Quellen-Eintrag (konsolidieren) |
| PromptListItem | gui/domains/operations/prompt_studio/ | Prompt-Eintrag in Liste |

### 5.3 Dialogs

| Komponente | Ort | Beschreibung |
|------------|-----|--------------|
| CommandPaletteDialog | gui/commands/palette.py | Befehlspalette (Modal) |
| WorkspaceGraphDialog | gui/navigation/workspace_graph.py | Systemkarte (Modal) |
| ProjectSwitcherDialog | gui/project_switcher/ | Projekt wechseln |
| TopicEditorDialog | gui/domains/operations/chat/ | Topic bearbeiten |
| SettingsDialog | gui/domains/settings/ | Legacy-Settings-Dialog (von ui) |
| AddSourceDialog | gui/domains/operations/knowledge/ | Quelle hinzufügen |
| CollectionDialog | gui/domains/operations/knowledge/ | Sammlung anlegen |

### 5.4 MainWindow-Komposition

```
ShellMainWindow (gui/shell/main_window.py)
├── TopBar (gui/shell/top_bar.py)
│   ├── ProjectSwitcherButton
│   ├── BreadcrumbBar
│   └── Aktionen (Help, Settings, Theme)
├── NavigationSidebar (gui/navigation/sidebar.py)
├── WorkspaceHost (gui/workspace/workspace_host.py)
│   └── [Screen je nach Bereich]
├── InspectorHost (gui/inspector/inspector_host.py) [Dock rechts]
└── BottomPanelHost (gui/monitors/bottom_panel_host.py) [Dock unten]
```

---

## 6. Zu entfernende Packages (Quellstruktur)

| Package | Aktion |
|---------|--------|
| `commands` | Inhalt → `core/commands/` |
| `context` | Inhalt → `core/context/` |
| `help` | Inhalt → `gui/help/` |
| `llm` | Inhalt → `core/llm/` |
| `models` | Leer – entfernen |
| `qa` | Inhalt → `services/` (Adapter) und `debug/` (QA Cockpit) |
| `resources` | Inhalt → `gui/resources/` |
| `runtime` | Inhalt → `debug/` |
| `ui` | Inhalt → `gui/` (Domains, Widgets, Dialogs) |

---

## 7. Merge-Kandidaten

| Quell 1 | Quell 2 | Ziel | Aktion |
|---------|---------|------|--------|
| `app/critic.py` | `app/agents/critic.py` | `app/agents/critic.py` | Root-critic als `ReviewModeConfig`/Platzhalter in agents.critic integrieren; Root-Datei entfernen |
| `gui/.../source_list_item.py` (SourceListItemWidget) | `ui/knowledge/source_list_item.py` (SourceListItem) | `gui/domains/operations/knowledge/panels/source_list_item.py` | API vereinheitlichen; eine Klasse mit optionalen Parametern oder Adapter |

---

## 8. Entfernungs-Kandidaten

| Datei | Grund |
|-------|-------|
| `app/__main__.py` | Optional: Kann bleiben, wenn `python -m app` gewünscht. Oder: In main.py integrieren. |
| `app/response_filter.py` | Minimaler Platzhalter; prüfen ob genutzt. Falls ungenutzt: entfernen. |
| `app/models/` | Leeres Package – entfernen |

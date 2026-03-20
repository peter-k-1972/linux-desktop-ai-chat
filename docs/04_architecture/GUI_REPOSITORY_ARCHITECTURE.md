# GUI-Repository-Architektur – Linux Desktop Chat

**Version:** 1.1  
**Datum:** 2026-03-15  
**Referenz:** docs/UX_CONCEPT.md, docs/PYSIDE6_UI_ARCHITECTURE.md  
**Status:** Verbindliche Modul- und Repository-Struktur für die PySide6-GUI

---

## 1. Einleitung

Dieses Dokument definiert die **verbindliche GUI-Modul- und Repository-Struktur** für die Linux Desktop Chat Anwendung. Es enthält **klare Architekturentscheidungen** – keine unverbindliche Sammlung von Möglichkeiten. Abweichungen bedürfen einer Architektur-Review.

**Leitprinzipien:**
- Shell getrennt von Feature-Modulen
- Navigation getrennt von Workspace-Inhalten
- Generische Panels getrennt von fachlichen Screens
- Einheitliche Muster für Erweiterbarkeit
- Keine Vermischung von globaler App-Struktur und Bereichs-Screens

---

## 2. Architekturentscheidungen – Vier-Säulen-Modell

### 2.1 Verbindliche Kategorisierung

Jede GUI-Komponente gehört **genau einer** der vier Kategorien an:

| Kategorie | Definition | Ort | Regel |
|----------|------------|-----|-------|
| **1. Framework/Shell** | App-Rahmen, Docking, Layout, Routing. Keine Fachlogik. | `gui/shell/`, `gui/navigation/`, `gui/workspace/` | Es gibt **genau eine** Instanz. Kein anderes Modul darf diese Verantwortung übernehmen. |
| **2. Generische UI-Bausteine** | Wiederverwendbare, fachlogikfreie Komponenten. | `gui/panels/base/`, `gui/components/` | Werden von allen Domains genutzt. Keine Domain-Imports. |
| **3. Fachliche Bereichsmodule** | Workspace-Views und Domain-spezifische Panels. | `gui/domains/<domain>/` | Pro Domain ein Verzeichnis. Keine Cross-Domain-Imports. |
| **4. Feature-lokale Panels** | Panels, die von mehreren Domains genutzt werden, aber fachlich sind. | `gui/inspector/inspectors/`, `gui/monitors/panels/` | Zentral, weil geteilt. Keine Domain „besitzt“ sie. |

### 2.2 Getroffene Entscheidungen (verbindlich)

| Entscheidung | Varianten | Gewählte Lösung | Begründung |
|--------------|-----------|-----------------|------------|
| **Fachliche Panels: Ort** | A) In Domain. B) Zentral nach Typ. | **A: In Domain** (`gui/domains/<domain>/panels/`) | Klare Verantwortlichkeit. Domain bündelt alle zugehörigen Panels. Keine zentrale „explorer/“, „editor/“-Sammlung. |
| **Inspector-Panels: Ort** | A) In Domain. B) Zentral in inspector/inspectors/. | **B: Zentral** (`gui/inspector/inspectors/`) | InspectorHost lädt per area_id aus Registry. Einheitlicher Ort für alle Inspector-Implementierungen. Vermeidet Verstreuung über Domains. |
| **Monitor-Panels: Ort** | A) In Domain runtime_debug. B) Zentral. | **B: Zentral** (`gui/monitors/panels/`) | Werden von Operations (Bottom Panel) und Runtime (Main Workspace) genutzt. Keine Domain-Zuordnung. |
| **Runtime-Workspace: Struktur** | A) Eigene Tabs. B) Reuse Monitor-Panels. | **B: Reuse** | Runtime-Workspace zeigt dieselben Monitor-Panel-Instanzen oder -Klassen wie Bottom Panel. Eine Implementierung, zwei Hosts. |
| **Workspace-Views: Ort** | Immer in Domain. | **Domain** | Keine Ausnahme. Jeder Bereich hat `gui/domains/<domain>/workspace_view.py`. |
| **Basis-Panels: Pflicht** | Immer oder optional. | **Immer** | Jedes fachliche Panel muss von BaseExplorer/Editor/Inspector/Monitor/Dashboard erben. Keine freistehenden QWidget-Panels. |
| **Docking: Ort** | Nur Shell. | **Nur gui/shell/docking_config.py** | Kein anderes Modul darf QDockWidget erstellen oder addDockWidget aufrufen. |
| **Bereichswechsel: Mechanismus** | If/Else. Registry. | **Registry** | NavRegistry + WorkspaceFactory. Keine If/Else-Ketten in MainWindow. |

### 2.3 Entscheidungsmatrix: Wo liegt Komponente X?

| Komponente | Kategorie | Ort |
|------------|-----------|-----|
| MainWindow, DockingConfig, LayoutConstants | Framework/Shell | gui/shell/ |
| NavigationSidebar, NavAreas, NavRegistry | Framework/Shell | gui/navigation/ |
| TabbedWorkspace, WorkspaceFactory, BaseWorkspaceView | Framework/Shell | gui/workspace/ |
| InspectorHost | Framework/Shell | gui/inspector/ |
| MonitorHost | Framework/Shell | gui/monitors/ |
| BaseExplorerPanel, BaseEditorPanel, … | Generische UI-Bausteine | gui/panels/base/ |
| StatusCard, EmptyStateWidget, SearchableList, … | Generische UI-Bausteine | gui/components/ |
| ChatWorkspaceView, SessionExplorer, ChatEditor | Fachliche Bereichsmodule | gui/domains/operations/chat/ |
| CommandCenterDashboard | Fachliche Bereichsmodule | gui/domains/dashboard/ |
| AgentRegistryExplorer, AgentEditor | Fachliche Bereichsmodule | gui/domains/control_center/agents/ |
| TestInventoryWorkspaceView, TestExplorer | Fachliche Bereichsmodule | gui/domains/qa_governance/test_inventory/ |
| SessionInspector, AgentInspector | Feature-lokale Panels | gui/inspector/inspectors/ |
| LogsMonitor, EventBusMonitor, AgentActivityMonitor | Feature-lokale Panels | gui/monitors/panels/ |

---

## 3. Oberste GUI-Verzeichnisstruktur

### 3.1 Vollständiger Baum

```
app/
├── main.py                              # Entry Point (keine GUI-Logik außer MainWindow-Instanziierung)
│
├── gui/                                 # = GUI-Root (alle PySide6-UI-Module)
│   ├── __init__.py
│   │
│   ├── shell/                           # A. Shell – App-Rahmen, Docking, Layout
│   │   ├── __init__.py
│   │   ├── main_window.py
│   │   ├── docking_config.py            # Docking-Logik, Zonen-Größen, Layout-Persistenz
│   │   └── layout_constants.py          # Breiten, Höhen, Min/Max
│   │
│   ├── navigation/                      # B. Navigation – Bereichswechsel, Routing
│   │   ├── __init__.py
│   │   ├── sidebar.py                   # NavigationSidebarWidget
│   │   ├── nav_areas.py                 # NavArea Enum, Bereichs-IDs
│   │   └── nav_registry.py              # Screen-Registrierung, Routing-Tabelle
│   │
│   ├── workspace/                       # C. Workspaces – Tab-Host, Screen-Container
│   │   ├── __init__.py
│   │   ├── tabbed_workspace.py           # TabbedWorkspace (QTabWidget)
│   │   ├── workspace_factory.py          # Factory: area_id → WorkspaceView
│   │   └── base_workspace_view.py       # Basisklasse für alle Workspace-Views
│   │
│   ├── panels/                          # D. Panels – generisch + fachlich
│   │   ├── __init__.py
│   │   ├── base/                        # Generische Basis-Panels
│   │   │   ├── __init__.py
│   │   │   ├── base_explorer.py
│   │   │   ├── base_editor.py
│   │   │   ├── base_inspector.py
│   │   │   ├── base_monitor.py
│   │   │   └── base_dashboard.py
│   │   ├── registry.py                  # PanelRegistry (zentral)
│   │   └── (keine fachlichen Panels – diese liegen in gui/domains/)
│   │
│   ├── inspector/                       # E. Inspector – kontextabhängiger Host
│   │   ├── __init__.py
│   │   ├── inspector_host.py             # Host-Container, set_context()
│   │   └── inspectors/                  # Fachliche Inspector-Implementierungen
│   │       ├── __init__.py
│   │       ├── session_inspector.py
│   │       ├── agent_inspector.py
│   │       └── ...
│   │
│   ├── monitors/                        # F. Bottom-Monitor-Panels
│   │   ├── __init__.py
│   │   ├── monitor_host.py               # Bottom-Panel-Host (QTabWidget)
│   │   └── panels/                      # Monitor-Panel-Implementierungen
│   │       ├── __init__.py
│   │       ├── logs_monitor.py
│   │       ├── eventbus_monitor.py
│   │       ├── metrics_monitor.py
│   │       ├── agent_activity_monitor.py
│   │       └── llm_trace_monitor.py
│   │
│   ├── components/                      # G. Shared Components – wiederverwendbare Kleinteile
│   │   ├── __init__.py
│   │   ├── status_card.py
│   │   ├── empty_state.py
│   │   ├── loading_overlay.py
│   │   ├── searchable_list.py
│   │   ├── collapsible_group.py
│   │   └── live_indicator.py
│   │
│   └── domains/                         # H. Domains – fachliche Bereichs-Screens
│       ├── __init__.py
│       ├── dashboard/                   # Kommandozentrale
│       │   ├── __init__.py
│       │   ├── workspace_view.py
│       │   └── panels/
│       │       └── command_center_dashboard.py
│       ├── operations/                  # Operations Center
│       │   ├── __init__.py
│       │   ├── chat/
│       │   │   ├── __init__.py
│       │   │   ├── workspace_view.py
│       │   │   └── panels/
│       │   │       ├── session_explorer.py
│       │   │       └── chat_editor.py
│       │   ├── agent_tasks/
│       │   │   ├── __init__.py
│       │   │   ├── workspace_view.py
│       │   │   └── panels/
│       │   ├── knowledge/
│       │   │   ├── __init__.py
│       │   │   ├── workspace_view.py
│       │   │   └── panels/
│       │   └── prompt_studio/
│       │       ├── __init__.py
│       │       ├── workspace_view.py
│       │       └── panels/
│       ├── control_center/              # Control Center
│       │   ├── __init__.py
│       │   ├── models/
│       │   ├── providers/
│       │   ├── agents/
│       │   ├── tools/
│       │   └── data_stores/
│       ├── qa_governance/               # QA & Governance
│       │   ├── __init__.py
│       │   ├── test_inventory/
│       │   ├── coverage_map/
│       │   ├── gap_analysis/
│       │   ├── incidents/
│       │   └── replay_lab/
│       ├── runtime_debug/               # Runtime / Debug
│       │   ├── __init__.py
│       │   └── workspace_view.py        # TabWidget mit Reuse von gui/monitors/panels/
│       └── settings/                    # Settings
│           ├── __init__.py
│           ├── workspace_view.py
│           └── panels/
│
├── agents/                             # Fachlogik (keine GUI)
├── rag/
├── prompts/
├── qa/                                 # QA-Adapter, DTOs (keine GUI)
├── debug/
├── metrics/
├── providers/
├── db.py
├── settings.py
├── resources/                           # Styles, Icons, QRC
│   ├── styles.py
│   └── icons/
└── ...
```

---

## 4. Erklärung jeder Hauptgruppe

### 4.1 Shell (`gui/shell/`)

**Verantwortlichkeit:** App-Rahmen, Fensterstruktur, Docking, Layout-Persistenz.

| Datei | Inhalt |
|-------|--------|
| `main_window.py` | QMainWindow-Subklasse. Erstellt und verwaltet Docks, CentralWidget, Toolbar, StatusBar. **Keine** Fachlogik, **keine** Kenntnis von konkreten Screens. Ruft nur `WorkspaceFactory`, `DockingConfig` auf. |
| `docking_config.py` | Zentrale Docking-Logik: `setup_docks(main_window)`, `restore_layout()`, `save_layout()`. Einziger Ort für QDockWidget-Konfiguration. |
| `layout_constants.py` | Konstanten: `NAV_SIDEBAR_WIDTH`, `INSPECTOR_WIDTH`, `BOTTOM_PANEL_HEIGHT`, etc. |

**Regel:** Kein anderes Modul darf QDockWidget erstellen oder Layout-Zonen konfigurieren. Alle Docking-Änderungen laufen über `docking_config.py`.

---

### 4.2 Navigation (`gui/navigation/`)

**Verantwortlichkeit:** Bereichswechsel, Routing, Screen-Registrierung.

| Datei | Inhalt |
|-------|--------|
| `sidebar.py` | NavigationSidebarWidget. Zeigt hierarchische Liste. Emittiert `area_selected(area_id)`. **Keine** Kenntnis von Workspace-Inhalten. |
| `nav_areas.py` | NavArea-Enum oder -Konstanten. Alle gültigen Bereichs-IDs. Single Source of Truth für Navigation. |
| `nav_registry.py` | Registrierung: `(area_id, factory, title, icon)`. WorkspaceFactory nutzt diese Registry. Domain-Module registrieren sich hier. |

**Regel:** Navigation enthält **keine** Fachlogik. Keine If/Else-Ketten für Bereichswechsel. Nur: area_id → Registry → Factory.

---

### 4.3 Workspace (`gui/workspace/`)

**Verantwortlichkeit:** Tab-Host für Screens, Routing von area_id zu View.

| Datei | Inhalt |
|-------|--------|
| `tabbed_workspace.py` | QTabWidget. Zeigt Workspace-Views als Tabs. `show_area(area_id)` – erstellt oder wechselt zu Tab. |
| `workspace_factory.py` | `create_view(area_id) -> QWidget`. Nutzt NavRegistry. Lazy Loading. |
| `base_workspace_view.py` | Abstrakte Basis: `area_id`, `refresh()`, `refresh_theme()`. Alle Domain-Workspace-Views erben davon. |

**Regel:** Workspace kennt nur area_id und Factory. Keine Kenntnis von Chat, QA, Agents etc. als Konzepte – nur als area_id.

---

### 4.4 Panels (`gui/panels/`)

**Verantwortlichkeit:** Generische Basis-Panels + zentrale Registry. Fachliche Panels liegen in Domains.

| Unterordner | Inhalt |
|-------------|--------|
| `base/` | BaseExplorerPanel, BaseEditorPanel, BaseInspectorPanel, BaseMonitorPanel, BaseDashboardPanel. Abstrakte Schnittstellen, gemeinsame Logik (Dirty-State, Refresh, Theme). |
| `registry.py` | PanelRegistry. `register(panel_id, factory, area_id)`. Für dynamisches Laden von Inspector- und Monitor-Panels. |

**Regel:** Basis-Panels sind generisch. Keine Domain-spezifische Logik in `base/`. Fachliche Panels erben von Base und liegen in `gui/domains/<domain>/panels/`.

---

### 4.5 Inspector (`gui/inspector/`)

**Verantwortlichkeit:** Kontextabhängiger rechter Bereich.

| Datei | Inhalt |
|-------|--------|
| `inspector_host.py` | Host-Container. `set_context(area_id, context_object)`. Lädt passendes Inspector-Panel aus Registry. |
| `inspectors/` | **Alle** konkreten Inspector-Panels: SessionInspector, AgentInspector, CollectionInspector, TestInspector, etc. |

**Architekturentscheidung:** Inspector-Panels liegen **ausschließlich** in `gui/inspector/inspectors/`. Keine Inspector-Panels in Domains. Begründung: Einheitlicher Ort, InspectorHost lädt per area_id aus Registry. Vermeidet Verstreuung.

---

### 4.6 Monitors (`gui/monitors/`)

**Verantwortlichkeit:** Bottom-Panel-Inhalte (Logs, Events, Metrics, Agent Activity, LLM Trace).

| Datei | Inhalt |
|-------|--------|
| `monitor_host.py` | QTabWidget. Tabs für Logs, Events, Metrics, Agent Activity, LLM Trace. Einziger Ort für Bottom-Panel-Struktur. |
| `panels/` | LogsMonitor, EventBusMonitor, MetricsMonitor, AgentActivityMonitor, LLMTraceMonitor. Alle erben von BaseMonitorPanel. |

**Regel:** Monitor-Panels sind **zentral** in `monitors/panels/`, weil sie von mehreren Bereichen genutzt werden (Operations, Runtime). Keine Domain-spezifischen Monitor-Panels außerhalb.

---

### 4.7 Components (`gui/components/`)

**Verantwortlichkeit:** Wiederverwendbare Kleinteile ohne Fachlogik.

| Komponente | Verwendung |
|------------|------------|
| StatusCard | Dashboard-Karten |
| EmptyStateWidget | Leerer Zustand in Explorern |
| LoadingOverlay | Ladeanzeige |
| SearchableList | Liste mit Suche |
| CollapsibleGroup | Aufklappbare Sektion |
| LiveIndicator | „Live“-Badge für Monitore |

**Regel:** Keine Fachlogik. Keine Abhängigkeit von agents, rag, qa etc. Nur PySide6 und ggf. `resources/styles`.

---

### 4.8 Domains (`gui/domains/`)

**Verantwortlichkeit:** Fachliche Screens, Workspace-Views, Domain-spezifische Panels.

| Domain | Enthält |
|--------|---------|
| `dashboard/` | CommandCenterWorkspace, CommandCenterDashboard |
| `operations/chat/` | ChatWorkspaceView, SessionExplorer, ChatEditor |
| `operations/agent_tasks/` | AgentTasksWorkspaceView, TaskExplorer, TaskEditor |
| `operations/knowledge/` | KnowledgeWorkspaceView, CollectionExplorer, DocumentEditor |
| `operations/prompt_studio/` | PromptStudioWorkspaceView, PromptExplorer, PromptEditor |
| `control_center/models/` | ModelsWorkspaceView, ModelExplorer, ModelEditor |
| `control_center/providers/` | ProvidersWorkspaceView, ProviderExplorer, ProviderEditor |
| `control_center/agents/` | AgentsWorkspaceView, AgentRegistryExplorer, AgentEditor |
| `control_center/tools/` | ToolsWorkspaceView, ToolExplorer, ToolEditor |
| `control_center/data_stores/` | DataStoresWorkspaceView, StoreExplorer, StoreEditor |
| `qa_governance/test_inventory/` | TestInventoryWorkspaceView, TestExplorer, TestInspector |
| `qa_governance/coverage_map/` | CoverageMapWorkspaceView, CoverageDashboard |
| `qa_governance/gap_analysis/` | GapAnalysisWorkspaceView, GapDashboard, GapEditor |
| `qa_governance/incidents/` | IncidentsWorkspaceView, IncidentExplorer, IncidentEditor |
| `qa_governance/replay_lab/` | ReplayLabWorkspaceView, ReplayExplorer, ReplayEditor |
| `runtime_debug/` | RuntimeWorkspaceView (TabWidget mit EventBus, Logs, Metrics, etc.) oder Nutzung von monitors/ |
| `settings/` | SettingsWorkspaceView, SettingsEditor |

**Regel:** Jede Domain hat maximal: `workspace_view.py`, `panels/`. Keine Domain kennt eine andere Domain. Keine Domain erstellt Docks oder konfiguriert Layout. Domain registriert sich in NavRegistry. Domain-Panels sind nur Explorer, Editor, Dashboard – **keine** Inspector-Panels (diese liegen in gui/inspector/inspectors/).

---

## 4. Zuordnung der wichtigsten UI-Komponenten

| Komponente | Gruppe | Pfad |
|-------------|--------|------|
| MainWindow | Shell | gui/shell/main_window.py |
| DockingConfig | Shell | gui/shell/docking_config.py |
| NavigationSidebarWidget | Navigation | gui/navigation/sidebar.py |
| NavArea, NavRegistry | Navigation | gui/navigation/nav_areas.py, nav_registry.py |
| TabbedWorkspace | Workspace | gui/workspace/tabbed_workspace.py |
| WorkspaceFactory | Workspace | gui/workspace/workspace_factory.py |
| BaseExplorerPanel, BaseEditorPanel, … | Panels | gui/panels/base/ |
| PanelRegistry | Panels | gui/panels/registry.py |
| InspectorHost | Inspector | gui/inspector/inspector_host.py |
| SessionInspector, AgentInspector | Feature-lokal | gui/inspector/inspectors/ |
| MonitorHost | Monitors | gui/monitors/monitor_host.py |
| LogsMonitor, EventBusMonitor, AgentActivityMonitor | Monitors | gui/monitors/panels/ |
| StatusCard, EmptyStateWidget | Components | gui/components/ |
| ChatWorkspaceView, SessionExplorer, ChatEditor | Domains | gui/domains/operations/chat/ |
| CommandCenterDashboard | Domains | gui/domains/dashboard/ |
| TestInventoryWorkspaceView, TestExplorer | Domains | gui/domains/qa_governance/test_inventory/ |
| AgentRegistryExplorer, AgentEditor | Domains | gui/domains/control_center/agents/ |

---

## 5. Benennungsregeln

### 5.1 Dateinamen

| Typ | Muster | Beispiel |
|-----|--------|----------|
| Workspace-View | `workspace_view.py` | chat/workspace_view.py |
| Panel (Explorer) | `*_explorer.py` | session_explorer.py |
| Panel (Editor) | `*_editor.py` | chat_editor.py |
| Panel (Inspector) | `*_inspector.py` | session_inspector.py |
| Panel (Monitor) | `*_monitor.py` | logs_monitor.py |
| Panel (Dashboard) | `*_dashboard.py` | command_center_dashboard.py |
| Basis-Klasse | `base_*.py` | base_explorer.py |

### 5.2 Klassennamen

| Typ | Muster | Beispiel |
|-----|--------|----------|
| Workspace-View | `<Domain><Subdomain>WorkspaceView` | ChatWorkspaceView, AgentTasksWorkspaceView |
| Explorer | `<Entity>Explorer` | SessionExplorer, TaskExplorer |
| Editor | `<Entity>Editor` | ChatEditor, PromptEditor |
| Inspector | `<Entity>Inspector` | SessionInspector, AgentInspector |
| Monitor | `<Source>Monitor` | LogsMonitor, EventBusMonitor |
| Dashboard | `<Context>Dashboard` | CommandCenterDashboard |

### 5.3 Modul-/Package-Namen

- **Snake_case** für Dateien und Verzeichnisse: `workspace_view.py`, `agent_tasks/`
- **Keine** CamelCase in Pfaden
- Domain-Namen: `dashboard`, `operations`, `control_center`, `qa_governance`, `runtime_debug`, `settings`

### 5.4 NavArea-IDs

- **Snake_case**, lowercase: `command_center`, `operations_chat`, `operations_agent_tasks`, `control_models`, `qa_test_inventory`, `runtime_eventbus`, `settings`

---

## 6. Erweiterungsregeln

### 6.1 Neuen Bereich (Unterbereich) hinzufügen

1. **NavArea erweitern:** `nav_areas.py` – neue Konstante
2. **NavRegistry erweitern:** `nav_registry.py` – Registrierung mit Factory
3. **Domain anlegen:** `gui/domains/<domain>/<subdomain>/`
   - `workspace_view.py`
   - `panels/` (falls nötig)
4. **Factory registrieren:** In `nav_registry.py` oder Domain-`__init__.py` bei App-Start

### 6.2 Neues Panel hinzufügen

| Panel-Typ | Ort | Vorgehen |
|-----------|-----|----------|
| Explorer/Editor/Dashboard (fachlich) | `gui/domains/<domain>/panels/` | Datei anlegen, von Base erben, in WorkspaceView einbinden |
| Inspector | `gui/inspector/inspectors/` | Panel erstellen, von BaseInspectorPanel erben, in InspectorRegistry registrieren. **Keine** Inspector-Panels in Domains. |
| Monitor | `gui/monitors/panels/` | Panel erstellen, von BaseMonitorPanel erben, in MonitorHost als Tab hinzufügen |
| Shared Component | `gui/components/` | Nur wenn von mindestens zwei Domains genutzt; keine Fachlogik |

### 6.3 Neue Domain hinzufügen

**Nur bei UX-Review und Begründung.** Maximal 6 Hauptbereiche.

1. `gui/domains/<neue_domain>/` anlegen
2. `workspace_view.py`, `panels/` erstellen
3. NavArea + NavRegistry erweitern
4. Navigation Sidebar-Konfiguration erweitern (in `sidebar.py` oder Konfigurationsdatei)

### 6.4 Panel-Registry-Nutzung

- **Inspector:** `InspectorHost.set_context(area_id, obj)` → Registry liefert passendes Inspector-Panel
- **Monitor:** Monitor-Panels sind fest in MonitorHost als Tabs. Keine dynamische Registry nötig, außer für optionale/Plugin-Monitore.

---

## 7. Anti-Pattern-Liste für GUI-Wildwuchs

| Anti-Pattern | Stattdessen |
|--------------|-------------|
| **QDockWidget außerhalb von docking_config.py** | Alle Docks in Shell, DockingConfig |
| **Layout-Logik in Domain-Panels** | Layout in Shell/Workspace; Panels nur Content |
| **If/Else für Bereichswechsel in MainWindow** | NavRegistry + WorkspaceFactory |
| **Neues Panel ohne Base-Klasse** | Immer von BaseExplorer/Editor/Inspector/Monitor/Dashboard erben |
| **Fachlogik in Navigation** | Navigation nur area_id; keine Chat-/QA-Logik |
| **Domain kennt andere Domain** | Keine Cross-Domain-Imports in gui/domains |
| **Eigener TabWidget pro Domain** | Ein TabbedWorkspace zentral; Domains liefern nur View |
| **Verstreute QSplitter-Konfiguration** | Splitter nur in Shell oder WorkspaceView; einheitliches Muster |
| **Panel in app/ root** | Alle Panels unter gui/panels oder gui/domains |
| **Dialog für komplexen Workflow** | Eigener Workspace-Bereich |
| **Mehrere konkurrierende Panel-Typen** | Nur 5: Explorer, Editor, Inspector, Monitor, Dashboard |
| **Ungeklärte Verantwortung** | Shell= Rahmen, Navigation= Routing, Workspace= Tabs, Domains= Content |

---

## 8. Zentrale vs. feature-lokale Komponenten (verbindlich)

### 8.1 Framework/Shell – zentral, genau eine Instanz

| Komponente | Ort | Regel |
|------------|-----|-------|
| MainWindow | gui/shell/ | Einzige QMainWindow-Instanz |
| DockingConfig | gui/shell/ | Einziger Ort für QDockWidget |
| NavigationSidebar | gui/navigation/ | Einzige Navigation |
| TabbedWorkspace | gui/workspace/ | Einziger Workspace-Host |
| WorkspaceFactory | gui/workspace/ | Einziges Routing |
| InspectorHost | gui/inspector/ | Einziger Inspector-Host |
| MonitorHost | gui/monitors/ | Einziges Bottom-Panel-Host |
| NavRegistry, PanelRegistry | gui/navigation/, gui/panels/ | Einzige Registrierungen |

### 8.2 Generische UI-Bausteine – zentral, wiederverwendbar

| Komponente | Ort | Regel |
|------------|-----|-------|
| BaseExplorerPanel, BaseEditorPanel, … | gui/panels/base/ | Alle Domain-Panels erben davon |
| StatusCard, EmptyStateWidget, … | gui/components/ | Keine Fachlogik, keine Domain-Imports |

### 8.3 Fachliche Bereichsmodule – domain-lokal

| Komponente | Ort | Regel |
|------------|-----|-------|
| WorkspaceView | gui/domains/<domain>/ | Pro Bereich genau eine |
| Explorer, Editor, Dashboard (fachlich) | gui/domains/<domain>/panels/ | Immer in der Domain, die den Kontext besitzt |

### 8.4 Feature-lokale Panels – zentral, von mehreren Domains genutzt

| Komponente | Ort | Regel |
|------------|-----|-------|
| SessionInspector, AgentInspector, … | gui/inspector/inspectors/ | **Alle** Inspector-Panels hier. Keine in Domains. |
| LogsMonitor, EventBusMonitor, … | gui/monitors/panels/ | **Alle** Monitor-Panels hier. Werden von Bottom Panel und Runtime-Workspace genutzt. |

---

## 9. Basisklassen und abstrakte GUI-Typen

### 9.1 Basisklassen-Hierarchie

```
QWidget
├── BaseWorkspaceView          # gui/workspace/base_workspace_view.py
│   └── area_id: str
│   └── refresh(), refresh_theme()
│
├── BaseExplorerPanel         # gui/panels/base/base_explorer.py
│   └── selection_changed, refresh()
│
├── BaseEditorPanel           # gui/panels/base/base_editor.py
│   └── dirty_changed, save(), revert()
│
├── BaseInspectorPanel        # gui/panels/base/base_inspector.py
│   └── set_object(obj), clear()
│
├── BaseMonitorPanel          # gui/panels/base/base_monitor.py
│   └── start(), pause(), clear(), refresh()
│
└── BaseDashboardPanel        # gui/panels/base/base_dashboard.py
    └── refresh()
```

### 9.2 Ablage der Basisklassen

- **Ort:** `gui/panels/base/`
- **Import:** `from app.gui.panels.base import BaseExplorerPanel, BaseEditorPanel, ...`
- **Regel:** Keine Domain-Imports in base/. Basisklassen kennen nur Qt und ggf. resources.

---

## 10. Docking- und Layoutlogik – Organisation

### 10.1 Einziger Ort: gui/shell/

| Datei | Verantwortung |
|-------|---------------|
| `docking_config.py` | `setup_docks(main_window)` – erstellt QDockWidgets, setzt allowedAreas, features, Größen. `restore_layout()`, `save_layout()` für Persistenz. |
| `layout_constants.py` | `NAV_SIDEBAR_WIDTH`, `INSPECTOR_WIDTH`, `BOTTOM_PANEL_HEIGHT`, `NAV_SIDEBAR_MIN`, etc. |
| `main_window.py` | Ruft `DockingConfig.setup_docks(self)` auf. Keine manuelle Dock-Erstellung. |

### 10.2 Regel

**Kein anderes Modul darf:**
- `addDockWidget` aufrufen
- `QDockWidget` instanziieren
- `setAllowedAreas`, `setFeatures` setzen

**Ausnahme:** Wenn ein Domain-Panel intern einen QSplitter für Explorer/Editor-Aufteilung nutzt – das ist **innerhalb** des Panel-Layouts, nicht App-Docking.

---

## 11. Screen-Registrierung, Navigation, Workspace-Routing

### 11.1 Ablauf

```
1. App-Start
   → NavRegistry lädt Konfiguration (aus Code oder JSON)
   → Jede Domain registriert: register(area_id, factory, title, icon)

2. Nutzer klickt in Sidebar
   → Sidebar emittiert area_selected(area_id)

3. MainWindow empfängt area_selected
   → TabbedWorkspace.show_area(area_id)

4. TabbedWorkspace
   → Prüft: Tab für area_id bereits offen? → Wechseln
   → Sonst: WorkspaceFactory.create_view(area_id) → Neuer Tab

5. WorkspaceFactory
   → NavRegistry.get_factory(area_id) → factory()
   → Lazy: View erst bei erstem Aufruf
```

### 11.2 NavRegistry-Struktur (Konzept)

```
NavRegistry
├── register(area_id, factory, title, icon, parent_area?)
├── get_factory(area_id) -> Callable
├── get_title(area_id) -> str
├── get_icon(area_id) -> str
├── get_children(area_id) -> [area_id, ...]   # Für hierarchische Sidebar
└── list_areas() -> [area_id, ...]
```

### 11.3 Registrierung durch Domains

Jede Domain hat einen Einstiegspunkt (z.B. in `__init__.py`):

```
# gui/domains/operations/chat/__init__.py
def register():
    from app.gui.navigation.nav_registry import get_nav_registry
    get_nav_registry().register(
        area_id=NavArea.OPERATIONS_CHAT,
        factory=lambda: ChatWorkspaceView(...),
        title="Chat",
        icon="chat.svg",
        parent_area=NavArea.OPERATIONS,
    )
```

MainWindow oder ein Bootstrap-Modul ruft bei Start alle `register()` der Domains auf.

---

## 12. Trennung Operations / QA / Runtime

### 12.1 Organisatorische Trennung

| Bereich | Domain-Pfad | Keine Vermischung mit |
|---------|-------------|------------------------|
| Operations | gui/domains/operations/ | control_center, qa_governance, runtime_debug |
| Control Center | gui/domains/control_center/ | operations, qa_governance, runtime_debug |
| QA & Governance | gui/domains/qa_governance/ | operations, control_center, runtime_debug |
| Runtime / Debug | gui/domains/runtime_debug/ + gui/monitors/ | operations, control_center, qa_governance |

### 12.2 Import-Regel

- **Domain A importiert nicht Domain B.** Keine `from app.gui.domains.qa_governance import ...` in operations.
- **Gemeinsame Nutzung:** Über Shell (Workspace wechselt), über Inspector (kontextabhängig), über Monitor (Bottom Panel).
- **Fachlogik:** Domains importieren `app.agents`, `app.qa`, `app.rag` etc. – das ist erlaubt. Nur keine GUI-Cross-Domain-Imports.

### 12.3 Runtime vs. Monitors (verbindliche Entscheidung)

**Entscheidung:** Runtime-Workspace und Bottom Panel nutzen **dieselben** Monitor-Panel-Klassen aus `gui/monitors/panels/`. Eine Implementierung, zwei Hosts.

- **Runtime/Debug als Hauptbereich:** Nutzer wählt „Runtime / Debug“ → RuntimeWorkspaceView zeigt TabWidget mit EventBus, Logs, Metrics, Agent Activity, LLM Trace (aus gui/monitors/panels/).
- **Bottom Panel:** MonitorHost zeigt dieselben Panel-Typen als Tabs. Nutzer kann bei Arbeit in Operations das Bottom Panel einblenden.
- **Keine Duplikation:** Keine eigenen Monitor-Panels in gui/domains/runtime_debug/. Nur gui/monitors/panels/.

---

## 13. Konkrete Empfehlung: Neue Screens und Panels anlegen

### 13.1 Neuer Screen (Workspace-Bereich)

1. Domain prüfen: Gehört zu bestehender Domain? → Unterbereich. Neue Domain? → UX-Review.
2. `gui/domains/<domain>/<subdomain>/` anlegen
3. `workspace_view.py` erstellen, von BaseWorkspaceView erben
4. In `nav_areas.py` area_id hinzufügen
5. In Domain-`__init__.py` oder zentraler Bootstrap: `NavRegistry.register(...)`
6. Sidebar-Konfiguration erweitern (falls hierarchisch)

### 13.2 Neues Panel (Explorer/Editor/Inspector/Dashboard)

1. **Typ wählen:** Explorer, Editor, Inspector, Monitor, Dashboard
2. **Ort:** `gui/domains/<domain>/panels/<name>_<typ>.py`
3. **Basis:** Von entsprechender Base-Klasse erben
4. **Einbindung:** In WorkspaceView einbinden (Layout)
5. **Registry:** Nur bei Inspector, wenn kontextabhängig geladen wird

### 13.3 Neues Monitor-Panel

1. `gui/monitors/panels/<name>_monitor.py` erstellen
2. Von BaseMonitorPanel erben
3. In `monitor_host.py` als neuen Tab registrieren
4. Keine Domain-Anbindung nötig – Monitor ist zentral

### 13.4 Neue Shared Component

1. Prüfen: Wirklich wiederverwendbar über mehrere Domains?
2. `gui/components/<name>.py` erstellen
3. Keine Fachlogik, keine Domain-Imports
4. In benötigten Panels importieren

---

## 14. Zusammenfassung

| Aspekt | Festlegung |
|--------|------------|
| **GUI-Root** | app/gui/ |
| **Shell** | gui/shell/ – MainWindow, DockingConfig, LayoutConstants |
| **Navigation** | gui/navigation/ – Sidebar, NavAreas, NavRegistry |
| **Workspace** | gui/workspace/ – TabbedWorkspace, Factory, BaseWorkspaceView |
| **Panels** | gui/panels/base/ + gui/domains/<domain>/panels/ |
| **Inspector** | gui/inspector/ – Host + inspectors/ |
| **Monitors** | gui/monitors/ – Host + panels/ |
| **Components** | gui/components/ – wiederverwendbare Kleinteile |
| **Domains** | gui/domains/ – dashboard, operations, control_center, qa_governance, runtime_debug, settings |
| **Docking** | Nur in gui/shell/docking_config.py |
| **Routing** | NavRegistry + WorkspaceFactory, keine If/Else |
| **Basisklassen** | gui/panels/base/ – 5 Typen |
| **Erweiterung** | Domain registriert sich; Panel in Domain oder monitors/ |

---

## 15. Migrationspfad (aktueller Zustand → Ziel)

**Detaillierte Migrations-Roadmap:** docs/GUI_MIGRATION_ROADMAP.md

### 15.1 Aktuelle Struktur (vor Migration)

```
app/
├── main.py
├── chat_widget.py              # → gui/domains/operations/chat/
├── sidebar_widget.py          # → gui/navigation/ + gui/domains/operations/chat/panels/
├── project_chat_list_widget.py # → gui/domains/operations/chat/
├── ui/
│   ├── command_center/        # → gui/domains/dashboard/ + gui/domains/qa_governance/
│   ├── chat/                  # → gui/domains/operations/chat/
│   ├── agents/                # → gui/domains/control_center/agents/ + operations/agent_tasks/
│   ├── debug/                 # → gui/monitors/panels/ + gui/domains/runtime_debug/
│   ├── sidepanel/             # → gui/domains/control_center/ (models, prompts) + gui/monitors/
│   └── settings_dialog.py     # → gui/domains/settings/
└── ...
```

### 15.2 Migrations-Reihenfolge (empfohlen)

1. **Phase 1 – Shell:** `gui/shell/` anlegen, MainWindow migrieren, DockingConfig einführen
2. **Phase 2 – Navigation:** `gui/navigation/` anlegen, Sidebar aus sidebar_widget extrahieren
3. **Phase 3 – Workspace:** `gui/workspace/` anlegen, TabbedWorkspace, Factory
4. **Phase 4 – Panels Base:** `gui/panels/base/` anlegen, Basisklassen
5. **Phase 5 – Components:** `gui/components/` anlegen, StatusCard etc.
6. **Phase 6 – Domains:** Schrittweise Domain für Domain migrieren (dashboard → operations/chat → …)
7. **Phase 7 – Inspector & Monitors:** `gui/inspector/`, `gui/monitors/` anlegen

### 15.3 Kompatibilität während Migration

- Alte `app/ui/` und neue `gui/` können temporär parallel existieren
- MainWindow kann schrittweise von QStackedWidget+Chat auf TabbedWorkspace+Domains umstellen
- Alte Imports (`from app.chat_widget import ChatWidget`) durch Adapter oder schrittweise Umstellung ersetzen

---

## 16. Verbindlichkeit

Diese Architektur ist **verbindliche Grundlage** für die GUI-Implementierung. Es handelt sich um **Architekturentscheidungen**, nicht um Empfehlungen.

| Aspekt | Verbindlichkeit |
|--------|-----------------|
| Vier-Säulen-Modell | Jede Komponente gehört genau einer Kategorie. Keine Ausnahmen ohne Review. |
| Fachliche Panels in Domains | Verbindlich. Keine zentrale explorer/editor-Sammlung. |
| Inspector-Panels zentral | Verbindlich. Alle in gui/inspector/inspectors/. |
| Monitor-Panels zentral | Verbindlich. Alle in gui/monitors/panels/. Runtime reuses, dupliziert nicht. |
| Docking nur in Shell | Verbindlich. Kein QDockWidget außerhalb docking_config.py. |
| Routing über Registry | Verbindlich. Keine If/Else-Ketten für Bereichswechsel. |
| Basis-Panels Pflicht | Verbindlich. Jedes fachliche Panel erbt von Base*. |

**Abweichungen** bedürfen einer Architektur-Review und dokumentierter Begründung.

---

*Diese Architektur ist verbindlich für alle GUI-Entwicklung.*

# Screen- und Klassenarchitektur – Linux Desktop Chat

**Version:** 1.0  
**Datum:** 2026-03-15  
**Referenz:** docs/UX_CONCEPT.md, docs/PYSIDE6_UI_ARCHITECTURE.md, docs/GUI_REPOSITORY_ARCHITECTURE.md  
**Status:** Verbindliche Grundlage für GUI-Implementierung

---

## 1. Architekturüberblick

### 1.1 Ebenenmodell

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│  Ebene 1: Application Shell                                                      │
│  MainWindow, DockingConfig, TopBar, StatusBar                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Ebene 2: Navigation Layer                                                       │
│  NavigationSidebar, NavRegistry, NavArea                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Ebene 3: Screen Registration / Routing Layer                                    │
│  NavRegistry, WorkspaceFactory                                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Ebene 4: Workspace Layer (TabbedWorkspace = WorkspaceHost)                      │
│  Enthält: WorkspaceViews (Screens) als Tabs                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Ebene 5: Screen Layer (WorkspaceViews)                                           │
│  CommandCenterScreen, ChatWorkspace, AgentTasksWorkspace, ...                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Ebene 6: Panel Layer                                                            │
│  Explorer-, Editor-, Dashboard-Panels innerhalb von Screens                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Ebene 7: Inspector Layer                                                       │
│  InspectorHost + Inspector-Panels (SessionInspector, AgentInspector, ...)         │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Ebene 8: Bottom Monitor Layer                                                   │
│  MonitorHost + Monitor-Panels (LogsMonitor, EventBusMonitor, ...)               │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Ebene 9: Shared UI Components                                                    │
│  StatusCard, EmptyStateWidget, BaseExplorerPanel, ...                            │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Kernantworten (verbindlich)

| Frage | Antwort |
|-------|---------|
| **Welche Klasse ist das eigentliche MainWindow?** | `MainWindow` (gui/shell/main_window.py). Subklasse von QMainWindow. Einzige Instanz. |
| **Welche Klasse verwaltet die linke Hauptnavigation?** | `NavigationSidebar` (gui/navigation/sidebar.py). Zeigt hierarchische Liste, emittiert area_selected. |
| **Welche Klasse verwaltet Bereichswechsel?** | `WorkspaceFactory` + `NavRegistry`. Factory erstellt/holt WorkspaceView; TabbedWorkspace zeigt ihn. MainWindow leitet area_selected an TabbedWorkspace weiter. |
| **Welche Klasse hält den zentralen Workspace?** | `TabbedWorkspace` (gui/workspace/tabbed_workspace.py). QTabWidget als CentralWidget. |
| **Welche Klassen repräsentieren Hauptscreens?** | Jeder Screen = eine WorkspaceView-Klasse. Es gibt keine „Hauptscreen“-Container; die 6 Bereiche sind Navigationsgruppen. Jeder Blatt-Screen (command_center, operations_chat, …) ist eine WorkspaceView. |
| **Welche Klassen repräsentieren Subscreens?** | Keine separate Subscreen-Klasse. Operations hat 4 Screens (Chat, Agent Tasks, Knowledge, Prompt Studio) – jeder ist eigenständige WorkspaceView. Kein „OperationsScreen“-Container. |
| **Welche Klassen repräsentieren Panels?** | Explorer-, Editor-, Dashboard-Panels (z.B. SessionExplorerPanel, ChatEditorPanel). Erben von BaseExplorerPanel, BaseEditorPanel, BaseDashboardPanel. |
| **Welche Klassen repräsentieren Inspector-Inhalte?** | Inspector-Panels (SessionInspector, AgentInspector, …). Erben von BaseInspectorPanel. Liegen in gui/inspector/inspectors/. |
| **Welche Klassen repräsentieren Bottom-Monitore?** | Monitor-Panels (LogsMonitor, EventBusMonitor, AgentActivityMonitor, …). Erben von BaseMonitorPanel. Liegen in gui/monitors/panels/. |
| **Welche Klassen sind wiederverwendbar?** | BaseExplorerPanel, BaseEditorPanel, BaseInspectorPanel, BaseMonitorPanel, BaseDashboardPanel, BaseWorkspaceView. Shared Components (StatusCard, EmptyStateWidget, …). |
| **Welche Klassen dürfen bereichsspezifisch sein?** | WorkspaceViews, Domain-Panels (Explorer, Editor, Dashboard). |

---

## 2. Screen-Matrix

### 2.1 Vollständige Liste der Screens

Jeder Screen = eine WorkspaceView = ein Tab im TabbedWorkspace = eine area_id.

| # | area_id | Screen-Klasse | Typ | Parent (Navigation) |
|---|---------|---------------|-----|---------------------|
| 1 | command_center | CommandCenterScreen | Hauptscreen | — |
| 2 | operations_chat | ChatWorkspace | Screen | Operations |
| 3 | operations_agent_tasks | AgentTasksWorkspace | Screen | Operations |
| 4 | operations_knowledge | KnowledgeWorkspace | Screen | Operations |
| 5 | operations_prompt_studio | PromptStudioWorkspace | Screen | Operations |
| 6 | control_models | ModelsWorkspace | Screen | Control Center |
| 7 | control_providers | ProvidersWorkspace | Screen | Control Center |
| 8 | control_agents | AgentsWorkspace | Screen | Control Center |
| 9 | control_tools | ToolsWorkspace | Screen | Control Center |
| 10 | control_data_stores | DataStoresWorkspace | Screen | Control Center |
| 11 | qa_test_inventory | TestInventoryWorkspace | Screen | QA & Governance |
| 12 | qa_coverage_map | CoverageMapWorkspace | Screen | QA & Governance |
| 13 | qa_gap_analysis | GapAnalysisWorkspace | Screen | QA & Governance |
| 14 | qa_incidents | IncidentsWorkspace | Screen | QA & Governance |
| 15 | qa_replay_lab | ReplayLabWorkspace | Screen | QA & Governance |
| 16 | runtime_eventbus | — | Monitor-Tab | Runtime (reuses Monitor) |
| 17 | runtime_logs | — | Monitor-Tab | Runtime |
| 18 | runtime_metrics | — | Monitor-Tab | Runtime |
| 19 | runtime_llm_calls | — | Monitor-Tab | Runtime |
| 20 | runtime_agent_activity | — | Monitor-Tab | Runtime |
| 21 | runtime_system_graph | SystemGraphWorkspace | Screen | Runtime |
| 22 | settings | SettingsScreen | Hauptscreen | — |

**Entscheidung:** Es gibt **keine** eigenständigen „Hauptscreen“-Container (z.B. OperationsScreen mit Sub-Tabs). Jeder Blatt-Bereich ist ein eigener Screen/Tab. Navigation gruppiert nur visuell (Operations → Chat, Agent Tasks, …). TabbedWorkspace zeigt pro area_id einen Tab.

### 2.2 Eigenständige Screens vs. Unter-Screens

| Kategorie | Definition | Beispiele |
|-----------|------------|-----------|
| **Eigenständiger Screen** | Erscheint als eigener Tab. Kein Parent-Screen. | CommandCenterScreen, SettingsScreen |
| **Unter-Screen (gruppiert)** | Erscheint als eigener Tab. Parent ist nur Navigationsgruppe, kein UI-Container. | ChatWorkspace, AgentTasksWorkspace (Parent: Operations in Sidebar) |
| **Runtime-Sonderfall** | runtime_eventbus bis runtime_agent_activity sind Tabs innerhalb von RuntimeWorkspace (QTabWidget). runtime_system_graph kann eigener Tab sein. | RuntimeWorkspace zeigt TabWidget mit Monitor-Panels |

**Architekturentscheidung:** Runtime-Bereich nutzt **RuntimeWorkspace** als Container mit interner QTabWidget (EventBus, Logs, Metrics, LLM Calls, Agent Activity, System Graph). Diese sind **keine** eigenständigen Screens im TabbedWorkspace, sondern Tabs innerhalb von RuntimeWorkspace. Begründung: 6 Runtime-Tabs würden TabbedWorkspace überladen; logische Gruppierung.

### 2.3 Screen → Panel → Inspector → Bottom-Monitor Zuordnung

| Screen | Explorer-Panel | Editor-Panel | Dashboard-Panel | Inspector | Bottom-Monitor |
|--------|----------------|--------------|-----------------|-----------|----------------|
| **CommandCenterScreen** | — | — | CommandCenterDashboard | — | — |
| **ChatWorkspace** | SessionExplorerPanel | ChatEditorPanel | — | SessionInspector | optional: Logs, AgentActivity |
| **AgentTasksWorkspace** | TaskExplorerPanel | TaskEditorPanel | — | AgentInspector | optional: AgentActivityMonitor |
| **KnowledgeWorkspace** | CollectionExplorerPanel | DocumentEditorPanel | — | CollectionInspector | — |
| **PromptStudioWorkspace** | PromptExplorerPanel | PromptEditorPanel | — | PromptInspector | — |
| **ModelsWorkspace** | ModelExplorerPanel | ModelEditorPanel | — | ModelInspector | — |
| **ProvidersWorkspace** | ProviderExplorerPanel | ProviderEditorPanel | — | ProviderInspector | — |
| **AgentsWorkspace** | AgentRegistryPanel | AgentEditorPanel | — | AgentDetailInspector | — |
| **ToolsWorkspace** | ToolExplorerPanel | ToolEditorPanel | — | ToolInspector | — |
| **DataStoresWorkspace** | DataStoreExplorerPanel | DataStoreEditorPanel | — | DataStoreInspector | — |
| **TestInventoryWorkspace** | TestExplorerPanel | — | — | TestDetailInspector | — |
| **CoverageMapWorkspace** | — | — | CoverageDashboard | — | — |
| **GapAnalysisWorkspace** | — | GapEditorPanel | GapDashboard | GapInspector | — |
| **IncidentsWorkspace** | IncidentExplorerPanel | IncidentEditorPanel | — | IncidentInspector | — |
| **ReplayLabWorkspace** | ReplayExplorerPanel | ReplayEditorPanel | — | ReplayInspector | — |
| **RuntimeWorkspace** | — | — | — | — | EventBus, Logs, Metrics, LLMCalls, AgentActivity, SystemGraph (als Tabs) |
| **SettingsScreen** | — | SettingsEditorPanel | — | — | — |

---

## 3. Klassen-Matrix

### 3.1 Shell-Klassen

| Klasse | Typ | Verantwortlichkeit | Generisch/Fach | Abhängigkeiten |
|--------|-----|-------------------|----------------|----------------|
| **MainWindow** | Shell | QMainWindow. Erstellt Docks via DockingConfig. Setzt CentralWidget (TabbedWorkspace). Verbindet area_selected → TabbedWorkspace.show_area. Keine Fachlogik. | Generisch | DockingConfig, TabbedWorkspace, NavigationSidebar, InspectorHost, MonitorHost |
| **DockingConfig** | Shell | setup_docks(mw), restore_layout(), save_layout(). Einziger Ort für QDockWidget. | Generisch | MainWindow |
| **LayoutConstants** | Shell | NAV_SIDEBAR_WIDTH, INSPECTOR_WIDTH, etc. | Generisch | — |
| **TopBar** | Shell | QToolBar. Globaler Status, Quick Actions, Suche/Command Palette. | Generisch | MainWindow |
| **NavigationSidebar** | Shell | QWidget. Hierarchische Liste. Emittiert area_selected(area_id). Keine Fachlogik. | Generisch | NavRegistry (für Struktur) |
| **TabbedWorkspace** | Shell | QTabWidget. WorkspaceHost. show_area(area_id). Fügt Tab hinzu oder wechselt. | Generisch | WorkspaceFactory |
| **InspectorHost** | Shell | QWidget. set_context(area_id, obj). Lädt Inspector-Panel aus Registry. | Generisch | InspectorRegistry |
| **MonitorHost** | Shell | QTabWidget. Tabs: Logs, Events, Metrics, AgentActivity, LLMTrace. | Generisch | Monitor-Panels |

### 3.2 Navigation- und Routing-Klassen

| Klasse | Typ | Verantwortlichkeit | Generisch/Fach | Abhängigkeiten |
|--------|-----|-------------------|----------------|----------------|
| **NavArea** | Routing | Enum/Konstanten aller area_ids. | Generisch | — |
| **NavRegistry** | Routing | register(area_id, factory, title, icon, parent_area). get_factory(area_id). get_children(area_id). | Generisch | — |
| **WorkspaceFactory** | Routing | create_view(area_id) → QWidget. Nutzt NavRegistry. Lazy Loading. | Generisch | NavRegistry |
| **NavigationItemDefinition** | Routing | DTO: area_id, title, icon, parent, children. Für Sidebar-Aufbau. | Generisch | NavArea |

### 3.3 Screen-Klassen (WorkspaceViews)

| Klasse | Typ | Verantwortlichkeit | Generisch/Fach | Abhängigkeiten |
|--------|-----|-------------------|----------------|----------------|
| **BaseWorkspaceView** | Basis | area_id, refresh(), refresh_theme(). Abstrakte Basis. | Generisch | — |
| **CommandCenterScreen** | Screen | Dashboard. Status-Karten, Quick Actions. Erbt BaseWorkspaceView. | Fach | CommandCenterDashboard |
| **ChatWorkspace** | Screen | Layout: SessionExplorer + ChatEditor. Koordiniert Panels. | Fach | SessionExplorerPanel, ChatEditorPanel |
| **AgentTasksWorkspace** | Screen | Layout: TaskExplorer + TaskEditor. | Fach | TaskExplorerPanel, TaskEditorPanel |
| **KnowledgeWorkspace** | Screen | Layout: CollectionExplorer + DocumentEditor. | Fach | CollectionExplorerPanel, DocumentEditorPanel |
| **PromptStudioWorkspace** | Screen | Layout: PromptExplorer + PromptEditor. | Fach | PromptExplorerPanel, PromptEditorPanel |
| **ModelsWorkspace** | Screen | Layout: ModelExplorer + ModelEditor. | Fach | ModelExplorerPanel, ModelEditorPanel |
| **ProvidersWorkspace** | Screen | Layout: ProviderExplorer + ProviderEditor. | Fach | ProviderExplorerPanel, ProviderEditorPanel |
| **AgentsWorkspace** | Screen | Layout: AgentRegistryPanel + AgentEditorPanel. | Fach | AgentRegistryPanel, AgentEditorPanel |
| **ToolsWorkspace** | Screen | Layout: ToolExplorer + ToolEditor. | Fach | ToolExplorerPanel, ToolEditorPanel |
| **DataStoresWorkspace** | Screen | Layout: DataStoreExplorer + DataStoreEditor. | Fach | DataStoreExplorerPanel, DataStoreEditorPanel |
| **TestInventoryWorkspace** | Screen | Layout: TestExplorer. | Fach | TestExplorerPanel |
| **CoverageMapWorkspace** | Screen | Layout: CoverageDashboard. | Fach | CoverageDashboard |
| **GapAnalysisWorkspace** | Screen | Layout: GapDashboard + GapEditor. | Fach | GapDashboard, GapEditorPanel |
| **IncidentsWorkspace** | Screen | Layout: IncidentExplorer + IncidentEditor. | Fach | IncidentExplorerPanel, IncidentEditorPanel |
| **ReplayLabWorkspace** | Screen | Layout: ReplayExplorer + ReplayEditor. | Fach | ReplayExplorerPanel, ReplayEditorPanel |
| **RuntimeWorkspace** | Screen | QTabWidget mit Monitor-Panels (EventBus, Logs, Metrics, LLMCalls, AgentActivity) + SystemGraph. | Fach | Monitor-Panels, SystemGraphPanel |
| **SettingsScreen** | Screen | Layout: SettingsEditorPanel. | Fach | SettingsEditorPanel |

### 3.4 Panel-Klassen (Domain)

| Klasse | Typ | Verantwortlichkeit | Generisch/Fach | Basis |
|--------|-----|-------------------|----------------|-------|
| **CommandCenterDashboard** | Panel | Status-Karten, Quick Actions. | Fach | BaseDashboardPanel |
| **SessionExplorerPanel** | Panel | Chat-Sessions, Projekte, Suche. | Fach | BaseExplorerPanel |
| **ChatEditorPanel** | Panel | Conversation + Composer. | Fach | BaseEditorPanel |
| **TaskExplorerPanel** | Panel | Task-Liste, Queue. | Fach | BaseExplorerPanel |
| **TaskEditorPanel** | Panel | Beauftragung, Parameter, Ergebnis. | Fach | BaseEditorPanel |
| **CollectionExplorerPanel** | Panel | Wissensräume, Collections. | Fach | BaseExplorerPanel |
| **DocumentEditorPanel** | Panel | Dokumente, Indizierung. | Fach | BaseEditorPanel |
| **PromptExplorerPanel** | Panel | Prompt-Liste. | Fach | BaseExplorerPanel |
| **PromptEditorPanel** | Panel | Prompt bearbeiten, Vorschau. | Fach | BaseEditorPanel |
| **ModelExplorerPanel** | Panel | Modell-Liste. | Fach | BaseExplorerPanel |
| **ModelEditorPanel** | Panel | Modell-Details, Parameter. | Fach | BaseEditorPanel |
| **ProviderExplorerPanel** | Panel | Provider-Liste. | Fach | BaseExplorerPanel |
| **ProviderEditorPanel** | Panel | Provider-Konfiguration. | Fach | BaseEditorPanel |
| **AgentRegistryPanel** | Panel | Agenten-Liste. | Fach | BaseExplorerPanel |
| **AgentEditorPanel** | Panel | Agent-Definition. | Fach | BaseEditorPanel |
| **ToolExplorerPanel** | Panel | Tool-Liste. | Fach | BaseExplorerPanel |
| **ToolEditorPanel** | Panel | Tool-Konfiguration. | Fach | BaseEditorPanel |
| **DataStoreExplorerPanel** | Panel | Store-Liste. | Fach | BaseExplorerPanel |
| **DataStoreEditorPanel** | Panel | Store-Konfiguration. | Fach | BaseEditorPanel |
| **TestExplorerPanel** | Panel | Tests nach Subsystem/Domain. | Fach | BaseExplorerPanel |
| **CoverageDashboard** | Panel | Achsen, Failure Classes. | Fach | BaseDashboardPanel |
| **GapDashboard** | Panel | Priorisierte Gaps. | Fach | BaseDashboardPanel |
| **GapEditorPanel** | Panel | Gap-Detail, Aktionen. | Fach | BaseEditorPanel |
| **IncidentExplorerPanel** | Panel | Incident-Liste. | Fach | BaseExplorerPanel |
| **IncidentEditorPanel** | Panel | Incident-Detail, Bindings. | Fach | BaseEditorPanel |
| **ReplayExplorerPanel** | Panel | Replay-Szenarien. | Fach | BaseExplorerPanel |
| **ReplayEditorPanel** | Panel | Replay ausführen. | Fach | BaseEditorPanel |
| **SettingsEditorPanel** | Panel | Einstellungen-Formular. | Fach | BaseEditorPanel |
| **SystemGraphPanel** | Panel | System-Zustandsgraph. | Fach | BaseMonitorPanel |

### 3.5 Inspector-Klassen

| Klasse | Typ | Verantwortlichkeit | Generisch/Fach | Basis |
|--------|-----|-------------------|----------------|-------|
| **SessionInspector** | Inspector | Session-Metadaten, RAG-Kontext. | Fach | BaseInspectorPanel |
| **AgentInspector** | Inspector | Agent-Info, Delegationen (in Agent Tasks). | Fach | BaseInspectorPanel |
| **AgentDetailInspector** | Inspector | Agent-Definition Details (in Control Center). | Fach | BaseInspectorPanel |
| **CollectionInspector** | Inspector | Collection-Details, Embedding-Info. | Fach | BaseInspectorPanel |
| **PromptInspector** | Inspector | Variablen, Metadaten. | Fach | BaseInspectorPanel |
| **ModelInspector** | Inspector | Modell-Metadaten. | Fach | BaseInspectorPanel |
| **ProviderInspector** | Inspector | Provider-Status. | Fach | BaseInspectorPanel |
| **ToolInspector** | Inspector | Tool-Metadaten. | Fach | BaseInspectorPanel |
| **DataStoreInspector** | Inspector | Store-Metadaten. | Fach | BaseInspectorPanel |
| **TestDetailInspector** | Inspector | Test-Details, Failure Class. | Fach | BaseInspectorPanel |
| **GapInspector** | Inspector | Gap-Details. | Fach | BaseInspectorPanel |
| **IncidentInspector** | Inspector | Incident-Bindings. | Fach | BaseInspectorPanel |
| **ReplayInspector** | Inspector | Replay-Metadaten. | Fach | BaseInspectorPanel |

### 3.6 Monitor-Klassen

| Klasse | Typ | Verantwortlichkeit | Generisch/Fach | Basis |
|--------|-----|-------------------|----------------|-------|
| **LogsMonitor** | Monitor | Anwendungslogs. | Fach | BaseMonitorPanel |
| **EventBusMonitor** | Monitor | EventBus-Stream. | Fach | BaseMonitorPanel |
| **MetricsMonitor** | Monitor | Laufzeit-Metriken. | Fach | BaseMonitorPanel |
| **LLMCallMonitor** | Monitor | LLM-Aufrufe, Token. | Fach | BaseMonitorPanel |
| **AgentActivityMonitor** | Monitor | Laufende Agenten, Schritte. | Fach | BaseMonitorPanel |

### 3.7 Shared-/Base-Klassen

| Klasse | Typ | Verantwortlichkeit | Generisch/Fach |
|--------|-----|-------------------|----------------|
| **BaseWorkspaceView** | Basis | area_id, refresh(), refresh_theme(). | Generisch |
| **BaseExplorerPanel** | Basis | selection_changed, refresh(). Liste/Baum. | Generisch |
| **BaseEditorPanel** | Basis | dirty_changed, save(), revert(). | Generisch |
| **BaseInspectorPanel** | Basis | set_object(obj), clear(). | Generisch |
| **BaseMonitorPanel** | Basis | start(), pause(), clear(), refresh(). | Generisch |
| **BaseDashboardPanel** | Basis | refresh(). Karten-Layout. | Generisch |
| **StatusCard** | Component | KPI-Karte. | Generisch |
| **EmptyStateWidget** | Component | „Keine X. [Aktion].“ | Generisch |
| **LoadingOverlay** | Component | Spinner/Skeleton. | Generisch |
| **SearchableList** | Component | Liste + Suche. | Generisch |
| **CollapsibleGroup** | Component | Aufklappbare Sektion. | Generisch |
| **LiveIndicator** | Component | „Live“-Badge. | Generisch |

---

## 4. Verantwortlichkeitsregeln

### 4.1 Was darf in die Shell?

| Erlaubt | Nicht erlaubt |
|---------|---------------|
| Docking-Konfiguration | Fachlogik (Chat, QA, Agents) |
| Layout-Zonen | Kenntnis von konkreten Screens (nur area_id) |
| Verbindung area_selected → show_area | If/Else für Bereichswechsel |
| Toolbar, StatusBar | Datenbankzugriff, API-Calls |
| Theme-Anwendung auf Shell-Zonen | |

### 4.2 Was darf in Screens (WorkspaceViews)?

| Erlaubt | Nicht erlaubt |
|---------|---------------|
| Layout aus Panels (Explorer + Editor, etc.) | Docking, QDockWidget |
| Koordination der Panels | Direkte Fachlogik (→ Services/Adapter) |
| refresh(), refresh_theme() | Kenntnis anderer Screens |
| Signal-Weitergabe (selection → InspectorHost) | Eigene Navigation |
| Aufruf von Services (z.B. RAGService) für Daten | |

### 4.3 Was darf in Panels?

| Erlaubt | Nicht erlaubt |
|---------|---------------|
| Darstellung und Interaktion für einen klar begrenzten Kontext | Layout anderer Panels |
| selection_changed, dirty_changed emittieren | Docking |
| Aufruf von Services/Adapter für Daten | Kenntnis des übergeordneten Screens (außer Callbacks) |
| Refresh, Theme | Bereichswechsel |
| Validierung eigener Eingaben | |

### 4.4 Was darf in Inspector-Panels?

| Erlaubt | Nicht erlaubt |
|---------|---------------|
| set_object(obj) – Anzeige von Metadaten | Bearbeitung (außer explizit vorgesehen) |
| Gruppierte Read-only-Anzeige | Fachlogik außer Darstellung |
| Aufklappbare Sektionen | Docking |
| | Kenntnis des aufrufenden Screens |

### 4.5 Was darf in Monitor-Panels?

| Erlaubt | Nicht erlaubt |
|---------|---------------|
| Live-Stream-Anzeige | Persistente Speicherung |
| Pause, Filter, Clear | Bearbeitung der Daten |
| Throttling bei hoher Rate | Docking |
| Export (optional) | |

### 4.6 Was darf NICHT in Navigation?

| Verboten |
|----------|
| Fachlogik (Chat, QA, Agents) |
| Kenntnis von Workspace-Inhalten |
| If/Else für area_id |
| Datenbankzugriff |
| API-Calls |

---

## 5. Interaktion: Shell, Navigation, Screens, Panels

### 5.1 Ablauf: Bereichswechsel

```
1. Nutzer klickt in NavigationSidebar auf "Chat"
2. NavigationSidebar emittiert area_selected("operations_chat")
3. MainWindow empfängt Signal, ruft TabbedWorkspace.show_area("operations_chat") auf
4. TabbedWorkspace prüft: Tab für "operations_chat" existiert?
   - Ja → setCurrentWidget(tab)
   - Nein → WorkspaceFactory.create_view("operations_chat") → addTab(view, title)
5. WorkspaceFactory: NavRegistry.get_factory("operations_chat")() → ChatWorkspace-Instanz
6. ChatWorkspace wird angezeigt
```

### 5.2 Ablauf: Inspector-Update

```
1. Nutzer wählt Session in SessionExplorerPanel
2. SessionExplorerPanel emittiert selection_changed(session_obj)
3. ChatWorkspace empfängt Signal (oder MainWindow als Vermittler)
4. MainWindow/InspectorHost.set_context("operations_chat", session_obj)
5. InspectorHost: InspectorRegistry.get_inspector("operations_chat", type(session_obj)) → SessionInspector
6. SessionInspector.set_object(session_obj)
7. SessionInspector zeigt Metadaten
```

### 5.3 Ablauf: Bottom-Monitor einblenden

```
1. Nutzer klickt Toggle "Bottom Panel" (in TopBar oder Menü)
2. MainWindow: MonitorHost-Dock setVisible(True)
3. MonitorHost zeigt Tabs (Logs, Events, Metrics, Agent Activity, LLM Trace)
4. Nutzer wählt Tab "Agent Activity"
5. AgentActivityMonitor wird angezeigt, startet Live-Update
```

### 5.4 Verantwortlichkeitskette

| Von | Nach | Inhalt |
|-----|------|--------|
| NavigationSidebar | MainWindow | area_selected(area_id) |
| MainWindow | TabbedWorkspace | show_area(area_id) |
| TabbedWorkspace | WorkspaceFactory | create_view(area_id) |
| WorkspaceFactory | NavRegistry | get_factory(area_id) |
| Domain-Panel | WorkspaceView | selection_changed(obj) |
| WorkspaceView | InspectorHost | set_context(area_id, obj) |
| InspectorHost | InspectorRegistry | get_inspector(area_id, obj_type) |

---

## 6. Screen-Registrierung und Panel-Zuordnung

### 6.1 Wie wird ein Screen registriert?

1. **NavArea erweitern:** `nav_areas.py` – neue Konstante (z.B. `OPERATIONS_CHAT = "operations_chat"`)
2. **NavRegistry.register aufrufen:** In Domain-`__init__.py` oder zentralem Bootstrap bei App-Start:
   ```
   NavRegistry.register(
       area_id=NavArea.OPERATIONS_CHAT,
       factory=lambda: ChatWorkspace(...),
       title="Chat",
       icon="chat.svg",
       parent_area=NavArea.OPERATIONS,
   )
   ```
3. **NavigationSidebar:** Liest Struktur aus NavRegistry (get_children) oder fester Konfiguration.

### 6.2 Wie wird ein Panel einem Screen zugeordnet?

- **Explorer/Editor/Dashboard:** Panel wird im WorkspaceView-Konstruktor instanziiert und ins Layout eingefügt. Keine Registry. WorkspaceView kennt seine Panels direkt.
- **Inspector:** InspectorRegistry.register(area_id, obj_type, factory). InspectorHost ruft bei set_context(area_id, obj) die Registry auf.
- **Monitor:** MonitorHost hat feste Tab-Liste. Keine dynamische Zuordnung. Neue Monitore werden in MonitorHost als Tab hinzugefügt.

### 6.3 Wie wird verhindert, dass Screen-Klassen zu groß werden?

| Regel | Umsetzung |
|-------|-----------|
| **Screen = Koordinator** | Screen erstellt nur Layout, delegiert Logik an Panels |
| **Panel = Einheit** | Jedes Panel hat eine klar begrenzte Verantwortung |
| **Max. 3–4 Panels pro Screen** | Explorer + Editor + optional Inspector-Signal. Kein Screen mit 10 Panels |
| **Services für Daten** | Screen/Panel ruft app.agents, app.rag etc. auf – keine Datenlogik im UI |
| **Basisklassen** | Gemeinsame Logik (Refresh, Theme) in Base-Klassen |

### 6.4 Wie wird verhindert, dass Fachlogik in Navigation oder Shell landet?

| Regel | Umsetzung |
|-------|-----------|
| **Navigation nur area_id** | NavigationSidebar emittiert nur String. Keine Objekte, keine Fachtypen |
| **Shell nur area_id** | MainWindow leitet area_id weiter. Kein if area_id == "chat": ... |
| **Registry für Routing** | WorkspaceFactory nutzt NavRegistry. Keine Switch-Cases in MainWindow |
| **Keine Domain-Imports in Shell** | gui/shell/, gui/navigation/, gui/workspace/ importieren keine gui/domains/ |
| **Lazy Loading** | Domain-Module werden erst bei create_view geladen |

---

## 7. Erweiterungsregeln

### 7.1 Neuer Hauptbereich

**Nur bei UX-Review.** Maximal 6 Hauptbereiche.

1. NavArea erweitern
2. gui/domains/<neue_domain>/ anlegen
3. WorkspaceView + Panels implementieren
4. NavRegistry.register bei App-Start
5. NavigationSidebar-Konfiguration erweitern

### 7.2 Neues Workspace-Modul (Unterbereich)

1. NavArea erweitern (z.B. `operations_neuer_bereich`)
2. gui/domains/operations/neuer_bereich/ anlegen
3. NeuerBereichWorkspace (von BaseWorkspaceView) + Panels
4. NavRegistry.register
5. NavigationSidebar: Neuer Eintrag unter Operations

### 7.3 Neues Panel

| Panel-Typ | Ort | Vorgehen |
|-----------|-----|----------|
| Explorer/Editor/Dashboard | gui/domains/<domain>/panels/ | Von Base erben, in WorkspaceView einbinden |
| Inspector | gui/inspector/inspectors/ | Von BaseInspectorPanel erben, InspectorRegistry.register |
| Monitor | gui/monitors/panels/ | Von BaseMonitorPanel erben, in MonitorHost als Tab hinzufügen |

### 7.4 Neuer Inspector

1. gui/inspector/inspectors/<name>_inspector.py anlegen
2. Von BaseInspectorPanel erben
3. InspectorRegistry.register(area_id, obj_type, factory)
4. Keine Änderung an WorkspaceView – InspectorHost lädt automatisch

### 7.5 Neuer Bottom-Monitor

1. gui/monitors/panels/<name>_monitor.py anlegen
2. Von BaseMonitorPanel erben
3. In MonitorHost.addTab() bei Setup hinzufügen
4. Optional: RuntimeWorkspace erweitern, falls Monitor auch dort erscheinen soll

---

## 8. Basisklassen-Empfehlung

### 8.1 Verbindlich einzuführende Basisklassen

| Klasse | Ort | Zweck |
|--------|-----|-------|
| **BaseWorkspaceView** | gui/workspace/base_workspace_view.py | area_id, refresh(), refresh_theme(). Alle Screens erben. |
| **BaseExplorerPanel** | gui/panels/base/base_explorer.py | selection_changed, refresh(). Liste/Baum, Suche. |
| **BaseEditorPanel** | gui/panels/base/base_editor.py | dirty_changed, save(), revert(). Formular-Logik. |
| **BaseInspectorPanel** | gui/panels/base/base_inspector.py | set_object(obj), clear(). Read-only-Muster. |
| **BaseMonitorPanel** | gui/panels/base/base_monitor.py | start(), pause(), clear(), refresh(). Live-Stream-Muster. |
| **BaseDashboardPanel** | gui/panels/base/base_dashboard.py | refresh(). Karten-Layout. |

### 8.2 Optionale Basisklassen (später)

| Klasse | Zweck |
|--------|-------|
| BaseExplorerWithToolbar | Explorer + Standard-Toolbar (Neu, Filter, Suche) |
| BaseEditorWithValidation | Editor + Validierungs-Hook |

---

## 9. Anti-Pattern-Liste

| Anti-Pattern | Stattdessen |
|--------------|-------------|
| Riesen-MainWindow mit Fachlogik | MainWindow schlank; Fachlogik in Screens/Panels/Services |
| If/Else für Bereichswechsel | NavRegistry + WorkspaceFactory |
| Screen mit Layout + Navigation + Daten + Runtime | Screen = Koordinator; Panels = UI; Services = Daten |
| Panel ohne klaren Zuständigkeitsrahmen | Panel = eine Entität, eine Verantwortung |
| Navigation importiert Domain-Module | Navigation nur area_id; Registry für Routing |
| Unklare Verantwortung Workspace vs. Panel | Workspace = Layout; Panel = Inhalt |
| Inspector-Logik in mehreren Screens dupliziert | Inspector zentral in gui/inspector/inspectors/ |
| Bottom-Panel-Wildwuchs | Feste Tabs in MonitorHost; neue Monitore nur nach Review |
| Feature-Modul mit eigener Shell-Logik | Shell ist zentral; Features registrieren sich |
| Inkonsistente Klassenbenennung | *Workspace, *Panel, *Inspector, *Monitor |

---

## 10. Hauptempfehlung

### 10.1 Architekturentscheidungen (verbindlich)

1. **MainWindow bleibt schlank.** Nur Docking, Routing, Signal-Vermittlung. Keine Fachlogik.
2. **Jeder Blatt-Bereich = ein Screen = ein Tab.** Keine Container-Screens (außer RuntimeWorkspace mit interner Tab-Gruppierung).
3. **Registry-basiertes Routing.** NavRegistry + WorkspaceFactory. Keine If/Else.
4. **Panels in Domains.** Explorer, Editor, Dashboard in gui/domains/<domain>/panels/.
5. **Inspector zentral.** Alle Inspector-Panels in gui/inspector/inspectors/.
6. **Monitor zentral.** Alle Monitor-Panels in gui/monitors/panels/. RuntimeWorkspace reuses.
7. **Basisklassen Pflicht.** Jedes Panel erbt von Base*.
8. **Screen = Koordinator.** Screen erstellt Layout, delegiert an Panels. Keine Monolithen.

### 10.2 Implementierungsreihenfolge

1. Shell (MainWindow, DockingConfig)
2. Navigation (Sidebar, NavArea, NavRegistry)
3. Workspace (TabbedWorkspace, WorkspaceFactory, BaseWorkspaceView)
4. Basis-Panels + Components
5. Inspector (InspectorHost, InspectorRegistry, erste Inspector-Panels)
6. Monitor (MonitorHost, erste Monitor-Panels)
7. Domains schrittweise (Dashboard → Chat → Agent Tasks → …)

---

*Diese Architektur ist verbindliche Grundlage für die GUI-Implementierung.*

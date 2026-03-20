# PySide6 UI-Architektur – Linux Desktop Chat

**Version:** 1.0  
**Datum:** 2026-03-15  
**Referenz:** docs/UX_CONCEPT.md  
**Repository-Struktur:** docs/GUI_REPOSITORY_ARCHITECTURE.md  
**Screen-/Klassenarchitektur:** docs/SCREEN_CLASS_ARCHITECTURE.md

---

## 1. Einleitung

Dieses Dokument leitet aus der UX-Blaupause eine konkrete **PySide6 UI-Architektur** ab. Es definiert Klassenstruktur, Fensterlayout, Docking, Navigation, Workspaces und Panel-Komponenten. Kein vollständiger Implementierungscode – ausschließlich Architektur und Strukturempfehlungen für eine robuste, modulare Desktop-Anwendung.

**Ziele:**
- Stabile Desktop-Layoutstruktur
- Docking-System mit QDockWidget
- Modulare, wiederverwendbare Panels
- Klare Navigation
- Erweiterbarkeit bei wachsender Komplexität

---

## 2. Empfohlene Klassenstruktur der GUI

### 2.1 Hierarchie-Übersicht

```
QMainWindow (MainWindow)
├── TopBarWidget (QWidget)                    # Optional: eigener Top-Bar-Container
├── NavigationSidebarDock (QDockWidget)
│   └── NavigationSidebarWidget (QWidget)
├── CentralStack (QStackedWidget)              # ODER TabbedWorkspace (QTabWidget)
│   └── [Workspace-Views je nach Bereich]
├── InspectorDock (QDockWidget)
│   └── InspectorPanel (QWidget)               # Host für kontextabhängigen Inspector
├── BottomPanelDock (QDockWidget)
│   └── BottomPanelWidget (QTabWidget)        # Logs, Events, Metrics, Agent Activity, LLM Trace
└── statusBar()
```

### 2.2 Kernklassen

| Klasse | Basis | Rolle |
|--------|-------|-------|
| **MainWindow** | QMainWindow | Root-Fenster, Layout-Setup, Docking-Konfiguration, Bereichswechsel |
| **NavigationSidebarWidget** | QWidget | Hierarchische Navigation (6 Hauptbereiche, Unterbereiche) |
| **TabbedWorkspace** | QTabWidget | Main Workspace mit Tab-basierten Screens |
| **InspectorPanel** | QWidget | Host-Container; zeigt kontextabhängig Inspector-Content |
| **BottomPanelWidget** | QTabWidget | Host für Monitor-Panels (Logs, Events, Metrics, Agent Activity, LLM Trace) |

### 2.3 Basis-Panel-Klassen (abstrakt/generisch)

| Klasse | Basis | Rolle |
|--------|-------|-------|
| **BaseExplorerPanel** | QWidget | Basis für Explorer-Panels (Liste, Baum, Auswahl) |
| **BaseEditorPanel** | QWidget | Basis für Editor-Panels (Bearbeitung, Dirty-State) |
| **BaseInspectorPanel** | QWidget | Basis für Inspector-Panels (Read-only Metadaten) |
| **BaseMonitorPanel** | QWidget | Basis für Monitor-Panels (Live-Stream, Pause, Filter) |
| **BaseDashboardPanel** | QWidget | Basis für Dashboard-Panels (Karten, KPIs) |

### 2.4 Bereichs-spezifische Workspace-Views

| Klasse | Basis | Bereich | Enthält |
|--------|-------|---------|---------|
| **CommandCenterWorkspace** | BaseDashboardPanel | Kommandozentrale | Status-Karten, Quick Actions |
| **OperationsWorkspace** | QStackedWidget | Operations | Chat, Agent Tasks, Knowledge, Prompt Studio |
| **ControlCenterWorkspace** | QStackedWidget | Control Center | Models, Providers, Agents, Tools, Data Stores |
| **QAGovernanceWorkspace** | QStackedWidget | QA & Governance | Test Inventory, Coverage, Gap, Incidents, Replay |
| **RuntimeDebugWorkspace** | QTabWidget | Runtime / Debug | EventBus, Logs, Metrics, LLM Calls, Agent Activity, System Graph |
| **SettingsWorkspace** | BaseEditorPanel | Settings | Einstellungen-Formular |

---

## 3. Fensterstruktur (MainWindow, DockWidgets)

### 3.1 Zonen-Mapping zu Qt-Widgets

| UX-Zone | Qt-Widget | Typ | Docking |
|---------|-----------|-----|---------|
| Top Bar | QToolBar oder TopBarWidget | QToolBar / QWidget | Oben, fest |
| Navigation Sidebar | NavigationSidebarDock | QDockWidget | Links, fest |
| Main Workspace | CentralStack / TabbedWorkspace | QStackedWidget / QTabWidget | CentralWidget |
| Inspector | InspectorDock | QDockWidget | Rechts, ein-/ausblendbar |
| Bottom Panel | BottomPanelDock | QDockWidget | Unten, ein-/ausblendbar |
| Status | statusBar() | QStatusBar | Unten, fest |

### 3.2 Docking-Konfiguration

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  Top Bar (QToolBar)                                                          │
├──────────┬──────────────────────────────────────────────┬────────────────────┤
│          │                                              │                    │
│  Nav     │         Main Workspace                       │   Inspector         │
│  Sidebar │         (CentralWidget)                      │   (QDockWidget)    │
│  (Dock)  │         TabbedWorkspace                      │   optional          │
│  links   │         oder QStackedWidget                  │   rechts           │
│          │                                              │                    │
├──────────┴──────────────────────────────────────────────┴────────────────────┤
│  Bottom Panel (QDockWidget) – optional, einblendbar                          │
│  QTabWidget: Logs | Events | Metrics | Agent Activity | LLM Trace             │
├─────────────────────────────────────────────────────────────────────────────┤
│  StatusBar                                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.3 Docking-Regeln

| Dock | allowedAreas | features | Standard |
|------|--------------|----------|----------|
| NavigationSidebarDock | Left, Right | Movable, Floatable | Left, 220px Breite |
| InspectorDock | Right, Left | Movable, Floatable, Closable | Right, 280px Breite, initial versteckt |
| BottomPanelDock | Bottom, Top | Movable, Floatable, Closable | Bottom, 200px Höhe, initial versteckt |

**Wichtig:** Navigation Sidebar soll nicht schließbar sein (oder nur mit Warnung). Inspector und Bottom Panel sind per Toggle ein-/ausblendbar.

### 3.4 TabCornerWidget für Workspace-Tabs

- TabBar des TabbedWorkspace: Schließen-Button pro Tab (optional)
- Maximal 7 offene Tabs; bei Überschreitung ältesten schließen oder Hinweis

---

## 4. Layoutstruktur des Hauptfensters

### 4.1 MainWindow-Layout (Pseudocode-Struktur)

```
MainWindow
├── setCentralWidget(tabbed_workspace)     # ODER stacked_workspace
├── addDockWidget(Left, navigation_dock)
├── addDockWidget(Right, inspector_dock)   # tabified oder split
├── addDockWidget(Bottom, bottom_panel_dock)
├── addToolBar(top_bar)
└── statusBar()
```

### 4.2 Splitter-Strategie (optional)

Für flexible Größenanpassung zwischen Navigation und Main:

```
QSplitter (horizontal)
├── NavigationSidebarWidget (min: 180, max: 320)
└── QSplitter (vertical)
    ├── TabbedWorkspace (Main)
    └── BottomPanelDock (min: 120, initial: 0 = versteckt)
```

**Alternative:** Standard QMainWindow-Docking ohne Splitter – Qt verwaltet die Größen. Empfohlen: reines Docking, einfacher zu warten.

### 4.3 Größen-Empfehlungen

| Zone | Min | Default | Max |
|------|-----|---------|-----|
| Navigation Sidebar | 180px | 220px | 320px |
| Inspector | 200px | 280px | 400px |
| Bottom Panel | 120px | 200px | 400px |
| Main Workspace | 400px | rest | — |

---

## 5. Struktur der Navigation

### 5.1 NavigationSidebarWidget – Aufbau

```
NavigationSidebarWidget (QWidget)
└── QVBoxLayout
    ├── Logo/App-Name (optional)
    ├── QListWidget oder QTreeWidget (Navigation Items)
    │   ├── Kommandozentrale
    │   ├── Operations (expandierbar)
    │   │   ├── Chat
    │   │   ├── Agent Tasks
    │   │   ├── Knowledge / RAG
    │   │   └── Prompt Studio
    │   ├── Control Center (expandierbar)
    │   │   ├── Models
    │   │   ├── Providers
    │   │   ├── Agents
    │   │   ├── Tools
    │   │   └── Data Stores
    │   ├── QA & Governance (expandierbar)
    │   │   ├── Test Inventory
    │   │   ├── Coverage Map
    │   │   ├── Gap Analysis
    │   │   ├── Incidents
    │   │   └── Replay Lab
    │   ├── Runtime / Debug (expandierbar)
    │   │   ├── EventBus Monitor
    │   │   ├── Logs
    │   │   ├── Metrics
    │   │   ├── LLM Calls
    │   │   ├── Agent Activity
    │   │   └── System Graph
    │   └── Settings
    └── (optional) Collapse-Button
```

### 5.2 Navigations-IDs / Enum

Empfohlen: Enum oder String-Konstanten für Bereichs-IDs.

```python
# Konzept (nicht Code)
class NavArea:
    COMMAND_CENTER = "command_center"
    OPERATIONS_CHAT = "operations_chat"
    OPERATIONS_AGENT_TASKS = "operations_agent_tasks"
    OPERATIONS_KNOWLEDGE = "operations_knowledge"
    OPERATIONS_PROMPT_STUDIO = "operations_prompt_studio"
    CONTROL_MODELS = "control_models"
    CONTROL_PROVIDERS = "control_providers"
    CONTROL_AGENTS = "control_agents"
    CONTROL_TOOLS = "control_tools"
    CONTROL_DATA_STORES = "control_data_stores"
    QA_TEST_INVENTORY = "qa_test_inventory"
    QA_COVERAGE_MAP = "qa_coverage_map"
    QA_GAP_ANALYSIS = "qa_gap_analysis"
    QA_INCIDENTS = "qa_incidents"
    QA_REPLAY_LAB = "qa_replay_lab"
    RUNTIME_EVENTBUS = "runtime_eventbus"
    RUNTIME_LOGS = "runtime_logs"
    # ... etc
    SETTINGS = "settings"
```

### 5.3 Signal-Flow

```
NavigationSidebarWidget.area_selected(area_id: str)
    → MainWindow.on_navigation_changed(area_id)
    → TabbedWorkspace.show_area(area_id)
    → ggf. InspectorPanel.set_context(area_id, context_object)
```

---

## 6. Struktur der Workspaces

### 6.1 TabbedWorkspace vs. QStackedWidget

| Ansatz | Vorteil | Nachteil |
|--------|---------|----------|
| **QTabWidget (TabbedWorkspace)** | Mehrere Bereiche parallel offen, Tab-Wechsel | Mehr Tabs bei vielen offenen Kontexten |
| **QStackedWidget** | Einfacher, nur ein Bereich sichtbar | Kein paralleles Arbeiten in mehreren Bereichen |

**Empfehlung:** TabbedWorkspace (QTabWidget) für Main Workspace. Nutzer kann Chat + Agent Tasks als Tabs offen haben. Bereichswechsel über Sidebar fügt neuen Tab hinzu oder wechselt zu bestehendem.

### 6.2 Workspace-View-Factory

Jeder Bereich hat eine Factory-Funktion oder -Klasse, die den entsprechenden Workspace-View erzeugt:

| Bereich | Workspace-View | Lazy Load |
|---------|----------------|-----------|
| Kommandozentrale | CommandCenterWorkspace | Nein (Start-Einstieg) |
| Operations / Chat | ChatWorkspaceView | Ja |
| Operations / Agent Tasks | AgentTasksWorkspaceView | Ja |
| Operations / Knowledge | KnowledgeWorkspaceView | Ja |
| Operations / Prompt Studio | PromptStudioWorkspaceView | Ja |
| Control Center / Models | ModelsWorkspaceView | Ja |
| Control Center / Providers | ProvidersWorkspaceView | Ja |
| Control Center / Agents | AgentsWorkspaceView | Ja |
| Control Center / Tools | ToolsWorkspaceView | Ja |
| Control Center / Data Stores | DataStoresWorkspaceView | Ja |
| QA / Test Inventory | TestInventoryWorkspaceView | Ja |
| QA / Coverage Map | CoverageMapWorkspaceView | Ja |
| QA / Gap Analysis | GapAnalysisWorkspaceView | Ja |
| QA / Incidents | IncidentsWorkspaceView | Ja |
| QA / Replay Lab | ReplayLabWorkspaceView | Ja |
| Runtime / EventBus | EventBusMonitorView | Ja |
| Runtime / Logs | LogsMonitorView | Ja |
| Runtime / Metrics | MetricsMonitorView | Ja |
| Runtime / LLM Calls | LLMTraceMonitorView | Ja |
| Runtime / Agent Activity | AgentActivityMonitorView | Ja |
| Runtime / System Graph | SystemGraphView | Ja |
| Settings | SettingsWorkspaceView | Ja |

### 6.3 Workspace-View-Struktur (Beispiel: Chat)

```
ChatWorkspaceView (QWidget)
└── QHBoxLayout
    ├── SessionExplorerPanel (BaseExplorerPanel)  # Links, oder in Sidebar
    ├── QSplitter (optional)
    │   ├── ChatEditorPanel (ConversationView + Composer)
    │   └── (optional) SessionInspectorPanel
    └── ...
```

**Hinweis:** SessionExplorer kann im Navigation-Bereich als zweite Sidebar erscheinen (Operations-spezifisch) oder als Teil des ChatWorkspaceView.

---

## 7. Panel-Komponenten

### 7.1 Generische Basis-Panels

#### BaseExplorerPanel (QWidget)

- **Schnittstelle:** `selection_changed(item)`, `refresh()`
- **Enthält:** QListWidget oder QTreeWidget, optional QLineEdit (Suche), Toolbar (Neu, Filter)
- **Subklassen:** SessionExplorer, TaskExplorer, CollectionExplorer, PromptExplorer, ModelExplorer, AgentRegistryExplorer, TestInventoryExplorer, IncidentExplorer, ReplayExplorer, …

#### BaseEditorPanel (QWidget)

- **Schnittstelle:** `dirty_changed(bool)`, `save()`, `revert()`
- **Enthält:** Formular oder Custom-Content, Speichern/Abbrechen-Buttons
- **Subklassen:** ChatEditor, TaskEditor, PromptEditor, AgentEditor, ModelEditor, GapEditor, IncidentEditor, ReplayEditor, SettingsEditor, …

#### BaseInspectorPanel (QWidget)

- **Schnittstelle:** `set_object(obj)` oder `set_context(area_id, context_obj)`
- **Enthält:** Gruppierte Labels/Read-only-Felder, optional aufklappbare Sektionen
- **Subklassen:** SessionInspector, AgentInspector, CollectionInspector, PromptInspector, TestInspector, …

#### BaseMonitorPanel (QWidget)

- **Schnittstelle:** `start()`, `pause()`, `clear()`, `refresh()`
- **Enthält:** QPlainTextEdit (Logs) oder Custom-View (Timeline, Graph), Filter, Live-Indikator
- **Subklassen:** EventBusMonitor, LogsMonitor, MetricsMonitor, LLMTraceMonitor, AgentActivityMonitor, …

#### BaseDashboardPanel (QWidget)

- **Schnittstelle:** `refresh()`
- **Enthält:** QGridLayout mit Karten (QFrame), Quick-Action-Buttons
- **Subklassen:** CommandCenterDashboard, CoverageDashboard, GapDashboard, …

### 7.2 Panel-Registry (Konzept)

Zentrale Registry für Panel-Typen, um dynamisches Laden zu ermöglichen:

```
PanelRegistry
├── register(panel_id, factory: Callable[[], QWidget])
├── create(panel_id) -> QWidget
└── list_panels(area_id) -> [panel_id, ...]
```

---

## 8. Wiederverwendbare UI-Module

### 8.1 Generische Komponenten (sollten generisch sein)

| Komponente | Zweck | Basis |
|------------|-------|-------|
| **StatusCard** | KPI-Karte für Dashboard | QFrame |
| **EmptyStateWidget** | „Keine X. [Aktion] um zu starten.“ | QWidget |
| **LoadingOverlay** | Spinner/Skeleton während Laden | QWidget |
| **SearchableList** | Liste mit eingebauter Suche | QWidget (QLineEdit + QListWidget) |
| **DirtyIndicator** | Punkt/Stern bei ungespeicherten Änderungen | QLabel oder Badge |
| **LiveIndicator** | „Live“-Badge für Monitor-Panels | QLabel |
| **CollapsibleGroup** | Aufklappbare Sektion | QWidget |
| **TabBarCloseButton** | Schließen-Button für Tabs | QPushButton |

### 8.2 Theming

- Zentrale `get_stylesheet(theme)` und `get_theme_colors(theme)`
- Alle Panels erhalten `theme: str` im Konstruktor und `refresh_theme(theme)` zur Laufzeit
- ObjectNames für gezieltes Styling (z.B. `#statusCard`, `#explorerPanel`)

### 8.3 Icons

- Zentrale Icon-Pfade (z.B. `settings.icons_path`)
- Einheitliche Icon-Größen (16, 24, 32)
- SVG bevorzugt (skalierbar)

---

## 9. Modulare GUI-Dateistruktur

### 9.1 Empfohlene Verzeichnisstruktur

```
app/
├── main.py                          # Entry, MainWindow-Instanziierung
├── ui/
│   ├── __init__.py
│   ├── main_window.py               # MainWindow-Klasse
│   ├── navigation/
│   │   ├── __init__.py
│   │   ├── navigation_sidebar.py     # NavigationSidebarWidget
│   │   └── nav_areas.py              # NavArea Enum, Konfiguration
│   ├── workspace/
│   │   ├── __init__.py
│   │   ├── tabbed_workspace.py       # TabbedWorkspace
│   │   ├── workspace_factory.py      # Factory für Workspace-Views
│   │   └── views/
│   │       ├── __init__.py
│   │       ├── command_center_view.py
│   │       ├── chat_workspace_view.py
│   │       ├── agent_tasks_view.py
│   │       ├── knowledge_view.py
│   │       ├── prompt_studio_view.py
│   │       ├── control_center_views.py  # oder je Unterbereich eine Datei
│   │       ├── qa_views.py
│   │       ├── runtime_views.py
│   │       └── settings_view.py
│   ├── panels/
│   │   ├── __init__.py
│   │   ├── base/
│   │   │   ├── __init__.py
│   │   │   ├── base_explorer.py
│   │   │   ├── base_editor.py
│   │   │   ├── base_inspector.py
│   │   │   ├── base_monitor.py
│   │   │   └── base_dashboard.py
│   │   ├── explorer/
│   │   │   ├── session_explorer.py
│   │   │   ├── task_explorer.py
│   │   │   ├── collection_explorer.py
│   │   │   └── ...
│   │   ├── editor/
│   │   │   ├── chat_editor.py
│   │   │   ├── task_editor.py
│   │   │   └── ...
│   │   ├── inspector/
│   │   │   ├── session_inspector.py
│   │   │   └── ...
│   │   ├── monitor/
│   │   │   ├── eventbus_monitor.py
│   │   │   ├── logs_monitor.py
│   │   │   ├── agent_activity_monitor.py
│   │   │   └── ...
│   │   └── dashboard/
│   │       ├── command_center_dashboard.py
│   │       └── ...
│   ├── inspector/
│   │   ├── __init__.py
│   │   └── inspector_panel.py         # Host, kontextabhängiger Content
│   ├── bottom_panel/
│   │   ├── __init__.py
│   │   └── bottom_panel_widget.py     # TabWidget mit Monitor-Panels
│   ├── components/                   # Wiederverwendbare Kleinteile
│   │   ├── __init__.py
│   │   ├── status_card.py
│   │   ├── empty_state.py
│   │   ├── loading_overlay.py
│   │   ├── searchable_list.py
│   │   └── collapsible_group.py
│   ├── chat/                         # Bestehend, ggf. refaktoriert
│   ├── agents/
│   ├── debug/
│   ├── sidepanel/                    # Ggf. in panels/ integrieren
│   └── settings_dialog.py
├── ...
```

### 9.2 Migrations-Hinweis

Die bestehende Struktur (`ui/command_center/`, `ui/chat/`, `ui/sidepanel/`, `ui/debug/`) kann schrittweise in die neue Struktur überführt werden. Kein Big-Bang-Refactoring.

---

## 10. Erweiterbarkeit

### 10.1 Dynamisch ladbare Panels

**Kandidaten für Lazy Loading:**
- Alle Workspace-Views außer Kommandozentrale
- Inspector-Content (wechselt je nach Kontext)
- Bottom-Panel-Tabs (Logs, Events, etc. erst bei erstem Öffnen laden)

**Mechanismus:**
- Factory-Funktion pro Panel/View
- Erst bei erstem Aufruf von `show_area(area_id)` wird die View erstellt
- Optional: `importlib` oder Plugin-System für externe Module (später)

### 10.2 Integration neuer Subsysteme

| Szenario | Vorgehen |
|----------|----------|
| **Neuer Agent-Typ** | Kein neuer Bereich. Agent Registry (Control Center) und Agent Tasks (Operations) erweitern. |
| **Neuer Provider** | Control Center / Providers: neuer Eintrag in ProviderExplorer, ProviderEditor erweitern. |
| **Neues QA-Subsystem** | QA & Governance: neuer Unterbereich oder neues Tab in bestehendem Workspace. |
| **Neues Monitor-Panel** | Runtime / Debug: neuer Tab in Bottom Panel oder Runtime Workspace. Factory erweitern. |
| **Neuer Hauptbereich** | UX-Review erforderlich. Maximal 6 Hauptbereiche. Nur bei starker fachlicher Begründung. |

### 10.3 Plugin-Punkt (optional, später)

Für maximale Erweiterbarkeit:
- `WorkspaceFactory.register(area_id, factory)` – neue Bereiche registrieren
- `PanelRegistry.register(panel_id, factory)` – neue Panels registrieren
- Konfigurationsdatei (z.B. JSON) für Navigation-Einträge

---

## 11. Generische vs. spezifische Komponenten

### 11.1 Generisch (wiederverwendbar)

| Komponente | Verwendung |
|------------|------------|
| BaseExplorerPanel, BaseEditorPanel, BaseInspectorPanel, BaseMonitorPanel, BaseDashboardPanel | Alle Bereichs-Panels |
| StatusCard, EmptyStateWidget, LoadingOverlay, SearchableList, CollapsibleGroup | Überall |
| NavigationSidebarWidget | Einmal, global |
| InspectorPanel (Host) | Einmal, Content wechselt |
| BottomPanelWidget (Host) | Einmal, Tabs wechseln |
| TabbedWorkspace | Einmal |

### 11.2 Spezifisch (bereichsgebunden)

| Komponente | Bereich |
|------------|---------|
| ChatEditor (ConversationView, Composer) | Operations / Chat |
| AgentTasksWorkspaceView | Operations / Agent Tasks |
| CommandCenterDashboard | Kommandozentrale |
| AgentEditor, AgentRegistryExplorer | Control Center / Agents |
| TestInventoryExplorer, CoverageDashboard | QA & Governance |
| EventBusMonitor, AgentActivityMonitor | Runtime / Debug |

---

## 12. Zusammenfassung

| Aspekt | Empfehlung |
|--------|------------|
| **Root** | QMainWindow |
| **Docking** | QDockWidget für Navigation (links), Inspector (rechts), Bottom (unten) |
| **Main Workspace** | QTabWidget (TabbedWorkspace) für Tab-basierte Screens |
| **Navigation** | NavigationSidebarWidget mit hierarchischer Liste (QListWidget/QTreeWidget) |
| **Panel-Basis** | 5 Basis-Klassen: Explorer, Editor, Inspector, Monitor, Dashboard |
| **Workspace-Views** | Pro Bereich eine View-Klasse; Factory für Lazy Loading |
| **Inspector** | Ein Host-Container; Content kontextabhängig |
| **Bottom Panel** | QTabWidget mit Monitor-Panels (Logs, Events, Metrics, Agent Activity, LLM Trace) |
| **Dateistruktur** | ui/navigation/, ui/workspace/, ui/panels/base|explorer|editor|inspector|monitor|dashboard/, ui/components/ |
| **Erweiterbarkeit** | Factory-Pattern, Panel-Registry, Lazy Loading |

---

*Diese Architektur ist die technische Grundlage für die PySide6-Implementierung. Sie steht in Einklang mit docs/UX_CONCEPT.md.*

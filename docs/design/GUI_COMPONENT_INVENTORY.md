# GUI-Komponenten-Inventar (Linux Desktop Chat / Obsidian Core)

**Zweck:** Vollständige Übersicht der tatsächlich vorhandenen GUI-Bausteine für Color-Usage-Planung.  
**Quelle:** Code unter `app/gui/` (Stand: Analyse 2026-03-22), ergänzt um Legacy-Einstieg `app/main.py`.  
**Verwandt:** [THEME_COMPONENT_MAPPING.md](./THEME_COMPONENT_MAPPING.md), [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md).

---

## 1. Shell & Fenster-Root

| Komponente | Klasse / Datei | Kurzbeschreibung |
|------------|----------------|------------------|
| **Shell Main Window** | `ShellMainWindow` — `app/gui/shell/main_window.py` | Root: TopBar, Zentralbereich (Breadcrumb + WorkspaceHost), Docks |
| **Top Bar** | `TopBar` (QToolBar) — `app/gui/shell/top_bar.py` | App-Titel, Project Switcher, Aktionen (Status, Workspace Map, Command Palette, Hilfe) |
| **Project Switcher** | `ProjectSwitcherButton` — `app/gui/project_switcher/` | Kontextwechsel Projekte |
| **Breadcrumb Bar** | `BreadcrumbBar` — `app/gui/breadcrumbs/` | Pfad / Kontext oberhalb des Workspaces |
| **Breadcrumb Manager** | `BreadcrumbManager` — `app/gui/breadcrumbs/manager.py` | Logik, kein sichtbares Widget |
| **Workspace Host** | `WorkspaceHost` — `app/gui/workspace/` | Zeigt registrierte Screens je `NavArea` |
| **Inspector Host** | `InspectorHost` — `app/gui/workbench/inspector/` | Rechter Dock-Inhalt, kontextabhängig |
| **Inspector Panel** | `InspectorPanel`, `InspectorRouter` — `app/gui/workbench/inspector/` | Router + spezifische Inspector-Views (Agent, Workflow, Chat, File, Generic, …) |
| **Bottom Panel Host** | `BottomPanelHost` — `app/gui/monitors/bottom_panel_host.py` | Unterer Dock: Tab-Widget für Monitore |
| **Navigation Sidebar** | `NavigationSidebar` — `app/gui/navigation/sidebar.py` | Hauptnavigation (Bereiche) |
| **Dock Widgets** | Qt `QDockWidget` — `app/gui/shell/docking_config.py` | Nav-Sidebar, Inspector, Bottom Panel |
| **Status Bar** | `QStatusBar` (falls gesetzt) | Globale Statuszeile (Legacy-Hauptfenster nutzt sie explizit) |

---

## 2. Registrierte Haupt-Screens (`register_all_screens`)

| Screen | Klasse | Bereich (`NavArea`) |
|--------|--------|---------------------|
| **Dashboard / Kommandozentrale** | `DashboardScreen` | `command_center` |
| **Operations** | `OperationsScreen` | `operations` |
| **Control Center** | `ControlCenterScreen` | `control_center` |
| **QA & Governance** | `QAGovernanceScreen` | `qa_governance` |
| **Runtime / Debug** | `RuntimeDebugScreen` | `runtime_debug` |
| **Settings** | `SettingsScreen` | `settings` |

*Hinweis:* In älterer Doku taucht „Project Hub“ als Nav-Punkt auf; im aktuellen `bootstrap.py` ist kein eigener Screen dafür registriert — Projektbezug läuft u. a. über Operations/Chat und den Project Switcher.

---

## 3. Domain: Operations (Auswahl)

| Komponente | Typ / Datei (Beispiel) |
|------------|-------------------------|
| **Operations Nav** | `OperationsNav` — `operations_nav.py` |
| **Chat Workspace** | `ChatWorkspace` — `chat/chat_workspace.py` |
| **Chat Navigation Panel** | `ChatNavigationPanel` — `chat/panels/chat_navigation_panel.py` |
| **Chat Conversation Panel** | `ChatConversationPanel` |
| **Chat Input Panel** | `ChatInputPanel` |
| **Chat Message Bubbles** | `ChatMessageBubbleWidget` — `chat_message_bubble.py` |
| **Chat Details Panel** | `ChatDetailsPanel` |
| **Chat Context Bar** | Kontextleiste (QSS `#chatContextBar`) |
| **Prompt Studio** | `PromptManagerPanel`, `PromptEditorPanel`, `NewPromptDialog`, … |
| **Knowledge** | `index_overview_panel`, Collection-Dialogs (`CreateCollectionDialog`, …) |
| **Workflows** | `WorkflowWorkspace`, `WorkflowCanvasWidget`, `WorkflowGraphicsView`/`Scene`, `WorkflowListPanel`, `WorkflowEditorPanel`, `WorkflowRunPanel`, `WorkflowInspectorPanel`, Node/Edge Graphics-Items |
| **Deployment** | `ReleasesPanel`, `RolloutsPanel`, `TargetsPanel`, `ReleaseEditDialog`, `RolloutRecordDialog` |
| **Projects** | `ProjectsWorkspace`, `ProjectListPanel`, `ProjectOverviewPanel`, `ProjectStatsPanel`, `NewProjectDialog`, `ProjectEditDialog` |
| **Audit / Incidents** | `IncidentsPanel`, `AuditActivityPanel` |
| **Agent Tasks** | `result_panel` u. a. |

---

## 4. Domain: Control Center

| Komponente | Beispiele |
|------------|-----------|
| **Workspaces** | `ProvidersWorkspace`, `ToolsWorkspace`, … |
| **Panels** | `ModelListPanel`, `ModelSummaryPanel`, `ModelStatusPanel`, `ModelActionPanel`, `ProviderListPanel`, `ProviderStatusPanel`, `DataStoreOverviewPanel`, `ToolRegistryPanel`, `LocalModelAssetsPanel`, `ModelQuotaPolicyPanel`, … |
| **Agent Performance** | `AgentPerformanceTab` (KPIs / Darstellung) |

---

## 5. Domain: QA & Governance

| Komponente | Datei / Rolle |
|------------|----------------|
| **QA Governance Screen** | `qa_governance_screen.py` |
| **QA Nav** | `qa_governance_nav.py` — QSS `#qaGovernanceNav*`, Selektion `color.domain.qa_nav.*` |
| **Workspaces** | `test_inventory_workspace`, `coverage_map_workspace`, `gap_analysis_workspace`, `incidents_workspace`, `replay_lab_workspace`, `base_analysis_workspace` |
| **Panels** | `test_inventory_panels`, `coverage_map_panels`, `gap_analysis_panels`, `incidents_panels`, `replay_lab_panels` |

---

## 6. Domain: Runtime / Debug

| Komponente | Beschreibung |
|------------|--------------|
| **Runtime Debug Screen** | Tab/Workspace-Host für Debug-Bereich |
| **Runtime Debug Nav** | `RuntimeDebugNav` — Monitoring-Optik (eigene Token-Familie) |
| **Theme Visualizer Entry** | `ThemeVisualizerEntryWorkspace` (wenn `LINUX_DESKTOP_CHAT_DEVTOOLS`) |
| **Monitore (Bottom Panel)** | `LogsMonitor`, `EventsMonitor`, `MetricsMonitor`, `AgentActivityMonitor`, `LlmTraceMonitor` |

---

## 7. Domain: Dashboard (Kommandozentrale)

| Komponente | Beschreibung |
|------------|--------------|
| **Dashboard Screen** | `DashboardScreen` |
| **Karten / Panels** | z. B. `active_work_panel`, `incidents_panel` |
| **Legacy-artige Karten** | `CommandCenterView` + `_StatusCard`, `_SubsystemCard` (`app/gui/domains/command_center/command_center_view.py`) — primär Legacy-Pfad |

---

## 8. Domain: Settings

| Komponente | Beschreibung |
|------------|--------------|
| **Settings Screen** | `SettingsScreen` |
| **Settings Workspace** | `SettingsWorkspace`, `SettingsHelpPanel` |
| **Kategorie-Panels** | `workspace_category`, `project_category`, `ModelSettingsPanel`, `ThemeSelectionPanel`, … |
| **Settings Dialog** | `SettingsDialog` |
| **Section Cards** | Wiederverwendbare `#settingsPanel` / Section-Frames |

---

## 9. Workbench & geteilte UI-Bausteine

| Komponente | Rolle |
|------------|--------|
| **Main Workbench** | `MainWorkbench` — alternativer/älterer Workbench-Einstieg (`app/gui/workbench/main_workbench.py`) |
| **Workbench Controller / Focus** | `WorkbenchController`, `WorkbenchFocusController`, kontextuelle Aktionen |
| **Explorer** | `ExplorerPanel`, `ExplorerTreeModel`, `explorer_items` |
| **Canvas** | `CanvasTabs`, `CanvasRouter`, `WorkbenchCanvasBase` |
| **Command Palette** | `CommandPaletteDialog`, `CommandRegistry`, `CommandItem` |
| **Section Card / Panel Header** | `SectionCard`, `PanelHeader` |
| **Empty State** | `EmptyStateWidget` |
| **Context Action Bar** | `ContextActionBar` |
| **Console Panel** | `ConsolePanel` |
| **Markdown (shared)** | `markdown_widgets.py` (`MarkdownView`, `MarkdownDocumentView`, …), `shared/markdown/*` |
| **Doc Search** | `DocSearchPanel` |
| **Help** | `HelpPanel`, kontextuelle Hilfe / `HelpWindow` (über Commands) |
| **Workspace Graph** | `WorkspaceGraphNode`, `WorkspaceGraphDialog`, `WorkspaceGraphDetailsPanel` |
| **AI Canvas** | `AiGraphScene`, `AiNodeLibraryPanel`, Node-Graphics-Items |
| **Workflow Builder / Model Compare / Agent Test** | `WorkflowBuilderCanvas`, `ModelCompareCanvas`, `AgentTestCanvas` |
| **Model Inspector (Legacy-Pfad)** | `ModelInspector`, `ProjectContextInspector` |

---

## 10. Grafiken & Szenen

| Komponente | Technik |
|------------|---------|
| **Workflow-Graph** | `QGraphicsView` / `QGraphicsScene`, `WorkflowNodeItem`, `WorkflowEdgeItem` |
| **AI-Flow-Graph** | `QGraphicsScene` + Rect-Items |
| **Workspace Graph** | Eigene Dialog-UI mit Buttons/Karten |

---

## 11. Standard-Qt-Widgets (häufig im Einsatz)

- **Buttons:** `QPushButton`, `QToolButton`, ToolBar-`QAction`s  
- **Eingaben:** `QLineEdit`, `QPlainTextEdit`, `QTextEdit`, `QComboBox`, `QSpinBox`, `QCheckBox`, `QRadioButton`, `QSlider`  
- **Listen & Tabellen:** `QListWidget`, `QTreeWidget`, `QTableWidget`  
- **Tabs:** `QTabWidget` (u. a. `CanvasTabs`, Bottom Panel)  
- **Dialoge:** `QDialog`, `QMessageBox`, `QMenu`  
- **Fortschritt:** `QProgressBar`  
- **Scroll:** `QScrollArea`  
- **Gruppierung:** `QGroupBox`, `QFrame`, `QSplitter`  

---

## 12. DevTools & Demos

| Komponente | Beschreibung |
|------------|--------------|
| **Theme Visualizer** | `ThemeVisualizerWindow`, eingebetteter Workspace, `ThemeComponentPreview` |
| **Markdown Demo** | `MarkdownDemoPanel`, `MarkdownDemoWorkspace` |
| **Markdown Rendering Demo** | `MarkdownRenderingDemoDialog` |

---

## 13. Legacy-Einstieg (nicht Shell)

| Komponente | Datei |
|------------|--------|
| **MainWindow (Legacy)** | `app/main.py` — `ChatWidget`, `CommandCenterView`, Sidebar, Toolbar |
| **Chat Widget** | `app/gui/legacy/chat_widget.py` |
| **File Explorer / Project Chat List** | `file_explorer_widget.py`, `project_chat_list_widget.py` |

Diese Pfad wird für Farb-Migration und Konsistenz mit `app/resources/styles.py` / `get_theme_colors` weiterhin berücksichtigt (siehe Audit/Mapping-Dokus).

---

## 14. Kurz-Checkliste (Kategorien wie im Auftrag)

- [x] Main Window (Shell + Legacy)  
- [x] Sidebar(s) — global + domain-spezifisch  
- [x] Toolbar / Top Bar  
- [x] Tabs — Canvas, Bottom Panel, Runtime-Workspaces  
- [x] Panels — zahlreich pro Domain  
- [x] Cards / Section Cards / Base Panel  
- [x] Dialoge  
- [x] Buttons / Inputs  
- [x] Tables / Lists / Trees  
- [x] Chat Bubbles + Markdown Renderer  
- [x] Badges — über Token-Spec (`color.badge.*`); konkrete Widgets je Screen  
- [x] Alerts — QMessageBox + semantische States  
- [x] Status — TopBar-Aktionen, StatusBar (Legacy), Indikator-Tokens  
- [x] Charts — Token `color.chart.*`, Nutzung z. B. Performance-Tab  
- [x] Menus / Tooltips — Token-Gruppen + Qt-Standard  
- [x] Monitore / Logs / Konsole — semantische Konsolenfarben möglich  
- [x] Workflow-/Graph-Visualisierung  

---

*Ende Inventar.*

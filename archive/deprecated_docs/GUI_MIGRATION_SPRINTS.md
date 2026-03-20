# GUI-Migrations-Sprintplanung – Linux Desktop Chat

**Version:** 1.0  
**Datum:** 2026-03-15  
**Referenz:** docs/GUI_MIGRATION_ROADMAP.md, docs/GUI_REPOSITORY_ARCHITECTURE.md, docs/SCREEN_CLASS_ARCHITECTURE.md  
**Status:** Verbindliche Arbeitsblöcke für Cursor

---

## 0. Executive Summary

Diese Sprintplanung zerlegt die GUI-Migration in **14 Architektur-Sprints**, die einzeln implementierbar, reviewbar und ohne monatelange Branches umsetzbar sind. Jeder Sprint bringt einen klaren architektonischen Fortschritt und hinterlässt die Anwendung lauffähig.

**Strategische Reihenfolge:** Shell → Navigation → Workspace → Inspector/Monitor (leer) → Pilot (Kommandozentrale) → Operations (Chat) → Control Center → QA → Runtime → Altstruktur → Konsolidierung.

---

## 1. Architektur-Strategische Antworten

### 1.1 Welche Architekturteile müssen zuerst stabilisiert werden?

| Priorität | Bereich | Begründung |
|-----------|---------|------------|
| **1** | Shell (MainWindow, DockingConfig) | Ohne stabile Shell ist jede Domain-Migration gefährdet. MainWindow ist aktuell God Object. |
| **2** | Navigation (NavRegistry, WorkspaceFactory) | Routing muss zentralisiert sein, bevor TabbedWorkspace area_id-basiert arbeiten kann. |
| **3** | Workspace (TabbedWorkspace) | Container für alle Screens. Muss vor Pilot-Migration existieren. |

### 1.2 Welche Refactorings dürfen parallel laufen?

| Parallel möglich | Bedingung |
|------------------|-----------|
| **InspectorHost + MonitorHost** (Sprint 6) | Beide sind leere Hosts, keine Abhängigkeit zu Domains |
| **Base-Panels + Components** (Sprint 5) | Keine Abhängigkeit zu laufender Migration |
| **Settings-Migration** (innerhalb Sprint 10) | Isoliert, Dialog → Workspace |
| **Control Center Subbereiche** (Models, Agents, Providers) | Innerhalb Sprint 10 sequenziell, aber unabhängig voneinander |

### 1.3 Welche Bereiche sollten NICHT gleichzeitig angefasst werden?

| Kombination | Risiko |
|-------------|--------|
| **Shell + Chat-Migration** | MainWindow und chat_widget haben enge Kopplung; gleichzeitige Änderung = Merge-Hölle |
| **Navigation + TabbedWorkspace** | TabbedWorkspace nutzt NavRegistry; Registry muss zuerst stehen |
| **ChatSidePanel-Aufteilung + ChatWorkspace** | ChatSidePanel ist Teil von ChatWidget; erst ChatWorkspace (Adapter), dann Aufteilung |
| **Altstruktur-Abbau + neue Domain-Migration** | Abbau nur wenn alle Bereiche migriert |

### 1.4 Welche Bereiche eignen sich als Pilotmigration?

| Pilot | Begründung |
|-------|------------|
| **Kommandozentrale (CommandCenterScreen)** | Relativ isoliert, QA-Adapter existiert, weniger Nutzer-Interaktion als Chat, Dashboard-Struktur überschaubar |

**Nicht als Pilot:** Chat (zu komplex, Kernfeature), Control Center (zu viele Unterbereiche), QA (viele Views).

### 1.5 Welche Bereiche sollten zuletzt migriert werden?

| Reihenfolge | Bereich | Begründung |
|--------------|---------|------------|
| **Zuletzt** | Altstruktur-Abbau (Sprint 13) | Erst wenn alle Bereiche in gui/ migriert |
| **Vorletzt** | GUI-Konsolidierung (Sprint 14) | Finale Bereinigung, Dokumentation |
| **Spät** | QA & Governance (Sprint 11) | Viele Views (QADrilldown, Governance, Operations), komplexe Struktur |

### 1.6 Wie verhindert man neue Architekturverstöße während der Migration?

| Maßnahme | Umsetzung |
|----------|-----------|
| **Governance-Regeln** | PR-Checkliste: Keine neuen GUI-Dateien in app/ außer gui/; kein QDockWidget außerhalb DockingConfig; kein If/Else für Bereichswechsel |
| **Cursor Rules** | `.cursor/rules/` oder RULE.md: Neue Panels müssen von Base* erben; neue Screens in gui/domains/ |
| **Linter/Pre-commit** | Grep-basierte Checks: `addDockWidget` nur in docking_config.py; `show_chat_view`/`show_command_center` nur als Adapter |

### 1.7 Welche Regeln sollten für neue GUI-Komponenten gelten?

| Regel | Quelle |
|-------|--------|
| Jede neue GUI-Datei in `app/gui/` oder als Vorbereitung | GUI_REPOSITORY_ARCHITECTURE |
| Jedes Panel von BaseExplorer/Editor/Inspector/Monitor/Dashboard erben | SCREEN_CLASS_ARCHITECTURE |
| Kein QDockWidget außerhalb DockingConfig | GUI_MIGRATION_ROADMAP §7 |
| Bereichswechsel nur über area_selected → TabbedWorkspace | GUI_MIGRATION_ROADMAP §7 |
| Keine Cross-Domain-Imports in gui/domains/ | GUI_REPOSITORY_ARCHITECTURE |

---

## 2. Sprintübersicht

| Sprint | Name | Dauer | Abhängigkeiten |
|--------|------|-------|----------------|
| 1 | GUI Shell Stabilisierung | 2–3 Tage | — |
| 2 | Navigation Architektur | 2–3 Tage | Sprint 1 |
| 3 | Screen Registry / Routing | 2–3 Tage | Sprint 2 |
| 4 | Workspace Host | 2–3 Tage | Sprint 3 |
| 5 | Panel Standardisierung | 2–3 Tage | — (parallel zu 2–4) |
| 6 | Inspector & Monitor Hosts | 1–2 Tage | Sprint 1 |
| 7 | Operations Pilotmigration (Chat) | 4–5 Tage | Sprint 4, 5 |
| 8 | Pilot Kommandozentrale | 3–4 Tage | Sprint 4 |
| 9 | Control Center Migration | 8–10 Tage | Sprint 8 |
| 10 | QA UI Integration | 6–8 Tage | Sprint 8 |
| 11 | Runtime Debug UI | 3–4 Tage | Sprint 6 |
| 12 | Altstruktur-Aufräumphase | 3–5 Tage | Sprint 7, 8, 9, 10, 11 |
| 13 | GUI Konsolidierung | 2–3 Tage | Sprint 12 |

**Hinweis:** Sprint 7 (Chat) und Sprint 8 (Kommandozentrale) können getauscht werden – Roadmap empfiehlt Kommandozentrale zuerst als Pilot. Hier: Chat als Kernfeature früher, da SidebarWidget bereits Chat-spezifisch ist. **Empfehlung:** Sprint 8 vor Sprint 7 (Pilot zuerst).

---

## 3. Detaillierte Sprintbeschreibungen

---

### Sprint 1: GUI Shell Stabilisierung

#### Ziel
MainWindow und Docking werden entkoppelt. DockingConfig wird eingeführt. MainWindow verliert keine Fachlogik, aber die Struktur wird vorbereitet. Fenster wird resizable.

#### Architekturänderung
- Docking-Logik aus MainWindow extrahiert → `gui/shell/docking_config.py`
- Layout-Konstanten zentralisiert → `gui/shell/layout_constants.py`
- `setFixedSize()` entfernt

#### Konkrete Implementierungsaufgaben
1. `app/gui/shell/` anlegen, `__init__.py`
2. `layout_constants.py`: NAV_SIDEBAR_WIDTH=220, INSPECTOR_WIDTH=280, BOTTOM_PANEL_HEIGHT=200
3. `docking_config.py`: Klasse DockingConfig mit `setup_docks(main_window, sidebar_widget)` – QDockWidget erstellen, SidebarWidget einhängen, addDockWidget
4. MainWindow: `init_sidebar()` durch `DockingConfig.setup_docks(self, self.sidebar)` ersetzen (Sidebar-Erstellung bleibt in MainWindow, Dock-Erstellung in DockingConfig)
5. `_lock_window_size()` entfernen oder `setFixedSize` deaktivieren

#### Betroffene Dateien / Module
- **Neu:** `app/gui/__init__.py`, `app/gui/shell/__init__.py`, `app/gui/shell/layout_constants.py`, `app/gui/shell/docking_config.py`
- **Geändert:** `app/main.py`

#### Risiken
- DockingConfig könnte Layout brechen → Nach jedem Schritt App starten und prüfen

#### Review-Fokus
- Kein QDockWidget-Code mehr in main.py
- DockingConfig ist einziger Ort für addDockWidget
- Chat, Sidebar, CommandCenter, Toolbar funktionieren unverändert

#### Done-Kriterien
- [ ] DockingConfig existiert und enthält QDockWidget-Erstellung für Sidebar
- [ ] MainWindow ruft DockingConfig.setup_docks() auf
- [ ] Kein QDockWidget in MainWindow außerhalb von DockingConfig
- [ ] App startet, Chat/Sidebar/CommandCenter/Toolbar funktionieren
- [ ] Fenster ist resizable (setFixedSize entfernt)

---

### Sprint 2: Navigation Architektur

#### Ziel
NavRegistry und WorkspaceFactory werden eingeführt. area_id-basiertes Routing vorbereitet. **Bestehende Widgets werden unverändert weitergereicht** – keine Migration der Views.

#### Architekturänderung
- NavRegistry: register(area_id, factory, title, icon)
- WorkspaceFactory: create_view(area_id) → Widget
- MainWindow ruft bei Bereichswechsel get_factory(area_id)() – noch kein TabbedWorkspace

#### Konkrete Implementierungsaufgaben
1. `app/gui/navigation/` anlegen
2. `nav_areas.py`: OPERATIONS_CHAT, COMMAND_CENTER
3. `nav_registry.py`: NavRegistry mit register(), get_factory(), get_title(), get_icon()
4. `workspace_factory.py` (in gui/workspace/ oder navigation/): create_view(area_id) nutzt NavRegistry
5. Bootstrap: Bei App-Start NavRegistry mit chat_widget- und command_center-Factory registrieren (lambda: existing_widget)
6. MainWindow: Toolbar-Button "Kommandozentrale" ruft WorkspaceFactory.create_view("command_center") → stacked_widget.setCurrentWidget(widget) – Adapter, kein TabbedWorkspace

#### Betroffene Dateien / Module
- **Neu:** `app/gui/navigation/__init__.py`, `nav_areas.py`, `nav_registry.py`, `app/gui/workspace/__init__.py`, `workspace_factory.py`
- **Geändert:** `app/main.py`

#### Risiken
- Zirkuläre Imports bei Registry-Bootstrap – Factory als lambda, lazy

#### Review-Fokus
- Kein neuer If/Else für Bereichswechsel – area_id → get_factory()()
- Bestehende show_chat_view/show_command_center können intern Factory nutzen

#### Done-Kriterien
- [ ] NavRegistry existiert, command_center und operations_chat registriert
- [ ] WorkspaceFactory.create_view(area_id) liefert chat_widget oder command_center
- [ ] Bereichswechsel über Toolbar nutzt Registry (kein hartes If/Else)

---

### Sprint 3: Screen Registry / Routing

#### Ziel
NavigationSidebar wird eingeführt. Bereichsauswahl über Sidebar statt nur Toolbar. area_selected-Signal fließt zu MainWindow.

#### Architekturänderung
- NavigationSidebarWidget: QListWidget mit "Chat", "Kommandozentrale" – itemClicked → area_selected.emit(area_id)
- MainWindow: _on_area_selected(area_id) → show_chat_view() oder show_command_center() (Adapter)

#### Konkrete Implementierungsaufgaben
1. `gui/navigation/sidebar.py`: NavigationSidebarWidget – Liste "Chat", "Kommandozentrale", area_selected-Signal
2. DockingConfig erweitern: NavigationSidebar-Dock (optional: oberhalb SidebarWidget oder integriert)
3. MainWindow: NavigationSidebar.area_selected.connect(self._on_area_selected)
4. _on_area_selected: WorkspaceFactory.create_view(area_id) → stacked_widget.setCurrentWidget()

#### Betroffene Dateien / Module
- **Neu:** `app/gui/navigation/sidebar.py`
- **Geändert:** `app/main.py`, `app/gui/shell/docking_config.py`

#### Risiken
- Doppelte Navigation (Toolbar + Sidebar) – klären: Toolbar-Button entfernen oder Sidebar als primär

#### Review-Fokus
- NavigationSidebar emittiert nur area_id, keine Fachlogik
- MainWindow leitet nur weiter, kein Switch-Case

#### Done-Kriterien
- [ ] NavigationSidebar existiert und zeigt Chat, Kommandozentrale
- [ ] Klick ruft _on_area_selected(area_id)
- [ ] Bereichswechsel funktioniert über Sidebar

---

### Sprint 4: Workspace Host

#### Ziel
QStackedWidget wird durch TabbedWorkspace (QTabWidget) ersetzt. Tab pro area_id. WorkspaceFactory liefert Tab-Inhalt.

#### Architekturänderung
- CentralWidget = TabbedWorkspace statt QStackedWidget
- TabbedWorkspace.show_area(area_id): Tab hinzufügen oder wechseln
- display_project(project_id) → TabbedWorkspace.add_or_show_project_tab(project_id)

#### Konkrete Implementierungsaufgaben
1. `gui/workspace/tabbed_workspace.py`: TabbedWorkspace (QTabWidget), show_area(area_id), add_or_show_project_tab(project_id)
2. MainWindow: setCentralWidget(TabbedWorkspace)
3. TabbedWorkspace.show_area("operations_chat") als Standard
4. NavigationSidebar/Toolbar → TabbedWorkspace.show_area(area_id)
5. display_project: TabbedWorkspace.add_or_show_project_tab(project_id), ProjectChatListWidget als Tab-Inhalt
6. apply_theme: TabbedWorkspace.currentWidget() und alle Tab-Widgets mit refresh_theme() versorgen

#### Betroffene Dateien / Module
- **Neu:** `app/gui/workspace/tabbed_workspace.py`
- **Geändert:** `app/main.py`, `app/gui/workspace/workspace_factory.py`

#### Risiken
- Tab-Wechsel könnte Chat-State beeinflussen – Tab-Inhalt bleibt geladen
- display_project: ProjectChatListWidget braucht parent mit open_chat

#### Review-Fokus
- TabbedWorkspace ist CentralWidget
- display_project funktioniert (Projekt-Tab)
- apply_theme iteriert über alle Tabs

#### Done-Kriterien
- [ ] TabbedWorkspace ist CentralWidget
- [ ] Chat und Kommandozentrale erscheinen als Tabs
- [ ] Bereichswechsel über NavigationSidebar funktioniert
- [ ] QStackedWidget entfernt
- [ ] display_project fügt Projekt-Tab hinzu

---

### Sprint 5: Panel Standardisierung

#### Ziel
Base-Panel-Klassen und Shared Components werden eingeführt. Keine Domain-Migration – nur Infrastruktur.

#### Architekturänderung
- BaseWorkspaceView, BaseExplorerPanel, BaseEditorPanel, BaseInspectorPanel, BaseMonitorPanel, BaseDashboardPanel
- StatusCard, EmptyStateWidget, LoadingOverlay, SearchableList, CollapsibleGroup, LiveIndicator (mindestens Skelette)

#### Konkrete Implementierungsaufgaben
1. `gui/panels/base/` anlegen
2. BaseWorkspaceView: area_id, refresh(), refresh_theme() – abstrakt
3. BaseExplorerPanel, BaseEditorPanel, BaseInspectorPanel, BaseMonitorPanel, BaseDashboardPanel – minimale Schnittstellen
4. `gui/components/` anlegen: StatusCard, EmptyStateWidget (mindestens)
5. Keine Migration bestehender Panels – nur Klassen bereitstellen

#### Betroffene Dateien / Module
- **Neu:** `app/gui/panels/__init__.py`, `app/gui/panels/base/__init__.py`, `base_workspace_view.py`, `base_explorer.py`, `base_editor.py`, `base_inspector.py`, `base_monitor.py`, `base_dashboard.py`
- **Neu:** `app/gui/components/__init__.py`, `status_card.py`, `empty_state.py`

#### Risiken
- Gering. Nur neue Dateien, keine Änderung an Bestand.

#### Review-Fokus
- Basisklassen haben klare Schnittstellen
- Keine Domain-Imports in base/ oder components/

#### Done-Kriterien
- [ ] BaseWorkspaceView existiert
- [ ] 5 Base-Panel-Klassen existieren
- [ ] Mindestens StatusCard, EmptyStateWidget existieren
- [ ] Bestehende App unverändert (keine Migration)

---

### Sprint 6: Inspector & Monitor Hosts

#### Ziel
InspectorHost und MonitorHost existieren als Docks. Noch leer oder mit Platzhaltern. ChatSidePanel bleibt unverändert.

#### Architekturänderung
- InspectorDock, BottomPanelDock in DockingConfig
- InspectorHost: set_context(area_id, obj) – Platzhalter "Wählen Sie ein Objekt aus."
- MonitorHost: QTabWidget mit Platzhalter-Tabs (Logs, Events, Metrics, Agent Activity, LLM Trace)

#### Konkrete Implementierungsaufgaben
1. `gui/inspector/` anlegen: inspector_host.py
2. InspectorHost: QWidget, set_context(), Platzhalter-Label
3. `gui/monitors/` anlegen: monitor_host.py
4. MonitorHost: QTabWidget, 5 Platzhalter-Tabs
5. DockingConfig: InspectorDock (rechts), BottomPanelDock (unten) – optional einblendbar

#### Betroffene Dateien / Module
- **Neu:** `app/gui/inspector/__init__.py`, `inspector_host.py`, `app/gui/monitors/__init__.py`, `monitor_host.py`
- **Geändert:** `app/gui/shell/docking_config.py`

#### Risiken
- Gering. Nur neue Docks. ChatSidePanel unverändert.

#### Review-Fokus
- Beide Hosts können ein-/ausgeblendet werden
- Keine Migration von ChatSidePanel-Inhalten

#### Done-Kriterien
- [ ] InspectorHost und MonitorHost existieren als Docks
- [ ] Beide ein-/ausblendbar
- [ ] ChatSidePanel unverändert

---

### Sprint 7: Operations Pilotmigration (Chat)

**Hinweis:** Roadmap empfiehlt Kommandozentrale als Pilot. Diese Sprintplanung stellt Chat vor Kommandozentrale, da Chat das Kernfeature ist und SidebarWidget bereits Chat-spezifisch. **Alternative:** Sprint 8 vor Sprint 7 ausführen (Pilot zuerst).

#### Ziel
Chat wird in ChatWorkspace überführt. **Adapter-Strategie:** ChatWidget als Ganzes in ChatWorkspace einbetten. Keine Extraktion von SessionExplorer/ChatEditor.

#### Architekturänderung
- ChatWorkspaceView erbt BaseWorkspaceView, enthält ChatWidget als Kind
- TabbedWorkspace.show_area("operations_chat") zeigt ChatWorkspaceView
- MainWindow delegiert new_chat, open_chat, save_chat an chat_widget (über ChatWorkspaceView.chat_widget)

#### Konkrete Implementierungsaufgaben
1. `gui/domains/operations/chat/` anlegen
2. ChatWorkspaceView: Konstruktor erhält client, db, orchestrator, settings, rag_service; erstellt ChatWidget, setzt als Layout-Inhalt
3. NavRegistry: operations_chat → Factory für ChatWorkspaceView
4. MainWindow: Bei area operations_chat Referenz auf chat_widget aus TabbedWorkspace.currentWidget().chat_widget holen
5. display_project: ProjectChatListWidget als Tab, parent=MainWindow (open_chat)
6. SidebarWidget bleibt, Verbindungen zu MainWindow bleiben

#### Betroffene Dateien / Module
- **Neu:** `app/gui/domains/__init__.py`, `app/gui/domains/operations/__init__.py`, `app/gui/domains/operations/chat/__init__.py`, `workspace_view.py`
- **Geändert:** `app/main.py`, `app/gui/navigation/nav_registry.py`, `app/gui/workspace/workspace_factory.py`, `app/gui/workspace/tabbed_workspace.py`

#### Risiken
- MainWindow braucht chat_widget-Referenz für Delegation – ChatWorkspaceView muss Property bereitstellen

#### Review-Fokus
- ChatWidget unverändert, nur eingebettet
- new_chat, open_chat, save_chat funktionieren
- display_project funktioniert

#### Done-Kriterien
- [ ] ChatWorkspaceView existiert, enthält ChatWidget
- [ ] TabbedWorkspace zeigt Chat bei area operations_chat
- [ ] new_chat, open_chat, save_chat funktionieren
- [ ] display_project funktioniert
- [ ] SidebarWidget unverändert

---

### Sprint 8: Pilot Kommandozentrale

#### Ziel
Kommandozentrale wird in Zielstruktur überführt. CommandCenterView wird aufgeteilt: Dashboard → gui/domains/dashboard/. QA-spezifische Teile bleiben vorerst in ui/command_center/, werden über Quick Action verlinkt.

#### Architekturänderung
- CommandCenterScreen in gui/domains/dashboard/
- CommandCenterDashboard: Status-Karten, Quick Actions (ohne QA-Drilldown als Hauptinhalt)
- QA-Views bleiben in ui/command_center/, area_id qa_drilldown etc. für später

#### Konkrete Implementierungsaufgaben
1. `gui/domains/dashboard/` anlegen
2. CommandCenterDashboard: Extraktion aus CommandCenterView – Status-Karten, Quick Actions
3. CommandCenterScreen (BaseWorkspaceView): Zeigt CommandCenterDashboard
4. NavRegistry: command_center → CommandCenterScreen
5. QA-Buttons in Dashboard: Führen zu area_id qa_* (vorerst alte View oder Platzhalter)

#### Betroffene Dateien / Module
- **Neu:** `app/gui/domains/dashboard/__init__.py`, `workspace_view.py`, `panels/command_center_dashboard.py`
- **Geändert:** `app/main.py`, `app/gui/navigation/nav_registry.py`
- **Unverändert (vorerst):** `app/ui/command_center/` (QA-Views)

#### Risiken
- QA-Content temporär über Quick Actions erreichbar – keine Verlust-Szenarien

#### Review-Fokus
- CommandCenterScreen zeigt nur Dashboard
- QA-Bereich über Quick Action erreichbar

#### Done-Kriterien
- [ ] CommandCenterScreen existiert in gui/domains/dashboard/
- [ ] CommandCenterScreen zeigt nur Dashboard
- [ ] QA-Bereich über Quick Action erreichbar
- [ ] BaseWorkspaceView wird genutzt

---

### Sprint 9: Control Center Migration

#### Ziel
Control Center (Models, Providers, Agents, Tools, Data Stores) wird migriert. ModelSettingsPanel, AgentManagerDialog, PromptManagerPanel werden in Workspaces überführt.

#### Architekturänderung
- ModelsWorkspace, AgentsWorkspace, PromptStudioWorkspace in gui/domains/control_center/ bzw. operations/
- ModelSettingsPanel aus ChatSidePanel → ModelsWorkspace
- AgentManagerDialog → AgentsWorkspace
- PromptManagerPanel → PromptStudioWorkspace

#### Konkrete Implementierungsaufgaben
1. **Settings zuerst:** SettingsDialog → SettingsScreen (gui/domains/settings/)
2. **Models:** ModelSettingsPanel extrahieren → ModelsWorkspace
3. **Agents:** AgentManagerDialog → AgentsWorkspace
4. **Prompt Studio:** PromptManagerPanel → PromptStudioWorkspace
5. NavRegistry für control_models, control_agents, operations_prompt_studio
6. ChatSidePanel: Modelle-, Prompts-Tabs entfernen oder durch Links ersetzen

#### Betroffene Dateien / Module
- **Neu:** `gui/domains/settings/`, `gui/domains/control_center/models/`, `gui/domains/control_center/agents/`, `gui/domains/operations/prompt_studio/`
- **Geändert:** `app/ui/sidepanel/chat_side_panel.py`, `app/main.py`

#### Risiken
- ChatSidePanel wird schlanker – Nutzer müssen neue Wege zu Models/Prompts finden

#### Review-Fokus
- Keine Dialogs für Bereichswechsel
- ChatSidePanel nur noch Debug (oder minimal)

#### Done-Kriterien
- [ ] Settings als Workspace
- [ ] Models, Agents, Prompt Studio als Workspaces
- [ ] ChatSidePanel ohne Modelle/Prompts-Tabs (oder Links)

---

### Sprint 10: QA UI Integration

#### Ziel
QA & Governance wird migriert. QADrilldownView, GovernanceView, Operations-Views → gui/domains/qa_governance/.

#### Architekturänderung
- TestInventoryWorkspace, CoverageMapWorkspace, GapAnalysisWorkspace, IncidentsWorkspace, ReplayLabWorkspace
- Bestehende Views aus ui/command_center/ werden in Domains eingebettet oder neu erstellt

#### Konkrete Implementierungsaufgaben
1. `gui/domains/qa_governance/` anlegen
2. QADrilldownView, GovernanceView, SubsystemDetailView → qa_governance/
3. Operations-Views (QA, Incident, Review, Audit) → qa_governance/
4. NavRegistry: qa_test_inventory, qa_coverage_map, qa_gap_analysis, qa_incidents, qa_replay_lab
5. NavigationSidebar: QA & Governance mit Untereinträgen

#### Betroffene Dateien / Module
- **Neu:** `gui/domains/qa_governance/test_inventory/`, `coverage_map/`, `gap_analysis/`, `incidents/`, `replay_lab/`
- **Geändert:** Imports aus ui/command_center/ → gui/domains/qa_governance/

#### Risiken
- QA hat viele Views – schrittweise Migration, Bereich für Bereich

#### Review-Fokus
- Keine Duplikation von QA-Logik
- Adapter (QADashboardAdapter) unverändert

#### Done-Kriterien
- [ ] QA-Bereiche in gui/domains/qa_governance/
- [ ] Alle QA-Views erreichbar über Navigation
- [ ] CommandCenter-Dashboard verlinkt zu QA

---

### Sprint 11: Runtime Debug UI

#### Ziel
AgentDebugPanel, EventTimelineView, TaskGraphView etc. → MonitorHost. RuntimeWorkspace mit Tabs für EventBus, Logs, Metrics, Agent Activity, LLM Trace.

#### Architekturänderung
- Monitor-Panels (LogsMonitor, EventBusMonitor, etc.) in gui/monitors/panels/
- MonitorHost mit echten Panels statt Platzhalter
- RuntimeWorkspace: TabWidget mit Reuse von Monitor-Panels
- ChatSidePanel: Debug-Tab entfernt, Link zu Runtime/MonitorHost

#### Konkrete Implementierungsaufgaben
1. `gui/monitors/panels/` mit LogsMonitor, EventBusMonitor, AgentActivityMonitor, LLMTraceMonitor (aus ui/debug/)
2. MonitorHost: Platzhalter durch echte Panels ersetzen
3. RuntimeWorkspace in gui/domains/runtime_debug/
4. ChatSidePanel: Debug-Tab entfernen, Link zu Runtime
5. NavRegistry: runtime_eventbus, runtime_logs, etc.

#### Betroffene Dateien / Module
- **Neu:** `gui/monitors/panels/logs_monitor.py`, `eventbus_monitor.py`, etc., `gui/domains/runtime_debug/`
- **Geändert:** `app/ui/sidepanel/chat_side_panel.py`, `app/ui/debug/` (Migration)

#### Risiken
- Debug-Panels haben EventBus-Abhängigkeiten – saubere Trennung

#### Review-Fokus
- Monitor-Panels zentral in gui/monitors/panels/
- RuntimeWorkspace reuses, dupliziert nicht

#### Done-Kriterien
- [ ] MonitorHost mit echten Monitor-Panels
- [ ] RuntimeWorkspace existiert
- [ ] ChatSidePanel ohne Debug-Tab

---

### Sprint 12: Altstruktur-Aufräumphase

#### Ziel
app/chat_widget.py, app/sidebar_widget.py, app/ui/command_center/ (Alt), app/ui/sidepanel/ (Alt) werden entfernt oder in gui/ konsolidiert.

#### Architekturänderung
- Alle GUI-Pfade führen über app/gui/
- Keine Alt-Imports mehr im aktiven Pfad

#### Konkrete Implementierungsaufgaben
1. Deprecation: Alt-Imports markieren, auf gui/ umstellen
2. chat_widget.py, sidebar_widget.py: In gui/domains/operations/chat/ integrieren (SessionExplorer aus SidebarWidget)
3. app/ui/command_center/: Reste nach QA-Migration löschen oder konsolidieren
4. app/ui/sidepanel/: Nach Control Center/Runtime-Migration löschen
5. main.py: Import von gui.shell.main_window (falls MainWindow migriert)

#### Betroffene Dateien / Module
- **Gelöscht/verschoben:** app/chat_widget.py, app/sidebar_widget.py, app/ui/ (Reste)
- **Geändert:** Alle Imports in app/

#### Risiken
- Vergessene Referenzen – Grep nach Alt-Imports

#### Review-Fokus
- Keine Alt-Struktur im aktiven Pfad
- Alle Tests grün

#### Done-Kriterien
- [ ] Keine Alt-Struktur mehr im aktiven Pfad
- [ ] app/gui/ ist die einzige GUI-Root
- [ ] Alle Tests grün

---

### Sprint 13: GUI Konsolidierung

#### Ziel
Finale Bereinigung, Dokumentation, Governance-Regeln als Cursor Rules.

#### Architekturänderung
- Keine strukturellen Änderungen – nur Konsolidierung

#### Konkrete Implementierungsaufgaben
1. RULE.md oder .cursor/rules/ mit Architektur-Regeln
2. Dokumentation (UX_CONCEPT, GUI_REPOSITORY_ARCHITECTURE, SCREEN_CLASS_ARCHITECTURE) auf Ist-Zustand prüfen
3. PR-Checkliste für GUI-Änderungen finalisieren
4. Linter/Pre-commit für Architektur-Verstöße (optional)

#### Betroffene Dateien / Module
- **Neu:** `.cursor/rules/gui-architecture.mdc` oder RULE.md
- **Geändert:** docs/*.md (Aktualisierung)

#### Risiken
- Keine

#### Review-Fokus
- Regeln sind umsetzbar und verständlich

#### Done-Kriterien
- [ ] Cursor Rules für GUI-Architektur
- [ ] Dokumentation aktuell
- [ ] PR-Checkliste vorhanden

---

## 4. Cursor-Arbeitsblöcke (konkret)

Jeder Sprint kann in Cursor als **einzelner Arbeitsblock** formuliert werden:

### Beispiel: Sprint 1 als Cursor-Prompt

```
AUFGABE: GUI Shell Stabilisierung (Sprint 1)

Kontext: Siehe docs/GUI_MIGRATION_ROADMAP.md Phase 1, docs/GUI_MIGRATION_SPRINTS.md Sprint 1.

Schritte:
1. Erstelle app/gui/shell/ mit layout_constants.py (NAV_SIDEBAR_WIDTH=220, etc.)
2. Erstelle docking_config.py mit DockingConfig.setup_docks(main_window, sidebar_widget)
3. Refaktoriere main.py: init_sidebar() → DockingConfig.setup_docks(self, self.sidebar)
4. Entferne _lock_window_size() / setFixedSize

Done: App startet, Docking funktioniert, Fenster resizable. Kein QDockWidget in main.py.
```

### Beispiel: Sprint 4 als Cursor-Prompt

```
AUFGABE: Workspace Host (Sprint 4)

Kontext: docs/GUI_MIGRATION_ROADMAP.md Phase 3, docs/GUI_MIGRATION_SPRINTS.md Sprint 4.

Schritte:
1. Erstelle gui/workspace/tabbed_workspace.py mit TabbedWorkspace (QTabWidget)
2. TabbedWorkspace.show_area(area_id), add_or_show_project_tab(project_id)
3. MainWindow: setCentralWidget(TabbedWorkspace), QStackedWidget entfernen
4. display_project → TabbedWorkspace.add_or_show_project_tab
5. apply_theme über alle Tab-Widgets

Done: Chat und Kommandozentrale als Tabs, display_project funktioniert.
```

---

## 5. Abhängigkeitsgraph (Sprints)

```
Sprint 1 (Shell)
    ├── Sprint 2 (Navigation)
    │       └── Sprint 3 (Screen Registry)
    │               └── Sprint 4 (Workspace)
    │                       ├── Sprint 7 (Chat)
    │                       └── Sprint 8 (Kommandozentrale)
    │                               ├── Sprint 9 (Control Center)
    │                               ├── Sprint 10 (QA)
    │                               └── Sprint 11 (Runtime)
    └── Sprint 6 (Inspector/Monitor)
            └── Sprint 11 (Runtime)

Sprint 5 (Panel Standardisierung) – parallel zu 2–4
Sprint 12 (Altstruktur) – nach 7, 8, 9, 10, 11
Sprint 13 (Konsolidierung) – nach 12
```

---

## 6. Zeitplan (Grobraster)

| Sprint | Dauer | Kumuliert |
|-------|-------|-----------|
| 1 | 2–3 Tage | 3 Tage |
| 2 | 2–3 Tage | 6 Tage |
| 3 | 2–3 Tage | 9 Tage |
| 4 | 2–3 Tage | 12 Tage |
| 5 | 2–3 Tage | 15 Tage (parallel) |
| 6 | 1–2 Tage | 17 Tage |
| 7 | 4–5 Tage | 22 Tage |
| 8 | 3–4 Tage | 26 Tage |
| 9 | 8–10 Tage | 36 Tage |
| 10 | 6–8 Tage | 44 Tage |
| 11 | 3–4 Tage | 48 Tage |
| 12 | 3–5 Tage | 53 Tage |
| 13 | 2–3 Tage | 56 Tage |

**Gesamt:** ca. 10–12 Wochen bei Vollzeit. Bei Teilzeit entsprechend länger.

---

*Diese Sprintplanung ist verbindliche Grundlage für die Cursor-Arbeitsblöcke. Abweichungen bedürfen einer Architektur-Review.*

# GUI-Migrations-Roadmap – Linux Desktop Chat

**Version:** 1.1  
**Datum:** 2026-03-15  
**Referenz:** docs/UX_CONCEPT.md, docs/GUI_REPOSITORY_ARCHITECTURE.md, docs/SCREEN_CLASS_ARCHITECTURE.md  
**Status:** Verbindliche Migrationsstrategie

---

## 0. Ausgangslage: Reales gewachsenes Projekt

**Dieses Dokument ist kein Greenfield-Plan.** Es beschreibt den Umbau einer **real existierenden, historisch gewachsenen** PySide6-GUI mit impliziten Kopplungen und uneinheitlichen Verantwortlichkeiten.

### 0.1 Strategische Entscheidung: Inkrementell statt Total-Rewrite

| Option | Bewertung | Entscheidung |
|--------|-----------|--------------|
| **Total-Rewrite** | Hohes Risiko, lange Laufzeit ohne lauffähige App, Verlust von getesteter Funktionalität | **Nein.** Kein zwingender Architekturgrund. |
| **Inkrementelle Zielmigration** | Lauffähige Zwischenzustände, schrittweise Entkopplung, bestehende Tests nutzbar | **Ja.** Bevorzugt. |

**Begründung:** Die App ist funktional stabil (717 Tests). Chat, CommandCenter, Sidebar funktionieren. Ein Total-Rewrite würde Monate ohne nutzbare App bedeuten und getestete Pfade gefährden. Die Zielarchitektur lässt sich durch Extraktion, Wrapper und schrittweisen Abbau erreichen.

### 0.2 Konkrete Ist-Struktur (Stand: 2026-03-15)

```
app/
├── main.py                    # MainWindow-Klasse, ~270 Zeilen
├── chat_widget.py             # ChatWidget, ~866 Zeilen, enthält ChatSidePanel
├── sidebar_widget.py          # SidebarWidget, Chats + Projekte + FileExplorer
├── project_chat_list_widget.py # Projekt-Chat-Liste, ruft parent.display_project/open_chat
├── file_explorer_widget.py    # In SidebarWidget eingebettet
├── ui/
│   ├── command_center/        # CommandCenterView + 8 Sub-Views (QADrilldown, Governance, …)
│   ├── chat/                  # ConversationView, ChatComposerWidget, ChatHeaderWidget
│   ├── sidepanel/             # ChatSidePanel, ModelSettingsPanel, PromptManagerPanel
│   ├── debug/                 # AgentDebugPanel, EventTimelineView, TaskGraphView, …
│   ├── agents/                # AgentManagerDialog, AgentProfilePanel, AgentListPanel
│   └── settings_dialog.py     # Modal-Dialog
└── ...
```

### 0.3 Dokumentierte Kopplungen (tatsächlicher Code)

| Von | Nach | Art | Code-Stelle |
|-----|------|-----|-------------|
| MainWindow | chat_widget | Direkt | self.chat_widget (Zeile 39–43) |
| MainWindow | sidebar | Direkt | self.sidebar (Zeile 115–116) |
| MainWindow | command_center | Direkt | self.command_center (Zeile 46–48) |
| MainWindow | stacked_widget | Direkt | self.stacked_widget (Zeile 44–50) |
| SidebarWidget | MainWindow.new_chat | Signal | sidebar.new_chat_clicked.connect(self.new_chat) |
| SidebarWidget | MainWindow.open_chat | Signal | sidebar.chat_selected.connect(self.open_chat) |
| SidebarWidget | MainWindow.display_project | hasattr(parent) | sidebar ruft parent.display_project(project_id) |
| MainWindow | chat_widget.chat_id | Direkt | add_file_to_current_chat, open_chat, save_chat |
| MainWindow | chat_widget.header.agent_combo | Direkt | _on_agent_selected_for_chat (Zeile 246–249) |
| MainWindow | chat_widget (apply_theme) | Direkt | apply_theme() ruft chat_widget.refresh_theme() |
| MainWindow | command_center (apply_theme) | Direkt | apply_theme() ruft command_center.refresh_theme() |
| ProjectChatListWidget | parent.open_chat | hasattr | parent.open_chat(chat_id) |
| ChatWidget | ChatSidePanel | Enthält | chat_widget enthält side_panel (rechts) |
| ChatSidePanel | ModelSettingsPanel, PromptManagerPanel, AgentDebugPanel | Tabs | 3 Tabs in ChatSidePanel |
| CommandCenterView | QADashboardAdapter, 8 Sub-Views | Stack | QStackedWidget mit 9 Indizes |

### 0.4 Implizite Abhängigkeiten (Risiken bei Migration)

| Abhängigkeit | Risiko bei Änderung |
|--------------|---------------------|
| MainWindow kennt chat_widget.chat_id | Jede Chat-Logik-Delegation muss chat_id durchreichen |
| MainWindow kennt chat_widget.header.agent_combo | Agent-Auswahl ist tief in ChatWidget verschachtelt |
| display_project manipuliert stacked_widget direkt | TabbedWorkspace muss dynamisches Hinzufügen unterstützen |
| SidebarWidget nutzt hasattr(parent) | Lose Kopplung – aber parent muss MainWindow sein |
| apply_theme() iteriert über chat_widget, command_center | Jeder neue Screen muss manuell in apply_theme |
| ChatWidget erstellt RAGService, Orchestrator-Abhängigkeiten | ChatWorkspace braucht Dependency-Injection |

---

## 1. Migrationsleitbild

### 1.1 Ziel

Die bestehende, gewachsene PySide6-GUI wird **kontrolliert und iterativ** in die definierte Zielarchitektur überführt. Die Anwendung bleibt während der gesamten Migration **lauffähig**. Es gibt **keinen Big-Bang-Rewrite**. Jede Phase endet mit einem **lauffähigen Zwischenzustand**.

### 1.2 Leitprinzipien

| Prinzip | Bedeutung |
|---------|------------|
| **Shell zuerst** | MainWindow und Docking werden zuerst entkoppelt und verschlankt. Ohne stabile Shell ist jede Feature-Migration gefährdet. |
| **Registry vor Migration** | NavRegistry und WorkspaceFactory werden eingeführt, bevor Feature-Bereiche migriert werden. Routing wird zentralisiert. |
| **Pilot vor Rollout** | Ein Bereich (Kommandozentrale) wird als Pilot migriert. Erst danach folgen Operations, Control Center, QA, Runtime. |
| **Altstruktur mit Exit** | Jede Phase hat einen Abbauplan. Keine dauerhafte Parallelarchitektur. |
| **Keine neuen Sonderfälle** | Alle neuen GUI-Komponenten folgen der Zielarchitektur. Keine „temporären“ Abweichungen ohne Rückbauplan. |

### 1.3 Erster architektonischer Hebel

**Der erste Hebel ist die Shell-Konsolidierung.**

Begründung: MainWindow enthält aktuell Docking (inline), Fachlogik (Chat, File, Project), direkte Screen-Steuerung (show_chat_view, show_command_center) und direkte Verweise auf Widgets. Solange MainWindow diese Verantwortlichkeiten trägt, kann keine saubere Feature-Migration erfolgen. Jede Domain-Migration würde gegen ein unklares MainWindow laufen.

**Reihenfolge-Entscheidung: Shell zuerst, dann Feature-Bereiche.**

---

## 2. Typische Ist-Zustands-Probleme in gewachsenen PySide6-GUIs

### 2.1 Analyse des aktuellen Zustands

| Problem | Ist-Zustand | Ziel |
|---------|-------------|------|
| **MainWindow als God Object** | MainWindow: Docking, Chat-Logik, File-Logik, Project-Logik, Screen-Switching, Settings-Callbacks, Agent-Integration | MainWindow: Nur Docking, Routing, Signal-Vermittlung |
| **Navigation über Toolbar** | Toolbar-Buttons (Hilfe, Settings, Agent Manager, Kommandozentrale). Keine hierarchische Sidebar. | NavigationSidebar mit 6 Hauptbereichen, area_id-basiert |
| **Routing über If/Else** | show_chat_view(), show_command_center(), display_project() – direkte Methodenaufrufe | NavRegistry + WorkspaceFactory, area_selected(area_id) |
| **Sidebar = Chat-spezifisch** | SidebarWidget: Chats, Projekte, File Explorer. Kein allgemeiner Bereichswechsel. | NavigationSidebar: Bereichswechsel | SessionExplorer: Chat-spezifisch, in ChatWorkspace |
| **QStackedWidget statt TabbedWorkspace** | 2–3 Views (Chat, CommandCenter, ProjectChatList). Kein Tab-basiertes Arbeiten. | TabbedWorkspace mit Tab pro area_id |
| **ChatSidePanel vermischt** | Modelle + Prompts + Debug in einem Panel. Modelle/Provider → Control Center, Prompts → Prompt Studio, Debug → Runtime/Bottom Panel | Aufteilung in Zielbereiche |
| **CommandCenter = QA-Dashboard** | CommandCenterView enthält QA-Drilldown, Governance, Operations, Subsystem-Detail. | Kommandozentrale: nur Übersicht | QA: eigener Bereich |
| **Agent Manager als Dialog** | AgentManagerDialog öffnet modal. | Agent Design → Control Center / Agents |
| **Kein InspectorHost** | Kein kontextabhängiger rechter Bereich | InspectorHost mit InspectorRegistry |
| **Kein Bottom Panel** | Debug-Panel im ChatSidePanel | MonitorHost mit Logs, Events, Metrics, Agent Activity, LLM Trace |
| **Verstreute GUI-Struktur** | app/chat_widget.py, app/sidebar_widget.py, app/ui/command_center/, app/ui/chat/, app/ui/sidepanel/, app/ui/agents/ | app/gui/ mit shell/, navigation/, workspace/, domains/, inspector/, monitors/ |
| **Fachlogik in MainWindow** | add_file_to_current_chat, add_file_to_project, new_chat, save_chat, open_chat, _on_agent_selected_for_chat | Delegation an Domain/ChatWorkspace oder Services |
| **Fenster fixiert** | setFixedSize() | Entfernen, flexible Größe |

### 2.2 Mapping: Ist → Ziel

| Ist-Komponente | Ziel-Komponente | Migrationsart |
|----------------|-----------------|---------------|
| MainWindow (app/main.py) | MainWindow (gui/shell/main_window.py) | Refactor + Extraktion |
| SidebarWidget (app/sidebar_widget.py) | NavigationSidebar + SessionExplorer (in Chat) | Aufteilung |
| ChatWidget (app/chat_widget.py) | ChatWorkspace (gui/domains/operations/chat/) | Migration |
| ChatSidePanel (Modelle, Prompts, Debug) | ModelSettingsPanel → Control Center | ModelsWorkspace | PromptManagerPanel → Prompt Studio | AgentDebugPanel → MonitorHost |
| CommandCenterView | CommandCenterScreen (Dashboard) + QA-Views → gui/domains/qa_governance/ | Aufteilung |
| AgentManagerDialog | AgentsWorkspace (Control Center) | Migration |
| SettingsDialog | SettingsScreen | Migration |
| ProjectChatListWidget | Teil von ChatWorkspace (Projekt-Kontext) | Integration |
| ui/debug/* | AgentDebugPanel, EventTimeline etc. → MonitorHost | Migration |

### 2.3 Kritischer Pfad: display_project und ProjectChatListWidget

**Ist-Verhalten (app/main.py, Zeilen 181–191):**
- SidebarWidget ruft `parent.display_project(project_id)` bei Projekt-Klick (sidebar_widget.py Zeile 186–187)
- MainWindow.display_project: entfernt ggf. altes ProjectChatListWidget aus stacked_widget, erstellt neues, fügt hinzu, zeigt an
- ProjectChatListWidget(parent=MainWindow) – ruft parent.open_chat(chat_id) bei Chat-Auswahl (project_chat_list_widget.py Zeile 94–95)

**Migrations-Strategie:**
- **Phase 3 (TabbedWorkspace):** display_project wird zu TabbedWorkspace.add_or_show_tab(area_id="operations_project", context=project_id). Tab-Inhalt: ProjectChatListWidget. Parent bleibt MainWindow (für open_chat).
- **Phase 6:** ProjectChatListWidget braucht open_chat – MainWindow oder ChatWorkspaceView. Da ProjectChatListWidget Chats eines Projekts zeigt und open_chat den Chat öffnet: MainWindow.open_chat bleibt. MainWindow delegiert an aktuelles chat_widget (aus ChatWorkspaceView).
- **Kein Total-Rewrite:** ProjectChatListWidget bleibt unverändert. Nur der Container (StackedWidget → TabbedWorkspace) wechselt.

---

## 3. Empfohlene Migrationsreihenfolge

### 3.1 Übersicht

```
Phase 0: Ist-Analyse und Architektur-Mapping
    ↓
Phase 1: Shell-Konsolidierung (MainWindow, DockingConfig)
    ↓
Phase 2: Navigation und Routing (NavRegistry, WorkspaceFactory, NavigationSidebar)
    ↓
Phase 3: Workspace-Host / TabbedWorkspace
    ↓
Phase 4: InspectorHost und MonitorHost (als leere Hosts)
    ↓
Phase 5: Pilotmigration Kommandozentrale
    ↓
Phase 6: Operations-Migration (Chat)
    ↓
Phase 7: Control Center, QA, Runtime, Settings
    ↓
Phase 8: Altstruktur-Abbau / Konsolidierung
```

### 3.2 Begründung der Reihenfolge

| Phase | Warum diese Reihenfolge? |
|-------|---------------------------|
| **Shell zuerst** | MainWindow und Docking sind die Basis. Ohne stabile Shell ist jede Domain-Migration gefährdet. |
| **Navigation vor Workspace** | NavRegistry muss existieren, bevor TabbedWorkspace area_id-basiert arbeiten kann. |
| **Workspace vor Pilot** | TabbedWorkspace muss den Pilot-Screen aufnehmen können. |
| **Inspector/Monitor als leere Hosts** | Platzhalter für spätere Integration. Kein Blockieren der Pilot-Migration. |
| **Kommandozentrale als Pilot** | Relativ isoliert, QA-Adapter bereits vorhanden, weniger komplex als Chat. |
| **Chat danach** | Kernfeature, größte Nutzung. Nach Pilot-Erfahrung. |
| **Control Center, QA, Runtime, Settings** | Können parallel oder nacheinander. QA hat bereits viele Views. |
| **Altstruktur-Abbau** | Erst wenn alle Bereiche migriert sind. |

---

## 4. Phasenmodell

### Phase 0: Ist-Analyse und Architektur-Mapping

**Ziel:** Vollständiges Mapping des Ist-Zustands auf die Zielarchitektur. Keine Code-Änderungen.

**Aktivitäten:**
- Erstellung einer detaillierten Ist-Zustands-Matrix (bereits in Abschnitt 2)
- Identifikation aller Abhängigkeiten zwischen MainWindow, ChatWidget, SidebarWidget, CommandCenterView
- Dokumentation aller Signal-Slot-Verbindungen
- Liste aller Stellen, die Docking/Layout betreffen
- Liste aller Stellen, die Bereichswechsel auslösen

**Done-Kriterien:**
- [ ] Ist-Zustands-Matrix vollständig
- [ ] Abhängigkeitsgraph dokumentiert
- [ ] Migrations-Risiken pro Komponente identifiziert
- [ ] Kein Code geändert

**Risiken:** Keine. Reine Analyse.

**Dauer:** 1–2 Tage

---

### Phase 1: Shell-Konsolidierung

**Ziel:** MainWindow und Docking werden entkoppelt. DockingConfig wird eingeführt. MainWindow verliert Fachlogik nicht sofort, aber die Struktur wird vorbereitet.

**Zwischenzustand nach Phase 1:**
- `app/gui/shell/docking_config.py` existiert
- `app/gui/shell/layout_constants.py` existiert
- `app/main.py` importiert DockingConfig, ruft setup_docks() auf
- **Unverändert:** chat_widget, sidebar, command_center, alle Signal-Verbindungen, Fachlogik in MainWindow

**Konkrete Schritte (Reihenfolge):**
1. `app/gui/shell/` anlegen, `__init__.py`
2. `layout_constants.py`: NAV_SIDEBAR_WIDTH=220, INSPECTOR_WIDTH=280, BOTTOM_PANEL_HEIGHT=200
3. `docking_config.py`: Klasse DockingConfig mit `setup_docks(main_window: QMainWindow)`. Inhalt: exakt die Logik aus `init_sidebar()` (Zeilen 110–128) – QDockWidget erstellen, SidebarWidget einhängen, addDockWidget. **SidebarWidget wird von MainWindow übergeben** (DockingConfig erhält Referenz oder erstellt sie nicht – MainWindow erstellt sidebar weiterhin, übergibt an setup_docks).
4. MainWindow: `init_sidebar()` durch `DockingConfig.setup_docks(self)` ersetzen. DockingConfig erhält self.sidebar_dock, self.sidebar – oder: MainWindow erstellt sidebar, ruft `DockingConfig.install_sidebar_dock(self, self.sidebar)`.
5. **Pragmatisch:** DockingConfig.setup_docks(mw) erhält mw, erstellt sidebar_dock, erstellt SidebarWidget(mw.db), setzt Verbindungen. MainWindow übergibt db. Oder: MainWindow erstellt sidebar wie bisher, DockingConfig nur für Dock-Container. **Empfehlung:** DockingConfig.setup_docks(mw, sidebar_widget) – Dock-Erstellung ausgelagert, Sidebar-Erstellung bleibt in MainWindow (minimaler Schnitt).
6. `_lock_window_size()` entfernen oder auskommentieren – setFixedSize() deaktivieren.

**Done-Kriterien:**
- [ ] DockingConfig existiert und enthält QDockWidget-Erstellung für Sidebar
- [ ] MainWindow ruft DockingConfig.setup_docks() auf
- [ ] Kein QDockWidget in MainWindow außerhalb von DockingConfig
- [ ] App startet, Chat/Sidebar/CommandCenter/Toolbar funktionieren
- [ ] Fenster ist resizable (setFixedSize entfernt)

**Risiken:**
- DockingConfig könnte Layout brechen → Nach Schritt 3: App starten, prüfen

**Dauer:** 2–3 Tage

---

### Phase 2: Navigation und Routing

**Ziel:** NavRegistry und WorkspaceFactory werden eingeführt. Routing über area_id. **Bestehende Widgets werden unverändert weitergereicht** – keine Migration der Views.

**Zwischenzustand nach Phase 2:**
- `app/gui/navigation/nav_areas.py`, `nav_registry.py`, `sidebar.py` existieren
- **Unverändert:** ChatWidget, CommandCenterView, SidebarWidget – alle bleiben wie sie sind
- NavigationSidebar (neu) zeigt "Chat" und "Kommandozentrale" – Klick ruft MainWindow._on_area_selected(area_id)
- MainWindow._on_area_selected ruft show_chat_view() oder show_command_center() – **Adapter, kein TabbedWorkspace noch**

**Konkrete Schritte:**
1. `app/gui/navigation/` anlegen
2. `nav_areas.py`: `OPERATIONS_CHAT = "operations_chat"`, `COMMAND_CENTER = "command_center"`
3. `nav_registry.py`: Klasse mit register(area_id, factory, title, icon), get_factory(area_id). **Factory für operations_chat:** `lambda: main_window.chat_widget` (MainWindow muss übergeben werden) – oder Factory erhält client, db, orchestrator und erstellt ChatWidget. **Pragmatisch:** Factory ist `lambda: existing_widget` – MainWindow übergibt bei register seine chat_widget- und command_center-Referenzen. Registry speichert Callable, die bei Aufruf das Widget zurückgibt.
4. `sidebar.py`: NavigationSidebarWidget – QListWidget mit "Chat", "Kommandozentrale". itemClicked → area_selected.emit(area_id)
5. MainWindow: NavigationSidebar als zweites Dock links (oberhalb oder unterhalb SidebarWidget) oder in Toolbar integriert. **Einfachste Variante:** Zwei Buttons "Chat" und "Kommandozentrale" in Toolbar durch NavigationSidebar ersetzen – oder NavigationSidebar als schmales Dock links, SidebarWidget darunter. **Empfehlung:** NavigationSidebar als kleines Dock oben links (Bereichsauswahl), SidebarWidget darunter (Chat-Sessions). Oder: Oberer Bereich in SidebarWidget = "Bereiche" (Chat, Kommandozentrale), unterer = Chats/Projekte. **Minimaler Schnitt:** Zunächst nur NavRegistry + WorkspaceFactory. NavigationSidebar kann in Phase 3 kommen. Phase 2: Registry + Factory, MainWindow ruft bei "Kommandozentrale"-Toolbar-Klick show_command_center – aber über WorkspaceFactory.get_factory("command_center")() – noch kein TabbedWorkspace.
6. Bootstrap in main(): Nach MainWindow-Erstellung: `get_nav_registry().register("command_center", lambda: win.command_center, "Kommandozentrale", "info.svg")` und analog für chat.

**Done-Kriterien:**
- [ ] NavRegistry existiert, command_center und operations_chat registriert
- [ ] WorkspaceFactory.create_view(area_id) liefert chat_widget oder command_center
- [ ] NavigationSidebar existiert (oder Toolbar nutzt Registry für Button-Actions)
- [ ] Kein neuer If/Else – area_id → get_factory()() → Widget

**Dauer:** 2–3 Tage

---

### Phase 3: Workspace-Host / TabbedWorkspace

**Ziel:** QStackedWidget wird durch TabbedWorkspace (QTabWidget) ersetzt. Tab pro area_id. WorkspaceFactory liefert Tab-Inhalt.

**Aktivitäten:**
1. **gui/workspace/** anlegen: tabbed_workspace.py, workspace_factory.py, base_workspace_view.py
2. **TabbedWorkspace** implementieren: QTabWidget, show_area(area_id). Fügt Tab hinzu oder wechselt.
3. **MainWindow:** CentralWidget = TabbedWorkspace statt QStackedWidget
4. **Start:** TabbedWorkspace.show_area("operations_chat") als Standard – Chat zuerst
5. **NavigationSidebar** → MainWindow → TabbedWorkspace.show_area(area_id)
6. **Toolbar-Button "Kommandozentrale"** entfernen oder durch Sidebar-Eintrag ersetzen

**Done-Kriterien:**
- [ ] TabbedWorkspace ist CentralWidget
- [ ] Chat und Kommandozentrale erscheinen als Tabs
- [ ] Bereichswechsel über NavigationSidebar funktioniert
- [ ] QStackedWidget entfernt
- [ ] display_project() – ProjectChatList: Entweder als eigener Tab (area_id) oder in Chat-Tab integriert. **Empfehlung:** Projekt-Kontext als Teil von Chat (Sub-View oder Tab innerhalb Chat). area_id: operations_chat mit Kontext project_id.

**Risiken:**
- Tab-Wechsel könnte Verhalten ändern (z.B. Chat-State) – Tab-Inhalt bleibt geladen
- ProjectChatList: Komplexität – vorerst als zusätzlicher Tab "Projekt" mit area_id operations_project?

**Stolpersteine:**
- display_project() fügt dynamisch Widget hinzu – TabbedWorkspace.add_or_show_project_tab(project_id). Siehe Abschnitt 2.3.
- apply_theme(): MainWindow muss alle Tab-Inhalte mit refresh_theme() versorgen. TabbedWorkspace.currentWidget() oder Iteration über alle Tab-Widgets.

**Dauer:** 2–3 Tage

---

### Phase 4: InspectorHost und MonitorHost (leere Hosts)

**Ziel:** InspectorHost und MonitorHost existieren als Docks. Noch leer oder mit Platzhaltern. ChatSidePanel bleibt unverändert. Vorbereitung für spätere Migration.

**Aktivitäten:**
1. **gui/inspector/** anlegen: inspector_host.py
2. **InspectorHost** implementieren: QWidget mit set_context(area_id, obj). Zeigt "Wählen Sie ein Objekt aus." oder Platzhalter.
3. **gui/monitors/** anlegen: monitor_host.py
4. **MonitorHost** implementieren: QTabWidget mit Platzhalter-Tabs (Logs, Events, Metrics, Agent Activity, LLM Trace)
5. **DockingConfig** erweitern: InspectorDock, BottomPanelDock hinzufügen
6. **Layout:** Inspector rechts (optional), Bottom unten (optional). Beide initial einblendbar.

**Done-Kriterien:**
- [ ] InspectorHost und MonitorHost existieren als Docks
- [ ] Beide können ein-/ausgeblendet werden
- [ ] ChatSidePanel bleibt unverändert (Modelle, Prompts, Debug) – keine Migration
- [ ] Keine neuen Monitor-Panels – nur leere Tabs oder Platzhalter

**Risiken:** Gering. Nur neue Docks.

**Dauer:** 1–2 Tage

---

### Phase 5: Pilotmigration Kommandozentrale

**Ziel:** Kommandozentrale wird in Zielstruktur überführt. CommandCenterView wird aufgeteilt: Dashboard- Teil (reine Übersicht) → gui/domains/dashboard/. QA-spezifische Teile → gui/domains/qa_governance/ (vorbereitet, noch nicht vollständig migriert).

**Aktivitäten:**
1. **gui/domains/** anlegen
2. **gui/domains/dashboard/** anlegen: workspace_view.py, panels/command_center_dashboard.py
3. **CommandCenterDashboard** extrahieren: Status-Karten, Quick Actions, System Status aus CommandCenterView. QA-Drilldown, Governance, Operations-Buttons entfernen oder in separate Views auslagern.
4. **CommandCenterScreen** (WorkspaceView): Zeigt nur CommandCenterDashboard. Von BaseWorkspaceView erben.
5. **NavRegistry:** command_center → CommandCenterScreen (neu)
6. **Bestehende CommandCenterView:** QA-Views (QADrilldownView, GovernanceView, etc.) bleiben vorerst in ui/command_center/. CommandCenterScreen importiert nur den Dashboard-Teil oder wird neu erstellt.

**Strategie:** Minimaler Schnitt. CommandCenterView wird nicht komplett umgebaut. Stattdessen: Neuer CommandCenterScreen mit reduziertem Dashboard. QA-Views bleiben in ui/command_center/ und werden über Quick-Action "QA & Governance" verlinkt (→ neuer area_id qa_*). Oder: CommandCenterScreen zeigt Stack mit Dashboard + Link zu QA. **Empfehlung:** Dashboard rein, QA-Buttons führen zu area_id qa_test_inventory oder ähnlich. QA-Bereich wird in Phase 7 migriert.

**Done-Kriterien:**
- [ ] CommandCenterScreen existiert in gui/domains/dashboard/
- [ ] CommandCenterScreen zeigt nur Dashboard (Status, Quick Actions)
- [ ] QA-Bereich ist über Quick Action erreichbar (führt zu area_id, der noch alte UI zeigt)
- [ ] BaseWorkspaceView existiert
- [ ] BaseDashboardPanel existiert (falls verwendet)

**Risiken:**
- QA-Content geht temporär „verloren“ wenn nur Dashboard migriert – Quick Actions müssen zu QA führen
- Bestehende CommandCenterView: Kann als Fallback für QA-Drilldown dienen (area_id qa_drilldown → alte View)

**Dauer:** 3–4 Tage

---

### Phase 6: Operations-Migration (Chat)

**Ziel:** Chat wird in ChatWorkspace überführt. **Inkrementell:** Zunächst ChatWidget als Ganzes in ChatWorkspace einbetten (Adapter). Keine Extraktion von SessionExplorer/ChatEditor in Phase 6.

**Strategie: Adapter vor Extraktion.** ChatWorkspace = QWidget mit QVBoxLayout, enthält **unverändert** ChatWidget als Kind. SidebarWidget bleibt als Dock. Keine Aufteilung von ChatWidget in Phase 6.

**Zwischenzustand nach Phase 6:**
- `app/gui/domains/operations/chat/workspace_view.py` existiert
- ChatWorkspaceView erbt von BaseWorkspaceView, enthält self._chat_widget = ChatWidget(...)
- TabbedWorkspace.show_area("operations_chat") zeigt ChatWorkspaceView
- ChatWorkspaceView erhält client, db, orchestrator, settings, rag_service im Konstruktor – übergibt an ChatWidget
- **SidebarWidget bleibt unverändert** – MainWindow behält sidebar, Verbindungen (new_chat, chat_selected, display_project) bleiben
- **display_project:** ProjectChatListWidget wird in TabbedWorkspace als neuer Tab hinzugefügt (area_id operations_project) oder als Teil von ChatWorkspace. **Empfehlung:** area_id operations_project, Tab "Projekt XY". TabbedWorkspace.addTab(ProjectChatListWidget(...)).

**Konkrete Schritte:**
1. `app/gui/domains/operations/chat/` anlegen
2. `base_workspace_view.py` in gui/workspace/ – falls noch nicht vorhanden
3. `ChatWorkspaceView`: Konstruktor erhält client, db, orchestrator, settings, rag_service. Erstellt ChatWidget(...), setzt als einzigen Inhalt. Layout.addWidget(self._chat_widget)
4. NavRegistry: operations_chat → Factory die ChatWorkspaceView erstellt (mit Dependencies von MainWindow)
5. MainWindow: Bei Erstellung ChatWorkspaceView-Factory mit client, db, orchestrator, settings, rag_service. Oder: MainWindow übergibt self an Factory, Factory holt Dependencies von MainWindow.
6. **display_project:** TabbedWorkspace muss addTab für dynamische Tabs unterstützen. display_project(project_id) → TabbedWorkspace.add_or_show_project_tab(project_id). ProjectChatListWidget braucht parent mit open_chat. **ChatWorkspaceView oder MainWindow** bleibt parent. ProjectChatListWidget(parent=main_window) – parent.open_chat existiert. Tab-Inhalt: ProjectChatListWidget.
7. **SidebarWidget:** Bleibt. Verbindungen zu MainWindow bleiben. new_chat, open_chat, chat_selected – MainWindow delegiert an chat_widget. **Wichtig:** TabbedWorkspace zeigt ChatWorkspaceView, der chat_widget enthält. MainWindow muss chat_widget-Referenz haben für open_chat etc. → ChatWorkspaceView exponierte chat_widget als Property, oder MainWindow holt aus TabbedWorkspace.currentWidget().chat_widget. **Pragmatisch:** MainWindow behält self._current_chat_widget. Bei show_area("operations_chat"): _current_chat_widget = workspace_view.chat_widget. Oder: ChatWorkspaceView registriert sich bei MainWindow als Chat-Provider.

**Done-Kriterien:**
- [ ] ChatWorkspaceView existiert, enthält ChatWidget
- [ ] TabbedWorkspace zeigt Chat bei area operations_chat
- [ ] new_chat, open_chat, save_chat funktionieren (MainWindow delegiert an aktuelles chat_widget)
- [ ] display_project funktioniert (Projekt-Tab)
- [ ] SidebarWidget unverändert, Verbindungen intakt

**Risiken:**
- MainWindow braucht Referenz auf chat_widget für Delegation – ChatWorkspaceView muss sie bereitstellen

**Dauer:** 4–5 Tage

---

### Phase 7: Control Center, QA, Runtime, Settings

**Ziel:** Control Center (Models, Providers, Agents, Tools, Data Stores), QA & Governance, Runtime/Debug, Settings werden migriert. ChatSidePanel wird aufgeteilt.

**Aktivitäten (priorisiert):**

1. **Settings:** SettingsDialog → SettingsScreen. Einfachste Migration (Dialog zu Workspace).
2. **Control Center / Models:** ModelSettingsPanel aus ChatSidePanel extrahieren → ModelsWorkspace. ModelSettingsPanel bleibt funktional, wird in ModelsWorkspace eingebettet.
3. **Control Center / Agents:** AgentManagerDialog → AgentsWorkspace. Agent-Manager-Panel wird als Workspace dargestellt.
4. **Prompt Studio:** PromptManagerPanel aus ChatSidePanel → PromptStudioWorkspace.
5. **Runtime / Debug:** AgentDebugPanel, EventTimelineView etc. → MonitorHost. Monitor-Panels als Tabs.
6. **QA & Governance:** Bestehende CommandCenter QA-Views (QADrilldownView, GovernanceView, etc.) → gui/domains/qa_governance/. TestInventory, CoverageMap, etc.
7. **ChatSidePanel:** Nach Migration von Models, Prompts, Debug: ChatSidePanel wird aufgelöst oder nur noch Inspector/kontextabhängig.

**Reihenfolge innerhalb Phase 7:**
- Settings (1–2 Tage)
- Models (2 Tage)
- Agents (2–3 Tage)
- Prompt Studio (2 Tage)
- Runtime/Monitor (3 Tage)
- QA (4–5 Tage)

**Done-Kriterien:**
- [ ] Alle 6 Hauptbereiche in Zielstruktur
- [ ] ChatSidePanel aufgelöst oder minimal
- [ ] Keine Dialogs für Bereichswechsel (Agent Manager, Settings als Workspace)
- [ ] MonitorHost mit echten Monitor-Panels (Logs, EventBus, Agent Activity, etc.)

**Risiken:**
- QA hat viele Views – schrittweise Migration
- Control Center: Models, Providers, Agents, Tools, Data Stores – einzeln migrieren

**Dauer:** 15–20 Tage (je nach Ressourcen)

---

### Phase 8: Altstruktur-Abbau / Konsolidierung

**Ziel:** app/chat_widget.py, app/sidebar_widget.py, app/ui/command_center/ (Alt), app/ui/sidepanel/ (Alt) werden entfernt oder in gui/ konsolidiert. Keine doppelten Strukturen.

**Aktivitäten:**
1. **Deprecation:** Alle Alt-Imports markieren, auf gui/ umstellen
2. **Löschen:** chat_widget.py, sidebar_widget.py (wenn vollständig ersetzt)
3. **Konsolidierung:** app/ui/ → app/gui/ (Rest umziehen)
4. **main.py:** Import von gui.shell.main_window
5. **Tests:** Alle GUI-Tests anpassen

**Done-Kriterien:**
- [ ] Keine Alt-Struktur mehr im aktiven Pfad
- [ ] app/gui/ ist die einzige GUI-Root
- [ ] Alle Tests grün
- [ ] Dokumentation aktualisiert

**Risiken:**
- Vergessene Referenzen auf Alt-Struktur
- Tests müssen angepasst werden

**Dauer:** 3–5 Tage

---

## 5. Zielzustand je Phase (Zusammenfassung)

| Phase | Architektonischer Zielzustand |
|-------|------------------------------|
| 0 | Ist-Analyse dokumentiert |
| 1 | DockingConfig, LayoutConstants, MainWindow verschlankt |
| 2 | NavRegistry, WorkspaceFactory, NavigationSidebar |
| 3 | TabbedWorkspace, Tab-basierter Bereichswechsel |
| 4 | InspectorHost, MonitorHost als Docks |
| 5 | CommandCenterScreen in gui/domains/dashboard/ |
| 6 | ChatWorkspace in gui/domains/operations/chat/ |
| 7 | Control Center, QA, Runtime, Settings migriert |
| 8 | Altstruktur entfernt, gui/ konsolidiert |

---

## 6. Risiken / Stolpersteine je Phase

| Phase | Risiko | Mitigation |
|-------|--------|------------|
| 1 | Docking bricht | Kleine Schritte, testen nach jeder Änderung |
| 2 | Doppelte Navigation | Klar: NavigationSidebar = Bereiche, SidebarWidget = Chat (temporär) |
| 3 | Tab-Verhalten anders als Stack | Tab-Inhalt bleibt geladen; keine Änderung |
| 4 | Leere Hosts unnötig | Akzeptabel; Vorbereitung für Phase 6/7 |
| 5 | QA-Content geht verloren | Quick Actions zu QA-Drilldown (alte View) |
| 6 | ChatWidget zu komplex | Adapter: ChatWidget als Ganzes in ChatWorkspace einbetten, dann schrittweise extrahieren |
| 7 | Zu viele Bereiche parallel | Einzeln migrieren: Settings → Models → Agents → … |
| 8 | Vergessene Referenzen | Grep nach Alt-Imports, Deprecation-Warnings |

---

## 7. Governance-Regeln für den Umbau

### 7.1 Während der Migration

| Regel | Umsetzung |
|-------|-----------|
| **Keine neuen GUI-Komponenten gegen Zielarchitektur** | Jede neue GUI-Datei muss in gui/ oder als Vorbereitung für gui/ liegen |
| **Kein neues Panel ohne Panel-Typ** | Jedes Panel muss Explorer, Editor, Inspector, Monitor oder Dashboard sein |
| **Kein neues Docking außerhalb DockingConfig** | Kein addDockWidget in Feature-Modulen |
| **Kein neues Routing über If/Else** | Bereichswechsel nur über area_selected → TabbedWorkspace |
| **Pull-Request-Check:** | GUI-Änderungen: Architektur-Review wenn außerhalb gui/ oder gegen Regeln |

### 7.2 Wann darf ein neues Panel entstehen?

- Wenn es einen der 5 Panel-Typen erfüllt
- Wenn es in gui/domains/<domain>/panels/ oder gui/inspector/inspectors/ oder gui/monitors/panels/ liegt
- Wenn es von Base* erbt

### 7.3 Wann muss ein bestehendes Panel erweitert werden?

- Wenn die neue Funktionalität zur gleichen Entität gehört (z.B. SessionExplorer + neue Filter)
- Wenn die Verantwortlichkeit nicht überschritten wird

### 7.4 Refactoring-Pflicht bei Strukturverstößen

- Neues Panel in app/ statt gui/ → Refactoring-Pflicht
- Neue If/Else für Bereichswechsel in MainWindow → Refactoring-Pflicht
- Neue QDockWidget außerhalb DockingConfig → Refactoring-Pflicht

---

## 8. Regeln für Zwischenarchitekturen

### 8.1 Was bleibt unverändert (bis zur jeweiligen Migrationsphase)

| Phase | Unverändert bleibt |
|-------|-------------------|
| 1 | chat_widget, sidebar_widget, command_center, project_chat_list_widget, Signal-Verbindungen, Fachlogik in MainWindow |
| 2 | Wie Phase 1. Zusätzlich: Toolbar-Buttons, show_chat_view, show_command_center |
| 3 | ChatWidget, CommandCenterView, SidebarWidget – nur Container ändert sich (StackedWidget → TabbedWorkspace) |
| 4 | Wie Phase 3. ChatSidePanel unverändert |
| 5 | ChatWidget, SidebarWidget, CommandCenterView (QA-Teile). Nur Dashboard wird neu erstellt |
| 6 | ChatWidget-Inhalt (ConversationView, Composer, Header, ChatSidePanel). ChatWidget wird als Ganzes in ChatWorkspace eingebettet |
| 7 | Erst hier: ChatSidePanel-Aufteilung, AgentManagerDialog → Workspace |
| 8 | Nichts – Altstruktur wird entfernt |

### 8.2 Parallelbetrieb Alt- und Neustruktur

| Regel | Beschreibung |
|-------|--------------|
| **Klare Grenze** | Alt: app/chat_widget, app/sidebar_widget, app/ui/. Neu: app/gui/ |
| **Adapter statt Neuschnitt** | Bestehende Widgets werden als Tab-Inhalt eingebettet. Kein Neubau von ChatWidget in Phase 6 |
| **Keine Vermischung** | Alt-Struktur importiert nicht gui/ (außer für Adapter). gui/ importiert Alt (ChatWidget, CommandCenterView) als Tab-Inhalt |
| **Exit-Plan** | Phase 6: SidebarWidget bleibt. Phase 8: SidebarWidget entfernt, wenn SessionExplorer in ChatWorkspace integriert |

### 8.3 Konkrete Zwischenzustände (Dateien pro Phase)

| Phase | Neue Dateien | Geänderte Dateien | Gelöschte Dateien |
|-------|--------------|-------------------|-------------------|
| 1 | gui/shell/docking_config.py, layout_constants.py | main.py | — |
| 2 | gui/navigation/nav_areas.py, nav_registry.py, sidebar.py | main.py | — |
| 3 | gui/workspace/tabbed_workspace.py, workspace_factory.py | main.py | — |
| 4 | gui/inspector/inspector_host.py, gui/monitors/monitor_host.py | main.py, docking_config.py | — |
| 5 | gui/domains/dashboard/workspace_view.py, command_center_dashboard.py | main.py, nav_registry | — |
| 6 | gui/domains/operations/chat/workspace_view.py | main.py, nav_registry, tabbed_workspace | — |
| 7 | gui/domains/control_center/*, qa_governance/*, runtime_debug/*, settings/* | diverse | — |
| 8 | — | main.py, imports | chat_widget.py, sidebar_widget.py (wenn ersetzt) |

### 8.4 Abbruchkriterien pro Phase

| Phase | Abbruch wenn |
|-------|--------------|
| 1 | Docking bricht irreparabel; MainWindow wird instabil |
| 2 | NavRegistry führt zu zirkulären Imports |
| 3 | TabbedWorkspace verursacht Speicher- oder State-Probleme |
| 5 | CommandCenterScreen kann nicht ohne QA-Verlust erstellt werden |
| 6 | Chat-Migration bricht Kernfunktionalität |
| 7 | Ein Bereich blockiert zu lange – Bereich überspringen, später nachholen |
| 8 | Tests brechen dauerhaft – Alt-Struktur temporär zurück |

---

## 9. Pilotbereich-Empfehlungen

### 9.1 Pilot: Kommandozentrale

**Begründung:**
- Relativ isoliert (keine komplexen Abhängigkeiten wie Chat)
- QA-Adapter (QADashboardAdapter) existiert bereits
- Weniger Nutzer-Interaktion als Chat
- Dashboard-Struktur (Karten, Quick Actions) ist überschaubar
- QA-spezifische Teile können ausgelagert werden

**Nicht als Pilot:** Chat (zu komplex), Control Center (zu viele Unterbereiche), QA (zu viele Views)

### 9.2 Spätere Migration (nach Pilot)

| Bereich | Reihenfolge | Begründung |
|---------|-------------|------------|
| **Settings** | Zuerst in Phase 7 | Einfach, Dialog → Workspace |
| **Models** | Danach | ModelSettingsPanel aus ChatSidePanel extrahierbar |
| **Agents** | Danach | AgentManagerDialog → Workspace |
| **Prompt Studio** | Danach | PromptManagerPanel extrahierbar |
| **Runtime/Monitor** | Danach | AgentDebugPanel etc. → MonitorHost |
| **QA** | Zuletzt | Viele Views, komplexe Struktur |

---

## 10. Abschluss-Empfehlung für die konkrete Umsetzung

### 10.1 Erste Schritte (sofort)

1. **Phase 0 abschließen:** Ist-Analyse-Matrix finalisieren (dieses Dokument)
2. **Phase 1 starten:** gui/shell/ anlegen, DockingConfig extrahieren
3. **Governance:** PR-Checkliste für GUI-Änderungen einführen

### 10.2 Entscheidungen

| Entscheidung | Empfehlung |
|--------------|------------|
| **Shell zuerst** | Ja. Ohne stabile Shell keine Feature-Migration. |
| **Pilot Kommandozentrale** | Ja. Isoliert, überschaubar. |
| **ChatSidePanel** | Phase 6: Unverändert. Phase 7: Aufteilung. |
| **Adapter für bestehende Widgets** | Ja. ChatWidget, CommandCenterView als Tab-Inhalt bis Migration. |
| **NavigationSidebar parallel zu SidebarWidget** | Ja, temporär. SidebarWidget bleibt für Chat-Sessions bis Phase 6. |
| **Fensterfixierung** | Phase 1 entfernen. |

### 10.3 Zeitplan (Grobraster)

| Phase | Dauer | Kumuliert |
|-------|-------|------------|
| 0 | 1–2 Tage | 2 Tage |
| 1 | 2–3 Tage | 5 Tage |
| 2 | 3–4 Tage | 9 Tage |
| 3 | 2–3 Tage | 12 Tage |
| 4 | 1–2 Tage | 14 Tage |
| 5 | 3–4 Tage | 18 Tage |
| 6 | 5–7 Tage | 25 Tage |
| 7 | 15–20 Tage | 45 Tage |
| 8 | 3–5 Tage | 50 Tage |

**Gesamt:** ca. 8–10 Wochen bei Vollzeit. Bei Teilzeit oder parallelen Aufgaben entsprechend länger.

### 10.4 Erfolgskriterien

- [ ] App läuft nach jeder Phase
- [ ] Alle bestehenden Tests grün (oder angepasst)
- [ ] Keine neuen Architekturverstöße
- [ ] Altstruktur nach Phase 8 entfernt
- [ ] Dokumentation (UX, GUI-Repo, Screen-Architektur) aktuell

### 10.5 Nächster konkreter Schritt (Sofort umsetzbar)

**Phase 0 abschließen:** Ist-Analyse prüfen (Abschnitt 0.2–0.4 dieses Dokuments). Abhängigkeitsgraph mit `rg "from app\.|import app\." app/` verifizieren.

**Phase 1 starten:**
1. `mkdir -p app/gui/shell`
2. `touch app/gui/shell/__init__.py`
3. `app/gui/shell/layout_constants.py` anlegen mit NAV_SIDEBAR_WIDTH=220
4. `app/gui/shell/docking_config.py` anlegen: `setup_sidebar_dock(main_window) -> (dock, sidebar)`. Erstellt QDockWidget, SidebarWidget(main_window.db), setzt Dock-Features, main_window.addDockWidget(Left, dock). Gibt (dock, sidebar) zurück.
5. In main.py `init_sidebar()`: `self.sidebar_dock, self.sidebar = setup_sidebar_dock(self)` – danach die Signal-Verbindungen (new_chat_clicked, chat_selected, file_added_to_chat, …) wie bisher.
6. App starten, prüfen (Chat, Sidebar, Kommandozentrale, Toolbar)
7. `_lock_window_size()` entfernen oder `setFixedSize` auskommentieren

**Wichtig:** Nach jedem Schritt: `python -m app.main` (oder der tatsächliche Startbefehl) ausführen. App muss starten und Chat/Sidebar/Kommandozentrale müssen funktionieren.

---

*Diese Roadmap ist verbindliche Grundlage für die GUI-Migration. Abweichungen bedürfen einer Architektur-Review.*

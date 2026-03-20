# GUI-Architektur-Guardrails – Linux Desktop Chat

**Version:** 1.0  
**Datum:** 2026-03-15  
**Referenz:** docs/GUI_REPOSITORY_ARCHITECTURE.md, docs/SCREEN_CLASS_ARCHITECTURE.md, docs/GUI_MIGRATION_ROADMAP.md  
**Status:** Verbindliche Review-Regeln für Pull Requests und GUI-Entwicklung

---

## 0. Einleitung

Diese Guardrails sind **verbindliche Architektur-Regeln** für die PySide6-GUI. Sie dienen als Review-Kriterien für Pull Requests, Refactorings und neue Features. Abweichungen bedürfen einer dokumentierten Architektur-Review.

**Anwendungsbereich:** Alle Änderungen an `app/gui/`, `app/main.py`, `app/ui/` sowie neue GUI-Module.

---

## A. Verbindliche GUI-Guardrails (nummeriert)

### 1. Shell-Verantwortlichkeit

#### G-1.1: Docking ausschließlich in DockingConfig

**Zweck:** Einziger Ort für QDockWidget-Konfiguration. Verhindert verstreute Layout-Logik.

**Begründung:** Ohne zentrale Docking-Logik entstehen inkonsistente Docks, Layout-Konflikte und unklare Verantwortung.

**Typischer Verstoß:** `main_window.addDockWidget(...)` in einem Domain-Modul; neues QDockWidget in `chat_widget.py`.

**Review-Verhalten:** **Blocker.** Alle `addDockWidget`, `QDockWidget`, `setAllowedAreas`, `setFeatures` müssen in `gui/shell/docking_config.py` stehen. Ausnahme: QSplitter innerhalb eines Panel-Layouts (nicht App-Docking).

---

#### G-1.2: MainWindow ohne Fachlogik

**Zweck:** MainWindow ist nur Rahmen, Docking, Routing, Signal-Vermittlung. Keine Fachlogik.

**Begründung:** God-Object MainWindow verhindert testbare, wartbare Domain-Migration.

**Typischer Verstoß:** `add_file_to_current_chat`, `save_chat`, `_on_agent_selected_for_chat` direkt in MainWindow; Datenbankzugriff, API-Calls in MainWindow.

**Review-Verhalten:** **Blocker** bei neuer Fachlogik. Bestehende: **Refactoring-Schuld** markieren, Ticket anlegen.

---

#### G-1.3: Keine If/Else-Ketten für Bereichswechsel in MainWindow

**Zweck:** Bereichswechsel ausschließlich über area_id → NavRegistry → WorkspaceFactory.

**Begründung:** If/Else-Ketten skalieren nicht, führen zu zirkulären Abhängigkeiten und blockieren neue Bereiche.

**Typischer Verstoß:** `if area_id == "chat": self.show_chat_view(); elif area_id == "command_center": ...` in MainWindow.

**Review-Verhalten:** **Blocker.** MainWindow darf nur `TabbedWorkspace.show_area(area_id)` oder `WorkspaceFactory.create_view(area_id)` aufrufen.

---

### 2. Navigation-Verantwortlichkeit

#### G-2.1: Navigation emittiert nur area_id

**Zweck:** NavigationSidebar kennt keine Workspace-Inhalte, keine Fachtypen, keine Objekte.

**Begründung:** Navigation als Routing-Layer muss von Domains entkoppelt werden. Sonst: zirkuläre Imports, Feature-Kopplung.

**Typischer Verstoß:** `area_selected.emit(chat_widget)`; `area_selected.emit(chat_id)`; Navigation importiert `ChatWorkspaceView`.

**Review-Verhalten:** **Blocker.** Signal `area_selected(str)` – nur area_id. Keine Domain-Imports in `gui/navigation/`.

---

#### G-2.2: Keine Fachlogik in Navigation

**Zweck:** Navigation enthält keine Chat-, QA-, Agent- oder sonstige Fachlogik.

**Begründung:** Navigation ist Framework-Layer. Fachlogik gehört in Domains.

**Typischer Verstoß:** `if area_id == "operations_chat": self.db.get_chats()`; Navigation ruft RAGService auf.

**Review-Verhalten:** **Blocker.** Kein `app.db`, `app.rag`, `app.agents`, `app.qa` in `gui/navigation/`.

---

### 3. Screen-Verantwortlichkeit

#### G-3.1: Screen = Koordinator, kein Monolith

**Zweck:** WorkspaceView erstellt Layout, delegiert an Panels. Keine Monolithen mit 10+ Panels.

**Begründung:** Große Screen-Klassen sind unwartbar, testbar nur mit großen Fixtures.

**Typischer Verstoß:** ChatWorkspace mit 800+ Zeilen, direkt ConversationView + Composer + Settings + Debug inline.

**Review-Verhalten:** **Refactoring-Schuld** bei >400 Zeilen. Max. 3–4 Panels pro Screen. Logik in Panels auslagern.

---

#### G-3.2: Screen kennt keine anderen Screens

**Zweck:** Keine Cross-Screen-Abhängigkeiten. Kein Screen ruft einen anderen Screen direkt auf.

**Begründung:** Vermeidet zirkuläre Abhängigkeiten und Feature-Kopplung.

**Typischer Verstoß:** `ChatWorkspace` ruft `CommandCenterScreen` auf; `SettingsScreen` importiert `ChatWorkspaceView`.

**Review-Verhalten:** **Blocker.** Bereichswechsel nur über area_selected → TabbedWorkspace. Kein direkter Import von WorkspaceView in anderer WorkspaceView.

---

#### G-3.3: Screen erbt von BaseWorkspaceView

**Zweck:** Einheitliche Schnittstelle: area_id, refresh(), refresh_theme().

**Begründung:** Ermöglicht TabbedWorkspace, apply_theme und zentrale Lifecycle-Behandlung.

**Typischer Verstoß:** Neuer Screen als QWidget ohne BaseWorkspaceView; keine refresh_theme().

**Review-Verhalten:** **Blocker** bei neuem Screen. Bestehende Screen-Migration: BaseWorkspaceView als Teil der Migration.

---

### 4. Workspace-Verantwortlichkeit

#### G-4.1: Ein TabbedWorkspace, ein zentraler Host

**Zweck:** Einziger Workspace-Host. Keine Domain mit eigenem TabbedWorkspace als Main-Container.

**Begründung:** TabbedWorkspace ist CentralWidget. Domains liefern nur View-Inhalt.

**Typischer Verstoß:** `OperationsWorkspace` mit eigenem QTabWidget für Chat, Agent Tasks, Knowledge – statt je eigener Tab im TabbedWorkspace.

**Review-Verhalten:** **Blocker.** Ausnahme: RuntimeWorkspace mit interner Tab-Gruppierung (Monitor-Panels) – dokumentiert, kein zweiter Main-Container.

---

#### G-4.2: WorkspaceFactory nutzt ausschließlich NavRegistry

**Zweck:** create_view(area_id) → NavRegistry.get_factory(area_id)() – keine Switch-Cases.

**Begründung:** Registry-basiertes Routing skaliert, erlaubt Lazy Loading, neue Bereiche ohne MainWindow-Änderung.

**Typischer Verstoß:** `if area_id == "chat": return ChatWidget(); elif area_id == "command_center": ...` in WorkspaceFactory.

**Review-Verhalten:** **Blocker.** WorkspaceFactory enthält nur Registry-Aufruf, keine If/Else.

---

### 5. Panel-Verantwortlichkeit

#### G-5.1: Jedes Panel erbt von Base*

**Zweck:** Explorer, Editor, Inspector, Monitor, Dashboard – jeweils von BaseExplorerPanel, BaseEditorPanel, BaseInspectorPanel, BaseMonitorPanel, BaseDashboardPanel.

**Begründung:** Einheitliche Schnittstellen, gemeinsame Logik (Refresh, Theme), klare Typisierung.

**Typischer Verstoß:** Neues QWidget-Panel ohne Base-Klasse; "schnelles" Panel als QFrame direkt.

**Review-Verhalten:** **Blocker** bei neuem Panel. Keine Ausnahmen ohne Architektur-Review.

---

#### G-5.2: Panel = eine Entität, eine Verantwortung

**Zweck:** Panel hat einen klar begrenzten Kontext. Kein Panel mit 5 Verantwortlichkeiten.

**Begründung:** Panel-Wildwuchs entsteht durch "noch schnell was hinzufügen". Klare Grenzen verhindern Monolithen.

**Typischer Verstoß:** `ChatSidePanel` mit Modelle + Prompts + Debug + Agent-Auswahl + Settings.

**Review-Verhalten:** **Refactoring-Schuld** bei Panel mit >3 Verantwortlichkeiten. Aufteilung in separate Panels vorschlagen.

---

#### G-5.3: Domain-Panels in gui/domains/<domain>/panels/

**Zweck:** Explorer, Editor, Dashboard liegen in der Domain, die den Kontext besitzt.

**Begründung:** Klare Verantwortlichkeit. Keine zentrale "explorer/"-Sammlung.

**Typischer Verstoß:** `SessionExplorerPanel` in `gui/panels/explorer/`; neues Panel in `app/` root.

**Review-Verhalten:** **Blocker** bei falschem Ort. Pfad: `gui/domains/<domain>/panels/<name>_<typ>.py`.

---

### 6. Inspector-Verantwortlichkeit

#### G-6.1: Inspector-Panels ausschließlich in gui/inspector/inspectors/

**Zweck:** Alle Inspector-Panels zentral. Keine Inspector-Panels in Domains.

**Begründung:** InspectorHost lädt per area_id aus Registry. Einheitlicher Ort, keine Verstreuung.

**Typischer Verstoß:** `SessionInspector` in `gui/domains/operations/chat/panels/`; `AgentInspector` in `gui/domains/control_center/agents/`.

**Review-Verhalten:** **Blocker.** Inspector-Panels nur in `gui/inspector/inspectors/`. In InspectorRegistry registrieren.

---

#### G-6.2: Inspector = Read-only, keine Bearbeitung

**Zweck:** Inspector zeigt Metadaten. Keine Bearbeitung (außer explizit vorgesehen).

**Begründung:** Inspector ist Kontext-Anzeige. Bearbeitung gehört in Editor-Panel.

**Typischer Verstoß:** `SessionInspector` mit Save-Button; Inspector ruft `db.update()` auf.

**Review-Verhalten:** **Refactoring-Schuld.** Bearbeitung in Editor auslagern. Inspector nur set_object(), clear().

---

### 7. Bottom-Monitor-Verantwortlichkeit

#### G-7.1: Monitor-Panels ausschließlich in gui/monitors/panels/

**Zweck:** Alle Monitor-Panels zentral. Keine Monitor-Panels in Domains.

**Begründung:** MonitorHost und RuntimeWorkspace nutzen dieselben Panels. Eine Implementierung, zwei Hosts.

**Typischer Verstoß:** `LogsMonitor` in `gui/domains/runtime_debug/`; `AgentActivityMonitor` in `gui/domains/operations/chat/`.

**Review-Verhalten:** **Blocker.** Monitor-Panels nur in `gui/monitors/panels/`. Von BaseMonitorPanel erben.

---

#### G-7.2: Monitor = Live-Stream, keine Persistenz

**Zweck:** Monitor zeigt Live-Daten. Keine persistente Speicherung der Daten.

**Begründung:** Monitor ist für Runtime-Sicht. Persistenz gehört in Services/Adapter.

**Typischer Verstoß:** `EventBusMonitor` speichert Events in DB; Monitor hat "Export to DB"-Button mit persistierender Logik.

**Review-Verhalten:** **Refactoring-Schuld.** Export optional, aber keine Persistenz im Panel. start(), pause(), clear(), refresh().

---

### 8. Routing / Screen Registry

#### G-8.1: NavRegistry als einzige Routing-Quelle

**Zweck:** Alle Screens registrieren sich in NavRegistry. Keine parallele Routing-Tabelle.

**Begründung:** Single Source of Truth. Neue Bereiche ohne MainWindow-Änderung.

**Typischer Verstoß:** Eigene `area_to_workspace`-Dict in MainWindow; Routing in Config-Datei ohne Registry.

**Review-Verhalten:** **Blocker.** Routing nur über NavRegistry. Keine parallele Routing-Logik.

---

#### G-8.2: area_id in snake_case, lowercase

**Zweck:** Einheitliche area_id: `operations_chat`, `command_center`, `qa_test_inventory`.

**Begründung:** Vermeidet Tippfehler, Case-Sensitivity-Probleme.

**Typischer Verstoß:** `OperationsChat`, `command-center`, `QA_Test_Inventory`.

**Review-Verhalten:** **Blocker** bei neuer area_id. Muster: `[bereich]_[subbereich]`, snake_case.

---

### 9. Naming / Modulstruktur

#### G-9.1: Dateinamen nach Typ

**Zweck:** workspace_view.py, *_explorer.py, *_editor.py, *_inspector.py, *_monitor.py, *_dashboard.py.

**Begründung:** Erkennbarkeit, Konvention, Tooling.

**Typischer Verstoß:** `chat_view.py` statt `workspace_view.py`; `session_list.py` statt `session_explorer.py`.

**Review-Verhalten:** **Refactoring-Schuld** bei Abweichung. Bei neuem Modul: **Blocker.**

---

#### G-9.2: Klassennamen nach Muster

**Zweck:** `<Entity>Explorer`, `<Entity>Editor`, `<Entity>Inspector`, `<Source>Monitor`, `<Context>Dashboard`, `<Domain>WorkspaceView`.

**Begründung:** Konsistente Namensgebung, schnelle Zuordnung.

**Typischer Verstoß:** `ChatListWidget` statt `SessionExplorerPanel`; `DebugView` statt `AgentActivityMonitor`.

**Review-Verhalten:** **Refactoring-Schuld** bei Abweichung. Bei neuer Klasse: Namenskonvention prüfen.

---

#### G-9.3: Domain-Pfade: snake_case

**Zweck:** `operations`, `control_center`, `qa_governance`, `runtime_debug`, `settings`.

**Begründung:** Keine CamelCase in Pfaden. Python-Konvention.

**Typischer Verstoß:** `ControlCenter/`, `QAGovernance/`.

**Review-Verhalten:** **Blocker** bei neuem Domain-Pfad.

---

### 10. Erweiterungsregeln für neue Screens

#### G-10.1: Neuer Screen nur bei UX-Begründung

**Zweck:** Neuer Screen = neuer Tab. Kein Screen "weil es gerade passt".

**Begründung:** Maximal 6 Hauptbereiche. Jeder Screen = Nutzer-Kontext. Vermeidet Screen-Wildwuchs.

**Typischer Verstoß:** Neuer Screen "Export" statt Erweiterung von Settings; neuer Screen "Quick Actions" statt Teil von Dashboard.

**Review-Verhalten:** **Blocker** bei neuem Screen ohne UX-Begründung. Frage: Gehört zu bestehendem Screen? Unterbereich?

---

#### G-10.2: Registrierung in NavRegistry

**Zweck:** Jeder Screen registriert sich bei App-Start. NavArea + NavRegistry erweitern.

**Begründung:** Ohne Registrierung ist Screen nicht erreichbar. Kein implizites Routing.

**Typischer Verstoß:** Neuer Screen ohne NavRegistry.register; Screen nur über direkten Aufruf erreichbar.

**Review-Verhalten:** **Blocker.** Neuer Screen muss in NavRegistry registriert sein.

---

### 11. Erweiterungsregeln für neue Panels

#### G-11.1: Wann neues Panel?

**Erlaubt:** Neue Entität (z.B. neuer Explorer-Typ); neue Verantwortung, die nicht zu bestehendem Panel passt; neuer Monitor-Typ; neuer Inspector-Typ für Kontext.

**Nicht erlaubt:** "Schnell was hinzufügen" in bestehendes Panel; Panel ohne Base-Klasse; Panel ohne klaren Typ (Explorer/Editor/Inspector/Monitor/Dashboard).

**Typischer Verstoß:** Neues QWidget-Panel für "Filter" statt Erweiterung von SearchableList; Panel ohne Base-Klasse.

**Review-Verhalten:** **Blocker** bei Panel ohne Base-Klasse. **Refactoring-Schuld** bei Panel, das bestehendes Panel hätte erweitern sollen.

---

#### G-11.2: Wann bestehendes Panel erweitern?

**Erforderlich:** Neue Funktionalität gehört zur gleichen Entität (z.B. SessionExplorer + neue Filter); Verantwortung wird nicht überschritten.

**Nicht erweitern:** Neue Entität (z.B. SessionExplorer + TaskExplorer); neue Verantwortung (z.B. Explorer + Editor vermischt).

**Typischer Verstoß:** Neues Panel für "Task-Suche" obwohl TaskExplorer um Filter erweitert werden könnte.

**Review-Verhalten:** Frage: "Gehört zu bestehender Entität?" Ja → Erweitern. Nein → Neues Panel.

---

### 12. Verbote für Fachlogik in falschen Schichten

#### G-12.1: Shell/Navigation/Workspace: Keine Domain-Imports

**Zweck:** gui/shell/, gui/navigation/, gui/workspace/ importieren keine gui/domains/.

**Begründung:** Framework-Layer darf nicht von Domains abhängen. Lazy Loading über Registry.

**Typischer Verstoß:** `from app.gui.domains.operations.chat import ChatWorkspaceView` in main_window.py.

**Review-Verhalten:** **Blocker.** Kein `from app.gui.domains` in shell/, navigation/, workspace/.

---

#### G-12.2: Domain A importiert nicht Domain B

**Zweck:** Keine Cross-Domain-Imports in gui/domains/.

**Begründung:** Domains sind unabhängig. Vermeidet Feature-Kopplung.

**Typischer Verstoß:** `from app.gui.domains.qa_governance import TestInventoryWorkspace` in operations/chat/.

**Review-Verhalten:** **Blocker.** Kein Cross-Domain-Import. Bereichswechsel über area_selected.

---

#### G-12.3: Components: Keine Fachlogik

**Zweck:** gui/components/ enthält keine Domain-Imports, keine app.agents, app.rag, app.qa.

**Begründung:** Components sind wiederverwendbar, fachlogikfrei.

**Typischer Verstoß:** StatusCard importiert RAGService; EmptyStateWidget hat Chat-spezifische Texte.

**Review-Verhalten:** **Blocker** bei Fachlogik in components/. Nur PySide6, resources/styles.

---

### 13. Regeln gegen parallele Sonderarchitekturen

#### G-13.1: Keine GUI-Dateien außerhalb app/gui/ (nach Migration)

**Zweck:** app/gui/ ist die einzige GUI-Root. Keine neuen GUI-Module in app/ root oder app/ui/ (Alt).

**Begründung:** Nach Migration: Altstruktur entfernt. Neue Dateien in Zielstruktur.

**Typischer Verstoß:** Neues Panel in `app/`; neues Modul in `app/ui/` statt `app/gui/`.

**Review-Verhalten:** **Blocker** bei neuem GUI-Modul außerhalb gui/. Während Migration: Hinweis auf Zielstruktur.

---

#### G-13.2: Kein Dialog für komplexen Workflow

**Zweck:** Komplexe Workflows = eigener Workspace-Bereich. Kein QDialog mit 5 Tabs.

**Begründung:** Dialoge blockieren, sind nicht tab-fähig, vermischen mit Main-Window-Kontext.

**Typischer Verstoß:** Agent Manager als Dialog mit 500 Zeilen; Settings als Dialog mit 10 Sektionen.

**Review-Verhalten:** **Refactoring-Schuld** bei Dialog >200 Zeilen. Vorschlag: Workspace-Bereich.

---

#### G-13.3: Nur 5 Panel-Typen

**Zweck:** Explorer, Editor, Inspector, Monitor, Dashboard. Keine neuen Typen ohne Architektur-Review.

**Begründung:** Begrenzte Typen = klare Kategorisierung. Kein "HybridPanel" oder "UtilityPanel".

**Typischer Verstoß:** Neuer Typ "ContextPanel"; "ActionPanel" statt Editor.

**Review-Verhalten:** **Blocker** bei neuem Panel-Typ ohne Review. Einordnung in einen der 5 Typen verlangen.

---

### 14. Regeln für Review und PR-Freigabe

#### G-14.1: GUI-Änderungen: Architektur-Check

**Zweck:** PRs mit GUI-Änderungen müssen gegen Guardrails geprüft werden.

**Begründung:** Architektur-Verstöße summieren sich. Früh stoppen.

**Review-Verhalten:** Bei PR mit Änderungen in app/gui/, app/main.py, app/ui/: Guardrail-Checkliste durchgehen.

---

#### G-14.2: Blocker = Kein Merge ohne Behebung

**Zweck:** Verstöße gegen G-1.1, G-1.2, G-1.3, G-2.1, G-2.2, G-3.2, G-3.3, G-4.1, G-4.2, G-5.1, G-5.3, G-6.1, G-7.1, G-8.1, G-8.2, G-9.3, G-10.1, G-10.2, G-11.1, G-12.1, G-12.2, G-12.3, G-13.1, G-13.3 blockieren Merge.

**Review-Verhalten:** Explizit "Blocker" markieren. PR nicht mergen bis behoben. Keine Ausnahme ohne Architektur-Review.

---

#### G-14.3: Refactoring-Schuld = Ticket, Merge möglich

**Zweck:** Weiche Verstöße werden dokumentiert, Ticket angelegt. Merge kann erfolgen, wenn funktional korrekt.

**Begründung:** Nicht jeder PR kann alles refactoren. Schuld dokumentieren, Rückbau planen.

**Review-Verhalten:** "Refactoring-Schuld" in Kommentar. Ticket mit Referenz auf PR. In Backlog.

---

### 15. Regeln für Rückbau veralteter GUI-Strukturen

#### G-15.1: Alt-Imports markieren, nicht still ersetzen

**Zweck:** Bei Migration: Alt-Import mit Deprecation-Warning oder Kommentar. Kein stiller Wechsel ohne Prüfung.

**Begründung:** Vergessene Referenzen führen zu versteckten Fehlern. Explizite Markierung.

**Typischer Verstoß:** Import von `app.chat_widget` still auf `app.gui.domains.operations.chat` umgestellt, ohne alle Aufrufer zu prüfen.

**Review-Verhalten:** Deprecation-Warning oder TODO mit Ticket. Migration schrittweise.

---

#### G-15.2: Keine doppelten Strukturen dauerhaft

**Zweck:** Alt- und Neustruktur nicht parallel als Dauerzustand. Jede Phase hat Exit-Plan.

**Begründung:** Doppelte Strukturen verursachen Verwirrung, doppelte Wartung.

**Typischer Verstoß:** `app/chat_widget.py` und `gui/domains/operations/chat/` parallel dauerhaft; beide aktiv im Pfad.

**Review-Verhalten:** **Blocker** bei PR, der doppelte Struktur als Dauerlösung etabliert. Exit-Plan verlangen.

---

#### G-15.3: Altstruktur entfernen nur nach vollständiger Migration

**Zweck:** app/chat_widget.py, app/sidebar_widget.py etc. erst löschen, wenn vollständig ersetzt.

**Begründung:** Vorzeitiges Löschen bricht Referenzen. Kein Big-Bang-Delete.

**Typischer Verstoß:** chat_widget.py gelöscht, obwohl ChatWorkspaceView noch ChatWidget importiert. Oder: Grep zeigt noch 10 Referenzen.

**Review-Verhalten:** Vor Löschen: `rg "chat_widget|sidebar_widget" app/` – 0 Treffer in aktivem Pfad. Tests grün.

---

## B. Harte Blocker im Review

Die folgenden Verstöße führen zu **keinem Merge** ohne Behebung:

| # | Verstoß | Regel |
|---|---------|-------|
| B1 | QDockWidget/addDockWidget außerhalb DockingConfig | G-1.1 |
| B2 | Fachlogik (Chat, QA, Agents, DB, API) in MainWindow | G-1.2 |
| B3 | If/Else für Bereichswechsel in MainWindow | G-1.3 |
| B4 | Navigation emittiert nicht area_id (String) | G-2.1 |
| B5 | Fachlogik in Navigation | G-2.2 |
| B6 | Screen kennt/ruft anderen Screen | G-3.2 |
| B7 | Neuer Screen ohne BaseWorkspaceView | G-3.3 |
| B8 | Eigener TabbedWorkspace als Main-Container in Domain | G-4.1 |
| B9 | If/Else in WorkspaceFactory statt Registry | G-4.2 |
| B10 | Neues Panel ohne Base-Klasse | G-5.1 |
| B11 | Domain-Panel außerhalb gui/domains/<domain>/panels/ | G-5.3 |
| B12 | Inspector-Panel außerhalb gui/inspector/inspectors/ | G-6.1 |
| B13 | Monitor-Panel außerhalb gui/monitors/panels/ | G-7.1 |
| B14 | Routing außerhalb NavRegistry | G-8.1 |
| B15 | area_id nicht snake_case, lowercase | G-8.2 |
| B16 | Domain-Pfad nicht snake_case | G-9.3 |
| B17 | Neuer Screen ohne UX-Begründung | G-10.1 |
| B18 | Neuer Screen nicht in NavRegistry | G-10.2 |
| B19 | Neues Panel ohne Base-Klasse | G-11.1 |
| B20 | Domain-Import in shell/navigation/workspace | G-12.1 |
| B21 | Cross-Domain-Import in gui/domains | G-12.2 |
| B22 | Fachlogik in gui/components | G-12.3 |
| B23 | Neues GUI-Modul außerhalb app/gui/ (nach Migration) | G-13.1 |
| B24 | Neuer Panel-Typ ohne Architektur-Review | G-13.3 |
| B25 | Doppelte Struktur als Dauerlösung | G-15.2 |

---

## C. Weiche Verstöße / Refactoring-Schulden

Die folgenden Verstöße werden dokumentiert, blockieren Merge aber nicht zwingend. Ticket anlegen.

| # | Verstoß | Regel | Empfehlung |
|---|---------|-------|------------|
| S1 | Screen >400 Zeilen | G-3.1 | Aufteilen in Panels |
| S2 | Panel mit >3 Verantwortlichkeiten | G-5.2 | Aufteilen |
| S3 | Inspector mit Bearbeitung | G-6.2 | Bearbeitung in Editor |
| S4 | Monitor mit Persistenz | G-7.2 | Persistenz in Service |
| S5 | Dateiname nicht nach Typ | G-9.1 | Umbenennen bei nächster Änderung |
| S6 | Klassenname nicht nach Muster | G-9.2 | Umbenennen bei nächster Änderung |
| S7 | Bestehendes Panel hätte erweitert werden sollen | G-11.2 | Refactoring-Ticket |
| S8 | Dialog >200 Zeilen für komplexen Workflow | G-13.2 | Migration zu Workspace planen |

---

## D. PR-Checkliste für GUI-Änderungen

Vor Merge eines PRs mit GUI-Änderungen:

### D.1 Pflicht-Check (Blocker)

- [ ] Kein QDockWidget/addDockWidget außerhalb DockingConfig
- [ ] Keine neue Fachlogik in MainWindow
- [ ] Kein If/Else für Bereichswechsel in MainWindow
- [ ] Navigation emittiert nur area_id (String)
- [ ] Keine Domain-Imports in shell/navigation/workspace
- [ ] Keine Cross-Domain-Imports in gui/domains
- [ ] Neuer Screen: BaseWorkspaceView, NavRegistry
- [ ] Neues Panel: Base-Klasse, korrekter Pfad (domains/panels/ oder inspector/inspectors/ oder monitors/panels/)
- [ ] area_id in snake_case, lowercase
- [ ] Kein neues GUI-Modul außerhalb app/gui/ (nach Migration)

### D.2 Empfohlener Check (Refactoring-Schuld)

- [ ] Screen <400 Zeilen
- [ ] Panel mit ≤3 Verantwortlichkeiten
- [ ] Inspector read-only
- [ ] Monitor ohne Persistenz
- [ ] Dateinamen und Klassennamen nach Konvention
- [ ] Kein Dialog >200 Zeilen für komplexen Workflow

### D.3 Funktionale Check

- [ ] App startet
- [ ] Betroffene Bereiche funktionieren
- [ ] Bestehende Tests grün (oder angepasst)
- [ ] Keine neuen Linter-Fehler

---

## E. Antworten auf zentrale Fragen

### Wann darf ein neues Panel eingeführt werden?

- Wenn es einen der 5 Panel-Typen erfüllt (Explorer, Editor, Inspector, Monitor, Dashboard)
- Wenn es eine neue Entität oder Verantwortung repräsentiert, die nicht zu bestehendem Panel passt
- Wenn es in `gui/domains/<domain>/panels/` (fachlich) oder `gui/inspector/inspectors/` (Inspector) oder `gui/monitors/panels/` (Monitor) liegt
- Wenn es von der entsprechenden Base-Klasse erbt

### Wann muss ein bestehendes Panel erweitert werden?

- Wenn die neue Funktionalität zur gleichen Entität gehört (z.B. SessionExplorer + Filter)
- Wenn die Verantwortung nicht überschritten wird

### Wann ist ein neuer Screen gerechtfertigt?

- Bei UX-Begründung: neuer Nutzer-Kontext, neuer Hauptbereich oder Unterbereich
- Maximal 6 Hauptbereiche
- Gehört nicht zu bestehendem Screen als Unterbereich

### Wann ist ein neuer Workspace gerechtfertigt?

- Jeder Screen = ein Tab im TabbedWorkspace. "Neuer Workspace" = neuer Screen. Siehe oben.
- Kein eigener TabbedWorkspace als Main-Container in einer Domain.

### Welche Klassen dürfen zentralen Zugriff auf Layout / Docking haben?

- **Nur:** MainWindow (ruft DockingConfig auf), DockingConfig (erstellt QDockWidgets, addDockWidget)

### Welche Klassen dürfen das ausdrücklich NICHT?

- **Nicht:** Domain-Module, Panels, WorkspaceViews, Navigation, Components, Inspector-Panels, Monitor-Panels

### Welche Änderungen müssen architektonisch begründet werden?

- Neuer Hauptbereich (6. Bereich)
- Neuer Panel-Typ (6. Typ)
- Abweichung von Guardrail (Ausnahme)
- Dialog statt Workspace für komplexen Workflow

### Welche GUI-Anti-Patterns sind absolut zu vermeiden?

| Anti-Pattern | Stattdessen |
|--------------|-------------|
| QDockWidget außerhalb DockingConfig | DockingConfig |
| If/Else für Bereichswechsel | NavRegistry + WorkspaceFactory |
| Panel ohne Base-Klasse | BaseExplorer/Editor/Inspector/Monitor/Dashboard |
| Fachlogik in Navigation/Shell | Domains, Services |
| Domain kennt andere Domain | area_selected, Registry |
| Eigener TabWidget pro Domain | TabbedWorkspace zentral |
| Panel in app/ root | gui/domains/ oder gui/inspector/ oder gui/monitors/ |
| Dialog für komplexen Workflow | Workspace-Bereich |
| Neuer Panel-Typ ohne Review | Einer der 5 Typen |
| God-Object MainWindow | MainWindow schlank, Delegation |

---

*Diese Guardrails sind verbindlich. Abweichungen bedürfen einer Architektur-Review und dokumentierter Begründung.*

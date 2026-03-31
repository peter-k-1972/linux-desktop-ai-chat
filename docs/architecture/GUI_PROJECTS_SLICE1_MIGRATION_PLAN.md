# GUI Projects Slice 1 Migration Plan

**Projekt:** Linux Desktop Chat  
**Status:** Architekturplanung / kanonisch  
**Scope:** Erste Legacy-GUI-Migrationsscheibe fuer `app.projects`  
**Nicht-Ziel:** Keine Implementierung, keine neuen Splits, keine Aenderung der Shell-/Host-Verantwortung in dieser Scheibe.

---

## 1. Ziel und Scope

Diese Scheibe zieht die produktive Legacy-GUI fuer **`app.projects`** fachlich an das bereits physisch gesplittete Segment nach, **ohne** das sichtbare Verhalten zu aendern.

**In Scope**

- `ProjectListPanel`
- `ProjectOverviewPanel`
- `ProjectInspectorPanel`
- Read-/Command-/HostCallback-Vertrag fuer diese drei Bereiche
- Presenter-/Sink-basierte Verdrahtung innerhalb des bestehenden `ProjectsWorkspace`

**Nicht in Scope**

- `create_project`
- `update_project`
- `delete_project`
- Milestone-Bearbeitung / Dialoge
- Project Switcher / Top Bar
- Shell-Navigation / `WorkspaceHost` / `NavArea`
- globaler Projektkontext als Host-Mechanismus

---

## 2. Betroffene produktive GUI-Komponenten

- [`app/gui/domains/operations/projects/projects_workspace.py`](../../app/gui/domains/operations/projects/projects_workspace.py)
- [`app/gui/domains/operations/projects/panels/project_list_panel.py`](../../app/gui/domains/operations/projects/panels/project_list_panel.py)
- [`app/gui/domains/operations/projects/panels/project_overview_panel.py`](../../app/gui/domains/operations/projects/panels/project_overview_panel.py)
- [`app/gui/domains/operations/projects/panels/project_inspector_panel.py`](../../app/gui/domains/operations/projects/panels/project_inspector_panel.py)
- passiv weiterverwendete Teilansichten unter `app/gui/domains/operations/projects/panels/` (`project_header_card.py`, `project_stats_panel.py`, `project_activity_panel.py`, `project_quick_actions_panel.py`)

---

## 3. Ziel-Interface

### 3.1 Read

Empfohlener Port: `ProjectsOverviewReadPort`

- `load_project_list(filter_text, *, active_project_id=None, selected_project_id=None) -> ProjectListLoadResult`
- `load_project_overview(project_id) -> ProjectOverviewState | None`
- `load_project_inspector(project_id) -> ProjectInspectorState | None`
- `load_active_project_snapshot() -> ActiveProjectSnapshot`
- `subscribe_active_project_changed(listener) -> SubscriptionHandle`

**Zweck:** Panels lesen nur noch segmentnahe ViewStates statt direkt `ProjectService` / Host-Kontext.

### 3.2 Commands

Empfohlener Port: `ProjectsOverviewCommandPort`

- `select_project(project_id | None) -> None`
- `set_active_project(project_id | None) -> CommandResult`

**Bewusst nicht enthalten:** `create_project`, `update_project`, `delete_project`, Milestone-Commands.

### 3.3 HostCallbacks

Empfohlener Vertrag: `ProjectsOverviewHostCallbacks`

- `on_project_selection_changed(payload) -> None`
- `on_request_open_chat(project_id, chat_id=None) -> None`
- `on_request_open_prompt_studio(project_id, prompt_id=None) -> None`
- `on_request_open_knowledge(project_id, source_path=None) -> None`
- `on_request_open_workflows(project_id) -> None`
- `on_request_open_agent_tasks(project_id) -> None`
- optional `on_request_set_active_project(project_id | None) -> None`

**Zweck:** Navigation, Shell-Reaktion und globaler Projektkontext bleiben im Host, ohne direkte Host-Imports in Panels.

---

## 4. DTO-/ViewState-Uebersicht

Empfohlene `ui_contracts`-Typen fuer Slice 1:

- `ProjectListItem`
- `ProjectOverviewState`
- `ProjectCoreView`
- `ProjectStatsView`
- `ProjectMonitoringView`
- `ProjectActivityView`
- `ProjectControllingView`
- `ProjectInspectorState`
- `ActiveProjectSnapshot`
- minimale Event-Payloads:
  - `ProjectSelectionChangedPayload`
  - `ActiveProjectChangedPayload`

**Regel:** Keine rohen Service-Dicts, keine ORM-Objekte, keine Host-Navigationsobjekte in den ViewStates.

---

## 5. Presenter-Set

- `ProjectsListPresenter`
  - laedt Liste, Filter, aktive Projektmarkierung, Selection-Ereignisse
- `ProjectOverviewPresenter`
  - laedt Overview-State, verarbeitet `set_active_project`, loest HostCallbacks fuer Quick Actions / Activity aus
- `ProjectInspectorPresenter`
  - laedt Inspector-State fuer das selektierte Projekt
- optional `ProjectsWorkspacePresenter`
  - minimaler Koordinator fuer `selected_project_id` zwischen den drei Panel-Presentern

**Grundsatz:** Panelnahe Presenter bleiben klein; `ProjectsWorkspace` wird nicht durch einen neuen God-Presenter ersetzt.

---

## 6. Migrationsreihenfolge

### Schritt 1 - Vertrags- und Adapterbasis

**Ziel**

- Ports, DTOs, HostCallbacks und Service-Adapter einfuehren

**Bleibt unveraendert**

- alle produktiven Panels
- `ProjectsWorkspace`
- Dialoge und Write-Pfade

### Schritt 2 - `ProjectListPanel`

**Ziel**

- Listenladen, Filter und Selection ueber `ProjectsListPresenter` + Sink

**Bleibt unveraendert**

- Overview-/Inspector-Logik
- Create/Edit/Delete/Milestones

### Schritt 3 - `ProjectOverviewPanel`

**Ziel**

- Overview-Daten ueber Port/ViewState
- Quick Actions / Activity nur noch ueber HostCallbacks

**Bleibt unveraendert**

- Dialoge
- Shell-/Navigation-Implementierung

### Schritt 4 - `ProjectInspectorPanel`

**Ziel**

- Inspector ueber `ProjectInspectorPresenter` + Sink

### Schritt 5 - minimale Workspace-Entlastung

**Ziel**

- `ProjectsWorkspace` reduziert sich auf Verdrahtung, Lifecycle und Legacy-Write-Pfade

---

## 7. Zulaessige Host-Verantwortung

Darf in Slice 1 bewusst im Host verbleiben:

- Shell-Komposition und Screen-Registrierung
- `WorkspaceHost.show_area`, `NavArea`, `operations_context`
- globaler Projektkontext / `ProjectContextManager`
- Host-Event-Bruecke fuer `active_project_changed`
- Top-Bar / Project Switcher
- bestehende Create/Edit/Delete/Milestone-Dialogpfade

---

## 8. Unzulaessige Restkopplungen

Sollten nach Slice 1 in den migrierten Panels nicht mehr vorkommen:

- direkter Import von `app.services.project_service`
- direkter Import / Zugriff auf `ProjectContextManager`
- direkte Navigation ueber `NavArea`, `WorkspaceHost`, `operations_context`
- direkte Verarbeitung roher Service-Dicts im Widget
- paneluebergreifende Fachlogik im `ProjectsWorkspace`

---

## 9. Empfohlene PR-/Commit-Scheiben

1. Vertrags- und Adapterbasis  
2. `ProjectListPanel`-Migration  
3. `ProjectOverviewPanel`-Migration  
4. `ProjectInspectorPanel`-Migration  
5. Workspace-Entlastung / Guard-Nachzug / Doku-Nachzug

**Regel:** Kleine, rueckbaubare Schritte; kein gleichzeitiger Umbau aller drei Panels.

---

## 10. Minimale DoR / DoD pro Schritt

### Schritt 1 - Vertrags- und Adapterbasis

**DoR**

- Ports / DTOs / HostCallbacks fachlich abgestimmt
- Zielorte festgelegt

**DoD**

- keine produktive Verhaltensaenderung
- Adapter koennen bestehende Services/Kontextmechanik kapseln

### Schritt 2 - `ProjectListPanel`

**DoR**

- Read-Port + ListPresenter + ListSink vorhanden

**DoD**

- keine direkten `ProjectService`-Imports mehr im List-Panel
- Auswahl, Filter und aktive Markierung unveraendert

### Schritt 3 - `ProjectOverviewPanel`

**DoR**

- Overview-State / Presenter / HostCallbacks vorhanden

**DoD**

- keine direkten `ProjectService`-, `NavArea`-, `WorkspaceHost`- oder `operations_context`-Zugriffe mehr im Overview-Panel
- Quick Actions / Activity verhalten sich unveraendert

### Schritt 4 - `ProjectInspectorPanel`

**DoR**

- Inspector-State / Presenter / Sink vorhanden

**DoD**

- keine direkte Datenbeschaffung mehr im Inspector-Panel
- leerer / fehlender Projektzustand bleibt stabil

### Schritt 5 - Workspace-Entlastung

**DoR**

- alle drei Panel-Pfade presenterbasiert

**DoD**

- `ProjectsWorkspace` enthaelt nur noch Verdrahtung, Lifecycle und unveraenderte Legacy-Write-Pfade
- keine Regression bei Create/Edit/Delete/Milestones oder Shell-Integration

---

## Verweise

- [`PACKAGE_PROJECTS_PHYSICAL_SPLIT.md`](PACKAGE_PROJECTS_PHYSICAL_SPLIT.md)
- [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md)
- [`GUI_REGISTRY.md`](GUI_REGISTRY.md)

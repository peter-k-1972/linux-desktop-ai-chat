# GUI Projects Slice 1 DoD Checklist

**Projekt:** Linux Desktop Chat  
**Status:** Architektur- und Abnahme-Checkliste / kanonisch  
**Bezug:** [`GUI_PROJECTS_SLICE1_MIGRATION_PLAN.md`](GUI_PROJECTS_SLICE1_MIGRATION_PLAN.md)

---

## 1. Geltungsbereich von Slice 1

Diese Checkliste gilt fuer die **erste Legacy-GUI-Migrationsscheibe** von **`app.projects`**.

**In Scope**

- `ProjectListPanel`
- `ProjectOverviewPanel`
- `ProjectInspectorPanel`
- presenter-/sink-basierte Verdrahtung im bestehenden `ProjectsWorkspace`
- Read-/Command-/HostCallback-Vertrag fuer diese drei Panels

**Nicht in Scope**

- `create_project`
- `update_project`
- `delete_project`
- Milestone-Dialoge / Milestone-Write-Pfade
- Project Switcher / Top Bar
- Shell-Navigation / `WorkspaceHost` / `NavArea`
- globaler Projektkontext als Host-Mechanismus

---

## 2. Umsetzungsreihenfolge

1. Vertrags- und Adapterbasis  
2. `ProjectListPanel`  
3. `ProjectOverviewPanel`  
4. `ProjectInspectorPanel`  
5. minimale Workspace-Entlastung

**Regel:** Kein Schritt darf eine groessere produktive Flaeche umstellen als in dieser Reihenfolge vorgesehen.

---

## 3. Schrittbezogene DoR / DoD

### Schritt 1 - Vertrags- und Adapterbasis

**Definition of Ready**

- Read-/Command-/HostCallback-Vertrag fachlich stabil
- DTO-/ViewState-Spezifikation festgelegt
- Zielorte fuer Ports, Adapter, Sinks und Presenter abgestimmt

**Definition of Done**

- Ports / DTOs / Callback-Vertraege eingefuehrt
- Service-/Host-Adapter kapseln bestehende Services und Kontextmechanik
- keine produktive GUI-Verhaltensaenderung

**Minimale Testpflicht**

- Architektur-/Import-Checks fuer neue Vertraege
- Adapter-Mapping-Smokes fuer leere / normale / Fehlerfaelle

**Verbotene Restkopplungen**

- direkte Panel-Imports neuer Services in diesem Schritt
- parallele ad-hoc-Datenvertraege ausserhalb der kanonischen Ports

**Akzeptable Zwischenzustaende**

- produktive Panels bleiben vollstaendig alt
- neue Adapter existieren zunaechst ungenutzt

---

### Schritt 2 - `ProjectListPanel`

**Definition of Ready**

- `ProjectsOverviewReadPort` und `ProjectsListPresenter` stehen bereit
- List-Sink ist definiert
- Initial-/Leer-/Fehlerverhalten ist presenter-seitig festgelegt

**Definition of Done**

- `ProjectListPanel` liest nicht mehr direkt aus `ProjectService`
- Filter, Auswahl und aktive Projektmarkierung verhalten sich unveraendert
- Host-seitiger aktiver Projektwechsel aktualisiert die Listenmarkierung weiter korrekt

**Minimale Testpflicht**

- Listenladen ohne Filter
- Listenladen mit Filter
- leere Trefferliste
- Auswahlwechsel
- aktives Projekt wird korrekt markiert

**Verbotene Restkopplungen**

- direkter `ProjectService`-Import im List-Panel
- direkte `ProjectContextManager`-Nutzung im List-Panel

**Akzeptable Zwischenzustaende**

- Overview und Inspector bleiben noch im Altpfad
- `ProjectsWorkspace` enthaelt weiter alte Auswahl-/Sync-Logik

---

### Schritt 3 - `ProjectOverviewPanel`

**Definition of Ready**

- `ProjectOverviewState` ist stabil
- `ProjectOverviewPresenter` und `ProjectOverviewSink` sind spezifiziert
- HostCallbacks fuer Navigation / Quick Actions sind festgelegt

**Definition of Done**

- `ProjectOverviewPanel` liest nur noch ueber Port/ViewState
- Quick Actions und Activity-Aktionen gehen nur noch ueber HostCallbacks
- sichtbares Verhalten fuer Stats, Monitoring, Activity und Controlling bleibt unveraendert
- `set_active_project` laeuft nicht mehr direkt aus dem Panel in Host-Strukturen

**Minimale Testpflicht**

- Overview fuer vorhandenes Projekt
- leerer Zustand ohne Projekt
- aktives Projekt setzen
- Activity-Klicks / Quick Actions fuehren weiter in dieselben Zielbereiche
- fehlendes Projekt / Fehlerfall bleibt stabil

**Verbotene Restkopplungen**

- direkter `ProjectService`-Import im Overview-Panel
- direkter Zugriff auf `NavArea`, `WorkspaceHost`, `operations_context`
- direkter Zugriff auf `ProjectContextManager`

**Akzeptable Zwischenzustaende**

- Dialoge fuer Edit/Delete/Milestones bleiben noch unveraendert im Workspace
- Inspector bleibt noch im Altpfad

---

### Schritt 4 - `ProjectInspectorPanel`

**Definition of Ready**

- `ProjectInspectorState` ist stabil
- `ProjectInspectorPresenter` und `ProjectInspectorSink` sind spezifiziert
- Selektionsquelle fuer Inspector ist geklaert

**Definition of Done**

- `ProjectInspectorPanel` bezieht seine Daten nur noch ueber Presenter/Port
- leerer Zustand und nicht mehr existierendes Projekt verhalten sich stabil
- Inspector folgt weiterhin der Auswahl im Projects-Bereich

**Minimale Testpflicht**

- Inspector bei initialer Auswahl
- Inspector nach Auswahlwechsel
- leerer Inspector ohne Auswahl
- fehlendes Projekt nach Reload

**Verbotene Restkopplungen**

- direkte Datenbeschaffung im Inspector-Panel
- direkte Service-/Kontext-Imports im Inspector-Panel

**Akzeptable Zwischenzustaende**

- `ProjectsWorkspace` koordiniert Auswahl weiterhin teilweise selbst

---

### Schritt 5 - minimale Workspace-Entlastung

**Definition of Ready**

- Liste, Overview und Inspector laufen presenterbasiert
- Restlogik im `ProjectsWorkspace` ist identifiziert

**Definition of Done**

- `ProjectsWorkspace` ist primaer Verdrahtungs- und Lifecycle-Container
- Read-/Sync-Fachlogik liegt nicht mehr im Workspace
- Create/Edit/Delete/Milestones bleiben funktional unveraendert
- Shell-Integration bleibt unveraendert

**Minimale Testpflicht**

- Initiales Laden des gesamten Projects-Workspaces
- Auswahlwechsel ueber alle drei Bereiche
- aktives Projektwechsel-Event aus dem Host
- keine Regression in Create/Edit/Delete/Milestones

**Verbotene Restkopplungen**

- paneluebergreifende Fachlogik im Workspace
- neue direkte Servicezugriffe fuer Read-Pfade im Workspace

**Akzeptable Zwischenzustaende**

- Legacy-Write-Pfade bleiben im Workspace
- Workspace bleibt Host-Container

---

## 4. Globale Abnahmekriterien fuer Slice 1

Slice 1 gilt insgesamt nur als abgenommen, wenn:

- `ProjectListPanel`, `ProjectOverviewPanel` und `ProjectInspectorPanel` fuer Read-Pfade presenter-/port-basiert sind
- migrierte Panels keine direkten `app.services.project_service`-Imports mehr enthalten
- migrierte Panels keine direkten `ProjectContextManager`-, `NavArea`-, `WorkspaceHost`- oder `operations_context`-Zugriffe mehr enthalten
- `ProjectsWorkspace` fuer Slice-1-Read-Pfade keine eigene Fachlogik mehr traegt
- sichtbares Verhalten fuer Auswahl, Anzeige, Quick Actions und Host-Synchronisation unveraendert bleibt
- Create/Edit/Delete/Milestones weiterhin funktionieren

---

## 5. Klare Nicht-Ziele fuer Slice 1

Nicht Ziel dieser Scheibe sind:

- Umstellung der Dialoge fuer Create/Edit/Delete
- Umstellung der Milestone-Write-Flows
- Umbau von Top Bar / Project Switcher
- neue GUI-Shell-Architektur
- Verlagerung des globalen Projektkontexts aus dem Host
- Optimierung oder funktionale Erweiterung des Projects-Bereichs

---

## 6. Was erst in spaeteren Slices folgen darf

Folgeslices duerfen sich kuemmern um:

- Create/Edit/Delete-Pfade
- Milestone-Dialoge und Milestone-Commands
- Project Switcher / Top-Bar-Anbindung
- weitere Host-Entlastung im `ProjectsWorkspace`
- Vereinheitlichung mit spaeteren `workflows`-/`persistence`-GUI-Slices
- strengere Guards fuer verbotene Direktimporte nach Abschluss der Umsetzung

---

## Verweise

- [`GUI_PROJECTS_SLICE1_MIGRATION_PLAN.md`](GUI_PROJECTS_SLICE1_MIGRATION_PLAN.md)
- [`PACKAGE_PROJECTS_PHYSICAL_SPLIT.md`](PACKAGE_PROJECTS_PHYSICAL_SPLIT.md)

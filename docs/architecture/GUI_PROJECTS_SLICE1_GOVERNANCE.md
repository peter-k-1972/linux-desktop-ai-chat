# GUI Projects Slice 1 Governance

**Projekt:** Linux Desktop Chat  
**Status:** Implementierungs-Governance / kanonisch  
**Bezug:** [`GUI_PROJECTS_SLICE1_MIGRATION_PLAN.md`](GUI_PROJECTS_SLICE1_MIGRATION_PLAN.md), [`GUI_PROJECTS_SLICE1_DOD_CHECKLIST.md`](GUI_PROJECTS_SLICE1_DOD_CHECKLIST.md)

---

## 1. Geltungsbereich von Slice 1

Diese Governance gilt fuer die spaetere Implementierung der **ersten Legacy-GUI-Migrationsscheibe** von **`app.projects`**.

**In Scope**

- `ProjectListPanel`
- `ProjectOverviewPanel`
- `ProjectInspectorPanel`
- zugehoerige Sinks, Presenter, Read-/Command-Ports und HostCallbacks
- schrittweise Entlastung des bestehenden `ProjectsWorkspace`

**Nicht in Scope**

- Create/Edit/Delete-Dialoge
- Milestone-Write-Pfade
- Project Switcher / Top Bar
- Shell- oder Navigations-Refactors
- Verlagerung des globalen Projektkontexts aus dem Host

---

## 2. Verbotene Direktimporte in migrierten Panels

Sobald ein Panel in Slice 1 migriert ist, darf es **nicht mehr direkt** importieren oder verwenden:

- `app.services.project_service`
- `app.core.context.project_context_manager`
- `app.gui.navigation.nav_areas`
- `app.gui.workspace.workspace_host`
- `app.gui.domains.operations.operations_context`
- andere Host-spezifische Navigations- oder Kontext-Helfer, die dieselbe Rolle verdeckt erneut einfuehren

**Regel:** Host-Reaktionen laufen nur noch ueber definierte HostCallbacks; Fachdaten nur noch ueber Ports / Presenter / ViewStates.

---

## 3. Zulaessige Abhaengigkeiten

Migrierte Panels duerfen abhaengen von:

- eigener Qt-Basislogik / kleine Qt-Widgets
- eigenem Sink
- eigenem Presenter
- `ui_contracts`-Typen / ViewStates / Event-Payloads
- passiven Unterwidgets innerhalb desselben GUI-Bereichs
- HostCallbacks **nur** ueber definierte Vertragsgrenzen

Presenter duerfen abhaengen von:

- den kanonischen Read-/Command-Ports
- `ui_contracts`
- eigenem Sink
- den definierten HostCallbacks

Adapter duerfen temporär abhaengen von:

- bestehenden Services
- bestehender Host-Kontextmechanik
- bestehender Host-Event-Bruecke

**Regel:** Direkte Host- oder Service-Abhaengigkeiten sind im Slice-1-Ziel nur noch in Adaptern und verbleibender Host-Verdrahtung zulaessig, nicht in migrierten Panels.

---

## 4. Erwartete Guard-Nachzuege

Nach Abschluss der produktiven Slice-1-Umsetzung sollen Architekturtests / Guards ergaenzt oder angepasst werden, die mindestens pruefen:

- migrierte Panels importieren **nicht** direkt `app.services.project_service`
- migrierte Panels importieren **nicht** direkt `ProjectContextManager`
- migrierte Panels importieren **nicht** direkt `NavArea`
- migrierte Panels importieren **nicht** direkt `WorkspaceHost`
- migrierte Panels importieren **nicht** direkt `operations_context`
- migrierte Panels nutzen ViewStates / Presenter / Sinks statt roher Service-Dicts
- `ProjectsWorkspace` enthaelt fuer Slice-1-Read-Pfade keine neue paneluebergreifende Fachlogik

Erwartete Guard-Ausrichtung:

- Import-/Dependency-Guards auf Dateiebene
- optional schmale Source-Text-Guards fuer verbotene Direktimporte
- keine zu breiten Guards, die Legacy-Write-Pfade derselben Scheibe unnoetig blockieren

---

## 5. Minimale PR-/Review-Regeln

Jede PR-Scheibe fuer Slice 1 muss nachweisen:

- ihr Scope entspricht genau der vorgesehenen Migrationsreihenfolge
- die betroffenen Panels halten die kanonischen Ports / Presenter / Sinks ein
- keine neue direkte Host- oder Service-Kopplung wird im migrierten Panel eingefuehrt
- sichtbares Verhalten bleibt unveraendert
- die minimale Testpflicht gemaess [`GUI_PROJECTS_SLICE1_DOD_CHECKLIST.md`](GUI_PROJECTS_SLICE1_DOD_CHECKLIST.md) ist erfuellt

Unzulaessige Scope-Ausweitungen in einer Slice-1-PR:

- Mitziehen von Create/Edit/Delete
- Mitziehen von Milestone-Write-Flows
- gleichzeitige Umstellung mehrerer Schritte ohne gesonderte Architekturfreigabe
- Shell-/Top-Bar-/Project-Switcher-Umbauten
- neue Feature-Arbeit im Projects-Bereich

Minimal erwartete Tests pro PR:

- passende Unit-/Mapping-Tests fuer Presenter / Adapter
- zielgerichtete GUI-/Smoke-Tests fuer den betroffenen Schritt
- Nachweis, dass bestehende Projects-Interaktion sichtbar stabil bleibt

---

## 6. Abbruchkriterien

Eine PR fuer Slice 1 gilt architektonisch als **nicht akzeptabel**, wenn mindestens eines davon zutrifft:

- ein migriertes Panel importiert weiter direkt `app.services.project_service`
- ein migriertes Panel importiert weiter direkt Host-Navigation oder Host-Kontext-Helfer
- neue Fachlogik wird in `ProjectsWorkspace` statt in Presenter / Port / Adapter eingebaut
- Scope greift in Create/Edit/Delete oder Milestone-Write-Pfade ein
- Ports / ViewStates werden durch rohe Service-Dicts unterlaufen
- sichtbares Verhalten aendert sich ohne ausdrueckliche Architekturentscheidung
- Tests / Smoke-Absicherung des jeweiligen Schritts fehlen

---

## Verweise

- [`GUI_PROJECTS_SLICE1_MIGRATION_PLAN.md`](GUI_PROJECTS_SLICE1_MIGRATION_PLAN.md)
- [`GUI_PROJECTS_SLICE1_DOD_CHECKLIST.md`](GUI_PROJECTS_SLICE1_DOD_CHECKLIST.md)
- [`PACKAGE_PROJECTS_PHYSICAL_SPLIT.md`](PACKAGE_PROJECTS_PHYSICAL_SPLIT.md)

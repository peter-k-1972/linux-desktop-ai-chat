# PHASE_BREAKDOWN – Gap-Schließung Linux Desktop Chat

**Stand:** 2026-03-20 · Basiert auf `docs/MASTER_REMEDIATION_PLAN.md` und den Audit-Reports.

---

## Phase 1: Kritische Widersprüche Doku vs. Anwendung

### Ziel

Entscheidungsträger und Entwickler arbeiten mit **korrekten Pfaden und Ist-Beschreibungen**; offensichtlich falsche BLOCKER in `DOC_GAP_ANALYSIS.md` sind bereinigt; Root-`README` und Architekturdocs widersprechen nicht dem CC-Tools/Data-Stores-Stand.

### Betroffene Module / Artefakte

- `docs/qa/architecture/AGENT_UI_ARCHITECTURE_EVALUATION.md`
- `docs/04_architecture/AGENTS_UI_ARCHITECTURE_AUDIT.md`
- `docs/04_architecture/COMMAND_CENTER_ARCHITECTURE.md`
- `docs/DOC_GAP_ANALYSIS.md`
- Root `README.md` (CC-Feature-Zeile)
- Referenzcode (nur zum Abgleich, keine Änderung in dieser Planphase): `app/gui/domains/control_center/workspaces/agents_workspace.py`, `app/gui/domains/command_center/command_center_view.py`

### Konkrete Aufgaben

1. **AGENT_UI_* und AGENTS_UI_ARCHITECTURE_AUDIT:** Texte anpassen: CC Agents = `AgentManagerPanel` + `AgentService`; **kein** `app/ui/agents/` als aktiver Pfad – oder Dokumente als **ARCHIV / Stand 2026-03-16** kennzeichnen mit Verweis auf kanonische Dateien (Quelle: DOC_PROMISE_MISMATCH, STATUS_AUDIT).
2. **COMMAND_CENTER_ARCHITECTURE.md:** Alle `app/ui/command_center/...` → `app/gui/domains/command_center/...` oder Archiv-Banner + Redirect-Hinweis (Quelle: DOC_PROMISE_MISMATCH).
3. **DOC_GAP_ANALYSIS.md:** BLOCKER/HIGH-Einträge zu README, introduction-Link, SETTINGS_ARCHITECTURE, settings_chat_context, SYSTEM_MAP-Ausschnitt **überprüfen und als erledigt markieren oder entfernen**; verbleibende Lücken (CLI, Deployment) stehen lassen (Quelle: DOC_PROMISE_MISMATCH, STATUS_AUDIT).
4. **README.md:** Control Center-Zeile präzisieren: Tools/Data Stores nur wenn **noch Demo** – als „Vorschau“ oder nach Phase 2/3 anpassen (Quelle: DOC_PROMISE_MISMATCH).

### Risiken

- Zeitverlust durch **vollständiges** statt **priorisiertes** Aufräumen aller `app/ui/`-Vorkommen in `docs/**` → **Mitigation:** Phase 5 für Massenkorrektur; Phase 1 nur P0-Dateien aus DOC_PROMISE_MISMATCH.

### Voraussetzungen

- Lesezugriff auf Repo; optional Abstimmung „Archiv vs. Rewrite“ für große Reports.

### Definition of Done

- Die drei genannten Architektur-/QA-Dokumente (Agent Evaluation, Agents Audit, Command Center Arch) enthalten **keine** behauptete aktive Codebasis unter nicht existierendem `app/ui/command_center` bzw. keine falsche CC-Agenten-Datenquelle **oder** sind eindeutig als historisch gekennzeichnet.
- `DOC_GAP_ANALYSIS.md` BLOCKER-Sektion reflektiert den **aktuellen** README-/Link-/Settings-/Help-Stand laut DOC_PROMISE_MISMATCH.
- `README.md` CC-Bullet widerspricht nicht dem dokumentierten Ist (Demo vs. Live nach Phase-2-Entscheid – mindestens Fußnote bis Phase 2 abgeschlossen).

---

## Phase 2: GUI-Platzhalter und tote UI-Verzweigungen

### Ziel

Keine **unmarkierten** Dummy-Tabellen und kein **irreführender** Dashboard-„Live“-Eindruck; tote Demo-Panels im CC-Bereich bereinigt; konsistente Erwartung zwischen „Kommandozentrale“ Dashboard und datenreichem Command Center.

### Betroffene Module

- `app/gui/domains/control_center/panels/tools_panels.py`, `tools_workspace.py`
- `app/gui/domains/control_center/panels/data_stores_panels.py`, `data_stores_workspace.py`
- `app/gui/domains/dashboard/dashboard_screen.py`, `dashboard/panels/*`
- `app/gui/domains/control_center/panels/agents_panels.py`, `control_center/panels/__init__.py`
- `app/gui/domains/operations/knowledge/panels/index_overview_panel.py`, `retrieval_status_panel.py`
- `app/gui/domains/operations/prompt_studio/panels/preview_panel.py`
- `app/gui/domains/operations/agent_tasks/panels/status_panel.py`, `queue_panel.py`
- `app/gui/navigation/workspace_graph.py` (optional EN→DE)
- `app/gui/domains/command_center/command_center_view.py` (Subsystem-Detail laut Kommentar)

### Konkrete Aufgaben

1. **CC Tools & Data Stores:** Produkentscheid: (a) **Live-Verdrahtung** in Phase 3 vorbereiten + UI mit „Lädt…/Fehler“ **oder** (b) **deutliche Demo-Kennzeichnung** (Banner, keine „Connected“-Claims) **oder** (c) **Nav-Einträge ausblenden** bis Live (Quelle: PLACEHOLDER_INVENTORY, STATUS_AUDIT, IMPLEMENTATION_GAP_MATRIX).
2. **Dashboard:** Entweder **Deep-Link** zu `CommandCenterView`/QA-Adapter, **Empty State** mit Erklärung, oder **Feature-Flag**/versteckter Eintrag bis Backend existiert (Quelle: PLACEHOLDER_INVENTORY, TEST_GAP_REPORT).
3. **`agents_panels.py`:** Entfernen aus Export / Datei löschen **oder** umbenennen und nur für Designer-Demo nutzen; Kollision `AgentRegistryPanel` auflösen (Quelle: STATUS_AUDIT, PLACEHOLDER_INVENTORY, TEST_GAP_REPORT).
4. **Knowledge/Prompt/Agent-Task-Platzhalter-Labels:** Entweder echte Daten in Phase 3 oder **ehrlicher** Kurztext („Noch keine Metriken“) statt widersprüchlichem „(Platzhalter)“ in Produktionspfad – konsistent mit Phase-1-Doku (Quelle: PLACEHOLDER_INVENTORY).
5. **`workspace_graph`:** Optional Lokalisierung (Quelle: PLACEHOLDER_INVENTORY, niedrig).

### Risiken

- Nutzer verlieren Menüeinträge → **Mitigation:** Release-Note + Help-Link.  
- Zu frühe Löschung von `agents_panels` ohne Prüfung externer Imports → **Mitigation:** `rg`/CI-Guard vor Merge.

### Voraussetzungen

- Phase 1 abgeschlossen (Texte und README aligned).  
- Entscheidungsprotokoll zu 2.1 und 2.2 (kurz).

### Definition of Done

- CC Tools/Data Stores: Kein Zustand mehr, in dem **nur** kleines Graulabel „Vorschau“ zwischen **produktionsreifen** Layout und **fiktiven** „Connected“-Daten steht – ohne dass ein **Banner oder Nav-Änderung** die Situation klärt (Erfüllung gemäß gewählter Strategie dokumentiert).
- Dashboard: Docstrings und sichtbare UI widersprechen sich nicht (kein „fertige“ Karte ohne Datenquelle ohne Hinweis).
- `agents_panels`-Duplikat: Entweder entfernt und `__init__.py` bereinigt **oder** formal in ADR/Commit beschrieben „nur Test/Demo“ mit verbotenem Shell-Mount (nachweisbar).
- Verbleibende „(Platzhalter)“-Strings in genannten Panels: Liste im Ticket; jeder entweder ersetzt durch reale Anzeige oder durch **nicht-widersprüchlichen** Empty-State-Text.

---

## Phase 3: Backend-Lücken und Verdrahtung

### Ziel

Für jede in Phase 2 als **„Live“** definierte UI-Fläche existiert eine **nachweisbare** Backend-Quelle (Service, DB-Health, Metrics); für **bewusst leere** Bereiche gibt es **keine** falschen Persistenz-Erwartungen.

### Betroffene Module (je nach Phase-2-Entscheid)

- `app/services/*`, `app/core/db/database_manager.py`, `app/rag/*` (Data Stores / Health)
- Bestehende Tool-Registry oder neues schmales API (CC Tools) – **nur wenn** Phase 2 „Live“ wählt (Quelle: IMPLEMENTATION_GAP_MATRIX, STATUS_AUDIT Backend-Gaps)
- `app/gui/domains/settings/categories/project_category.py`, `workspace_category.py` + ggf. `AppSettings`-Keys
- `app/pipelines/executors/placeholder_executors.py` + Pipeline-Definitionen/Registry
- `app/critic.py` – Verifikation und ggf. Implementierung oder Entfernung (Quelle: STATUS_AUDIT, IMPLEMENTATION_GAP_MATRIX)
- Knowledge: Anbindung von `index_overview_panel` / `retrieval_status_panel` an `knowledge_service` o. Ä.
- Prompt Studio: `preview_panel` an Test-Lab oder readonly renderer
- Agent Tasks: Status/Queue an `DebugStore`/Runner, falls vorhanden

### Konkrete Aufgaben

1. **CC Tools:** Service- oder Config-Lese-Pfad; Fehlerbehandlung bei fehlender Registry (Quelle: IMPLEMENTATION_GAP_MATRIX).  
2. **CC Data Stores:** SQLite/Chroma/File-Status aus echten Health-Checks; keine hardcodierten „Healthy“ (Quelle: PLACEHOLDER_INVENTORY).  
3. **Settings Project/Workspace:** Mindestens **ein** persistierter Key **oder** Nav-Eintrag reduzieren + Doku „noch nicht verfügbar“ (Quelle: IMPLEMENTATION_GAP_MATRIX).  
4. **Pipelines:** Tests für `StepResult` der Placeholder-Executors; optional UI-Warnung bei Workflow mit Comfy/Media-Schritten (Quelle: TEST_GAP_REPORT, PLACEHOLDER_INVENTORY).  
5. **`critic.py`:** Aufrufer-Suche; TODO auflösen durch Implementierung oder Deprecation (Quelle: STATUS_AUDIT).

### Risiken

- Blockierung durch fehlende Produktdefinition für Project/Workspace-Settings → **Mitigation:** Phase-2-„defer“-Pfad nutzen.

### Voraussetzungen

- Phase 2 abgeschlossen mit schriftlicher Entscheidung pro Fläche.

### Definition of Done

- Jede „Live“-UI aus Phase 2 hat **einen** dokumentierten Datenfluss (1 Absatz in `docs/` oder Moduldocstring).  
- Keine `dummy_data`-Arrays mehr in produktiv genutzten CC-Panels **ohne** ausdrückliche Demo-Flag-UI (falls Demo beibehalten).  
- `critic.py`: Zustand **aktiv / entfernt / dokumentiert deaktiviert** – kein offenes TODO ohne Ticket.

---

## Phase 4: Testabdeckung

### Ziel

**Grüne** Test-Collection in der Referenz-Umgebung; neue Regressionen für geänderte Flächen; Absicherung der behobenen Doku-vs-Code-Aussagen.

### Betroffene Module

- `pytest.ini`, ggf. `conftest.py`, fehlerhafte Testmodule (laut Collection-Output)
- Neue/geänderte Tests unter `tests/unit/`, `tests/ui/`, `tests/integration/` für CC, Dashboard, Executors
- `tests/architecture/` bei Umbenennung/Entfernung `agents_panels`

### Konkrete Aufgaben

1. **Collection-Errors:** 30 Fehler analysieren; fehlende optional deps, falsche Imports, Qt-Headless – beheben oder markieren (Quelle: TEST_GAP_REPORT).  
2. **CC Tools/Data Stores:** Nach Phase-2/3 Strategie – Tests für „kein falsches Live“ oder für echte Datenbindung (Quelle: TEST_GAP_REPORT).  
3. **Dashboard:** Smoke oder Widget-Test für Empty-State/Link (Quelle: TEST_GAP_REPORT).  
4. **PlaceholderExecutors:** Unit-Test erwarteter `success=False` und Fehlertext (Quelle: TEST_GAP_REPORT).  
5. **Doku-Regression:** Optional Test/Skript, das prüft, dass `agents_workspace` `AgentManagerPanel` importiert (kein Rückfall zu Demo-Tabelle in Doku-nahen Guards) – **nur wenn** als sinnvoll erachtet.  
6. **Bestehende Schwerpunkte** aus `docs/AUDIT_REPORT.md` bei Änderungen an Chat/Kontext nicht verschlechtern.

### Risiken

- CI unterscheidet sich von lokal → **Mitigation:** `docs/DEVELOPER_GUIDE.md` oder CI-YAML um Referenzmatrix ergänzen (Phase 5).

### Voraussetzungen

- Phase 3 für die getesteten Live-Pfade abgeschlossen oder gemockt.

### Definition of Done

- `pytest --collect-only` in Referenz-CI **exit 0**.  
- Neue Tests für alle Backlog-Items mit Test-Anforderung **grün**.  
- Keine neuen `dummy_data`-Pfade in Shell ohne zugehörigen Test der Kennzeichnung (falls Demo).

---

## Phase 5: Dokumentationskonsolidierung

### Ziel

Einheitliche **Onboarding-** und **Developer-**Story; CLI/Repro nachvollziehbar; historische `app/ui/`-Reports klar als Archiv oder korrigiert.

### Betroffene Artefakte

- `docs/DOC_GAP_ANALYSIS.md` (Restlücken)
- Neue oder erweiterte: `docs/05_developer_guide/` (CLI), ggf. `DEPLOYMENT.md` oder Verweis „nicht unterstützt“
- Massen-Reports unter `docs/04_architecture/`, `docs/refactoring/` mit `app/ui/` (Quelle: DOC_PROMISE_MISMATCH, STATUS_AUDIT)
- `tools/generate_system_map.py` + Regenerationshinweis (Quelle: DOC_GAP)

### Konkrete Aufgaben

1. **CLI / Repro-Registry:** Eine kanonische Datei mit Befehlen, Eingaben, Ausgabeartefakten (Quelle: DOC_GAP_ANALYSIS, STATUS_AUDIT).  
2. **Archiv-Banner** oder Pfadkorrektur für die wichtigsten noch verlinkten Migration-Reports (Priorität: alles, was von `docs/README.md` oder `00_map` verlinkt wird).  
3. **SYSTEM_MAP / FEATURE_REGISTRY:** Regenerations-Workflow in Developer-Guide erwähnen (Quelle: DOC_GAP).  
4. **Deployment:** Entweder Minimal-Dokument **oder** explizit „out of scope“ mit Begründung (Quelle: DOC_GAP offene Lücke).

### Risiken

- Scope-Explosion → **Mitigation:** nur verlinkte Pfade und P0-Mismatches aus Phase 1 Liste.

### Voraussetzungen

- Phase 1 und relevante Codeänderungen aus 2–3 abgeschlossen (Doku beschreibt Ist).

### Definition of Done

- DOC_GAP „Quick Wins“ und offene CLI/Deployment-Punkte **aktualisiert oder bewusst verschoben** mit Ticket-IDs.  
- Kein von der Startseite erreichbarer Doc-Link mit **falschem** `app/ui/command_center`-Pfad ohne Hinweis.

---

## Phase 6: Gesamt-QA und Release-Freigabe

### Ziel

Formale Abnahme gemäß `docs/QA_ACCEPTANCE_MATRIX.md`; Release-Notes mit Restrisiken.

### Betroffene Module

Gesamtsystem; CI; ggf. `docs/CHANGELOG*` oder Release-Tag-Prozess.

### Konkrete Aufgaben

1. Matrix Zeile für Zeile abhaken mit Nachweis (Log, PR-Link, Screenshot wo nötig).  
2. **Manuelle Explorations-Checkliste** (kurz): CC Agents CRUD, Chat Send, Knowledge Quelle hinzufügen (falls im Scope), Settings speichern.  
3. **Sign-off:** Maintainer + QA-Rolle (kann dieselbe Person sein, muss benannt sein).

### Risiken

- „Fast grün“ → **Mitigation:** Matrix markiert blockierend vs. nachgelagert.

### Voraussetzungen

- Phase 4 und für Release relevante Phase-5-Punkte erfüllt.

### Definition of Done

- Alle **blockierenden** Zeilen in `QA_ACCEPTANCE_MATRIX.md` erfüllt.  
- Dokumentierte **akzeptierte Restrisiken** (z. B. kein Live-Ollama in CI).  
- Tag oder internes Release-Dokument mit Versionshinweis.

---

*Ende PHASE_BREAKDOWN*

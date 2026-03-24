# IST-Analyse: Linux Desktop Chat — Anschlussfähigkeit für Portfolio-/Projekt-/Produktions-Plattform

**Erstellt:** 2026-03-23  
**Methode:** ausschließlich Code- und Schema-Fundstellen im Repository; keine Soll-Architektur, keine Implementierungsempfehlungen jenseits Wiederverwendbarkeit vs. Neuaufbau.

---

## A. Executive Summary

Die Codebasis ist bereits **stark entlang „Projekt + Chat + Knowledge (RAG) + Workflows + Agentenprofile + Betrieb (Audit/Incidents/Deployment)“** gewachsen. Persistenz liegt überwiegend in **einer SQLite-Datei** (`chat_history.db`, per Umgebungsvariable überschreibbar), wobei **zwei parallele Spuren** existieren: (1) **direktes sqlite3** über `DatabaseManager` und mehrere Repository-Klassen, (2) **SQLAlchemy-ORM** für Modell-Nutzung, Quotas und lokale Modell-Assets (Alembic-Revision `phase_a_001`).

Es gibt **keine Portfolio-Ebene**, **keine fachlichen Produktionsbereiche** (Musik, Video, …) als erstklassiges Datenmodell und **kein generisches Aufgaben-/Issue-Tracking** auf Projektebene. **„Task“** taucht vor allem als **optionaler String in Agent-Metriken** und in **UI-/Debug-Begriffen** auf, nicht als Domänenobjekt für Projektmanagement.

**Workflows** sind technisch ausgereift (Definitionen in SQLite, Runs, Node-Runs, Schedules, Status-Enums) und bilden die **stärkste bestehende Brücke** zu orchestrierten Mehrstufern. **Agenten** sind als **SQLite-Profile** mit optionaler `project_id` und JSON-Feldern (u. a. `workflow_bindings`, `knowledge_spaces`) modelliert — **kein** dedizierter „Butler“-Typ im Schema.

**Reporting** ist fragmentiert: QA-/Governance-Artefakte werden aus **`docs/qa`-JSON** gelesen (`QAGovernanceService`); **Audit** ist append-only in `audit_events`; **Metriken** in `agent_metric_events`. Ein **einheitliches Report-Objektmodell** in der DB fehlt.

**Rollen/Rechte** im Sinne von Benutzern, Mandanten oder ACLs **sind im untersuchten Anwendungscode nicht als Schema vorhanden**; „Role“ bezeichnet primär **LLM-Modell-Rollen** (`ModelRole`).

---

## B. Bestehende Domänenobjekte und ihre Fundstellen

### B.1 `project`

| Aspekt | Fundstelle |
|--------|------------|
| SQLite-Tabelle `projects` | `app/core/db/database_manager.py` (CREATE + Migrationen: u. a. `lifecycle_status`, Budget, Kunde, externe Referenzen) |
| Service-API | `app/services/project_service.py` |
| Lebenszyklus-Werte (validiert) | `app/projects/lifecycle.py` |
| Meilensteine `project_milestones` | `database_manager.py`; Nutzung/Controlling-Hilfen z. B. `app/projects/controlling.py` (von Tests referenziert) |
| GUI | `app/gui/domains/operations/projects/` (`projects_workspace.py`, Panels, Dialoge) |

**Semantik im Code:** Projekt bündelt Chats (`project_chats`), Topics, Dateiverknüpfungen, optional RAG-Space `project_{id}`, löscht/entkoppelt Workflows, Prompts, Agenten bei Delete (siehe Docstring in `delete_project`).

### B.2 `workflow`

| Aspekt | Fundstelle |
|--------|------------|
| Tabellen `workflows`, `workflow_runs`, `workflow_node_runs` | `database_manager.py` → `_migrate_workflows` |
| Optional `project_id` auf Definition | Spalte + Index in derselben Migration |
| Domänen-Datentypen | `app/workflows/models/definition.py` (`WorkflowDefinition`, `WorkflowNode`, `WorkflowEdge`) |
| Status | `app/workflows/status.py` (`WorkflowDefinitionStatus`, `WorkflowRunStatus`, `NodeRunStatus`) |
| Persistenz-API | `app/workflows/persistence/workflow_repository.py` |
| Service | `app/services/workflow_service.py`, Adapter `workflow_*_adapter.py` |
| GUI | `app/gui/domains/operations/workflows/` |
| Agent-Referenzen in Definitionen | `app/workflows/queries/agent_workflow_definitions.py` |

### B.3 `task` (Abgrenzung)

- **Keine** Tabelle oder Service für „Projektaufgaben“ / Tickets im untersuchten Kernpfad identisch mit PM-„Task“.
- **`agent_metric_events.task_id`**: optionales TEXT-Feld für Metriken — `app/metrics/metrics_store.py`.
- **GUI:** „Agent Tasks“-Workspace = **spezialisierte Agenten-Personas**, nicht Aufgabenliste — `app/gui/domains/operations/operations_nav.py` (`operations_agent_tasks`).
- **`DepartmentInfo`** für `planning` erwähnt „Task-Zerlegung“ als Beschreibungstext — `app/agents/departments.py` (kein persistiertes Task-Modell).

### B.4 `run`

- **Workflow:** `workflow_runs`, `workflow_node_runs` — `database_manager.py`; Status-Enums `app/workflows/status.py`.
- **Pipeline:** `PipelineRun` — `app/pipelines/models/run.py`, Service explizit **in-memory** — `app/pipelines/services/pipeline_service.py` (Docstring: keine Persistenz Phase 1).
- **Schedule-Kopplung:** `workflow_schedules`, `schedule_run_log` — `database_manager.py` → `_migrate_workflow_schedules`.

### B.5 `asset`

| Begriff im Code | Bedeutung | Fundstelle |
|-----------------|-----------|------------|
| **`ModelAsset`** | Lokale Modell-Datei (GGUF etc.), ORM-Tabelle `model_assets` | `app/persistence/orm/models.py` |
| **`files` / `project_files` / `chat_files`** | Pfade als Workspace-/Kontext-Dateien | `database_manager.py` |
| **UI „Assets“** | Anzeige lokaler Modell-Inventare | `app/gui/domains/control_center/panels/local_assets_panel.py` |

**Kollision mit Zielbild:** Das Wort „Asset“ ist **bereits für LLM-Modellartefakte und Icon/Theme-Pfade** (`app/utils/paths.py` → `assets/`) belegt, nicht für generische Produktions-Assets (Medien).

### B.6 `file`

- Tabellen `files`, `project_files`, `chat_files` — `database_manager.py`.
- Methoden `get_or_create_file`, `list_files_for_chat`, `list_workspace_roots_for_chat` — dieselbe Datei.

### B.7 `model` (LLM)

- **`messages.model`**: SQLite-Spalte — Migration `_migrate_messages_model` in `database_manager.py`.
- **`ModelEntry` / `ModelRegistry`**: Konfiguration — `app/core/models/registry.py`.
- **`ModelRole`**: semantische Rollen für Routing — `app/core/models/roles.py` (nicht RBAC).
- **ORM:** `ModelUsageRecord`, Aggregationen, Quotas — `app/persistence/orm/models.py`.

### B.8 `agent`

- Tabelle `agents` — `app/agents/agent_repository.py` (CREATE TABLE inkl. `project_id`, `workflow_bindings`, `knowledge_spaces`, `department`, `escalation_policy`, …).
- Services: `app/services/agent_service.py`, `agent_operations_read_service.py`, u. a.
- GUI: Control Center „Agents“ + Operations „Agent Tasks“ (siehe `navigation_registry.py`).

### B.9 `context`

- **Chat:** `ChatContextPolicy`, Render-Limits — `app/chat/context_policies.py`; Spalten `default_context_policy` auf `projects` / `chats` — `database_manager.py`.
- **Workflow-Ausführung:** eigene Kontextstrukturen — z. B. `app/workflows/execution/context.py` (nicht identisch mit Chat-Policy).
- **Projekt-Kontext in GUI:** `app/core/context/project_context_manager.py` (Wechsel-Listener, EventBus-Hinweis im Modul).

### B.10 `event`

- **Persistiert:** `audit_events` — `database_manager.py`; Typkonstanten — `app/core/audit/models.py` (`AuditEventType`).
- **Metriken:** `agent_metric_events` — `metrics_store.py`.
- **Laufzeit (Debug):** `app/debug/event_bus.py` (über `debug_store.py` / GUI angebunden) — **kein** Ersatz für auditierbare Geschäftsereignisse.

### B.11 `report`

- **Kein** zentrales `reports`-DB-Schema im untersuchten Umfang.
- **Tool-Reports** (Markdown/JSON) z. B. unter `tools/*_report*.py` — Repository-Werkzeuge.
- **QA-/Governance-Lesepfad:** `app/services/qa_governance_service.py` (JSON unter `docs/qa`).

### B.12 `audit`

- Tabelle `audit_events`, Service — `app/services/audit_service.py`, Repository — `app/core/audit/repository.py`.
- Incidents parallel — Tabelle `incidents` — `database_manager.py`; `app/services/incident_service.py` (nicht vollständig eingelesen, Existenz über Imports/Tests gesichert).

### B.13 `knowledge` / Docs

- **RAG:** `app/rag/models.py` (`Document`, `Chunk`), `app/rag/knowledge_models.py` (`KnowledgeEntry` — Self-Improving-RAG-Kontext).
- **Service:** `app/services/knowledge_service.py` — Spaces, `project_{id}`, `sources.json`, `collections.json` unter RAG-Base-Path.
- **Prompts als Wissen/Vorlagen:** `prompts`-Tabelle — `app/prompts/prompt_repository.py`; `prompt_type` inkl. `template` — `app/prompts/prompt_models.py`.

### B.14 Weitere relevante Domänenobjekte

- **`topics`**: Gruppierung von Chats innerhalb eines Projekts — `database_manager.py`.
- **Deployment:** `deployment_targets`, `deployment_releases`, `deployment_rollouts` — `database_manager.py`; GUI `app/gui/domains/operations/deployment/`; Audit-Typen in `AuditEventType`.
- **Scheduling:** `app/services/schedule_service.py` + `app/workflows/persistence/schedule_repository.py` (Fundstelle über Glob/Struktur; Detail: Schedule-Tabellen in `database_manager.py`).
- **Abteilungen (Agenten):** `Department` Enum — `app/agents/departments.py` (planning, research, development, media, automation, system).

---

## C. Bestehende Datenmodell-/Schema-Lage

### C.1 Monolithische SQLite-Datei, zwei Zugriffsmuster

- **URL / Pfad:** `app/persistence/session.py` → `get_database_url()` default `sqlite:///…/chat_history.db`.
- **Spur 1 — sqlite3 + handgeschriebene SQL:** `DatabaseManager` legt Tabellen an und migriert per `ALTER`/`CREATE IF NOT EXISTS` (`database_manager.py`).
- **Spur 2 — SQLAlchemy + Alembic:** `alembic/versions/phase_a_001_model_usage_foundation.py` erzeugt ORM-Tabellen (`model_usage_records`, `model_usage_aggregates`, `model_quota_policies`, `model_storage_roots`, `model_assets`).

### C.2 Tabellen-Inventar (aus CREATE-Statements im Code)

**In `database_manager.py`:**  
`chats`, `messages`, `projects`, `topics`, `project_chats`, `files`, `project_files`, `chat_files`, `workflows`, `workflow_runs`, `workflow_node_runs`, `workflow_schedules`, `schedule_run_log`, `audit_events`, `incidents`, `deployment_targets`, `deployment_releases`, `deployment_rollouts`, `project_milestones`.

**In separaten Repositories:**  
`agents` — `agent_repository.py`;  
`prompts`, `prompt_versions` — `prompt_repository.py`;  
`agent_metric_events` — `metrics_store.py`.

**ORM (Alembic + `app/persistence/orm/models.py`):** siehe C.1.

### C.3 Kein ORM für Kerndomäne „Projekt/Chat/Workflow“

Projekt-, Chat- und Workflow-Kern werden **nicht** über SQLAlchemy-Entities in `app/persistence/orm/models.py` abgebildet; dort liegt der Schwerpunkt auf **Modell-Nutzung und lokalen Modell-Dateien**.

---

## D. Bereits vorhandene projekt-/workflowrelevante GUI- und Service-Strukturen

### D.1 Navigation / Workspaces

- **Single Source of Truth:** `app/core/navigation/navigation_registry.py` — Einträge für Projekte, Chat, Knowledge, Prompt Studio, Workflows, Deployment, Betrieb (Audit/Incidents), Agent Tasks, Control Center, Runtime Debug, QA Cockpit, …
- **Operations-Subnav:** `app/gui/domains/operations/operations_nav.py` — feste Liste der Operations-Workspaces (Projekte → … → Agent Tasks).

### D.2 Services (Auswahl, nicht exhaustiv)

| Thema | Modul |
|-------|--------|
| Projekte | `app/services/project_service.py` |
| Workflows | `app/services/workflow_service.py` |
| Schedule | `app/services/schedule_service.py` |
| Knowledge/RAG | `app/services/knowledge_service.py` |
| Prompts | `app/prompts/prompt_service.py` |
| Agenten | `app/services/agent_service.py` |
| Audit | `app/services/audit_service.py` |
| Incidents | `app/services/incident_service.py` |
| Deployment | `app/services/deployment_operations_service.py` |
| QA-Ansicht | `app/services/qa_governance_service.py` |
| Modell-Kontingentierung | `app/services/model_quota_service.py` |
| Pipelines | `app/pipelines/services/pipeline_service.py` (in-memory) |

### D.3 Repositories / Manager / Registries

- **Repositories:** `workflow_repository`, `schedule_repository`, `AgentRepository`, `PromptRepository`, `AuditRepository`, `deployment/repository.py` (laut Projektstruktur).
- **Registries:** u. a. `app/core/models/registry.py` (Modelle), `app/workflows/registry/node_registry.py` (Workflow-Knotentypen), Tool-Registry-Erwähnung in Navigation (`cc_tools`).

---

## E. Architekturanschlüsse für die geplanten Ebenen

1. **Projekt-Ebene (Zielbild 2):** Bereits vorhanden: CRUD, Lebenszyklus, Budget/Aufwand, Meilensteine, Topic-Gruppierung, Projekt-Knowledge-Space, projektbezogene Prompts und Agenten (`project_id`).
2. **Portfolio-Ebene (Zielbild 1):** Kein Anschluss im Schema; flache `projects`-Liste. Ein Portfolio müsste **neu** als Entität oder Konvention eingeführt werden (nicht im IST-Code).
3. **Bereichs-/Produktions-Ebene (Zielbild 3):** Keine den sechs genannten Bereichen entsprechende Tabelle oder Enum. **Nächstliegende** textliche Struktur: `agents.department` + `Department.MEDIA`-Beschreibung (`departments.py`) — **ohne** feingranulare Domäne „Musik vs. Video vs. …“.
4. **Globale vs. projektbezogene Workflows:** `WorkflowDefinition.project_id` + JSON-Konsistenz beim Projekt-Löschen (`delete_project` in `database_manager.py`) — **direkter technischer Anschluss** für „globale“ vs. „projektgebundene“ Vorlagen.
5. **Workflow-Templates auf mehreren Ebenen:** Es gibt **gespeicherte Workflow-Definitionen** und **Prompt-Templates** (`prompt_type=template`). Eine **dritte hierarchische Template-Ebene** (Portfolio → Projekt → Bereich) ist **nicht** im Datenmodell ausgedrückt.
6. **Agenten-Hierarchie (Butler / Projekt / Fach):** Ein Agent ist ein Datensatz mit optionaler `project_id` und `department`; **keine** Typisierung als Butler vs. Fachagent im Schema. **Workflow-Bindings** als JSON legen nahe, dass **Orchestrierung über Workflows** stärker modelliert ist als „Agent-Rollenbaum“.
7. **Wissen:** Projektgebundener RAG-Space und `knowledge_spaces` auf Agent — **Anschluss** für pro Projekt / pro Agent; **kein** separates „Wissensgraph“-Produktmodell in der App-DB (QA-Knowledge-Graph existiert unter `scripts/qa/knowledge_graph/` als Skript-/QA-Domäne).

---

## F. Kollisionen / Lücken / Risiken

| Thema | Befund |
|-------|--------|
| **Begriff „Asset“** | Belegt durch `ModelAsset` und UI „lokale Assets“; kollidiert semantisch mit „Creative Asset“ im Zielbild. |
| **Begriff „Task“** | UI „Agent Tasks“ + Metrik-Feld `task_id` vs. PM-Tasks — hohe Verwechslungsgefahr bei Erweiterung. |
| **Begriff „Role“** | `ModelRole` = LLM-Routing, nicht Organisations-Rolle. |
| **Doppelte Persistenz-Spur** | sqlite3-Manager vs. SQLAlchemy auf derselben Datei — Erweiterungen müssen Migrationen **an beiden Stellen** oder durch klare Ownership-Regeln koordinieren (IST: so gewachsen). |
| **Pipeline vs. Workflow** | Zwei Ausführungsmodelle; Pipeline **ohne** DB-Persistenz — Risiko paralleler „Run“-Konzepte. |
| **Events** | `audit_events` (persistiert) vs. `EventBus` (Laufzeit/Debug) — verschiedene Lebensdauer und Zweck. |
| **Reporting** | Kein gemeinsames Report-Modell; QA-Daten in `docs/qa`, Audit getrennt, Metriken getrennt. |
| **Multi-User / Mandantenfähigkeit** | Keine Fundstelle für User-Accounts, ACLs oder Mandanten-ID in den untersuchten Kernschemas. |
| **Produktionsbereiche** | Keine Abbildung der genannten sechs Bereiche als Daten — nur grobe Agent-Abteilung optional. |

---

## G. Empfehlung: Wiederverwendbar vs. voraussichtlich neu

**Direkt wiederverwendbar (technisch, ohne Umbau in diesem Dokument):**

- Projekt-Entität inkl. Meilensteine, Budget-Felder, Lebenszyklus — `database_manager.py`, `project_service.py`, `projects/lifecycle.py`.
- Workflow-Definitionen, Runs, Node-Runs, Schedules inkl. GUI und Services.
- Agentenprofile inkl. `project_id` und JSON-Erweiterungsfelder.
- KnowledgeService / RAG pro Projekt (`project_{id}`).
- Audit + Incidents + Deployment-Tabellen als „Betrieb light“.
- Prompt-/Template-System (`prompts`, `prompt_versions`).

**Voraussichtlich neu oder fundamental zu erweitern (weil im IST nicht vorhanden oder semantisch anders):**

- Portfolio-/Programm-Ebene über Projekte hinweg.
- Explizite Produktionsbereiche (Musik, Video, …) inkl. Datenmodell und UI-Navigation.
- Einheitliches Aufgaben-/Issue-Modell (PM-Tasks), Abhängigkeiten, Zuweisung.
- Generisches „Creative Asset“-Modell mit Versionierung, Rechten, Ableitungen.
- Benutzer, Teams, Mandanten, ACLs / Policies auf Objektebene (über Modell-Quota hinaus).
- Einheitliches Reporting-Objekt (zusammenführend Audit, KPIs, Export).
- Dedizierte „Butler“- vs. „Fachagent“-Semantik (falls gewünscht) über reine Konvention hinaus.

---

## H. Mapping-Tabelle: Zielbegriff → IST

Legende **Qualität:** *stark* = durchgängig Schema+Service+GUI oder klarer Kernpfad; *teilweise* = existiert, aber andere Semantik oder Lücke; *fehlt* = keine belastbare Fundstelle im Anwendungskern.

| Soll-Begriff / Konzept | Existiert bereits? | Wo (Fundstellen) | Qualität | Empfehlung für spätere Erweiterung |
|------------------------|-------------------|------------------|----------|-------------------------------------|
| Portfolio / Programm | Nein | — | fehlt | Neu modellieren; nicht im IST |
| Projekt | Ja | `projects`, `ProjectService`, GUI Operations → Projekte | stark | Weiter nutzen als Anker |
| Produktionsbereich (Musik, Video, …) | Nein (als Domäne) | — | fehlt | Neu; `topics`/`department` nur schwache Analogie |
| Globaler Verwaltungs-Agent („Butler“) | Nein (als Typ) | Agenten allgemein `agents`-Tabelle | fehlt | Neu als Konvention/Typ oder eigene Entität |
| Projekt-Butler | Nein | `agents.project_id` optional | teilweise | Konvention möglich; kein IST-Typ |
| Bereichs-/Fachagent | Teilweise | `agents.department`, Workflow `agent`-Knoten | teilweise | Erweitern/verschärfen separat vom IST-Schema |
| Workflow (orchestriert) | Ja | `workflows`, `workflow_runs`, Services, GUI | stark | Primärer technischer Anker |
| Workflow-Template (mehrstufig) | Teilweise | Gespeicherte `WorkflowDefinition`; kein Portfolio-Layer | teilweise | Hierarchie neu definieren |
| Task (PM) | Nein | — | fehlt | Neu; nicht mit „Agent Tasks“ verwechseln |
| Run (Ausführung) | Ja | Workflow-Runs; Pipeline-Run nur RAM | stark/teilweise | Pipeline-Persistenz klären, falls relevant |
| Asset (Produktion) | Nein | `ModelAsset` / Datei-Tabellen = andere Bedeutung | Kollision | Neues Vokabular oder neues Modell |
| Datei / Workspace-Pfad | Ja | `files`, `project_files`, `chat_files` | stark | Für Dateibezug nutzbar |
| Modell (LLM) | Ja | `messages.model`, Registry, ORM Usage | stark | Bereits etabliert |
| Agent | Ja | `agents`, Services, GUI | stark | Erweiterbar über JSON-Spalten |
| Kontext (Chat) | Ja | `ChatContextPolicy`, DB-Spalten `default_context_policy` | stark | Nicht mit Workflow-Execution-Context verwechseln |
| Ereignis (fachlich auditierbar) | Ja | `audit_events` | stark | Anbinden für neue Domänen |
| Ereignis (Laufzeit) | Ja | `EventBus` / `DebugStore` | teilweise | Nur Debug/UX, nicht als Audit-Ersatz |
| Report (einheitlich) | Nein | QA JSON, Tool-Reports | fehlt | Neu oder zusammenführen |
| Audit | Ja | `audit_events`, `AuditService` | stark | Weiter nutzen |
| Wissen / Docs | Ja | RAG, `KnowledgeService`, Prompts | stark | Weiter nutzen |
| Milestone | Ja | `project_milestones` | stark | Weiter nutzen |
| Rollen / Rechte (Organisation) | Nein | — | fehlt | Neu |
| Policy (Kontingent) | Ja | `ModelQuotaPolicy` | stark | Nur Modell-Nutzung, nicht Objekt-ACL |
| Controlling (Budget/Zeit) | Teilweise | Budget/Aufwand/Meilensteine am Projekt | teilweise | Portfolio-/Bereichs-Kosten nicht modelliert |
| Vorlage / Template | Ja | Prompt `template`; Workflow-Definition als Vorlage | teilweise | Getrennte Welten im IST |

---

## I. Tests mit Bezug zu Architekturgrenzen (Auswahl, codebelegt)

| Bereich | Beispiel-Tests |
|---------|----------------|
| Projekte Phase B (Budget, Meilensteine) | `tests/test_projects_phase_b.py` |
| Projekt + Audit | `tests/unit/services/test_project_service_r1_audit.py` |
| ORM / Usage / Quota / lokale Registry | `tests/unit/test_phase_a_orm_services.py` |
| Workflows (Service, Repo, Executor, Serialization, …) | `tests/unit/workflows/test_*.py` (mehrere Dateien) |
| Audit-Service | `tests/unit/services/test_audit_service.py` |
| Agent-Operationen (Lesen) | `tests/unit/services/test_agent_operations_read_service.py` |
| GUI Workflows | `tests/unit/gui/test_workflow_*.py` |
| Scheduling | `tests/unit/scheduling/test_schedule_*.py` |

Diese Tests **fixieren** vor allem: SQLite-Migrationen/CRUD für Projekte, Workflow-Persistenz/Ausführung, ORM-Nutzungspfad für Modell-Assets/Quotas, Audit-Anbindung — **nicht** Portfolio- oder PM-Task-Logik (weil nicht implementiert).

---

*Ende des IST-Berichts.*

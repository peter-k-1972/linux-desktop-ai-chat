# Soll-Ist-Abgleich: Datenmodell PM-/Produktions-Plattform vs. Linux Desktop Chat

**Stand:** 2026-03-23  
**Methode:** Abgleich des Zielobjektkatalogs mit realen Tabellen, ORM-Entitäten, Services und bekannter GUI-Domänen im Repository. Keine Implementierung, kein Greenfield-Modell.

**Querschnitt:** Ergänzend konsultiert: `docs/analysis/PROJECT_MANAGEMENT_PLATFORM_IST_ANALYSIS.md`, `app/core/db/database_manager.py`, `app/persistence/orm/models.py`, `app/agents/agent_repository.py`, `app/agents/farm/`.

---

## A. Executive Summary

Das System besitzt bereits **ausgebaute, persistierte Kernpfade** für **Projekte** (inkl. Budget-/Aufwandsskalare und Meilensteine), **Workflow-Definitionen und -läufe** (`workflows`, `workflow_runs`, `workflow_node_runs`, Schedules), **Agentenprofile** (`agents` mit optionaler `project_id` und JSON-Ergänzungen), **Chat/Nachrichten**, **Dateipfade** (`files`/`project_files`), **Audit- und Incident-Objekte** sowie **Deployment-Historie**. Dazu kommt ein **separater ORM-Strang** (SQLAlchemy/Alembic) für **Modell-Nutzung, Quotas und lokale Modell-Dateien** (`model_usage_*`, `model_quota_policies`, `model_assets`).

**Nicht vorhanden** als relationales Erstklassobjekt sind: **Portfolio/Programm**, **Produktionsbereich** (`project_area`), **generisches Work-Item/Task**, **Creative-Asset mit Versionierung**, **Kostenjournal** (nur planerische Skalare am Projekt), **einheitliches Report-Objekt**, **normiertes Knowledge-/Dokumenten-Item in SQL**, **Review-/Freigabe-Workflow** und **generische Policy-Verknüpfung** (stattdessen: fachlich begrenzte Policies).

**Kritische semantische Kollision:** Der Begriff **„Asset“** ist im IST für **LLM-Modell-Artefakte** (`model_assets`) und **UI-/Workspace-Dateipfade** besetzt — nicht für Produktions-Assets im PM-Sinne.

**Evolutiv sinnvoll:** Erweiterungen **unterhalb** von `projects` (Bereiche, Aufgaben) und **Neben** bestehender Workflow-/Audit-Pfade, ohne die **Zwei-Wege-Persistenz** (sqlite3-`DatabaseManager` vs. SQLAlchemy) zu vernachlässigen.

---

## B. Bestehende relevante Entitäten

### B.1 SQLite (`DatabaseManager` und zugehörige Repositories)

| Tabelle / Objekt | Rolle im IST |
|------------------|--------------|
| `projects` | Zentrales Projekt inkl. `lifecycle_status`, Planungsdaten, `budget_*`, `estimated_effort_hours`, Kunden-/Referenzfelder |
| `project_milestones` | Meilensteine mit `status`, `target_date`, `sort_order` |
| `topics`, `project_chats`, `chats`, `messages` | Konversationsstruktur; `topics` gruppieren Chats im Projekt |
| `files`, `project_files`, `chat_files` | Verknüpfung von Pfaden mit Projekt/Chat |
| `workflows` | Workflow-Definition (`definition_json`, `project_id` optional) |
| `workflow_runs`, `workflow_node_runs` | Lauf und Knotenläufe mit Status und Payloads |
| `workflow_schedules`, `schedule_run_log` | Geplante Ausführung und Protokoll |
| `audit_events` | Append-only Ereignisse mit optional `project_id`, `workflow_id`, `run_id` |
| `incidents` | Störungs-/Fehlerobjekte (u. a. Workflow-Bezug) |
| `deployment_targets`, `deployment_releases`, `deployment_rollouts` | Release-/Rollout-Historie |
| `agents` | Agentenprofil (Persistenz in `AgentRepository`) |
| `prompts`, `prompt_versions` | Prompt-Bibliothek inkl. Projektbezug |
| `agent_metric_events` | Metrik-Events (inkl. optionalem `task_id` als Freitext) |

**Fundstelle:** `app/core/db/database_manager.py`, `app/agents/agent_repository.py`, `app/prompts/prompt_repository.py`, `app/metrics/metrics_store.py`.

### B.2 SQLAlchemy-ORM (gleiche DB-Datei, anderer Zugriffspfad)

| Entität | Rolle im IST |
|---------|--------------|
| `ModelUsageRecord`, `ModelUsageAggregate` | Nutzungs- und Aggregationsereignisse (Tokens, Kostenfelder optional) |
| `ModelQuotaPolicy` | Kontingent-/Policy-Regeln für Modellnutzung (Scope über `scope_type`/`scope_ref`) |
| `ModelStorageRoot`, `ModelAsset` | Inventar lokaler Modell-Dateien |

**Fundstelle:** `app/persistence/orm/models.py`, Alembic `alembic/versions/phase_a_001_model_usage_foundation.py`.

### B.3 Nicht-relational / Dateisystem / In-Memory (trotzdem fachlich „Objekte“)

| Konzept | IST |
|---------|-----|
| RAG-Dokumente/Chunks | Vector Store + Metadaten pro Space; Quellenlisten z. B. `sources.json` unter RAG-Pfad — `app/services/knowledge_service.py` |
| Pipeline-Runs | In-Memory im `PipelineService` — `app/pipelines/services/pipeline_service.py` (explizit keine DB-Persistenz Phase 1) |
| QA-/Governance-Daten | JSON unter `docs/qa` — `app/services/qa_governance_service.py` |
| Deklarative Agentenfarm-Rollen | JSON-Katalog — `app/agents/farm/default_catalog.json` + Loader |

---

## C. Terminologie-Mapping Ist ↔ Zielbild

| Zielbegriff | Ist-Name / Träger | Anschlussfähigkeit |
|-------------|-------------------|-------------------|
| **project** | `projects` | Direkt |
| **portfolio / program / project_group** | Keine Tabelle; implizit „alle Projekte“ in UI/Listen | Nur konzeptionell über neues Objekt oder Konvention |
| **project_area / production_area** | Kein Objekt; **Annäherung:** `topics` (Chat-Gruppierung), `agents.department`, ggf. Farm-`scope_level` `production_area` (deklarativ, nicht DB) | Schwach; fachlich nicht gleichwertig |
| **agent_definition** | Zeile in `agents` + Profil-Dataclass; **ergänzend** Farm-Katalog (`AgentFarmRoleDefinition`) | Teilweise: Runtime-Profil vs. deklarative Rolle |
| **agent_assignment** | Implizit: `agents.project_id`; keine generische Zuweisungstabelle (User, Rolle, Zeitraum) | Nur teilweise |
| **workflow_definition** | `workflows` + `WorkflowDefinition` (Code) | Direkt |
| **workflow_instance** | `workflow_runs` (+ `workflow_node_runs`) | Direkt (anderer Name) |
| **task / work_item** | Kein PM-Task; `agent_metric_events.task_id` (Freitext); Agent-Subsystem `Task`/`TaskGraph` für **interne Agentenplanung**, nicht SQL-PM | Gering; Begriffskollision mit „Agent Tasks“-UI |
| **asset** | `model_assets` (ORM); `files`; Verzeichnis `assets/` (Icons/Themes) | **Kollision** mit Ziel „Produktions-Asset“ |
| **asset_version** | Nicht als Entität; ggf. implizit über Dateipfad/Checksum bei `ModelAsset` | Fehlt für generische Assets |
| **milestone** | `project_milestones` | Direkt |
| **event** | `audit_events`; dazu Laufzeit-`EventBus` (Debug) | Audit-Teil direkt; Debug nicht fachlich gleich |
| **report** | Kein DB-Objekt; QA-/Tool-Reports verteilt | Fehlt als Einheit |
| **cost_entry / controlling_entry** | `projects.budget_amount` / Währung / `estimated_effort_hours`; `ModelUsageRecord` mit Kostenfeldern (LLM); `app/projects/controlling.py` = **Anzeige-Helfer**, kein Journal | Nur Aggregat/Ist-Kosten LLM, kein Controlling-Ledger |
| **knowledge_item / documentation_item** | RAG `Document`/`Chunk` (Code), Chroma o. Ä.; Prompts in SQL; Handbuch Markdown im Repo | Fragmentiert, größtenteils nicht normiert in einer PM-Tabelle |
| **review / approval** | `incidents` (Status-Lebenszyklus); `app/critic.py` ausdrücklich **nicht produktiv** für Review-Lauf | Kein Freigabe-/Review-Datenmodell |
| **policy / rule linkage** | `ModelQuotaPolicy`; `ChatContextPolicy` (Enum im Code); `agents.escalation_policy` (TEXT); Workflow-Validierung im `node_registry` | Stückweise; keine generische Policy-Engine in SQL |

---

## D. Fehlende Kernobjekte (relational klar)

1. **portfolio / program** — keine Eltern-Entität über `projects`.  
2. **project_area** — keine Untergliederung des Projekts für Produktion (nur `topics` für Chats).  
3. **work_item / task** — kein PM-Issue mit Status, Verantwortung, Relation zu Meilenstein/Asset.  
4. **production asset + version** — kein vom LLM-`ModelAsset` getrenntes Medien-/Deliverable-Modell.  
5. **report** (persistiert, referenzierbar) — nicht vorhanden.  
6. **cost_entry** (Ist-Kosten, Sammelbuchungen, Zuordnung zu Task/Projekt/Bereich) — nicht vorhanden; nur Plan-Skalare und LLM-Usage-Records.  
7. **agent_assignment** (explizit: wer/was/wann/gültig) — nicht vorhanden.  
8. **review / approval** (Schritt, Entscheid, Signatur) — nicht vorhanden.  
9. **Einheitliches knowledge_item in SQL** — Wissen hängt an RAG-Dateien und Prompts, nicht an einem PM-Dokumentenmodell.

---

## E. Kritische Kollisionen

| Bereich | Konflikt |
|---------|----------|
| **Asset** | Ziel „Produktions-Asset“ vs. IST `model_assets` + Chat-`files` + Repo-`assets/` |
| **Task** | Ziel „Work item“ vs. UI „Agent Tasks“ und Metrik `task_id` vs. Agent-interne `Task` |
| **Role** | Ziel Organisations-/Prozessrolle vs. `ModelRole` (LLM-Routing) |
| **Event** | Ziel Geschäftsereignis vs. Debug-EventBus vs. `audit_events` (gut, aber unterschiedliche Abdeckung) |
| **Workflow vs. Pipeline** | Zwei Ausführungskonzepte; Pipeline ohne DB — Gefahr doppelter „Instance“-Semantik |
| **Persistenz-Dualität** | Schema-Erweiterungen müssen klären: neue Tabellen über `DatabaseManager`-Migrationen **und/oder** Alembic — inkonsistente Ownership erhöht Migrationsrisiko |
| **Tests** | Bestehende Tests sichern u. a. Projekte Phase B, Workflows, Audit, ORM-Usage — neue Objekte ohne Brüche müssen dieselben Grenzen respektieren (`tests/test_projects_phase_b.py`, `tests/unit/workflows/`, `tests/unit/test_phase_a_orm_services.py`) |

---

## F. Evolutiver Erweiterungspfad in Phasen

**Phase F1 — Wenig invasiv, hohe Kohärenz mit IST**

- Neue Entitäten **unter** `projects`: z. B. `project_areas` (oder Umbenennung nach Produktvokabular) mit FK `project_id`.  
- Optional später: `portfolios` + `projects.portfolio_id` (nullable), um Bestandsprojekte nicht zu brechen.  
- **work_items** mit FK auf `project_id`, optional `project_milestone_id`, optional `project_area_id` — vor GUI-Tiefe Services + Migration + Tests.

**Phase F2 — Anbindung an vorhandene Orchestrierung**

- Verknüpfung **work_item** ↔ `workflow_runs` (z. B. optional `run_id` oder Verknüpfungstabelle), ohne Workflow-Kern zu duplizieren.  
- **agent_assignment** als eigene Tabelle oder erst als erweiterte Metadaten, sobald Klienten/Rollen im Produkt klar sind.

**Phase F3 — Asset- und Wissensmodell**

- **Neues** Produktions-Asset (anderer Tabellenname als `model_assets`, z. B. `production_assets`) inkl. Versionstabelle — explizit **nicht** `model_assets` überladen.  
- Knowledge: entweder weiter RAG-first mit **referenzieller** Brücke (ID in SQL → externer Store) oder schrittweise Normalisierung — jeweils mit klarem „Source of truth“.

**Phase F4 — Controlling & Reporting**

- **cost_entries** oder Nutzung von `ModelUsageRecord` nur für LLM-Kosten klar trennen von **Projekt-Ist-Kosten**.  
- **reports** als eigene Tabelle oder als generierte Artefakte mit Metadatenzeile (Speicherort, Typ, Bezug zu `project_id`).

---

## G. Empfehlung für einen ersten minimalen Ausbau

*(Empfehlung auf Planungsebene — keine Umsetzung in diesem Dokument.)*

1. **`portfolio_id` nullable auf `projects`** **oder** separate `portfolios`-Tabelle mit FK — minimal, rückwärtskompatibel, entspricht dem dringendsten strukturellen Loch zum Zielbild.  
2. **`project_areas` (oder äquivalent)** mit `project_id`, `name`, `type`/`slug` — technische Basis für „Bereichs-/Produktions-Ebene“, ohne sofort alle Medien-Domänen zu modellieren.  
3. **`work_items`** klein halten: `id`, `project_id`, `title`, `status`, `created_at`, optional `milestone_id` — erst danach Relationen zu Agenten/Workflows erweitern.

Damit lassen sich GUI und Services schrittweise anbinden, ohne Workflow- oder Agent-Tabellen sofort zu ändern.

---

## H. Empfehlung: vorerst außerhalb des ORM / der SQL-Kernmigration lassen

| Bereich | Begründung |
|---------|------------|
| **Workflow-Definition als JSON-Graph** | Bereits in `definition_json` etabliert; zusätzliche Template-Schichten können als JSON/YAML neben dem Code bleiben, bis Instanzen gebunden werden müssen. |
| **Agentenfarm-Katalog** | Bereits als JSON + Loader in `app/agents/farm/` — bis Mapping auf `agents` festliegt, nicht in SQLite duplizieren. |
| **Prompt-Templates / Prompt-Versionen** | Bereits `prompts`/`prompt_versions`; erweiterte „Dokumentationsvorlagen“ können zunächst dort oder im Repo bleiben. |
| **QA-/Governance-Reports** | Artefakt unter `docs/qa` + Leseservice — kein Zwang zur sofortigen `reports`-Tabelle. |
| **ChatContextPolicy / node_registry-Validierung** | Regeln als Code + Konfiguration sind im IST tragfähig; generische „Policy-Engine“ in SQL früh einzuführen, erzeugt hohe Komplexität bei geringem Nutzen in Phase 1. |
| **Pipeline-Definitionen** | In-Memory-Service — erst persistieren, wenn Produktpipelines feststehen und von Workflows abgegrenzt sind. |

---

## I. Priorisierte Matrix

*Risiko:* hoch = Kollision/technische Schuld; mittel = Migration/Service-Touch; niedrig = isolierte Ergänzung.  
*Einführung:* **jetzt** = kleiner, kompatibler DB-Schritt planbar; **später** = abhängig von Klärung; **nicht so** = bewusst nicht als SQL-Kern oder nicht ohne Begriffs-/Architekturklärung.

| Objekt | existiert bereits | Anschlussfähigkeit | Risiko | Empfohlene Einführung |
|--------|-------------------|--------------------|--------|------------------------|
| project | Ja (`projects`) | Hoch | Niedrig | jetzt (erweitern statt ersetzen) |
| portfolio / program | Nein | Mittel (FK auf Projekt) | Mittel | später / minimal jetzt (`portfolio_id`) |
| project_area | Nein | Mittel (neu unter Projekt) | Mittel | jetzt (schlanke Tabelle) |
| agent_definition | Ja (`agents` + Farm-JSON) | Hoch | Mittel (Duplikat vermeiden) | später (Mapping-Schicht) |
| agent_assignment | Implizit nur | Niedrig | Hoch (ohne User/Rollenmodell) | später |
| workflow_definition | Ja (`workflows`) | Hoch | Niedrig | jetzt (nur bei Bedarf erweitern) |
| workflow_instance | Ja (`workflow_runs`) | Hoch | Niedrig | jetzt (Benennung im Fachmodell angleichen) |
| task / work_item | Nein (PM) | Niedrig | Hoch (Begriff „Task“) | später / jetzt unter neuem Namen `work_item` |
| asset (Produktion) | Nein | Niedrig | **Hoch** (Kollision `model_assets`) | später + neuer Name |
| asset_version | Nein | — | Hoch | später |
| milestone | Ja (`project_milestones`) | Hoch | Niedrig | jetzt |
| event | Ja (`audit_events` + Debug) | Mittel | Mittel | später (einheitliches Fach-Event nur nach Schema-Design) |
| report | Nein | Niedrig | Mittel | später / zunächst Datei+Metadaten |
| cost_entry | Nein (Journal) | Teilweise (Budget-Skalare, LLM-Usage) | Mittel | später |
| knowledge_item | Fragmentiert (RAG, Prompts) | Mittel | Hoch (Store vs. SQL) | später (Referenzmodell) |
| documentation_item | Prompts, Repo-Docs | Mittel | Niedrig (außerhalb DB) | nicht so (SQL) zuerst |
| review / approval | Nein | Niedrig | Hoch | später |
| policy / rule linkage | Teilweise (Quota, Code) | Mittel | Hoch (generisch) | nicht so (generisches ORM) zuerst |

---

*Ende des Berichts.*

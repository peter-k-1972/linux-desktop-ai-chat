# Cursor-Ersatz light — Basissystem (Verdichtung des Bestands)

**Status:** Entscheidungs- und Planungsgrundlage (keine Implementierung in diesem Dokument).  
**Ziel:** Aus vorhandenen Seed-Agenten, Farm-Rollen, Workflow-Knoten und Referenztests eine **kanonische Agentenfamilie**, eine **kleine Workflow-Template-Bibliothek** und eine **Minimal-Tool-Schicht** ableiten — ohne neue Rollen zu erfinden, wo der Bestand bereits Träger liefert.

---

## 1. Kurzbericht

Das Projekt hat bereits **18 gleichwertig gepflegte Chat-Personas** (`seed_agents.py`), eine **DAG-Workflow-Engine** mit acht Knotentypen, **Referenz-DAGs in Tests**, **Chat-Delegation** (`/delegate`, `chain_delegate`) sowie **einzelne Tool-Anbindungen** (z. B. `rag`, `web_search`, `comfyui` an Profilen; generischer `tool_call`-Knoten). Für einen **Cursor-Ersatz light** fehlt vor allem eine **klare Hierarchie**: wenige Basistypen für den Alltag, Spezialisten explizit als Erweiterung; dazu **5 wiederverwendbare Workflow-Templates** aus den vorhandenen Bausteinen; und eine **knappe Tool-Schicht** (Filesystem, Suche, Git, Tests), die noch **nicht** als kanonische Executor-Typen an die Minimal-Familie gebunden ist.

**Sofort spielbar:** Chat mit **Developer**- und **Author**-Basistyp (Code/Debugger bzw. Documentation), **Research & Knowledge** mit RAG/Web, **Planner** plus `/delegate` für Zerlegung. **Nicht** ohne Weiteres Cursor-nah: geschlossene Schleife „Repo lesen → patchen → testen → committen“, weil die dafür nötigen Tools in den Profilen und Workflows noch nicht standardisiert sind.

---

## 2. Ausgewertete Quellen

| Quelle | Relevanz |
|--------|----------|
| `app/agents/seed_agents.py` | Autoritative 18 Agentenprofile (Rollen, Modelle, Capabilities, Tools, Knowledge Spaces) |
| `app/agents/farm/default_catalog.json` | Farm-/Butler-/QA-/Doku-Meta-Rollen (draft), Abgrenzung zu Chat-Seeds |
| `app/agents/agent_profile.py` | Felder für spätere Template-Zuordnung (capabilities, tools, workflow_bindings, …) |
| `app/core/models/roles.py` | `ModelRole` / Modellzuordnung |
| `app/workflows/models/definition.py` | `WorkflowDefinition`, Knoten/Kanten |
| `app/workflows/registry/node_registry.py` | Kanonische Knotentypen: `start`, `end`, `noop`, `prompt_build`, `agent`, `tool_call`, `context_load`, `chain_delegate` |
| `tests/unit/workflows/test_phase6_workflow_integration.py` | Referenz: prompt_build, agent, tool_call |
| `tests/unit/workflows/test_workflow_phase7_reference_e2e.py` | Referenz: lineare DAGs inkl. context_load, chain_delegate |
| `docs/FEATURES/workflows.md`, `docs/FEATURES/agents.md` | Abgrenzung Workflow-Editor vs. Chat-Ketten |
| `docs_manual/workflows/agent_usage.md` | `/delegate`, Agent-Auswahl |
| `docs/dev/CONTEXT_INSPECTION_WORKFLOW.md` | Kontext-Inspect als Prozess (lesend), Bezug zu `context_load` |

---

## 3. Kanonische Agentenfamilie (6 Basistypen)

Ziel: **6 Basistypen** statt 18 gleichrangiger Personas. Zuordnung erfolgt **nur** aus dem Seed-Bestand; keine neuen Rollennamen als Laufzeit-Agenten erforderlich — die Basistypen sind **Gruppierungs- und Template-Ebene** (Doku, Routing, spätere UI-Gruppierung).

### 3.1 Übersicht

| Basistyp | Seed-Agent(en) | Primärer Zweck |
|----------|----------------|----------------|
| **Planner** | Planner Agent | Aufgaben zerlegen, priorisieren, Vorbereitung für Delegation |
| **Analyst / Quality** | Critic Agent; anteilig Monitor Agent | Bewerten, Lücken, Logik, Qualität; Monitoring als analytische Lesart |
| **Research & Knowledge** | Research Agent, Knowledge Agent | Fakten, RAG, Wissensräume, Quellenbezug |
| **Developer** | Code Agent, Debugger Agent | Implementierung, Refactoring, Fehleranalyse |
| **Author / Documentation** | Documentation Agent | Technische Texte, README, API-Docs |
| **Automation & Integration** | Tool Agent, Workflow Agent, Scheduler Agent | Tool-Koordination, Medien-/ComfyUI-Pipelines, zeitliche Planung (abstrakt) |

**Spezialisten / spätere Erweiterung (bewusst nicht Basistyp):**

| Agent | Begründung |
|-------|------------|
| **Script Agent** | Enger Anwendungsfall (Skripte); kann unter **Developer** gebündelt werden, bleibt fachlich Spezialist. |
| **Voice, Image, Video, Music Agent** | Medien-Domäne; für Cursor-light irrelevant, weiterhin eigenständige Personas. |
| **System, Update, Recovery, Monitor Agent** | Betrieb/Infra; **Monitor** optional teilweise mit **Analyst / Quality** assoziiert, die vier bleiben **Operations-Spezialisten** außerhalb des Dev-Editor-Kerns. |

### 3.2 Pro Basistyp (Detail)

#### Planner

| Feld | Inhalt |
|------|--------|
| **Seed** | Planner Agent (`planner_agent`) |
| **Zweck** | Strukturierung komplexer Aufgaben, Plan vor Ausführung |
| **Typische Fähigkeiten** | `summarize`, `analysis` (laut Seed) |
| **Typische Eingaben** | Freitextaufgabe, Ziele, Constraints |
| **Typische Ausgaben** | Stufenpläne, Checklisten, priorisierte Schritte |
| **Spezialisten** | — |

#### Analyst / Quality

| Feld | Inhalt |
|------|--------|
| **Seed** | Critic Agent (`critic_agent`); Monitor Agent (`monitor_agent`) für Status/Anomalien-Lesart |
| **Zweck** | Kritik, Vollständigkeit, Widersprüche; ergänzend Beobachtung von Monitoring-Daten |
| **Typische Fähigkeiten** | `analysis`; Monitor zusätzlich `system_monitoring` |
| **Typische Eingaben** | Kandidatentexte, Anforderungen, Logs/Status (Monitor) |
| **Typische Ausgaben** | Findings, Verbesserungsvorschläge, strukturierte Einschätzung |
| **Spezialisten** | Farm-Rolle `farm.project.qa_review` ist inhaltlich parallel, aber **nicht** als Chat-Seed — spätere Verknüpfung, keine neue Fantasie-Rolle |

#### Research & Knowledge

| Feld | Inhalt |
|------|--------|
| **Seed** | Research Agent (`research_agent`), Knowledge Agent (`knowledge_agent`) |
| **Zweck** | Recherche, Faktenprüfung, antworten aus indexiertem Wissen |
| **Typische Fähigkeiten** | `research`, `rag`, `summarize`, `analysis` |
| **Typische Eingaben** | Fragen, Themen, Suchraum |
| **Typische Ausgaben** | Antworten mit Quellenbezug, strukturierte Rechercheergebnisse |
| **Spezialisten** | — (zwei Seeds = eine Familie mit Schwerpunkt web+RAG vs. rein Wissensraum) |

#### Developer

| Feld | Inhalt |
|------|--------|
| **Seed** | Code Agent (`code_agent`), Debugger Agent (`debugger_agent`); **Script Agent** als Erweiterung derselben Familie |
| **Zweck** | Code erzeugen/ändern, Bugs eingrenzen |
| **Typische Fähigkeiten** | `code`, `refactor`, `documentation`, `debug`, `analysis` |
| **Typische Eingaben** | Spezifikation, Stacktraces, Snippets |
| **Typische Ausgaben** | Codevorschläge, Fix-Vorschläge, Erklärungen |
| **Spezialisten** | Script Agent |

#### Author / Documentation

| Feld | Inhalt |
|------|--------|
| **Seed** | Documentation Agent (`documentation_agent`) |
| **Zweck** | Lesbare technische Dokumentation |
| **Typische Fähigkeiten** | `documentation`, `summarize` |
| **Typische Eingaben** | Thema, Zielgruppe, bestehende Rohfassung |
| **Typische Ausgaben** | README-Abschnitte, API-Beschreibungen, strukturierte Docs |
| **Spezialisten** | — |

#### Automation & Integration

| Feld | Inhalt |
|------|--------|
| **Seed** | Tool Agent (`tool_agent`), Workflow Agent (`workflow_agent`), Scheduler Agent (`scheduler_agent`) |
| **Zweck** | Koordination von Werkzeugen und Pipelines (inkl. ComfyUI), zeitliche Aufgaben (konzeptionell) |
| **Typische Fähigkeiten** | `workflow_creation` (Tool/Workflow/Scheduler), Medien beim Workflow Agent |
| **Typische Eingaben** | Tool-Spezifikation, Pipeline-Briefing |
| **Typische Ausgaben** | Ausführungspläne, strukturierte Koordinationsantworten |
| **Spezialisten** | Medien-Agenten bleiben außerhalb dieser Integrations-Familie für Cursor-light |

**Farm-Katalog (`default_catalog.json`):** Portfolio-/Projekt-/Bereichs-Butler sowie `knowledge_docs` / `reporting_controlling` sind **Meta-Orchestrierung** auf Portfolio-Ebene — **keine** Ersatz-Basistypen, sondern spätere **Zuordnungsebene** über bestehende Seeds (z. B. Planner + Research + Developer).

---

## 4. Workflow-Template-Bibliothek (5 Basistemplates)

Alle Templates nutzen **nur** vorhandene Knotentypen. Namen sind **konventionell**; technische IDs legt der Nutzer im Editor fest. Referenzimplementierungen: Phase-6/7-Tests (siehe Quellen).

### Template 1 — **Prepare → Execute → Review**

| Feld | Inhalt |
|------|--------|
| **Ziel** | Aufgabe formalisieren, mit passendem Agent ausführen, mit zweitem Agent (Review) gegenprüfen |
| **Typische Kette** | `start` → `prompt_build` → `agent` (Executor, z. B. Developer) → `agent` (Reviewer, z. B. Analyst/Critic-Slug) → `end` |
| **Inputs** | Variablen für `prompt_build` (z. B. Aufgabe, Kontext); ggf. `model_override` auf Agent-Knoten |
| **Outputs** | Letzter Agent-Output als `final_output`-Relevantes; Zwischenpayloads in Node-Runs |
| **Geeignete Basistypen** | Developer + Analyst/Quality; oder Research + Analyst |
| **Wiederverwendbarkeit** | Hoch — Kernmuster für qualitätsbewusste Einzelaufgaben |
| **Bestandsnähe** | Erweiterung von `ref_spa` (eine Agent-Stufe) um **zweiten** `agent`-Knoten |

### Template 2 — **Analyze → Decide → Document**

| Feld | Inhalt |
|------|--------|
| **Ziel** | Analyse, dann Entscheidung/Struktur, dann Dokumentation |
| **Typische Kette** | `start` → `prompt_build` → `agent` (Planner oder Research) → `prompt_build` (Entscheidungstemplate) → `agent` (Planner/Developer) → `agent` (Author) → `end` |
| **Inputs** | Fragestellung, Constraints, Stilvorgaben für Doku |
| **Outputs** | Analyse-Text, Entscheidungszusammenfassung, Dokumentationsartefakt |
| **Basistypen** | Planner, Research & Knowledge, Author |
| **Wiederverwendbarkeit** | Mittel (mehrstufig, aber linear) |
| **Bestandsnähe** | Kombination mehrerer `prompt_build` + `agent`; kein neuer Knotentyp |

### Template 3 — **Context Inspect**

| Feld | Inhalt |
|------|--------|
| **Ziel** | Chat-Kontext wie in Produktion auflösen und für Diagnose oder Prompting nutzen |
| **Typische Kette** | `start` → `context_load` → `end` **oder** → `prompt_build` → `agent` → `end` |
| **Inputs** | `chat_id`, optional `request_context_hint`, `context_policy` (siehe `context_load`-Validierung) |
| **Outputs** | `context_text` / Payload-Fragmente; optional LLM-Zusammenfassung |
| **Basistypen** | Analyst, Planner, Research (nachgelagert) |
| **Wiederverwendbarkeit** | Hoch für Support und „light“-Transparenz |
| **Bestandsnähe** | `ref_scl` in Phase-7-Tests; Parallele zu `docs/dev/CONTEXT_INSPECTION_WORKFLOW.md` |

### Template 4 — **Tool Run Pipeline**

| Feld | Inhalt |
|------|--------|
| **Ziel** | Deterministische oder skriptierte Schritte vor/nach LLM |
| **Typische Kette** | `start` → `prompt_build` (optional) → `tool_call` → `noop` (optional merge) → `end` |
| **Inputs** | Run-Payload für Executor; `executor_type` / `executor_config` am `tool_call`-Knoten |
| **Outputs** | `tool_result` im Payload; bei Kette mit Agent erweiterbar |
| **Basistypen** | Automation & Integration; Developer sobald Code-Tools angebunden |
| **Wiederverwendbarkeit** | Sehr hoch — **zentrales** Muster für Cursor-light nach Tool-Implementierung |
| **Bestandsnähe** | `ref_stc`, `p6_tc` |

### Template 5 — **Delegate / Orchestrate**

| Feld | Inhalt |
|------|--------|
| **Ziel** | TaskPlanner/ExecutionEngine ohne Chat-Widget — mehrteilige Aufgaben |
| **Typische Kette** | `start` → `prompt_build` → `chain_delegate` (`mode`: `plan_only` oder `execute`) → `end` |
| **Inputs** | Nutzeraufgabe im Prompt; optional `model_override`, `planner_model` |
| **Outputs** | `result_text`, `aggregated_output`, `graph_summary`, `delegation_metadata` (laut Stub/Engine) |
| **Basistypen** | Planner; Ausführung durch Engine den zugewiesenen Agenten |
| **Wiederverwendbarkeit** | Hoch für große Aufgaben; **komplementär** zu Chat-`/delegate` |
| **Bestandsnähe** | `ref_spcd`; Chat: `docs_manual/workflows/agent_usage.md` |

---

## 5. Minimal-Tool-Schicht (Kandidatenliste)

**Hinweis:** Die Engine hat den Knoten **`tool_call`** mit generischem `executor_type` — die folgende Liste beschreibt **sinnvolle Executor-/Tool-Abstraktionen** für Cursor-light, nicht implementierte Module.

| # | Tool-Kandidat | Zweck | Basistypen | Templates | Bestands-Ähnliches | Priorität |
|---|---------------|-------|------------|-----------|-------------------|-----------|
| 1 | **Workspace lesen** (Datei/Liste) | Ground Truth aus Repo | Developer, Research, Author | Tool Run, Prepare→Execute | `rag` liefert indexiertes Wissen, **nicht** rohes FS | **Sofort** für Cursor-light |
| 2 | **Workspace schreiben / Patch anwenden** | Änderungen materialisieren | Developer | Prepare→Execute→Review, Tool Run | — | **Sofort** |
| 3 | **Repo-Suche** (Text/Symbol) | Navigation ohne vollständiges Lesen | Developer, Research | Tool Run, Analyze→… | `rag` teilweise; kein Ersatz für Live-Suche | **Sofort** |
| 4 | **Tests / Befehl ausführen** | Verifikation | Developer, Analyst | Tool Run, nach Execute | `external_command_hooks` am Tool Agent leer | **Sofort** |
| 5 | **Git-Status / Diff lesen** | Änderungsüberblick, Review-Input | Developer, Analyst | Context-nah + Tool Run | — | **Hoch** |
| 6 | **Verzeichnisbaum / glob** | Scope für Refactors | Developer | Tool Run | — | **Mittel** |
| 7 | **Lint / statische Prüfung** (optional) | Schnelles Feedback | Analyst, Developer | nach Execute | — | **Mittel** |
| 8 | **web_search** (bereits) | Externe Fakten | Research | divers | Research Agent im Seed | **Bereits** (wo konfiguriert) |
| 9 | **rag** (bereits) | Indexiertes Wissen | Research, Developer, Author | divers | Mehrere Seeds | **Bereits** |
| 10 | **Structured validate** (z. B. JSON-Schema) | Pipeline-Gates | Analyst, Automation | Tool Run | generisch über `tool_call` möglich | **Später** |

**Kern für „light“:** die ersten **fünf** (1–5); ohne **1–2** bleibt das System ein reiner Chat-Assistent ohne Cursor-Nähe.

---

## 6. Lückenanalyse (produktive Nutzbarkeit)

### 6.1 Bereits produktiv nutzbar

- **Chat:** Developer-Basistyp (Code, Debugger), Author, Research & Knowledge (mit RAG/Web), Planner.
- **Orchestrierung:** `/delegate` und Workflow-Template **Delegate / Orchestrate** (`chain_delegate`).
- **Transparenz:** Context-Inspect-Template (`context_load`) und bestehende Context-Inspection-Doku.
- **Tool-Pipeline:** `tool_call` mit vorhandenen Executor-Typen (z. B. `python_callable` in Tests) — **produktiv** sobald sinnvolle Executor registriert sind (außerhalb dieses Dokuments).

### 6.2 Fehlend für erste interne „Cursor-Aufgaben“

- **Kanonische Bindung:** Basistypen und Templates sind hier **beschrieben**, aber noch **nicht** als UI-Gruppierung, Routing-Regeln oder gebündelte Presets abgebildet.
- **Filesystem + Patch + Suche + Git + Test-Runner** als **eine** abgestimmte Minimal-Schicht hinter `tool_call` (oder äquivalent).
- **Fertige Workflow-Presets** im Editor (nur Daten), die die 5 Templates als Startpunkte duplizierbar machen — ohne neue Engine-Features.

### 6.3 Größter Hebel — drei Punkte

1. **Workspace lesen + schreiben/patchen** — sonst kein editor-nahses Arbeiten.  
2. **Einheitliche Test-/Befehlsausführung** — sonst keine Vertrauenskette „Änderung funktioniert“.  
3. **Git-Status/Diff als Standard-Input** für Review- und Developer-Flows — sonst blindes Modellieren ohne Ist-Zustand.

---

## 7. Empfehlung

### 7.1 Sofort als „Cursor-Ersatz light“ spielbar

- **Mensch + Chat:** Developer + Author + Research + Planner wie heute.
- **Größere Aufgaben:** `/delegate` oder gespeicherter Workflow **Delegate / Orchestrate**.
- **Qualität:** Zweistufig im Workflow **Prepare → Execute → Review** (zwei `agent`-Knoten mit Critic-Slug), sobald im Editor nachgebaut.

Erwartungshaltung: **ohne** Tool-Schicht (Abschnitt 5, Punkte 1–2 mindestens) ist das **kein** Ersatz für Cursor im Sinne von Repo-Manipulation — nur ein **starker IDE-begleitender Chat**.

### 7.2 Nächster Ausbau (Reihenfolge)

1. **Minimal-Tool-Executor** hinter `tool_call`: lesen, schreiben/patchen, suchen ( drei zuerst ).  
2. **Git-Status/Diff** und **Testkommando** als vierte/fünfte Executor-Familie.  
3. **Editor-Presets** oder Doku-Verweise: die **5 Templates** als „Copy-from-doc“ oder einmalig importierbare JSON-Beispiele (separater Schritt, nicht Teil dieses Dokuments).  
4. **UI/Control Center:** Agentenliste nach **6 Basistypen** gruppieren (nur Darstellung/Routing-Hinweis, keine Änderung der Seed-Daten nötig für den Start).

---

## 8. Änderungshistorie

| Datum | Änderung |
|-------|----------|
| 2026-03-25 | Erstfassung: Verdichtung aus Seed-Agenten, Farm-Katalog, Workflow-Knoten und Referenztests |

# Workflows

Diese Seite beschreibt zwei verschiedene Dinge, die im Projekt „Workflow“ heißen:

1. **Workflow-Editor (Operations)** – gespeicherte, validierte **DAGs** aus Knoten, die über den **WorkflowService** ausgeführt und in SQLite persistiert werden.
2. **Chat-/System-Abläufe** – fest verdrahtete Pfade im Chat (RAG, Research, `/delegate`, …), **ohne** Bezug zum Workflow-Editor.

---

## Workflow-Editor (Operations → Workflows)

### Zweck

- Workflows **definieren**, **validieren**, **speichern** und **manuell testen** (Test-Run mit optionalem `initial_input`).
- Ausführung läuft **seriell** über einen **DAG** (keine parallelen Zweige in der Engine, keine Kanten-Bedingungen).
- **Kein** Ersatz für den Chat: Knoten nutzen Backend-Services (`AgentTaskRunner`, Kontext-Explainability, TaskPlanner/ExecutionEngine, Pipeline-Executors), nicht die Chat-Oberfläche.

### Oberfläche

| Bereich | Funktion |
|--------|----------|
| **Liste** | Gespeicherte Workflows (Spalte **Projekt**: „Global“ oder Projektname), Neu / Duplizieren / Löschen; Filterung nach aktivem Projekt siehe unten |
| **Tabellen-Editor** | Knoten und Kanten bearbeiten, Speichern, Validieren, JSON-Export |
| **Canvas** | Graphische Ansicht; Status-Overlay, wenn ein **Run** gewählt ist und passende **NodeRuns** existieren |
| **Inspector** (Dock) | `node_id`, Typ, Titel, `config` (JSON), Anwendung auf das Modell |
| **Run-Bereich** | Historie der Runs, NodeRuns, Ein-/Ausgabe-Payloads (JSON-Text), Sprung zum Knoten im Editor |

### Projektzuordnung

- Jeder gespeicherte Workflow ist **global** (`project_id` leer / in der Liste „Global“) oder einem **Projekt** zugeordnet.
- **Neuer Workflow:** Übernimmt standardmäßig das **aktive Projekt** (Kopfzeile / ProjectContextManager). Ohne aktives Projekt wird der Workflow **global** angelegt.
- **Liste:** Ist ein Projekt aktiv, erscheinen **dieses Projekt** und alle **globalen** Workflows. Ohne aktives Projekt werden **alle** Workflows angezeigt (kein Filter).
- **Editor:** Feld **Projekt** (Dropdown): Zuordnung ändern und speichern; globale Workflows sind bewusst **nicht** „kaputt“, sondern für alle Projekte nutzbar.
- Wechsel des aktiven Projekts **lädt die Liste neu**; ungespeicherte Änderungen am geöffneten Workflow bleiben erhalten (es erscheint ggf. keine Zeilenmarkierung in der Liste, wenn der Workflow zur anderen Zuordnung nicht passt).
- **Projekt löschen:** dem Projekt zugeordnete Workflows werden **nicht** gelöscht, sondern auf **global** gestellt (`project_id` entfällt in DB und in der gespeicherten Definition).

### Knotentypen (Stand Produktiv)

| `node_type` | Rolle |
|-------------|--------|
| `start` | Einstieg; genau **ein** aktiver Start pro Workflow |
| `end` | Abschluss; setzt `final_output`; mindestens ein aktives **End** |
| `noop` | Optional `config.merge` in die Payload |
| `prompt_build` | `template` / `prompt_text` / `prompt_id`, optional `variable_map` |
| `agent` | `agent_id` oder `agent_slug`, optional `model_override` |
| `tool_call` | `executor_type` + `executor_config` (z. B. `python_callable`) |
| `context_load` | Kontext über Explainability-Pfad; `chat_id` in Config oder Eingabe; optional `request_context_hint`, `context_policy` |
| `chain_delegate` | TaskPlanner + optional Ausführung; `mode`: `plan_only` oder `execute`; optional `model_override`, `planner_model` |

### Persistenz

- Definitionen und Runs liegen in der **App-Datenbank** (Tabellen `workflows`, `workflow_runs`, `workflow_node_runs`).
- Spalte **`workflows.project_id`**: `NULL` = global; sonst ID aus der Tabelle `projects`. Zusätzlich steht `project_id` in der serialisierten Definition (JSON).
- Bestehende Datenbanken: ältere Workflows werden bei Migration auf **`project_id` NULL** (global) gesetzt.
- Jeder Run speichert einen **Definition-Snapshot** zum Zeitpunkt des Starts (inkl. `project_id` im Snapshot; alte Runs passen nicht zwingend zur aktuell editierten Definition).

### Grenzen (ehrlich)

- **Keine** Auswertung von `edge.condition` in der Engine (Warnung bei der Validierung).
- **Kein** Human-in-the-loop, keine Script-Sprache für Bedingungen.
- **`context_load`** braucht eine gültige **`chat_id`** zur Laufzeit; ohne passenden Chat schlägt die echte Kontextauflösung fehl (Tests nutzen Adapter-Stubs).
- **`chain_delegate` / `execute`** braucht routbare Agenten in der Registry; ohne Zuordnung können Tasks fehlschlagen.
- **`cancel_run`** bricht **nur** Läufe ab, die noch **aktiv** im Service stehen (während `start_run` blockiert); bereits beendete Runs werden nicht zurückgesetzt.

### Siehe auch

- In-App-Hilfe: `help/operations/workflows_workspace.md` (Kontexthilfe Workspace **operations_workflows**).
- Entwickler: `docs/05_developer_guide/WORKFLOW_MODULE_QA_CHECKLIST.md` (manuelle Abnahme).

---

## Chat- und System-Abläufe (nicht Workflow-Editor)

Die folgenden Abläufe sind **fest im Chat bzw. in Services** verdrahtet und erscheinen **nicht** als gespeicherte Workflow-Dateien im Editor.

### Standard-Chat

```
User → Modell-Router → Orchestrator → Provider → LLM → Stream → UI
```

### RAG-Chat

```
User → RAGService.augment_if_enabled() → Retriever → Kontext
    → erweiterter Prompt → LLM → Stream → UI
```

### Research-Workflow

```
User → Planner → RAG Retriever → LLM → Critic → Antwort
```

Aktivierung u. a. Rolle „Research“ oder `/research`.

### Delegation im Chat (`/delegate`)

```
User → /delegate <Anfrage>
    → Task Planner → Task Graph
    → Delegation Engine → Agent-Zuordnung
    → Execution Engine (mit Chat-Anbindung)
    → aggregierte Antwort
```

### Self-Improving (optional)

```
LLM-Antwort → Knowledge Extractor → Validator → Vector-Space (z. B. self_improving)
```

---

## Task Graph (Begriff)

Im **Agenten-/Delegations-Code** (nicht zwingend im Workflow-Editor):

- **Task**: Beschreibung, Status, zugewiesener Agent  
- **TaskGraph**: DAG von Tasks  
- **Execution Engine**: führt Tasks nacheinander aus (Vorbereitung für spätere Parallelität)

Der Workflow-Knoten **`chain_delegate`** nutzt dieselbe Planner-/Engine-Basis, injiziert aber eine **Backend-`run_fn`** (ohne ChatWidget), siehe `workflow_orchestration_adapter`.

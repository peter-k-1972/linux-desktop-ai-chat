# Feature: Workflow-Editor (gespeicherte DAGs)

**Operations → Workflows** — eigener Workspace für **persistierte** Workflow-Definitionen (Knoten/Kanten), Validierung, Test-Run und Run-Historie. Workflows sind **global** oder einem **Projekt** zugeordnet (`workflows.project_id`, Feld im Editor). Implementierung: `app/workflows/`, `app/services/workflow_service.py`, GUI unter `app/gui/domains/operations/workflows/`.

## Abgrenzung

- **Nicht** dasselbe wie Chat-Slash-Commands (`/delegate`, `/research`, …) oder die „Ketten“ in [chains.md](chains.md) (Kontext-/Delegations-Pfade im Chat).
- **Kein** Scheduling, kein Human-Approval-Schritt, keine Auswertung von Kanten-Bedingungen in der Engine (siehe [Benutzerhandbuch – Workflows](../02_user_manual/workflows.md)).

## Inhalt

| Thema | Ort |
|-------|-----|
| Bedienung & Grenzen | [docs/02_user_manual/workflows.md](../02_user_manual/workflows.md) |
| In-App-Hilfe | `help/operations/workflows_workspace.md` |
| Manuelle QA | [WORKFLOW_MODULE_QA_CHECKLIST.md](../05_developer_guide/WORKFLOW_MODULE_QA_CHECKLIST.md) |
| Automatisierte Tests | `tests/unit/workflows/`, `tests/unit/gui/test_workflow_*` |

## Dev Assist Workflow

**ID:** `workflow.dev_assist.analyze_modify_test_review`  
**Definition:** `app/workflows/dev_assist_definition.py` (`build_dev_assist_workflow_definition`)  
**Hilfs-Callables:** `app/workflows/dev_assist_tools.py`

End-to-End-Entwicklungsassistenz auf Basis der bestehenden Workflow-Engine (ohne AWL): Zieldatei lesen (`cl.file.read`), Qualitätsanalyse und Planung per Agenten (`critic_agent`, `planner_agent`, `code_agent`, `documentation_agent`), Patch-Anwendung (`cl.file.patch`), Tests (`cl.test.run`), Review und kurze Doku. Marker `[DEV_ASSIST_PHASE=…]` in den Prompts erleichtern Tests und Tracing.

**Eingabe (mindestens):** `target_file`, `problem_description`; optional `test_scope`, `test_args`, `workspace_root` (Pflicht für die Cursor-light-Tools), optional `command_key` (Standard `pytest`).

**Ausgabe (End-Knoten):** strukturiert u. a. `analysis`, `plan`, `patch_applied`, `test_results`, `review`, `documentation` (plus `tool_result`/`logs` vom Finalisierungsschritt).

**Tests:** `tests/integration/workflows/test_dev_assist_workflow.py` — in temporärem Workspace Datei ändern und `pytest` ausführen (Agenten per `set_workflow_agent_sync_override`).

## Siehe auch

- [Feature: Prompts](prompts.md) — `prompt_build`-Knoten kann `prompt_id` nutzen  
- [Feature: Agenten](agents.md) — `agent`- und `chain_delegate`-Knoten  
- [Feature: Ketten](chains.md) — Abgrenzung Pipeline-Engine vs. Workflow-Editor  
- [Cursor-light Tools](../developer/CURSOR_LIGHT_TOOLS.md) — `tool_call` + `executor_type: cursor_light`  

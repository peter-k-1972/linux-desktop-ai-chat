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

## Siehe auch

- [Feature: Prompts](prompts.md) — `prompt_build`-Knoten kann `prompt_id` nutzen  
- [Feature: Agenten](agents.md) — `agent`- und `chain_delegate`-Knoten  
- [Feature: Ketten](chains.md) — Abgrenzung Pipeline-Engine vs. Workflow-Editor  

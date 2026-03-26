# Feature: Agenten

## Inhalt

- [Zweck](#zweck)
- [Funktionsweise](#funktionsweise)
- [Project Butler](#project-butler)
- [Project Butler im Chat](#project-butler-im-chat)
- [Konfiguration](#konfiguration)
- [Beispiel](#beispiel)
- [Typische Fehler](#typische-fehler)

**Siehe auch**

- [Feature: Chat](chat.md) · [Architektur – Agenten und Delegation](../ARCHITECTURE.md#23-agenten-und-delegation)  
- [Benutzerhandbuch – Delegation](../USER_GUIDE.md#55-delegation)

**Typische Nutzung**

- [Agenten (Workflow)](../../docs_manual/workflows/agent_usage.md)  
- [Hilfe: Agenten](../../help/operations/agents_overview.md) · [Control Center – Agents](../../help/control_center/control_center_agents.md)

## Zweck

Spezialisierte Rollen (Profile) für Aufgaben, Agent-Tasks und Orchestrierung – inklusive Delegation über `/delegate`.

## Funktionsweise

- **Paket:** `app/agents/` – Profile, Registry, Repository, Planner, Delegation Engine, Execution Engine, Task Runner.  
- **Services:** `app/services/agent_service.py`, Zugriff über `agents` in der Service-Infrastruktur.  
- **UI:**  
  - Operations → **Agent Tasks**  
  - Control Center → **Agents**  
- **Seed-Daten:** `app/agents/seed_agents.py` – wird vom Help-Generator (`app/help/doc_generator.py`) für die Tabelle „Agentenprofile“ genutzt.  
- **Slash-Command:** `/delegate <Prompt>` setzt `use_delegation=True` in `SlashCommandResult` (`app/core/commands/chat_commands.py`); die weitere Ausführung liegt im Chat-/Agentenpfad.

## Project Butler

**Zweck:** Einfache, deterministische Orchestrierungsschicht: Nutzeranfrage einlesen, per Heuristik einen passenden **Workflow** wählen und ihn ausschließlich über **`WorkflowService.start_run`** ausführen (kein Bypass der Workflow-Engine, kein Multi-Agent-Ausbau).

**Logische Agenten-ID / Profil:** `agent.project.butler` (Seed: `app/agents/seed_agents.py`, Slug `project_butler`). Die eigentliche Logik liegt in **`ProjectButlerService`** (`app/services/project_butler_service.py`).

**Unterstützte Workflows (Phase 1):**

| Workflow-ID | Einsatzzweck |
|-------------|----------------|
| `workflow.dev_assist.analyze_modify_test_review` | Codeänderungen, Bugfixes, Refactoring |
| `workflow.analyze_decide_document` | Analyse, Erklärung, Bewertung, Architektur (aktuell deterministischer Platzhalter-Knoten) |
| `workflow.context_inspect` | Kontext-, Debug- und „Warum“-Fragen (Platzhalter; später z. B. Inspection-Service) |

**Klassifikation:** Schlüsselwort-Listen mit fester Priorität (zuerst Dev-Assist, dann Analyse, dann Kontext). Erweiterbar über `ButlerClassificationRule` / Parameter `rules` an `classify_user_request` bzw. `ProjectButlerService.handle`.

**Beispiele (Aufruf):**

```python
from app.services.project_butler_service import ProjectButlerService
from app.services.workflow_service import get_workflow_service

butler = ProjectButlerService(get_workflow_service())
out = butler.handle(
    "Bitte den Parser-Bug fixen",
    optional_context={"workspace_root": "/pfad/zum/projekt", "target_file": "parser.py"},
)
# out: selected_workflow, reasoning, result (Run-Zusammenfassung oder no_workflow_matched / Fehler)
```

Voraussetzung: Die gewählten Workflow-Definitionen sind in der App-Datenbank gespeichert (wie jeder andere Workflow auch). Hilfsdefinitionen: `app/workflows/butler_support_definitions.py`, Dev-Assist: `app/workflows/dev_assist_definition.py`.

## Project Butler im Chat

**Wann es anspringt:** Über den bestehenden Sendepfad **`ChatPresenter.run_send_async`** (keine parallele Chat-Architektur). Butler aktiv, wenn die Nachricht mit **`/butler`** beginnt (Präfix wird abgeschnitten) **oder** eines dieser Wörter als Substring vorkommt: `fix`, `bug`, `refactor`, `analysiere`, `analyse`, `bewerte`, `erkläre`/`erklaere`, `context`, `debug`, `warum`. Andernfalls **unverändert** normales Chat-Modell (LLM-Stream).

**Phase-1-Workflows:** wie unter [Project Butler](#project-butler): `workflow.dev_assist.analyze_modify_test_review`, `workflow.analyze_decide_document`, `workflow.context_inspect` (Auswahl weiterhin über `ProjectButlerService` / `WorkflowService.start_run`).

**Kontext an den Butler:** `chat_id` (immer) und optional `workspace_root`, falls aus `list_workspace_roots_for_chat` ableitbar (`build_butler_optional_context` in `app/chat/butler_chat_integration.py`).

**Abschalten:** `LINUX_DESKTOP_CHAT_DISABLE_BUTLER=1`. **Hinweis:** Der deprecated Workspace-Sendeinstieg (`LINUX_DESKTOP_CHAT_LEGACY_CHAT_SEND=1`, siehe `docs/04_architecture/CHAT_SEGMENT_CLOSEOUT.md`) nutzt **keinen** Butler; der Standardpfad ist ChatPresenter.

## Konfiguration

Agenten sind persistiert (Datenbank/Repository). Modellzuweisung pro Profil über Felder wie `assigned_model` / Rollen (siehe Agenten-Modelle in `app/agents/agent_profile.py`).

## Beispiel

**Beispiel** — Profil und Delegation:

1. Control Center → Agents – Profil ansehen oder bearbeiten.  
2. Im Chat `/delegate Fasse die letzten drei Commits zusammen` senden.

## Typische Fehler

| Problem | Ursache |
|---------|---------|
| Leeres Agent-Dropdown | Repository nicht initialisiert oder DB leer – Neustart, Seed prüfen |
| Delegation reagiert nicht | Kein Text nach `/delegate`; oder Fehler im Agent-Pfad (Logs Runtime Debug) |

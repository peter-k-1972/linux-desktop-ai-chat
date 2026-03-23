# Agents

## Verwandte Themen

- [Chat](../chat/README.md) · [Kontext / Policies](../context/README.md) · [GUI](../gui/README.md)  
- [Ketten / Delegation](../../../docs/FEATURES/chains.md#3-delegation-kette-agenten) · [Feature: Agenten](../../../docs/FEATURES/agents.md)  
- [Workflow: Agenten](../../workflows/agent_usage.md)

## 1. Fachsicht

Das **Agenten-Subsystem** verwaltet **Profile**, **Aufgaben** und **Orchestrierung** (Planner, Delegation, Execution). Nutzer wählen Agenten im Chat oder nutzen **Operations → Agent Tasks** bzw. **Control Center → Agents**. Slash-Command **`/delegate`** aktiviert in der Command-Schicht `use_delegation=True` (`app/core/commands/chat_commands.py`); die weitere Ausführung liegt in den Agenten- und Chat-Pfaden.

**Paket:** `app/agents/`

## 2. Rollenmatrix

| Rolle | Nutzung |
|-------|---------|
| **Fachanwender** | Agent auswählen; Agent Tasks; `/delegate <Text>`. |
| **Admin** | Persistenz der Agent-Daten (SQLite/Repository-Kontext der App). |
| **Entwickler** | `agent_profile.py`, `agent_repository.py`, `planner.py`, `delegation_engine.py`, `execution_engine.py`, `agent_service.py`, … |
| **Business** | „Spezialisierte Assistenten“ und Aufgabenautomatisierung. |

## 3. Prozesssicht

### 3.1 Chat mit Agentenprofil

```
User wählt Agent (GUI)
        │
        ▼
AgentProfile (system_prompt, assigned_model / Rolle)
        │
        ▼
Gleicher Chat-Pfad wie Modul Chat → Provider
```

### 3.2 Delegation (Einstieg Slash-Command)

```
Eingabe: /delegate <Aufgabe>
        │
        ▼
parse_slash_command → use_delegation=True, remaining_text=Aufgabe
        │
        ▼
ChatService / Agenten-Pipeline
  (Planner → Task Graph → Delegation Engine → Execution Engine)
  — konkrete Aufrufkette in app/agents/*.py
```

**Relevante Dateien (Auswahl):** `planner.py`, `delegation_engine.py`, `execution_engine.py`, `orchestration_service.py`, `agent_task_runner.py`.

## 4. Interaktionssicht

**UI**

- `operations_agent_tasks` → `AgentTasksWorkspace` (`operations_screen.py`)
- `cc_agents` → `AgentsWorkspace` (`control_center_screen.py`)
- Chat: Agentenwahl je nach `chat_workspace.py`-Implementierung

**Services**

- `app/services/agent_service.py`
- Infrastruktur-Registrierung: `agents`, `agent_service` (siehe `docs/SYSTEM_MAP.md`)

**Seed / Hilfe**

- `app/agents/seed_agents.py` — u. a. für `app/help/doc_generator.py` (`generated_agents`)

## 5. Fehler- / Eskalationssicht

| Problem | Ursache |
|---------|---------|
| Leeres Agent-Dropdown | Repository/DB nicht befüllt; Seed fehlgeschlagen. |
| `/delegate` ohne Wirkung | Kein Text nach `/delegate` → nur Hinweis-`SlashCommandResult`. |
| Task hängt | Execution/Planner-Fehler; Logs unter Runtime Debug / Agent Activity. |

## 6. Wissenssicht

| Begriff | Ort |
|---------|-----|
| `AgentProfile` | `app/agents/agent_profile.py` |
| `AgentRepository` | `app/agents/agent_repository.py` |
| `operations_agent_tasks`, `cc_agents` | Workspace-IDs in `operations_screen.py`, `control_center_screen.py` |
| `use_delegation` | `SlashCommandResult` in `app/core/commands/chat_commands.py` |

## 7. Perspektivwechsel

| Perspektive | Fokus |
|-------------|--------|
| **User** | Agent Tasks, Chat-Agent, `/delegate`. |
| **Admin** | Datenhaltung Agent-Tabellen. |
| **Dev** | Orchestrierungsgraph, Fehlerpfade, Live-Tests `tests/live/`. |

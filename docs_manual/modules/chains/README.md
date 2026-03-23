# Chains

## Verwandte Themen

- [Kontext](../context/README.md) · [Agenten](../agents/README.md) · [Chat](../chat/README.md)  
- [Feature: Ketten](../../../docs/FEATURES/chains.md) · [Architektur – Datenfluss](../../../docs/ARCHITECTURE.md#2-datenfluss)

## 1. Fachsicht

Im Repository gibt es **kein** Top-Level-Paket oder Produktmodul mit dem Namen **chains**. „Ketten“ bezeichnet hier **mehrere unabhängige Ablaufketten**, die im Code vorkommen:

1. **Kontext-Override-Kette** — feste Priorität der Kontext-Konfiguration in `ChatService._resolve_context_configuration` (`app/services/chat_service.py`).
2. **Explainability `policy_chain`** — serialisierte Darstellung der Kontextentscheidung (`app/context/explainability/context_explanation_serializer.py`, Funktion `_policy_chain_to_dict`).
3. **Delegations-Kette** — Einstieg `/delegate` → `use_delegation` in `app/core/commands/chat_commands.py` → Agenten-Pipeline in `app/agents/` (Planner, Delegation, Execution).
4. **Pipeline-Engine** — generische Schritt-Ausführung in `app/pipelines/` (`engine`, `executors`, `services/pipeline_service.py`); Service-Name `pipeline_service` in `docs/SYSTEM_MAP.md`.

## 2. Rollenmatrix

| Rolle | Nutzung |
|-------|---------|
| **Fachanwender** | `/delegate`; ggf. Pipelines über zugehörige UI (falls angebunden). |
| **Admin** | Keine zentrale „Chain“-Konsole. |
| **Entwickler** | Prioritätsliste in `ChatService`, Serializer, Agenten-Module, `app/pipelines/`. |
| **Business** | Orchestrierung komplexer Aufgaben (Delegation); technische Pipelines getrennt betrachten. |

## 3. Prozesssicht

### 3.1 Kontext-Override-Kette

Siehe Modul **context** — `_PRIORITY_SOURCES`:

`profile_enabled` → `explicit_context_policy` → `chat_default_context_policy` → `project_default_context_policy` → `request_context_hint` → `individual_settings`.

### 3.2 policy_chain (Explainability)

```
ChatService / ContextExplainService
        │
        ▼
ContextExplanation / Trace
        │
        ▼
context_explanation_serializer._policy_chain_to_dict
        │
        ▼
JSON-Felder (deterministische Key-Reihenfolge laut Modul-Docstring)
```

### 3.3 Delegation

```
/parse → use_delegation + Text
        │
        ▼
Agenten: planner, delegation_engine, execution_engine (app/agents/)
```

### 3.4 Pipeline-Engine

```
PipelineDefinition / Run
        │
        ▼
Engine + Step-Executors (Shell, Python, … in app/pipelines/executors/)
```

## 4. Interaktionssicht

| Kette | UI | API / Code |
|-------|-----|------------|
| Kontext-Override | Settings → Advanced (nur Mode); Inspector/Debug | `ChatService` |
| policy_chain | QA-Observability / Introspection (Runtime-Workspaces) | Serializer, `context_explain_service` |
| Delegation | Chat-Eingabe `/delegate` | `chat_commands`, `app/agents/` |
| Pipelines | Aufrufer von `app/pipelines/services/pipeline_service.py` (nicht im Modulhandbuch einzeln aufgelistet) | `app/pipelines/` |

## 5. Fehler- / Eskalationssicht

| Problem | Kontext |
|---------|---------|
| Manuelle Kontext-Settings unwirksam | Höhere Priorität in Override-Kette aktiv. |
| policy_chain-Drift in Tests | Serializer-Änderung; QA-Dokus unter `docs/qa/`. |
| `/delegate` ohne Aktion | Leerer Resttext nach Command. |
| Pipeline-Schritt fehlgeschlagen | Executor oder Definition in `app/pipelines/`. |

## 6. Wissenssicht

| Begriff | Ort |
|---------|-----|
| `_PRIORITY_SOURCES` | `app/services/chat_service.py` |
| `policy_chain` | `app/context/explainability/context_explanation_serializer.py` |
| `use_delegation` | `app/core/commands/chat_commands.py` |
| `PipelineRun`, `PipelineDefinition` | `app/pipelines/models/` (Export in `app/pipelines/__init__.py`) |

## 7. Perspektivwechsel

| Perspektive | Fokus |
|-------------|--------|
| **User** | `/delegate` verstehen; Kontextmodus. |
| **Admin** | — |
| **Dev** | Keine Vermischung der vier Ketten; jeweils eigenes Paket lesen. |

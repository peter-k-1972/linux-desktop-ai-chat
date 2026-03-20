# EventBus-Governance – Policy

**Projekt:** Linux Desktop Chat  
**Referenz:** `docs/architecture/EVENTBUS_GOVERNANCE_ANALYSIS.md`  
**Tests:** `tests/architecture/test_eventbus_governance_guards.py`

---

## 1. Ziel

Event-Erzeugung, Event-Verbrauch und Event-Transport klar regeln. Schutz vor semantischer Drift, unkontrollierter Event-Nutzung und versteckten Kopplungen.

---

## 2. Erlaubte Event-Deklarationsorte

| Ort | Inhalt |
|-----|--------|
| **app/debug/agent_event.py** | EventType-Enum, AgentEvent-Dataclass |
| **app/gui/events/project_events.py** | EVENT_PROJECT_CONTEXT_CHANGED (separates System) |

**Regel:** Neue Event-Typen nur in agent_event.py (EventType). Keine freien Event-Strings.

---

## 3. Erlaubte Event-Namensräume

| Namensraum | Ort | Event-Typen |
|------------|-----|-------------|
| **AgentEvent / EventType** | app.debug.agent_event | TASK_CREATED, TASK_STARTED, TASK_COMPLETED, TASK_FAILED, AGENT_SELECTED, MODEL_CALL, TOOL_EXECUTION, RAG_RETRIEVAL_FAILED |
| **Project Events** | app.gui.events.project_events | project_context_changed |

---

## 4. Wer Events publizieren darf

| Modul | Erlaubt | Weg |
|-------|---------|-----|
| **app/agents/** | Ja | emit_event(), get_event_bus().emit() |
| **app/rag/** | Ja | emit_event() |
| **app/core/llm/** | Ja (Ausnahme) | emit_event() |
| **app/gui/legacy/chat_widget** | Ja | emit_event() |
| **app/metrics/** | Nein (nur Subscriber) | — |
| **app/services/** | Nein (außer agent_service nutzt get_debug_store lesend) | — |
| **app/providers/** | Nein | — |
| **app/debug/** | Nur emitter.py (intern) | emit_event() |

---

## 5. Wer Events konsumieren darf

| Modul | Erlaubt | Weg |
|-------|---------|-----|
| **app/debug/debug_store** | Ja | EventBus.subscribe() |
| **app/metrics/metrics_collector** | Ja (Ausnahme) | EventBus.subscribe() |
| **app/gui/** | Lesend über get_debug_store() | Kein direkter subscribe() |
| **app/services/agent_service** | Lesend über get_debug_store() | get_active_tasks, get_agent_status, get_event_history |

---

## 6. Welche Module den EventBus direkt kennen dürfen

| Modul | EventBus / get_event_bus | emit_event |
|-------|--------------------------|------------|
| app/debug/emitter | Ja | — (definiert) |
| app/debug/event_bus | Ja | — |
| app/debug/debug_store | Ja | — |
| app/agents/agent_task_runner | get_event_bus | — |
| app/metrics/metrics_collector | Ja | — |
| app/agents/* (execution_engine, orchestration_service, research_agent) | — | Ja |
| app/rag/* | — | Ja |
| app/core/llm/llm_complete | — | Ja (Ausnahme) |
| app/gui/legacy/chat_widget | — | Ja |

---

## 7. Welche Module den EventBus NICHT kennen dürfen

| Modul | Verbot |
|-------|--------|
| **app/providers/** | EventBus, emit_event, get_event_bus |
| **app/prompts/** | EventBus, emit_event |
| **app/tools/** | EventBus, emit_event |
| **app/utils/** | EventBus, emit_event |
| **Beliebige Domain-Panels** (außer chat_widget) | emit_event – nur über definierte Publisher |

---

## 8. Regeln für Debug-/Metrics-/Observability-Events

- **EventType:** Nur in agent_event.py erweitern; Architektur-Review bei neuen Typen
- **emit_event:** Nur in erlaubten Publisher-Modulen
- **DebugStore:** Muss alle EventType-Werte in _process_event berücksichtigen (oder explizit ignorieren)
- **MetricsCollector:** Filtert TASK_COMPLETED, TASK_FAILED, MODEL_CALL; neue Typen optional
- **Fehlertoleranz:** emit_event darf Hauptfunktion nicht beeinträchtigen (try/except)

---

## 9. Regeln gegen GUI-Shortcut-Kopplung

- **GUI darf nicht:** Beliebige Events an EventBus senden, um Services zu triggern
- **GUI darf:** get_debug_store() lesend nutzen; subscribe_project_events für Projekt-Kontext
- **Keine Abkürzung:** GUI → emit_event → Service-Logik. Events sind Observability, nicht Steuerung.

---

## 10. Regeln gegen Wildwuchs bei Event-Namen

- **Keine String-Literale** für Event-Typen außerhalb EventType-Enum
- **EventType erweitern:** Nur in agent_event.py; Guard prüft Konsistenz
- **project_events:** EVENT_PROJECT_CONTEXT_CHANGED ist einziger String; in project_events.py definiert

---

## 11. Regeln für neue Event-Typen / neue Event-Familien

1. EventType in agent_event.py erweitern
2. DebugStore._process_event ggf. anpassen (oder bewusst nur event_history)
3. MetricsCollector ggf. anpassen (wenn Metrik-relevant)
4. Guard-Konfiguration prüfen (KNOWN_EVENT_PUBLISHERS)
5. Architektur-Review

---

## 12. Ausnahmen

| Ausnahme | Begründung |
|----------|------------|
| core/llm → debug | emit_event für LLM-Tracing; optional, still bei Fehler |
| metrics → debug | MetricsCollector muss EventBus subscriben |
| core/context → gui | emit_project_context_changed (Project Events, nicht Debug EventBus) |

Neue Ausnahmen nur nach Architektur-Review.

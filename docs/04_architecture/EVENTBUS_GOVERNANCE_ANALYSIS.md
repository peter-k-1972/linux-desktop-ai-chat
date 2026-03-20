# EventBus-Governance – Analyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Kontext:** Event-/Debug-/Observability-System gegen Drift und unkontrollierte Kopplung absichern.

---

## 1. Beteiligte Module

### 1.1 Debug EventBus (zentrales Event-System)

| Modul | Pfad | Verantwortlichkeit |
|-------|------|--------------------|
| **EventBus** | `app/debug/event_bus.py` | Zentraler Bus: subscribe(), emit(), get_event_bus() |
| **AgentEvent** | `app/debug/agent_event.py` | Event-Struktur; EventType-Enum |
| **Emitter** | `app/debug/emitter.py` | emit_event() – Einstiegspunkt für Publisher |
| **DebugStore** | `app/debug/debug_store.py` | Subscriber; speichert Events, aggregiert für Debug-UI |
| **MetricsCollector** | `app/metrics/metrics_collector.py` | Subscriber; wandelt AgentEvents in AgentMetricEvents |

### 1.2 Project Events (separates System)

| Modul | Pfad | Verantwortlichkeit |
|-------|------|--------------------|
| **project_events** | `app/gui/events/project_events.py` | Eigenes Callback-System: subscribe_project_events, emit_project_context_changed |
| **ProjectContextManager** | `app/core/context/project_context_manager.py` | Publisher: emit_project_context_changed |

**Hinweis:** Project Events nutzen NICHT den Debug EventBus. Eigenes _project_listeners-Array.

### 1.3 Qt-Signale (nicht EventBus)

- GUI-Widgets nutzen PySide6 Signals (.emit()). Das ist ein separates System.
- Keine Vermischung mit EventBus.

---

## 2. Event-Erzeuger (Publisher)

| Modul | Event-Typen | Weg |
|-------|-------------|-----|
| **chat_widget** | MODEL_CALL, TOOL_EXECUTION | emit_event() |
| **agent_task_runner** | TASK_*, MODEL_CALL | get_event_bus().emit() |
| **execution_engine** | TASK_*, AGENT_SELECTED | emit_event() |
| **orchestration_service** | TASK_CREATED | emit_event() |
| **research_agent** | TASK_STARTED, TASK_COMPLETED | emit_event() |
| **llm_complete** | MODEL_CALL | emit_event() (core → debug, Ausnahme) |
| **rag/service** | RAG_RETRIEVAL_FAILED | emit_event() |
| **rag/retriever** | RAG_RETRIEVAL_FAILED | emit_event() |

---

## 3. Event-Verbraucher (Subscriber)

| Modul | Abonniert | Verwendung |
|-------|-----------|------------|
| **DebugStore** | EventBus.subscribe() | Speichert Events, liefert an Debug-UI |
| **MetricsCollector** | EventBus.subscribe() | TASK_COMPLETED, TASK_FAILED, MODEL_CALL → MetricsStore |

---

## 4. Event-Transportpfade

```
Publisher (emit_event / get_event_bus().emit())
    → EventBus.emit(AgentEvent)
        → DebugStore._on_event()
        → MetricsCollector._on_event()
```

- **Ein Bus:** Singleton EventBus
- **Ein Event-Typ:** AgentEvent mit EventType-Enum
- **Kein Topic-Filter:** Alle Subscriber erhalten alle Events; Filterung in Listener

---

## 5. Event-Namensräume / Event-Typen

**EventType (app/debug/agent_event.py):**

| Wert | Bedeutung |
|------|-----------|
| TASK_CREATED | Task erstellt |
| TASK_STARTED | Task gestartet |
| TASK_COMPLETED | Task abgeschlossen |
| TASK_FAILED | Task fehlgeschlagen |
| AGENT_SELECTED | Agent ausgewählt |
| MODEL_CALL | Modellaufruf |
| TOOL_EXECUTION | Tool ausgeführt |
| RAG_RETRIEVAL_FAILED | RAG-Abruf fehlgeschlagen |

**Keine String-basierten Event-Namen** – EventType ist Enum; typsicher.

---

## 6. Implizite Verträge

| Vertrag | Beteiligte | Inhalt |
|---------|------------|--------|
| Event-Struktur | AgentEvent | timestamp, agent_name, task_id, event_type, message, metadata |
| emit_event-Signatur | Emitter | event_type, agent_name, task_id, message, metadata |
| DebugStore-Verarbeitung | DebugStore | Verarbeitet alle EventType-Werte (außer RAG_RETRIEVAL_FAILED nur in event_history) |
| MetricsCollector | MetricsCollector | Nur TASK_COMPLETED, TASK_FAILED, MODEL_CALL |
| Fehlertoleranz | Emitter | try/except; Fehler still ignorieren (Debug darf Hauptfunktion nicht beeinträchtigen) |

---

## 7. Mögliche Drift-Risiken

| Risiko | Beschreibung | Wahrscheinlichkeit |
|--------|--------------|--------------------|
| **Neuer EventType ohne DebugStore** | EventType erweitert, DebugStore verarbeitet ihn nicht | Mittel |
| **Neuer EventType ohne MetricsCollector** | MetricsCollector filtert; neuer Typ wird ignoriert | Niedrig (akzeptabel) |
| **Wildwuchs bei emit_event-Aufrufen** | Beliebige Module rufen emit_event auf | Mittel |
| **GUI importiert debug direkt** | GUI nutzt get_debug_store, AgentEvent, EventType | Bereits der Fall – für Debug-UI notwendig |
| **core/llm → debug** | llm_complete importiert emit_event | Dokumentierte Ausnahme |
| **metrics → debug** | MetricsCollector importiert EventBus, AgentEvent | Dokumentierte Ausnahme |
| **services → debug** | agent_service importiert get_debug_store | Kein Verbot in FORBIDDEN_IMPORT_RULES |

---

## 8. Mögliche Layerverletzungen

| Verletzung | Status |
|------------|--------|
| core → debug | llm_complete: KNOWN_IMPORT_EXCEPTIONS |
| core → gui | project_context_manager: emit_project_context_changed; KNOWN_IMPORT_EXCEPTIONS |
| metrics → debug | MetricsCollector: KNOWN_IMPORT_EXCEPTIONS |
| services → debug | agent_service: get_debug_store – kein Verbot |
| gui → debug | runtime_debug, monitors: get_debug_store, AgentEvent – für Debug-UI erlaubt |
| debug → gui | FORBIDDEN: debug darf gui nicht importieren |

---

## 9. Mögliche zyklische Abhängigkeiten

| Abhängigkeit | Zyklus? |
|--------------|---------|
| debug → agents, rag, core, services | Nein – debug importiert diese nicht |
| agents → debug | Ja (emit_event, get_event_bus) |
| rag → debug | Ja (emit_event) |
| core/llm → debug | Ja (emit_event) |
| metrics → debug | Ja (EventBus, AgentEvent) |
| gui → debug | Ja (get_debug_store) |
| services → debug | Ja (get_debug_store) |

**Keine Zyklen innerhalb debug.** Debug ist Blatt (wird importiert, importiert nicht zurück).

---

## 10. Risiken durch String-basierte Events

**Gering:** EventType ist Enum. Keine freien Event-Strings. EventType.value wird nur für Serialisierung/Display genutzt.

---

## 11. Risiken durch unkontrollierte Subscriptions

| Risiko | Beschreibung |
|--------|--------------|
| Nur DebugStore und MetricsCollector subscriben | Kontrolliert |
| GUI subscribiert nicht direkt | GUI liest über get_debug_store().get_event_history() |
| Keine dynamischen Subscriptions aus beliebigen Modulen | Aktuell stabil |

---

## 12. Erlaubte vs. verbotene EventBus-Nutzung

| Aktion | Erlaubt in | Verboten in |
|--------|------------|-------------|
| emit_event() | agents, rag, gui/legacy/chat_widget, core/llm (Ausnahme) | — |
| get_event_bus() | debug (emitter, debug_store), agents (agent_task_runner), metrics (MetricsCollector) | — |
| EventBus.subscribe() | DebugStore, MetricsCollector | Beliebige GUI-Module (außer über DebugStore) |
| get_debug_store() | gui (runtime_debug, monitors), services (agent_service) | — |

---

## 13. Zusammenfassung

- **Ein EventBus:** Debug EventBus (AgentEvent)
- **Zwei Subscriber:** DebugStore, MetricsCollector
- **Viele Publisher:** agents, rag, chat_widget, core/llm
- **EventType-Enum:** Typsicher, kein String-Wildwuchs
- **Project Events:** Separates System, nicht EventBus
- **Drift-Hebel:** EventType nur in agent_event.py erweitern; emit_event nur in erlaubten Modulen; Guards für EventBus-Import, EventType-Konsistenz

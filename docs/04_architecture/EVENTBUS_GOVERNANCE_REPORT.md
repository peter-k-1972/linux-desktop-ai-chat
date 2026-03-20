# EventBus-Governance – Abschlussreport

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Status:** Freigabe

---

## 1. Analysierter Ist-Zustand

### 1.1 Event-Systeme

| System | Ort | Beschreibung |
|--------|-----|--------------|
| **Debug EventBus** | app/debug/ | AgentEvent, EventType, emit_event, EventBus, DebugStore, MetricsCollector |
| **Project Events** | app/gui/events/project_events | Eigenes Callback-System; kein EventBus |
| **Qt-Signale** | GUI-Widgets | PySide6 Signals; separates System |

### 1.2 Publisher (emit_event)

- agents: execution_engine, orchestration_service, research_agent, agent_task_runner
- rag: service, retriever
- core/llm: llm_complete (Ausnahme)
- gui/legacy: chat_widget

### 1.3 Subscriber

- DebugStore (EventBus.subscribe)
- MetricsCollector (EventBus.subscribe)

### 1.4 EventType-Enum

- TASK_CREATED, TASK_STARTED, TASK_COMPLETED, TASK_FAILED
- AGENT_SELECTED, MODEL_CALL, TOOL_EXECUTION, RAG_RETRIEVAL_FAILED

---

## 2. Gefundene Risiken

| Risiko | Bewertung | Maßnahme |
|--------|-----------|----------|
| Wildwuchs bei emit_event | Mittel | Guard: nur erlaubte Module importieren emitter |
| EventBus in beliebigen Modulen | Mittel | Guard: nur erlaubte Module importieren event_bus |
| providers/tools/prompts/utils → debug | Niedrig | Guard: FORBIDDEN_EVENTBUS_IMPORTER_PACKAGES |
| EventType außerhalb agent_event | Niedrig | Guard: EventType nur in agent_event.py definieren |
| debug → gui | Verboten | Guard: debug importiert nicht app.gui |
| project_events vermischt mit EventBus | Keiner | Guard: project_events importiert kein debug |
| EventType-Werte-Drift | Niedrig | Guard: erwartete EventType-Werte |

---

## 3. Implementierte Guards

| Guard | Test | Beschreibung |
|-------|------|--------------|
| **A** | test_emit_event_only_in_allowed_modules | emit_event nur in ALLOWED_EMIT_EVENT_IMPORTERS |
| **B** | test_eventbus_only_in_allowed_modules | EventBus/get_event_bus nur in ALLOWED_EVENTBUS_DIRECT_IMPORTERS |
| **C** | test_forbidden_packages_do_not_import_debug | providers, prompts, tools, utils importieren nicht app.debug |
| **D** | test_event_type_only_defined_in_agent_event | EventType-Enum nur in agent_event.py |
| **E** | test_debug_does_not_import_gui | debug importiert nicht app.gui |
| **F** | test_project_events_separate_from_debug_eventbus | project_events nutzt eigenes System |
| **G** | test_event_type_enum_has_expected_values | EventType enthält erwartete Werte |
| **H** | test_debug_store_and_metrics_collector_subscribe | DebugStore und MetricsCollector subscriben |

**Datei:** `tests/architecture/test_eventbus_governance_guards.py`  
**Markierung:** `@pytest.mark.architecture`, `@pytest.mark.contract`

---

## 4. Minimal-invasive Korrekturen

| Änderung | Datei | Beschreibung |
|----------|-------|--------------|
| ALLOWED_EMIT_EVENT_IMPORTERS | arch_guard_config.py | Erlaubte Module für emit_event |
| ALLOWED_EVENTBUS_DIRECT_IMPORTERS | arch_guard_config.py | Erlaubte Module für EventBus |
| FORBIDDEN_EVENTBUS_IMPORTER_PACKAGES | arch_guard_config.py | providers, prompts, tools, utils |

**Keine Änderungen am Produktivcode.**

---

## 5. Verbleibende Risiken

| Risiko | Status | Empfehlung |
|--------|--------|------------|
| core/llm → debug | Dokumentierte Ausnahme | KNOWN_IMPORT_EXCEPTIONS |
| metrics → debug | Dokumentierte Ausnahme | KNOWN_IMPORT_EXCEPTIONS |
| Neuer EventType | Manuell | Policy definiert Prozess |
| GUI nutzt get_debug_store | Erlaubt | Lesender Zugriff für Debug-UI |

---

## 6. Freigabe

**EventBus-Governance ist implementiert und abgesichert.**

- Analyse: `docs/architecture/EVENTBUS_GOVERNANCE_ANALYSIS.md`
- Policy: `docs/architecture/EVENTBUS_GOVERNANCE_POLICY.md`
- Guards: `tests/architecture/test_eventbus_governance_guards.py` (8 Tests)
- Config: `arch_guard_config.ALLOWED_EMIT_EVENT_IMPORTERS`, `ALLOWED_EVENTBUS_DIRECT_IMPORTERS`, `FORBIDDEN_EVENTBUS_IMPORTER_PACKAGES`

**Restpunkte:** Keine blockierenden.

# QA Level 3 – Risk-based Coverage Map

**Datum:** 15. März 2026  
**Basis:** Testsuite nach QA Level 2 (425 Tests ohne live/slow)  
**Zweck:** Maschinennahe Übersicht – welche Risikoarten sind abgedeckt, welche nicht?

---

## Legende

| Symbol | Bedeutung |
|--------|-----------|
| ✅ | Abgedeckt – Tests vorhanden |
| ⚠️ | Teilweise – Lücken oder schwache Abdeckung |
| ❌ | Nicht abgedeckt – Risiko sichtbar |

---

## 1. Workflow Coverage

| Workflow | Status | Tests / Domäne | Lücken |
|----------|--------|----------------|--------|
| Chat send → Antwort | ✅ | golden_path/test_chat_golden_path, smoke/test_full_workflow | – |
| Chat mit Agent | ✅ | golden_path/test_agent_in_chat_golden_path | – |
| Chat mit RAG | ✅ | golden_path/test_chat_rag_golden_path, integration/test_rag_chat_integration | – |
| Agent CRUD | ✅ | golden_path/test_agent_golden_path, ui/test_agent_hr_ui | – |
| Prompt CRUD + Apply | ✅ | golden_path/test_prompt_golden_path, ui/test_prompt_manager_ui | – |
| Debug Panel → Timeline | ✅ | golden_path/test_debug_panel_golden_path, cross_layer/test_debug_view_matches_failure_events | – |
| RAG Index → Retrieve | ✅ | golden_path/test_rag_golden_path | – |
| Modell wechseln | ✅ | integration/test_model_settings_chat | – |

**Gesamt:** ✅ Workflow Coverage gut abgedeckt.

---

## 2. Contract Coverage

| Vertrag | Status | Datei | EventType/Struktur |
|---------|--------|-------|--------------------|
| AgentEvent | ✅ | test_debug_event_contract | TASK_*, MODEL_CALL, TOOL_EXECUTION, RAG_RETRIEVAL_FAILED |
| LLM Stream Chunk | ✅ | test_llm_stream_contract | content, thinking, error, done |
| ToolExecutionEntry | ✅ | test_tool_result_contract | status: started, completed, failed |
| ResponseResult | ✅ | test_tool_result_contract | display_text, ResponseStatus |
| TaskInfo | ✅ | test_tool_result_contract | – |
| RAG Retrieval | ✅ | test_rag_retrieval_contract | – |
| Prompt | ✅ | test_prompt_contract | – |
| AgentProfile | ✅ | test_agent_profile_contract | – |

**Gesamt:** ✅ Contract Coverage vollständig für bekannte Strukturen.

**Drift-Risiko:** Neuer EventType ohne Contract-Test → Sentinel empfohlen (Phase 5).

---

## 3. Failure Coverage

| Fehlerszenario | Status | Datei | Fehlerklasse |
|----------------|--------|-------|--------------|
| Tool-Exception | ✅ | test_tool_failure | tool_failure_visibility |
| EventStore fehlende metadata | ✅ | test_event_store_failure | contract_schema_drift |
| DebugStore Trim | ✅ | test_event_store_failure | – |
| RAG Retrieval Exception | ✅ | test_rag_retrieval_failure | rag_silent_failure |
| ChromaDB Import-Fehler | ✅ | test_chroma_import_failure | optional_dependency_missing |
| LLM Chunk malformed | ✅ | test_llm_chunk_parsing_failure | contract_schema_drift |
| SQLite Lock | ✅ | test_sqlite_lock | – |
| EventBus Listener Exception | ✅ | test_event_bus_listener_error | – |
| RAG leere Ergebnisse | ✅ | test_rag_empty_results | – |
| Ollama kaputte Antwort | ✅ | test_ollama_broken_response | – |
| Metrics bei Task-Failure | ✅ | test_metrics_on_failed_chat_or_task | metrics_false_success |

**Gesamt:** ✅ Failure Coverage breit abgedeckt.

**Lücke:** ChromaDB nicht erreichbar (Netzwerk) – nur Import-Fehler getestet.

---

## 4. Async Coverage

| Szenario | Status | Datei | Fehlerklasse |
|----------|--------|-------|--------------|
| Shutdown während Task | ✅ | test_shutdown_during_task | _streaming nach Cancellation |
| Spätes Signal auf zerstörtes Widget | ✅ | test_signal_after_widget_destroy, test_chatwidget_signal_after_destroy | late_signal_use_after_destroy |
| Debug Clear während Refresh | ✅ | test_debug_clear_during_refresh | async_race |
| Agent-Wechsel während Stream | ✅ | test_agent_change_during_stream | – |
| Chat Streaming Behavior | ✅ | test_chat_streaming_behavior | – |
| RAG Chat Integration async | ✅ | test_rag_chat_integration | – |
| App Startup async | ✅ | test_app_startup | – |

**Gesamt:** ✅ Async Coverage für kritische Pfade vorhanden.

---

## 5. Cross-Layer Coverage

| Schichten | Status | Datei | Wahrheitsebene |
|-----------|--------|-------|----------------|
| Prompt Apply → Request | ✅ | test_prompt_apply_affects_real_request | UI ↔ Service ↔ Request |
| Debug View ↔ Failure Events | ✅ | test_debug_view_matches_failure_events | Store ↔ Timeline |
| Chat Header Agent | ✅ | test_chat_ui (cross_layer) | UI ↔ Service |
| Prompt Manager | ✅ | test_prompt_manager_ui | UI ↔ Service |
| Agent Delete | ✅ | test_agent_delete_removes_from_list | UI ↔ Service |

**Gesamt:** ✅ Cross-Layer für Kernworkflows abgedeckt.

---

## 6. Startup / Degraded Coverage

| Szenario | Status | Datei | Fehlerklasse |
|----------|--------|-------|--------------|
| RAG Service degraded (Chroma fehlt) | ✅ | test_app_starts_with_optional_dependencies_missing | degraded_mode_failure |
| MainWindow mit echtem ChatWidget | ✅ | smoke/test_app_startup | startup_ordering |
| Chat nutzbar nach degraded RAG | ✅ | test_app_starts_with_optional_dependencies_missing | – |

**Gesamt:** ✅ Startup/Degraded abgedeckt.

**Lücke:** Andere optionale Abhängigkeiten (z.B. Ollama nicht erreichbar) – nur RAG/Chroma getestet.

---

## 7. Debug / Observability Coverage

| Aspekt | Status | Datei | Hinweis |
|--------|--------|-------|---------|
| Event in Timeline sichtbar | ✅ | test_event_timeline_shows_event_content, test_debug_view_matches_failure_events | TASK_FAILED, RAG_RETRIEVAL_FAILED |
| Clear entfernt Events | ✅ | test_debug_panel_clear_removes_events | – |
| AgentActivity Task-Status | ✅ | test_agent_activity_shows_task_status | – |
| EventStore ↔ DebugStore | ✅ | test_debug_consistency | – |

**Gesamt:** ✅ Debug-Sichtbarkeit für Failure-Events abgedeckt.

**Drift-Risiko:** Neuer EventType ohne Timeline-Display → Sentinel empfohlen.

---

## 8. Metrics-under-Failure Coverage

| Szenario | Status | Datei | Fehlerklasse |
|----------|--------|-------|--------------|
| TASK_FAILED erhöht failed, nicht completed | ✅ | test_metrics_on_failed_chat_or_task | metrics_false_success |
| MODEL_CALL bei error ≠ TASK_COMPLETED | ✅ | test_metrics_on_failed_chat_or_task | – |
| avg_runtime nur aus TASK_COMPLETED | ✅ | test_metrics_on_failed_chat_or_task | – |
| Gemischte Failures/Completions | ✅ | test_metrics_on_failed_chat_or_task | – |

**Gesamt:** ✅ Metrics unter Failure abgedeckt.

---

## 9. Zusammenfassung – Coverage nach Risikoart

| Risikoart | Status | Priorität für Drift |
|-----------|--------|---------------------|
| Workflow Coverage | ✅ | – |
| Contract Coverage | ✅ | Hoch (neue EventTypes) |
| Failure Coverage | ✅ | Mittel (neue Services) |
| Async Coverage | ✅ | Mittel (neue async-Pfade) |
| Cross-Layer Coverage | ✅ | Hoch (neue Workflows) |
| Startup/Degraded | ✅ | Mittel (neue optionale Deps) |
| Debug/Observability | ✅ | Hoch (neue EventTypes) |
| Metrics-under-Failure | ✅ | – |

---

## 10. Bekannte Lücken (für Level-3-Sentinels)

| Lücke | Typ | Empfehlung |
|-------|-----|------------|
| Neuer EventType ohne Contract | Drift | Meta-Test: EventType-Liste vs. Contract-Test |
| Neuer EventType ohne Timeline-Display | Drift | Sentinel: event_timeline_view type_map |
| ChromaDB Netzwerk-Fehler | Failure | Optional: test_chroma_unreachable |
| Ollama nicht erreichbar | Startup | Optional: degraded_mode ohne Ollama |

---

*Coverage Map erstellt am 15. März 2026. Basis: QA_LEVEL2_REPORT.md, AUDIT_MATRIX.md, Projektcode.*

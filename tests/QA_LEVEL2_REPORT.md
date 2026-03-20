# QA Level 2 – Implementierungsbericht

**Datum:** 15. März 2026  
**Status:** Erste Iteration abgeschlossen  
**Teststand:** 386 Tests bestanden (ohne live/slow)

---

## 1. NEU ANGELEGT

### 1.1 tests/contracts/test_tool_result_contract.py

| Test | Fehlerklasse |
|------|--------------|
| `test_tool_execution_entry_has_required_fields` | ToolExecutionEntry-Struktur für DebugStore/UI |
| `test_tool_execution_entry_status_values` | status: started, completed, failed |
| `test_task_info_has_required_fields` | TaskInfo für AgentActivityView |
| `test_response_result_has_required_fields` | ResponseResult für OutputPipeline/ChatWidget |
| `test_response_result_display_text_on_success` | display_text() bei Erfolg |
| `test_response_result_display_text_on_failure` | display_text() bei Fehler |
| `test_response_status_values_stable` | ResponseStatus-Enum Stabilität |

### 1.2 tests/failure_modes/test_event_store_failure.py

| Test | Fehlerklasse |
|------|--------------|
| `test_debug_store_handles_event_with_missing_metadata` | Event mit leerer metadata crasht nicht |
| `test_debug_store_trim_at_max_history` | Trim-Logik, clear() funktioniert |

### 1.3 tests/failure_modes/test_tool_failure.py

| Test | Fehlerklasse |
|------|--------------|
| `test_tool_exception_returns_error_text_instead_of_crashing` | Tool-Exception → Fehlermeldung, kein Crash |
| `test_tool_exception_emits_failed_event` | Tool-Exception → emit_event mit status "failed" |

---

## 2. GEÄNDERT / VERBESSERT

### 2.1 tests/async_behavior/test_shutdown_during_task.py

**Vorher:** `test_run_chat_cancellation_cleans_up` prüfte nur `assert widget is not None` (kosmetisch).

**Nachher:** Prüft `_streaming is False` nach Task-Cancellation. Verhindert Regression: UI bleibt in Streaming-State hängen, zweiter Send blockiert.

**Diagnostik:** Bei Fehlschlag wird `dump_streaming_state(widget)` in die Fehlermeldung eingebettet.

### 2.2 tests/helpers/diagnostics.py

**Neu:** `dump_streaming_state(widget)` – gibt Streaming-Status für Async-Tests aus.

### 2.3 tests/helpers/test_diagnostics.py

**Neu:** `test_dump_streaming_state_none`, `test_dump_streaming_state_with_widget`.

---

## 3. ERSETZT

Keine Tests ersetzt (nur bestehende gehärtet).

---

## 4. OFFEN / NÄCHSTE SCHRITTE

| Priorität | Bereich | Beschreibung |
|-----------|---------|--------------|
| 1 | **Async** | `test_spaetes_signal_auf_zerstoertes_widget` – spätes Signal auf zerstörtes Widget |
| 2 | **Failure** | `test_chroma_db_unavailable` – ChromaDB nicht erreichbar |
| 3 | **Schwache Tests** | `test_conversation_view_add_message` – count() > 0 → sichtbarer Text prüfen |
| 4 | **Contract** | `test_llm_chunk_structure` – Stream-Chunk-Pflichtfelder |
| 5 | **Cross-Layer** | `test_prompt_apply_requested_signal_emits` – bereits P1, prüfen ob ausreichend |

---

## 5. MARKER / CI

Bereits in pytest.ini vorhanden:

- `@pytest.mark.contract`
- `@pytest.mark.async_behavior`
- `@pytest.mark.failure_mode`
- `@pytest.mark.cross_layer`

**CI-Empfehlung:** `pytest -m "not live and not slow"` als Standard-Check.

---

## 6. ZUSAMMENFASSUNG

| Metrik | Wert |
|--------|------|
| Neue Tests | 13 |
| Verbesserte Tests | 1 |
| Neue Diagnose-Helper | 1 |
| Abgedeckte Fehlerklassen | Tool-Exception, EventStore-Metadata, DebugStore-Trim, _streaming nach Cancellation, Tool/Response/Event Contracts |

---

# QA Level 2 – Iteration 2

**Datum:** 15. März 2026  
**Status:** Abgeschlossen  
**Teststand:** 398 Tests bestanden (ohne live/slow)

---

## 1. NEU ANGELEGT (Iteration 2)

### 1.1 tests/async_behavior/test_signal_after_widget_destroy.py

| Test | Fehlerklasse |
|------|--------------|
| `test_signal_after_widget_destroy_no_crash` | late signal → use-after-destroy |
| `test_signal_before_destroy_delivered` | Kontrolltest: Signal vor Zerstörung |

### 1.2 tests/contracts/test_llm_stream_contract.py

| Test | Fehlerklasse |
|------|--------------|
| `test_extract_chunk_parts_accepts_content_chunk` | LLM-Stream-Schema |
| `test_extract_chunk_parts_accepts_thinking_only_chunk` | thinking-only Chunk |
| `test_extract_chunk_parts_accepts_error_chunk` | error-Chunk |
| `test_extract_chunk_parts_handles_missing_message` | fehlendes message |
| `test_extract_chunk_parts_handles_message_none` | message=None |
| `test_chunk_done_field_used_by_chat_widget` | done-Feld |
| `test_valid_chunk_structures_are_stable` | stabile Chunk-Strukturen |

### 1.3 tests/failure_modes/test_rag_retrieval_failure.py

| Test | Fehlerklasse |
|------|--------------|
| `test_rag_service_handles_retrieval_exception` | RAG subsystem failure |
| `test_rag_failure_emits_event` | RAG-Failure-Event im DebugStore |
| `test_chat_continues_when_rag_fails` | Chat läuft weiter bei RAG-Fehler |

---

## 2. GEÄNDERT (Iteration 2)

### 2.1 App-Code

- **app/debug/agent_event.py:** `EventType.RAG_RETRIEVAL_FAILED` ergänzt
- **app/rag/service.py:** `emit_event(RAG_RETRIEVAL_FAILED)` bei Exception in `augment_if_enabled`
- **tests/contracts/test_debug_event_contract.py:** `RAG_RETRIEVAL_FAILED` in Stabilitätstest

### 2.2 Schwache Tests gehärtet

| Test | Vorher | Nachher |
|------|--------|---------|
| `test_conversation_view_add_message` (ui) | count() >= 1 | + sichtbarer Text, role |
| `test_conversation_view_add_assistant_message` | msg is not None | + sichtbarer Inhalt |
| `test_conversation_view_add_message` (smoke) | count() >= 1 | + bubble.text() Inhalt |

---

## 3. OFFENE RISIKEN (nach Iteration 2) → in Iteration 3 behoben

| Priorität | Risiko | Iteration 3 |
|-----------|--------|-------------|
| 1 | Chunk mit `message` als Nicht-Dict | Abgedeckt |
| 2 | ChromaDB-Import-Fehler | Abgedeckt |
| 3 | Spätes Signal auf ChatWidget | Abgedeckt |

---

# QA Level 2 – Iteration 3

**Datum:** 15. März 2026  
**Status:** Abgeschlossen  
**Teststand:** 413 Tests bestanden (ohne live/slow)

---

## 1. NEU ANGELEGT (Iteration 3)

### 1.1 tests/failure_modes/test_llm_chunk_parsing_failure.py

| Test | Fehlerklasse |
|------|--------------|
| `test_extract_chunk_parts_message_is_string` | LLM stream schema drift |
| `test_extract_chunk_parts_message_is_list` | malformed chunk input |
| `test_extract_chunk_parts_chunk_is_none` | chunk=None |
| `test_extract_chunk_parts_chunk_is_string` | chunk=str |
| `test_extract_chunk_parts_chunk_is_list` | chunk=list |
| `test_extract_chunk_parts_content_missing_in_message` | content fehlt |
| `test_extract_chunk_parts_thinking_missing_in_message` | thinking fehlt |
| `test_extract_chunk_parts_error_takes_precedence_over_message` | error vs message |
| `test_extract_chunk_parts_empty_dict` | leeres Chunk |

### 1.2 tests/failure_modes/test_chroma_import_failure.py

| Test | Fehlerklasse |
|------|--------------|
| `test_vector_store_raises_vector_store_error_on_import_error` | Optional dependency missing |
| `test_retriever_returns_empty_on_vector_store_error` | degraded RAG mode |
| `test_rag_service_degrades_when_chroma_unavailable` | RAG sauber deaktiviert |
| `test_vector_store_error_message_mentions_chromadb` | hilfreiche Fehlermeldung |

### 1.3 tests/async_behavior/test_chatwidget_signal_after_destroy.py

| Test | Fehlerklasse |
|------|--------------|
| `test_chatwidget_late_signal_no_crash` | late signal / use-after-destroy |
| `test_chatwidget_signal_during_destroy_no_crash` | async UI race |

---

## 2. GEÄNDERT (Iteration 3)

### 2.1 Produktionscode – defensive Guards

- **app/chat_widget.py**
  - `_extract_chunk_parts`: Guards für chunk=None, chunk nicht Dict, message nicht Dict
  - `on_update_chat`: try/except RuntimeError
  - `_safe_emit_update`: neuer Helper, alle update_chat_signal.emit in run_chat ersetzt
  - `run_chat`: try/except RuntimeError um _get_active_agent, finally-Block

### 2.2 Diagnostik

- **tests/helpers/diagnostics.py:** `dump_chunk_state`, `dump_rag_state` ergänzt

---

## 3. ABGEDECKTE RISIKEN (Iteration 3)

| Risiko | Status |
|--------|--------|
| Chunk mit message als Nicht-Dict | Abgedeckt |
| ChromaDB-Import-Fehler | Abgedeckt |
| Spätes Signal auf ChatWidget | Abgedeckt |

---

## 4. VERBLEIBENDE RISIKEN

- Keine kritischen offenen Risiken aus dem Sprint

---

# QA Level 2 – Iteration 4

**Datum:** 15. März 2026  
**Status:** Abgeschlossen  
**Teststand:** 425 Tests bestanden (ohne live/slow)

---

## 1. NEU ANGELEGT (Iteration 4)

### 1.1 tests/cross_layer/test_prompt_apply_affects_real_request.py

| Test | Fehlerklasse |
|------|--------------|
| `test_prompt_apply_affects_real_request` | UI says prompt applied, backend request uses wrong or stale prompt |
| `test_prompt_apply_no_stale_after_second_apply` | Zweiter Prompt-Apply ersetzt – kein stale erster Prompt |

### 1.2 tests/cross_layer/test_debug_view_matches_failure_events.py

| Test | Fehlerklasse |
|------|--------------|
| `test_task_failed_event_visible_in_timeline` | Debug view lies or omits failure events |
| `test_rag_retrieval_failed_event_visible_in_timeline` | RAG-Failure in Timeline sichtbar |
| `test_debug_panel_timeline_matches_store` | Store vs. View Diskrepanz |

### 1.3 tests/startup/test_app_starts_with_optional_dependencies_missing.py

| Test | Fehlerklasse |
|------|--------------|
| `test_main_window_starts_with_rag_service_degraded` | optional dependency missing breaks startup |
| `test_chat_available_after_startup_with_degraded_rag` | Chat nutzbar nach Startup mit fehlender Chroma |
| `test_main_window_starts_with_real_rag_service_no_chroma_import` | Chroma-Import lazy, nicht beim Start |

### 1.4 tests/failure_modes/test_metrics_on_failed_chat_or_task.py

| Test | Fehlerklasse |
|------|--------------|
| `test_task_failed_increases_failed_not_completed` | failure path corrupts or falsifies metrics |
| `test_mixed_failures_and_completions_metrics_correct` | Vermischung completed/failed |
| `test_model_call_on_failure_does_not_increase_completed` | MODEL_CALL mit error ≠ TASK_COMPLETED |
| `test_runtime_plausible_on_failure` | avg_runtime nur aus TASK_COMPLETED |

---

## 2. GEÄNDERT (Iteration 4)

### 2.1 tests/helpers/diagnostics.py

**Neu:** `dump_prompt_request_state`, `dump_debug_failure_state`, `dump_startup_mode_state`, `dump_metrics_state`

### 2.2 pytest.ini

**Neu:** Marker `startup` für Startup-Tests

---

## 3. ABGEDECKTE ZIELBEREICHE

| Bereich | Status |
|---------|--------|
| Cross-Layer Prompt Truth | Abgedeckt |
| Debug Truth / Failure Event Visibility | Abgedeckt |
| Startup in Degraded Mode | Abgedeckt |
| Metrics unter Failure Conditions | Abgedeckt |

---

## 4. ZUSAMMENFASSUNG ITERATION 4

| Metrik | Wert |
|--------|------|
| Neue Tests | 12 |
| Neue Dateien | 4 |
| Erweiterte Diagnostik | 4 Helper |
| Testanzahl (ohne live/slow) | 425 |

---

## 5. EMPFEHLUNG

**QA Level 2 kann als abgeschlossen gelten.** Die vier Zielbereiche der Iteration 4 sind vollständig abgedeckt. Keine neuen Features, kein Audit, keine großen Refactorings – ausschließlich Tests mit echtem Fehlererkennungswert.

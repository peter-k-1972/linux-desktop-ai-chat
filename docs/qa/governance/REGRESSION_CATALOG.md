# QA Level 3 – Regression Catalog

**Datum:** 15. März 2026  
**Zweck:** Strukturierte Zuordnung von Fehlern und Regressionen zu Fehlerklassen.  
**Erweiterung:** Bei neuem Bug → Fehlerklasse zuordnen, ggf. Test ergänzen, hier eintragen.

---

## Fehlerklassen (Definition)

| ID | Fehlerklasse | Beschreibung | Typische Ursache |
|----|--------------|--------------|------------------|
| `ui_state_drift` | UI-Zustand weicht von Backend ab | UI zeigt veraltete oder falsche Daten | Stale State, fehlendes Refresh |
| `async_race` | Race Condition in async/Event-Loop | Unvorhersehbares Verhalten bei parallelen Aktionen | qasync, Signal-Reihenfolge |
| `late_signal_use_after_destroy` | Signal auf zerstörtes Widget | Crash oder UB bei spätem Signal | Widget destroyed, Signal noch pending |
| `request_context_loss` | Request-Kontext geht verloren | Falscher Prompt/Agent/Modell in Anfrage | Stale Closure, falscher Scope |
| `rag_silent_failure` | RAG-Fehler wird nicht sichtbar | Chat läuft weiter, Nutzer weiß nicht, dass RAG fehlschlug | Exception verschluckt, kein Event |
| `debug_false_truth` | Debug-Panel zeigt Falsches | Timeline/Store zeigt nicht, was passiert ist | Event nicht emittiert, View filtert falsch |
| `startup_ordering` | Falsche Initialisierungsreihenfolge | App crasht oder UI kaputt beim Start | Dependency-Order, lazy init |
| `degraded_mode_failure` | Degraded Mode bricht App | Optionale Abhängigkeit fehlt → Crash statt Graceful Degradation | Kein try/except, harter Import |
| `contract_schema_drift` | Schema/Struktur geändert | Consumer erwartet anderes Format | API-Änderung ohne Anpassung |
| `metrics_false_success` | Metrics zählen falsch | TASK_FAILED als completed, oder umgekehrt | Falsche Event-Zuordnung |
| `tool_failure_visibility` | Tool-Fehler nicht sichtbar | Tool wirft, UI zeigt nichts oder crasht | Exception nicht gefangen, kein Event |
| `optional_dependency_missing` | Optionale Dependency fehlt | ImportError oder Crash statt Degradation | ChromaDB, Ollama etc. |

---

## Zuordnung: Tests → Fehlerklassen

### failure_modes/

| Datei | Test | Fehlerklasse |
|-------|------|--------------|
| test_chroma_unreachable | test_retriever_returns_empty_on_chroma_connection_error | rag_silent_failure |
| test_chroma_unreachable | test_rag_service_handles_chroma_unreachable | rag_silent_failure |
| test_chroma_unreachable | test_chroma_unreachable_emits_rag_retrieval_failed_event | debug_false_truth |
| test_prompt_service_failure | test_prompt_service_create_handles_failure | – |
| test_prompt_service_failure | test_prompt_service_update_handles_failure | – |
| test_prompt_service_failure | test_prompt_service_delete_handles_failure | – |
| test_prompt_service_failure | test_prompt_service_get_handles_failure | – |
| test_prompt_service_failure | test_prompt_service_list_all_handles_failure | – |
| test_tool_failure | test_tool_exception_returns_error_text_instead_of_crashing | tool_failure_visibility |
| test_tool_failure | test_tool_exception_emits_failed_event | tool_failure_visibility |
| test_event_store_failure | test_debug_store_handles_event_with_missing_metadata | contract_schema_drift |
| test_event_store_failure | test_debug_store_trim_at_max_history | – |
| test_rag_retrieval_failure | test_rag_service_handles_retrieval_exception | rag_silent_failure |
| test_rag_retrieval_failure | test_rag_failure_emits_event | rag_silent_failure, debug_false_truth |
| test_rag_retrieval_failure | test_chat_continues_when_rag_fails | rag_silent_failure |
| test_chroma_import_failure | test_vector_store_raises_vector_store_error_on_import_error | optional_dependency_missing |
| test_chroma_import_failure | test_rag_service_degrades_when_chroma_unavailable | degraded_mode_failure |
| test_llm_chunk_parsing_failure | test_extract_chunk_parts_* | contract_schema_drift |
| test_metrics_on_failed_chat_or_task | test_task_failed_increases_failed_not_completed | metrics_false_success |
| test_metrics_on_failed_chat_or_task | test_model_call_on_failure_does_not_increase_completed | metrics_false_success |
| test_event_bus_listener_error | test_listener_exception_does_not_break_bus | – |

### contracts/

| Datei | Test | Fehlerklasse |
|-------|------|--------------|
| test_chat_event_contract | test_chat_update_signal_emits_str_bool | ui_state_drift |
| test_chat_event_contract | test_chat_update_signal_payload_form_stable | ui_state_drift |
| test_chat_event_contract | test_chat_update_signal_required_fields_contract | ui_state_drift |

### async_behavior/

| Datei | Test | Fehlerklasse |
|-------|------|--------------|
| test_shutdown_during_task | test_run_chat_cancellation_cleans_up | ui_state_drift (streaming hängt) |
| test_signal_after_widget_destroy | test_signal_after_widget_destroy_no_crash | late_signal_use_after_destroy |
| test_chatwidget_signal_after_destroy | test_chatwidget_late_signal_no_crash | late_signal_use_after_destroy |
| test_chatwidget_signal_after_destroy | test_chatwidget_signal_during_destroy_no_crash | async_race |
| test_rag_concurrent_retrieval | test_rag_concurrent_augment_no_race | async_race (RAG) |
| test_debug_clear_during_refresh | test_debug_clear_during_refresh_no_crash | async_race |

### cross_layer/

| Datei | Test | Fehlerklasse |
|-------|------|--------------|
| test_prompt_apply_affects_real_request | test_prompt_apply_affects_real_request | request_context_loss |
| test_prompt_apply_affects_real_request | test_prompt_apply_no_stale_after_second_apply | request_context_loss |
| test_debug_view_matches_failure_events | test_task_failed_event_visible_in_timeline | debug_false_truth |
| test_debug_view_matches_failure_events | test_rag_retrieval_failed_event_visible_in_timeline | debug_false_truth |
| test_debug_view_matches_failure_events | test_debug_panel_timeline_matches_store | debug_false_truth |

### startup/

| Datei | Test | Fehlerklasse |
|-------|------|--------------|
| test_startup_without_ollama | test_main_window_starts_when_ollama_unreachable | degraded_mode_failure |
| test_startup_without_ollama | test_chat_available_after_startup_without_ollama | degraded_mode_failure |
| test_app_starts_with_optional_dependencies_missing | test_main_window_starts_with_rag_service_degraded | degraded_mode_failure |
| test_app_starts_with_optional_dependencies_missing | test_chat_available_after_startup_with_degraded_rag | degraded_mode_failure |
| test_app_starts_with_optional_dependencies_missing | test_main_window_starts_with_real_rag_service_no_chroma_import | startup_ordering |

### regression/

| Datei | Test | Fehlerklasse |
|-------|------|--------------|
| test_agent_delete_removes_from_list | test_agent_delete_removes_from_service_list | ui_state_drift |
| test_agent_delete_removes_from_list | test_agent_delete_removes_from_ui_list | ui_state_drift |
| test_chat_composer_send_signal_actually_emits | test_chat_composer_send_signal_actually_emits | – |

---

## Historische Bugs (aus AUDIT_REPORT)

| Bug | Fehlerklasse | Fix |
|-----|--------------|-----|
| Model-Router „hi“ False Positive | contract_schema_drift | Word-Boundaries |
| FileSystemTools Einzeldatei-Sicherheit | – | allowed_files |
| RAG-Tests Settings-Überschreibung | ui_state_drift | MinimalChatWidget blockiert rag_check |
| Doppelter Import chat_widget | – | Redundanz entfernt |

---

## Erweiterung bei neuem Bug

1. **Fehlerklasse zuordnen** (oder neue anlegen)
2. **Test schreiben** falls noch keiner existiert
3. **Hier eintragen** unter „Zuordnung“ oder „Historische Bugs“
4. **Marker** `@pytest.mark.regression` setzen falls sinnvoll

---

## Erweiterung: QA Incident Replay (geplant)

| Artefakt | Zweck |
|----------|-------|
| [QA_INCIDENT_ARTIFACT_STANDARD.md](QA_INCIDENT_ARTIFACT_STANDARD.md) | **Verbindlicher** Artefaktstandard |
| [incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md](incidents/_schema/INCIDENT_YAML_FIELD_STANDARD.md) | **Verbindlicher** Feldkatalog für incident.yaml |
| [incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md](incidents/_schema/REPLAY_YAML_FIELD_STANDARD.md) | **Verbindlicher** Feldkatalog für replay.yaml (Reproduktionsvertrag) |
| [incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md](incidents/_schema/BINDINGS_JSON_FIELD_STANDARD.md) | **Verbindlicher** Feldkatalog für bindings.json (Integrationsschicht) |
| [incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md](incidents/_schema/QA_INCIDENT_REPLAY_LIFECYCLE.md) | **Verbindlicher** Lifecycle (Incident + Replay Status, Governance) |
| [QA_INCIDENT_REPLAY_INTEGRATION.md](QA_INCIDENT_REPLAY_INTEGRATION.md) | **Integrationsarchitektur** (Projektion in Catalog, Control Center, Autopilot) |
| [incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md](incidents/_schema/QA_INCIDENT_SCRIPTS_ARCHITECTURE.md) | **Skript-Architektur** (create, enrich, validate, bind, project) |
| [QA_INCIDENT_REPLAY_ARCHITECTURE.md](QA_INCIDENT_REPLAY_ARCHITECTURE.md) | Incident → Replay → Regression Guard |
| [QA_INCIDENT_REPLAY_SCHEMA.json](QA_INCIDENT_REPLAY_SCHEMA.json) | Feldkatalog, Statusmodell |

Bei neuem Bug: Incident-Verzeichnis anlegen → incident.yaml, replay.yaml, bindings.json, notes.md → Fehlerklasse in bindings.json → Test.

---

*Regression Catalog erstellt am 15. März 2026.*

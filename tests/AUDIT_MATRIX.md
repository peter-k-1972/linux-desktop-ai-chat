# Audit-Matrix: Kernworkflows → QA-Bauplan

**Datum:** 2025-03-15  
**Zweck:** Belastbarer QA-Bauplan aus Test-Audit pro Kernworkflow

---

## Legende

| Spalte | Bedeutung |
|--------|------------|
| **Bestehende Tests** | Datei + Testname, Typ (Unit/UI/Integration/etc.) |
| **Echte Lücken** | Was fehlt, um reale Fehler zu erkennen |
| **Höchste Risiken** | Fehlerarten mit größtem Impact |
| **Neue Tests zuerst** | Priorisierte Liste mit erweiterten Metadaten |
| **Typ** | Unit / UI / Integration / Golden Path / Regression / Live |
| **async-sensitive** | yes = Race-/Loop-Risiken, Event-Loop-Synchronisation relevant; nutze `qtbot.waitUntil`, `pytest-asyncio` |
| **Schichten** | Betroffene Wahrheitsebenen: UI, Service, Persistenz, Event/Debug, Metrics – Assertions auf allen Ebenen |
| **regression_candidate** | yes = Standard-Repro für reale Bugs; Test in `tests/regression/` ablegen oder `@pytest.mark.regression` |

---

# 1. CHAT

## 1.1 Bestehende Tests

| Datei | Test | Typ |
|-------|------|-----|
| `test_chat_streaming.py` | `test_stream_content_only`, `test_stream_thinking_only_*`, `test_stream_mixed_*`, `test_stream_done_without_content`, `test_stream_api_error_chunk`, `test_stream_thinking_only_then_retry_succeeds` | Unit |
| `test_chat_history_filtering.py` | `test_placeholder_and_error_texts_filtered_from_history`, `test_empty_or_none_like_history_entries_are_ignored` | Unit |
| `ui/test_chat_ui.py` | `test_conversation_view_opens`, `test_conversation_view_add_message`, `test_conversation_view_add_assistant_message`, `test_chat_composer_opens`, `test_chat_composer_send_signal`, `test_chat_input_accepts_text`, `test_chat_header_opens` | UI |
| `regression/test_chat_composer_send_signal_actually_emits.py` | `test_chat_composer_send_signal_actually_emits` | Regression, UI |
| `golden_path/test_chat_golden_path.py` | `test_chat_send_message_receive_response_displayed_and_persisted` | Golden Path |
| `smoke/test_basic_chat.py` | `test_chat_widget_importable`, `test_conversation_view_add_message`, `test_chat_widget_placeholder_check`, `test_complete_mock` | Smoke |
| `smoke/test_full_workflow.py` | `test_prompt_send_receive_mock`, `test_chat_widget_has_run_chat` | Smoke |
| `golden_path/test_agent_in_chat_golden_path.py` | `test_agent_system_prompt_in_messages_when_selected` | Golden Path |

## 1.2 Echte Lücken

| Lücke | Beschreibung |
|-------|--------------|
| **ConversationView Inhalt** | `add_message` prüft nur `message_layout.count() >= 1`, nicht sichtbaren Text/Rolle |
| **ChatHeader Agent-Befüllung** | `agent_combo is not None` – keine Prüfung, ob Agenten geladen/auswählbar sind |
| **ChatHeader Modell-Befüllung** | `model_combo` existiert, aber keine Modell-Liste/auswahl geprüft |
| **RAG-Toggle Wirkung** | `rag_check` existiert, aber kein Test ob RAG tatsächlich in `run_chat` genutzt wird |
| **Side-Panel → Chat** | Prompt übernehmen, Modell wechseln – keine UI-Tests für Signal-Wirkung |
| **Chat-Widget echter Flow** | Smoke mockt alles; kein Test: MainWindow → ChatWidget → run_chat → UI-Update |
| **Senden während Streaming** | Kein Test: Senden blockiert oder serialisiert – brandgefährlich für qasync/Streaming-Stack |

## 1.3 Höchste Risiken

| Risiko | Fehlerart | Impact |
|--------|-----------|--------|
| R1 | Antwort kommt, UI zeigt Platzhalter/leer | Kritisch |
| R2 | Agent gewählt, System-Prompt nicht in Messages | Kritisch (bereits Golden Path) |
| R3 | RAG aktiviert, Kontext nicht in Antwort | Kritisch |
| R4 | Modell-Wechsel hat keine Wirkung | Hoch |
| R5 | Prompt aus Side-Panel landet nicht im Chat | Hoch |

## 1.4 Neue Tests zuerst (Chat)

| # | Test | Typ | async | Schichten | regression | P |
|---|------|-----|-------|-----------|------------|---|
| 1 | `test_conversation_view_message_content_visible` – Nachricht zeigt korrekten Text und Rolle | UI | no | UI | yes | P0 |
| 2 | `test_chat_header_agent_selection_populates_and_affects_messages` – Agent-Combo befüllt, Auswahl wirkt | UI | no | UI, Service | yes | P0 |
| 3 | `test_rag_toggle_enabled_context_in_response` – RAG an → Antwort enthält Kontext | Golden Path | **yes** | UI, Service | yes | P0 |
| 4 | `test_send_while_streaming_is_blocked_or_serialized` – Senden während Stream blockiert oder serialisiert (brandgefährlich für Stack) | Integration | **yes** | UI, Service | yes | P0 |
| 5 | `test_model_settings_change_affects_chat` – Modell wechseln → anderes Modell in API | Integration | no | UI, Service | yes | P1 |
| 6 | `test_prompt_apply_to_chat_visible` – Prompt übernehmen → Inhalt im Composer/Chat | UI | no | UI, Service, Request-Building | yes | P1 |
| 7 | `test_chat_full_flow_main_window` – MainWindow mit echtem ChatWidget, minimale Mocks | Smoke | **yes** | UI, Service, Persistenz | yes | P2 |

---

# 2. AGENTEN

## 2.1 Bestehende Tests

| Datei | Test | Typ |
|-------|------|-----|
| `unit/test_agents.py` | AgentProfile, AgentRegistry, AgentService, AgentFactory – CRUD, Validierung, Slug, Duplicate, Status | Unit |
| `integration/test_sqlite.py` | `test_create_and_get_agent`, `test_create_and_get_by_slug`, `test_update_agent`, `test_delete_agent`, `test_list_all_with_filters`, `test_persistence_across_connections` | Integration |
| `ui/test_agent_hr_ui.py` | `test_agent_manager_panel_opens`, `test_agent_manager_new_button_clickable`, `test_agent_list_panel_opens`, `test_agent_profile_panel_opens`, `test_agent_profile_panel_loads_profile`, `test_agent_manager_delete_button` | UI |
| `ui/test_ui_behavior.py` | `test_agent_profile_panel_loads_profile_shows_correct_data`, `test_agent_list_selection_loads_profile`, `test_agent_save_updates_service` | UI |
| `regression/test_agent_delete_removes_from_list.py` | `test_agent_delete_removes_from_service_list`, `test_agent_delete_removes_from_ui_list` | Regression, UI |
| `state_consistency/test_agent_consistency.py` | `test_agent_update_registry_consistency` | State Consistency |
| `golden_path/test_agent_golden_path.py` | `test_agent_create_save_load_edit_delete` | Golden Path |
| `golden_path/test_agent_in_chat_golden_path.py` | `test_agent_system_prompt_in_messages_when_selected` | Golden Path |
| `smoke/test_agent_workflow.py` | `test_agent_select_from_registry`, `test_agent_factory_creates_from_profile`, `test_agent_factory_creates_from_id`, `test_agent_can_handle_task`, `test_agent_get_context`, `test_agent_get_system_prompt` | Smoke |
| `test_agent_hr.py` | CRUD, Filter, Aktivieren/Deaktivieren, Registry, Modell-Zuweisung, Validierung | Unit |
| `test_orchestration.py` | Task, TaskGraph, Planner, Delegation, ExecutionEngine | Unit |
| `live/test_agent_execution.py` | `test_execution_engine_run_task` | Live |

## 2.2 Echte Lücken

| Lücke | Beschreibung |
|-------|--------------|
| **Neu-Button Wirkung** | `test_agent_manager_new_button_clickable` klickt nur – kein neuer Agent in Liste |
| **Profil load_profile** | `test_agent_profile_panel_loads_profile` prüft nur `hasattr` – kein Inhalt |
| **UI-Liste nach Delete** | Regression prüft `service.list_all()`, nicht ob `list_widget` den Agenten entfernt hat |
| **Gelöschter Agent ausgewählt** | Agent in Chat/Header ausgewählt, dann gelöscht → Header/Chat hat stale Referenz? |
| **Agent-Auswahl im Chat** | Golden Path mockt `header.agent_combo` – kein echter UI-Flow |
| **Registry nach UI-Update** | State-Consistency nur Service↔Registry, nicht UI→Service→Registry |

## 2.3 Höchste Risiken

| Risiko | Fehlerart | Impact |
|--------|-----------|--------|
| R1 | Agent löschen → noch in UI-Liste sichtbar | Hoch (Regression deckt Service ab) |
| R2 | Agent bearbeiten → Registry liefert alte Werte | Mittel |
| R3 | Neu-Button klicken → kein neuer Agent | Mittel |
| R4 | Agent in Chat auswählen → System-Prompt nicht in API | Kritisch (Golden Path mit Mock) |

## 2.4 Neue Tests zuerst (Agenten)

| # | Test | Typ | async | Schichten | regression | P |
|---|------|-----|-------|-----------|------------|---|
| 1 | `test_agent_new_button_creates_agent_in_list` – Neu klicken → Agent in Liste, auswählbar | UI | no | UI, Service | yes | P0 |
| 2 | `test_agent_delete_removes_from_list_widget` – Nach Delete: `list_widget` enthält Agent nicht mehr | UI, Regression | no | UI, Service, Persistenz | yes | P0 |
| 3 | `test_deleted_selected_agent_falls_back_cleanly` – Gelöschter Agent war ausgewählt → Header/Chat hat keinen stale Agent mehr | UI | no | UI, Service | yes | P0 |
| 4 | `test_agent_selection_in_chat_header_real_ui` – Echter ChatHeader mit Agent-Combo, Auswahl → Messages | Golden Path | no | UI, Service | yes | P1 |
| 5 | `test_agent_ui_save_registry_consistency` – Bearbeiten → Speichern → Registry.refresh() → gleiche Werte | State Consistency | no | UI, Service, Persistenz | yes | P1 |

---

# 3. PROMPT-SYSTEM

## 3.1 Bestehende Tests

| Datei | Test | Typ |
|-------|------|-----|
| `unit/test_prompt_system.py` | PromptService CRUD, DirectoryStorage, create_storage_backend | Unit |
| `state_consistency/test_prompt_consistency.py` | `test_prompt_db_list_editor_consistency` – DB ↔ list_all ↔ get | State Consistency |
| `golden_path/test_prompt_golden_path.py` | `test_prompt_create_save_load_edit_delete` – Service-Ebene | Golden Path |
| `test_prompt_repository.py` | DatabasePromptStorage, DirectoryPromptStorage | Unit |

## 3.2 Echte Lücken

| Lücke | Beschreibung |
|-------|--------------|
| **PromptManagerPanel** | **Keine UI-Tests** – Anlegen, Speichern, Laden, Bearbeiten, Löschen im UI |
| **Prompt-Liste nach Save** | Prompt speichern → erscheint in Liste? |
| **Prompt laden → Editor** | Aus Liste laden → Editor zeigt korrekten Inhalt? |
| **Prompt in Chat übernehmen** | "In Chat übernehmen" → Signal, Chat erhält Inhalt? |
| **ChatSidePanel** | Tab-Wechsel, Prompt-Panel-Integration – nicht getestet |
| **ModelSettingsPanel** | Modell-Auswahl, Einstellungen – nicht getestet |

## 3.3 Höchste Risiken

| Risiko | Fehlerart | Impact |
|--------|-----------|--------|
| R1 | Prompt speichern → Liste leer / falscher Inhalt | Kritisch |
| R2 | Prompt laden → Editor zeigt anderen Prompt | Hoch |
| R3 | "In Chat übernehmen" ohne Effekt | Hoch |
| R4 | Filter/Suche zeigt falsche Treffer | Mittel |

## 3.4 Neue Tests zuerst (Prompt-System)

*Aktuell einer der größten blinden Flecken – UI-Tests hier P0/P1-würdig.*

| # | Test | Typ | async | Schichten | regression | P |
|---|------|-----|-------|-----------|------------|---|
| 1 | `test_prompt_manager_panel_save_appears_in_list` – Neu → Editor füllen → Speichern → in Liste | UI | no | UI, Service, Persistenz | yes | P0 |
| 2 | `test_prompt_manager_panel_load_shows_in_editor` – Aus Liste laden → Editor-Inhalt = Prompt | UI | no | UI, Service | yes | P0 |
| 3 | `test_prompt_manager_panel_delete_removes_from_list` – Löschen → nicht mehr in Liste | UI | no | UI, Service, Persistenz | yes | P0 |
| 4 | `test_prompt_apply_requested_signal_emits` – "In Chat übernehmen" → Signal mit Prompt | UI | no | UI, Service | yes | P1 |
| 5 | `test_prompt_ui_service_storage_roundtrip` – UI → Service → DB → Reload → UI | State Consistency | no | UI, Service, Persistenz | yes | P1 |
| 6 | `test_prompt_manager_panel_search_filter` – Suche/Filter zeigt korrekte Treffer | UI | no | UI, Service | no | P2 |

---

# 4. DEBUG / METRICS

## 4.1 Bestehende Tests

| Datei | Test | Typ |
|-------|------|-----|
| `test_debug.py` | AgentEvent, EventBus, DebugStore (task_created, lifecycle, model_usage, tool_execution, clear, emit_event) | Unit, Integration |
| `integration/test_event_bus.py` | emit, multiple subscribers, unsubscribe, listener exception | Integration |
| `ui/test_debug_panel_ui.py` | `test_debug_panel_opens`, `test_debug_panel_has_tabs`, `test_debug_panel_clear_button`, `test_agent_activity_view_opens`, `test_event_timeline_view_opens`, `test_event_timeline_refresh`, `test_agent_activity_refresh` | UI |
| `state_consistency/test_debug_consistency.py` | `test_debug_event_store_consistency` – EventBus → DebugStore | State Consistency |
| `golden_path/test_debug_panel_golden_path.py` | `test_debug_event_visible_in_store_and_refresh` – emit → store → get_event_history | Golden Path |
| `unit/test_metrics.py` | AgentMetric, MetricsStore, MetricsService, MetricsCollector | Unit |
| `test_metrics.py` | metrics_store, collector (task_completed, failed, model_call), statistics | Unit |

## 4.2 Echte Lücken

| Lücke | Beschreibung |
|-------|--------------|
| **Event in Timeline sichtbar** | `test_event_timeline_refresh` prüft nur `view.isVisible()` – kein Event-Inhalt |
| **Clear-Button Wirkung** | `test_debug_panel_clear_button` klickt nur – nicht ob Events gelöscht |
| **AgentActivityView Inhalt** | `test_agent_activity_refresh` prüft nur `isVisible()` |
| **TaskGraphView, ToolExecutionView, ModelUsageView** | Keine Tests |
| **Metrics in Agent-Profil** | Timeline-Darstellung – nicht getestet |

## 4.3 Höchste Risiken

| Risiko | Fehlerart | Impact |
|--------|-----------|--------|
| R1 | Event emittiert → nicht in Timeline sichtbar | Hoch |
| R2 | Clear-Button → Events bleiben | Mittel |
| R3 | Metrics werden nicht korrekt aggregiert | Mittel |

## 4.4 Neue Tests zuerst (Debug/Metrics)

*`test_event_timeline_shows_event_content` ist fast Pflicht – ohne ihn dem Debug-Panel nicht vertrauen.*

| # | Test | Typ | async | Schichten | regression | P |
|---|------|-----|-------|-----------|------------|---|
| 1 | `test_event_timeline_shows_event_content` – Event emittieren → refresh → View zeigt Message/Agent | UI | **yes** | UI, Event/Debug | yes | P0 |
| 2 | `test_debug_panel_clear_removes_events` – Events hinzufügen → Clear → get_event_history leer | UI | no | UI, Event/Debug | yes | P0 |
| 3 | `test_agent_activity_shows_task_status` – Task-Event → Activity-View zeigt Status | UI | **yes** | UI, Event/Debug | yes | P1 |
| 4 | `test_metrics_timeline_in_agent_profile` – Metrics → Profil-Timeline zeigt Daten | UI | no | UI, Metrics | no | P2 |

---

# 5. RAG

## 5.1 Bestehende Tests

| Datei | Test | Typ |
|-------|------|-----|
| `unit/test_rag.py` | load_document, Chunker, ContextBuilder, EmbeddingService (mock), VectorStore, Retriever | Unit |
| `integration/test_chroma.py` | `test_add_and_query_chunks`, `test_delete_by_ids`, `test_add_with_precomputed_embeddings` | Integration |
| `golden_path/test_rag_golden_path.py` | `test_rag_index_retrieve_context` – Dokument → Chunks → VectorStore → Retriever → Context | Golden Path |
| `live/test_rag_pipeline.py` | `test_index_and_retrieve`, `test_augment_if_enabled`, `test_augment_disabled_returns_original` | Live |
| `test_rag.py` | (Root-Level, falls vorhanden) | Unit |

## 5.2 Echte Lücken

| Lücke | Beschreibung |
|-------|--------------|
| **RAG-UI** | RAG-Checkbox im Header, Settings – keine UI-Tests |
| **RAG aktiviert → Chat** | ChatWidget nutzt RAG wenn aktiviert? Kein E2E |
| **RAG-Fehlerpfad** | RAG scheitert → Chat läuft weiter? System markiert transparent, dass kein Kontext verwendet wurde? |
| **Knowledge Space Auswahl** | Settings rag_space_combo – nicht getestet |
| **Indexierung über UI** | Kein UI für Indexierung (evtl. nur Script) – dokumentieren |

## 5.3 Höchste Risiken

| Risiko | Fehlerart | Impact |
|--------|-----------|--------|
| R1 | RAG aktiviert, Kontext nicht in Antwort | Kritisch |
| R2 | RAG-Toggle hat keine Wirkung auf run_chat | Hoch |
| R3 | Falscher Knowledge Space genutzt | Mittel |
| R4 | RAG scheitert → Chat bricht ab oder verhält sich undurchsichtig | Hoch |

## 5.4 Neue Tests zuerst (RAG)

| # | Test | Typ | async | Schichten | regression | P |
|---|------|-----|-------|-----------|------------|---|
| 1 | `test_rag_enabled_augments_query_in_chat` – RAG an, run_chat → augment_if_enabled aufgerufen | Integration | **yes** | Service | yes | P0 |
| 2 | `test_rag_failure_degrades_transparently` – RAG scheitert → Chat läuft weiter, System markiert nachvollziehbar, dass kein RAG-Kontext verwendet wurde | Integration | **yes** | Service, UI | yes | P0 |
| 3 | `test_rag_toggle_syncs_with_settings` – Header rag_check → settings.rag_enabled | UI | no | UI, Service | yes | P1 |
| 4 | `test_rag_golden_path_with_chat_widget` – ChatWidget mit RAG, FakeClient, Index → Antwort enthält Kontext | Golden Path | **yes** | UI, Service | yes | P1 |

---

# 6. STARTUP / MAINWINDOW

## 6.1 Bestehende Tests

| Datei | Test | Typ |
|-------|------|-----|
| `smoke/test_app_startup.py` | `test_qapplication_available`, `test_main_module_importable`, `test_main_window_importable`, `test_critical_imports`, `test_main_window_creation`, `test_app_settings_loads` | Smoke |
| `test_app.py` | (Root-Level – prüfen) | Smoke/Unit |

## 6.2 Echte Lücken

| Lücke | Beschreibung |
|-------|--------------|
| **test_main_window_creation** | ChatWidget, OllamaClient, Provider komplett gemockt – fast keine echte Logik |
| **Echter App-Start** | Kein Test: `python -m app.main` startet ohne Crash |
| **DB-Initialisierung** | MainWindow mit echter DB – nicht getestet |
| **Theme/Settings laden** | Settings werden geladen und angewendet? |

## 6.3 Höchste Risiken

| Risiko | Fehlerart | Impact |
|--------|-----------|--------|
| R1 | App startet nicht (Import, Init) | Kritisch |
| R2 | MainWindow-Verbindungen falsch (Chat↔SidePanel↔Header) | Hoch |
| R3 | DB-Pfad falsch, Persistenz fehlgeschlagen | Mittel |

## 6.4 Neue Tests zuerst (Startup/MainWindow)

*`test_main_window_with_real_chat_widget` extrem wertvoll – durchbricht den künstlich geglätteten Startpfad.*

| # | Test | Typ | async | Schichten | regression | P |
|---|------|-----|-------|-----------|------------|---|
| 1 | `test_main_window_with_real_chat_widget` – MainWindow mit echtem ChatWidget, FakeOllama, Temp-DB | Smoke | **yes** | UI, Service, Persistenz | yes | P0 |
| 2 | `test_app_main_importable_and_runnable` – `main.main()` kann aufgerufen werden (evtl. mit frühem Exit) | Smoke | **yes** | UI | yes | P1 |
| 3 | `test_main_window_signal_connections` – ChatWidget.send_requested → _on_send verbunden | Integration | no | UI, Service | yes | P2 |

---

# 7. ZUSAMMENFASSUNG: QA-BAUPLAN

## 7.1 Priorität P0 (sofort)

| Bereich | Test | Typ | async | regression |
|---------|------|-----|-------|------------|
| Chat | `test_conversation_view_message_content_visible` | UI | no | yes |
| Chat | `test_chat_header_agent_selection_populates_and_affects_messages` | UI | no | yes |
| Chat | `test_rag_toggle_enabled_context_in_response` | Golden Path | **yes** | yes |
| Chat | `test_send_while_streaming_is_blocked_or_serialized` | Integration | **yes** | yes |
| Agenten | `test_agent_new_button_creates_agent_in_list` | UI | no | yes |
| Agenten | `test_agent_delete_removes_from_list_widget` | UI, Regression | no | yes |
| Agenten | `test_deleted_selected_agent_falls_back_cleanly` | UI | no | yes |
| Prompt | `test_prompt_manager_panel_save_appears_in_list` | UI | no | yes |
| Prompt | `test_prompt_manager_panel_load_shows_in_editor` | UI | no | yes |
| Prompt | `test_prompt_manager_panel_delete_removes_from_list` | UI | no | yes |
| Debug | `test_event_timeline_shows_event_content` | UI | **yes** | yes |
| Debug | `test_debug_panel_clear_removes_events` | UI | no | yes |
| RAG | `test_rag_enabled_augments_query_in_chat` | Integration | **yes** | yes |
| RAG | `test_rag_failure_degrades_transparently` | Integration | **yes** | yes |
| Startup | `test_main_window_with_real_chat_widget` | Smoke | **yes** | yes |

## 7.2 Priorität P1

| Bereich | Test | Typ | async | regression |
|---------|------|-----|-------|------------|
| Chat | `test_model_settings_change_affects_chat` | Integration | no | yes |
| Chat | `test_prompt_apply_to_chat_visible` | UI | no | yes |
| Agenten | `test_agent_selection_in_chat_header_real_ui` | Golden Path | no | yes |
| Agenten | `test_agent_ui_save_registry_consistency` | State Consistency | no | yes |
| Prompt | `test_prompt_apply_requested_signal_emits` | UI | no | yes |
| Prompt | `test_prompt_ui_service_storage_roundtrip` | State Consistency | no | yes |
| Debug | `test_agent_activity_shows_task_status` | UI | **yes** | yes |
| RAG | `test_rag_toggle_syncs_with_settings` | UI | no | yes |
| RAG | `test_rag_golden_path_with_chat_widget` | Golden Path | **yes** | yes |
| Startup | `test_app_main_importable_and_runnable` | Smoke | **yes** | yes |

## 7.3 Priorität P2

| Bereich | Test | Typ | async | regression |
|---------|------|-----|-------|------------|
| Chat | `test_chat_full_flow_main_window` | Smoke | **yes** | yes |
| Agenten | (weiterer Registry-Consistency) | – | – | – |
| Prompt | `test_prompt_manager_panel_search_filter` | UI | no | no |
| Debug | `test_metrics_timeline_in_agent_profile` | UI | no | no |
| Startup | `test_main_window_signal_connections` | Integration | no | yes |

## 7.4 Metadaten-Übersicht

| Metrik | P0 | P1 | P2 |
|--------|----|----|-----|
| **async-sensitive** | 7 | 3 | 1 |
| **regression_candidate** | 15 | 10 | 1 |
| **Testtypen** | UI: 8, Integration: 3, Golden Path: 1, Smoke: 1 | UI: 5, Integration: 1, Golden Path: 2, State: 2, Smoke: 1 | UI: 2, Smoke: 1, Integration: 1 |

## 7.5 Nächste Schritte

1. **P0-Tests implementieren** – 15 Tests, Fokus auf UI-Verhalten, async-sensitive Flows, Regression-Kandidaten
2. **Async-Tests** – `qtbot.waitUntil`, `pytest-asyncio`, Event-Loop-Synchronisation beachten
3. **Regression-Workflow** – Tests mit `regression_candidate: yes` in `tests/regression/` ablegen oder als `@pytest.mark.regression` markieren
4. **Fixtures konsolidieren** – `temp_db_path`, `agent_service` zentral in `conftest.py`
5. **CI-Integration** – `pytest -m "not live and not slow"` als Standard-Check

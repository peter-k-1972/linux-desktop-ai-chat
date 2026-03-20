# P0-Testplan – Audit-Matrix

**Basis:** AUDIT_MATRIX.md §7.1  
**Datum:** 2025-03-15  
**Zweck:** Konkrete Implementierungsliste aller 15 P0-Testfälle

---

## Legende

| Feld | Bedeutung |
|------|-----------|
| **Testtyp** | ui, integration, golden_path, state_consistency, regression, async_behavior, startup, live |
| **Schichten** | UI, Service, Persistenz, Event/Debug, Metrics |
| **Realitätsgrad** | Mock (stark isoliert), Fake (realistische Stub-Logik), Real (echte Komponenten) |
| **Bugklasse** | Welches reale Fehlverhalten dieser Test verhindert |

---

# 1. CHAT (4 Tests)

## 1.1 test_conversation_view_message_content_visible

| Feld | Wert |
|------|------|
| **Testname** | `test_conversation_view_message_content_visible` |
| **Dateipfad** | `tests/ui/test_chat_ui.py` |
| **Testtyp** | ui, regression |
| **Schichten** | UI |
| **Realitätsgrad** | Fake (ConversationView, ChatMessageWidget echt) |
| **Fixtures / Testdaten** | qtbot |
| **Kern-Assertions** | `add_message("user", "Hallo")` → message_layout enthält Widget mit bubble.text() == "Hallo"; `add_message("assistant", "Antwort")` → bubble.text() == "Antwort"; Rolle sichtbar |
| **Bugklasse** | Nachricht wird hinzugefügt, aber Inhalt nicht sichtbar / falscher Inhalt / falsche Rolle |

---

## 1.2 test_chat_header_agent_selection_populates_and_affects_messages

| Feld | Wert |
|------|------|
| **Testname** | `test_chat_header_agent_selection_populates_and_affects_messages` |
| **Dateipfad** | `tests/ui/test_chat_ui.py` |
| **Testtyp** | ui, regression |
| **Schichten** | UI, Service |
| **Realitätsgrad** | Fake (ChatHeaderWidget, AgentRegistry; ensure_seed_agents) |
| **Fixtures / Testdaten** | qtbot, temp_db_path, agent_repository, test_agent |
| **Kern-Assertions** | Agent-Combo befüllt (count > 1); Auswahl ändert currentData(); Auswahl wirkt auf Messages (System-Prompt) |
| **Bugklasse** | Agent-Combo leer; Auswahl hat keine Wirkung auf API-Messages |

---

## 1.3 test_rag_toggle_enabled_context_in_response

| Feld | Wert |
|------|------|
| **Testname** | `test_rag_toggle_enabled_context_in_response` |
| **Dateipfad** | `tests/golden_path/test_chat_rag_golden_path.py` |
| **Testtyp** | golden_path, async_behavior, regression |
| **Schichten** | UI, Service |
| **Realitätsgrad** | Fake (FakeOllamaClient, FakeDB); Mock (rag_service.augment_if_enabled) |
| **Fixtures / Testdaten** | settings (rag_enabled=True), CapturingChatWidget, FakeDB, FakeOllamaClient |
| **Kern-Assertions** | RAG an → augment_if_enabled aufgerufen mit enabled=True; Antwort enthält RAG-Kontext-Token |
| **Bugklasse** | RAG aktiviert, aber Kontext nicht in Antwort |

---

## 1.4 test_send_while_streaming_is_blocked_or_serialized

| Feld | Wert |
|------|------|
| **Testname** | `test_send_while_streaming_is_blocked_or_serialized` |
| **Dateipfad** | `tests/integration/test_chat_streaming_behavior.py` |
| **Testtyp** | integration, async_behavior, regression |
| **Schichten** | UI, Service |
| **Realitätsgrad** | Fake (Client mit langsamem Stream, ChatWidget) |
| **Fixtures / Testdaten** | settings, qtbot, FakeOllamaClient (langsamer Stream) |
| **Kern-Assertions** | Während Stream: zweiter run_chat blockiert oder serialisiert; keine doppelte API-Anfrage |
| **Bugklasse** | Doppelte Sends, Race Conditions, korrupte Antworten bei qasync/Streaming-Stack |

---

# 2. AGENTEN (3 Tests)

## 2.1 test_agent_new_button_creates_agent_in_list

| Feld | Wert |
|------|------|
| **Testname** | `test_agent_new_button_creates_agent_in_list` |
| **Dateipfad** | `tests/ui/test_agent_hr_ui.py` |
| **Testtyp** | ui, regression |
| **Schichten** | UI, Service |
| **Realitätsgrad** | Real (AgentManagerPanel, AgentService, AgentRepository); Fake (temp_db) |
| **Fixtures / Testdaten** | qtbot, temp_db_path |
| **Kern-Assertions** | Vorher: list_widget.count() = N; Neu klicken; Nachher: count() = N+1; neuer Agent in Liste, auswählbar |
| **Bugklasse** | Neu-Button klicken → kein neuer Agent in Liste |

---

## 2.2 test_agent_delete_removes_from_list_widget

| Feld | Wert |
|------|------|
| **Testname** | `test_agent_delete_removes_from_list_widget` |
| **Dateipfad** | `tests/regression/test_agent_delete_removes_from_list.py` |
| **Testtyp** | ui, regression |
| **Schichten** | UI, Service, Persistenz |
| **Realitätsgrad** | Real (AgentManagerPanel, AgentService); Fake (temp_db); Mock (QMessageBox) |
| **Fixtures / Testdaten** | qtbot, temp_db_path, QMessageBox.patch |
| **Kern-Assertions** | Agent erstellen, auswählen, löschen → list_widget enthält Agent-ID nicht mehr (iterate items) |
| **Bugklasse** | Agent aus DB gelöscht, aber noch in UI-Liste sichtbar |

---

## 2.3 test_deleted_selected_agent_falls_back_cleanly

| Feld | Wert |
|------|------|
| **Testname** | `test_deleted_selected_agent_falls_back_cleanly` |
| **Dateipfad** | `tests/regression/test_agent_delete_removes_from_list.py` |
| **Testtyp** | ui, regression |
| **Schichten** | UI, Service |
| **Realitätsgrad** | Real (ChatHeaderWidget, Agent-Combo, AgentManagerPanel); Fake (temp_db) |
| **Fixtures / Testdaten** | qtbot, temp_db_path, ChatHeaderWidget mit Agent-Combo |
| **Kern-Assertions** | Agent in Header ausgewählt, dann gelöscht → header.agent_combo zeigt keinen stale Agent mehr |
| **Bugklasse** | Gelöschter Agent war ausgewählt → Header/Chat hat stale Referenz |

---

# 3. PROMPT-SYSTEM (3 Tests)

## 3.1 test_prompt_manager_panel_save_appears_in_list

| Feld | Wert |
|------|------|
| **Testname** | `test_prompt_manager_panel_save_appears_in_list` |
| **Dateipfad** | `tests/ui/test_prompt_manager_ui.py` |
| **Testtyp** | ui, regression |
| **Schichten** | UI, Service, Persistenz |
| **Realitätsgrad** | Real (PromptManagerPanel, PromptService); Fake (temp_db) |
| **Fixtures / Testdaten** | qtbot, temp_db_path, prompt_service |
| **Kern-Assertions** | Neu → Editor füllen (Titel, Content) → Speichern → prompt_list.count() >= 1; Item-Text enthält Titel |
| **Bugklasse** | Prompt speichern → Liste leer / falscher Inhalt |

---

## 3.2 test_prompt_manager_panel_load_shows_in_editor

| Feld | Wert |
|------|------|
| **Testname** | `test_prompt_manager_panel_load_shows_in_editor` |
| **Dateipfad** | `tests/ui/test_prompt_manager_ui.py` |
| **Testtyp** | ui, regression |
| **Schichten** | UI, Service |
| **Realitätsgrad** | Real (PromptManagerPanel, PromptService); Fake (temp_db) |
| **Fixtures / Testdaten** | qtbot, temp_db_path, prompt_service |
| **Kern-Assertions** | Prompt in Liste → Klick → editor.title_edit.text() == prompt.title; editor zeigt korrekten Inhalt |
| **Bugklasse** | Prompt laden → Editor zeigt anderen Prompt / falschen Inhalt |

---

## 3.3 test_prompt_manager_panel_delete_removes_from_list

| Feld | Wert |
|------|------|
| **Testname** | `test_prompt_manager_panel_delete_removes_from_list` |
| **Dateipfad** | `tests/ui/test_prompt_manager_ui.py` |
| **Testtyp** | ui, regression |
| **Schichten** | UI, Service, Persistenz |
| **Realitätsgrad** | Real (PromptManagerPanel, PromptService); Fake (temp_db); Mock (QMessageBox) |
| **Fixtures / Testdaten** | qtbot, temp_db_path, prompt_service, QMessageBox.patch |
| **Kern-Assertions** | Prompt auswählen → Löschen (Bestätigung) → nicht mehr in prompt_list |
| **Bugklasse** | Löschen ohne Effekt; Prompt bleibt in Liste |

---

# 4. DEBUG / METRICS (2 Tests)

## 4.1 test_event_timeline_shows_event_content

| Feld | Wert |
|------|------|
| **Testname** | `test_event_timeline_shows_event_content` |
| **Dateipfad** | `tests/ui/test_debug_panel_ui.py` |
| **Testtyp** | ui, async_behavior, regression |
| **Schichten** | UI, Event/Debug |
| **Realitätsgrad** | Real (EventBus, DebugStore, EventTimelineView) |
| **Fixtures / Testdaten** | qtbot, EventBus, DebugStore |
| **Kern-Assertions** | Event emittieren → store.get_event_history() enthält es; View.refresh() → View zeigt event.message / Agent |
| **Bugklasse** | Event emittiert → nicht in Timeline sichtbar |

---

## 4.2 test_debug_panel_clear_removes_events

| Feld | Wert |
|------|------|
| **Testname** | `test_debug_panel_clear_removes_events` |
| **Dateipfad** | `tests/ui/test_debug_panel_ui.py` |
| **Testtyp** | ui, regression |
| **Schichten** | UI, Event/Debug |
| **Realitätsgrad** | Real (DebugPanel, DebugStore, EventBus) |
| **Fixtures / Testdaten** | qtbot, EventBus, DebugStore mit vorab emittierten Events |
| **Kern-Assertions** | Events vor Clear; Clear-Button klicken → store.get_event_history() == [] |
| **Bugklasse** | Clear-Button ohne Wirkung; Events bleiben |

---

# 5. RAG (2 Tests)

## 5.1 test_rag_enabled_augments_query_in_chat

| Feld | Wert |
|------|------|
| **Testname** | `test_rag_enabled_augments_query_in_chat` |
| **Dateipfad** | `tests/integration/test_rag_chat_integration.py` |
| **Testtyp** | integration, async_behavior, regression |
| **Schichten** | Service |
| **Realitätsgrad** | Fake (FakeOllamaClient, FakeDB, RecordingRAGService) |
| **Fixtures / Testdaten** | qtbot, settings (rag_enabled=True), MinimalChatWidget, RecordingRAGService |
| **Kern-Assertions** | run_chat("Was ist Python?") → augment_calls enthält query, enabled=True |
| **Bugklasse** | RAG aktiviert, aber augment_if_enabled nicht aufgerufen |

---

## 5.2 test_rag_failure_degrades_transparently

| Feld | Wert |
|------|------|
| **Testname** | `test_rag_failure_degrades_transparently` |
| **Dateipfad** | `tests/integration/test_rag_chat_integration.py` |
| **Testtyp** | integration, async_behavior, regression |
| **Schichten** | Service, UI |
| **Realitätsgrad** | Fake (RecordingRAGService return query, False; FakeOllamaClient) |
| **Fixtures / Testdaten** | qtbot, settings (rag_enabled=True), MinimalChatWidget |
| **Kern-Assertions** | RAG return (query, False) → Chat läuft weiter; client.call_count == 1; Antwort sichtbar |
| **Bugklasse** | RAG scheitert → Chat bricht ab; keine transparente Degradation |

---

# 6. STARTUP / MAINWINDOW (1 Test)

## 6.1 test_main_window_with_real_chat_widget

| Feld | Wert |
|------|------|
| **Testname** | `test_main_window_with_real_chat_widget` |
| **Dateipfad** | `tests/smoke/test_app_startup.py` |
| **Testtyp** | smoke, async_behavior, regression |
| **Schichten** | UI, Service, Persistenz |
| **Realitätsgrad** | Real (MainWindow, ChatWidget, DB); Fake (FakeOllamaClient, temp_db) |
| **Fixtures / Testdaten** | temp_db_path, FakeOllamaClient, AppSettings |
| **Kern-Assertions** | MainWindow erstellt; chat_widget ist echtes ChatWidget; chat_id setzbar |
| **Bugklasse** | Künstlich geglätteter Startpfad; echte Verkabelung nicht getestet |

---

# 7. ZUSAMMENFASSUNG

| # | Bereich | Test | Dateipfad | Typ | async |
|---|---------|------|------------|-----|-------|
| 1 | Chat | test_conversation_view_message_content_visible | tests/ui/test_chat_ui.py | ui | no |
| 2 | Chat | test_chat_header_agent_selection_populates_and_affects_messages | tests/ui/test_chat_ui.py | ui | no |
| 3 | Chat | test_rag_toggle_enabled_context_in_response | tests/golden_path/test_chat_rag_golden_path.py | golden_path | yes |
| 4 | Chat | test_send_while_streaming_is_blocked_or_serialized | tests/integration/test_chat_streaming_behavior.py | integration | yes |
| 5 | Agenten | test_agent_new_button_creates_agent_in_list | tests/ui/test_agent_hr_ui.py | ui | no |
| 6 | Agenten | test_agent_delete_removes_from_list_widget | tests/regression/test_agent_delete_removes_from_list.py | ui, regression | no |
| 7 | Agenten | test_deleted_selected_agent_falls_back_cleanly | tests/regression/test_agent_delete_removes_from_list.py | ui, regression | no |
| 8 | Prompt | test_prompt_manager_panel_save_appears_in_list | tests/ui/test_prompt_manager_ui.py | ui | no |
| 9 | Prompt | test_prompt_manager_panel_load_shows_in_editor | tests/ui/test_prompt_manager_ui.py | ui | no |
| 10 | Prompt | test_prompt_manager_panel_delete_removes_from_list | tests/ui/test_prompt_manager_ui.py | ui | no |
| 11 | Debug | test_event_timeline_shows_event_content | tests/ui/test_debug_panel_ui.py | ui | yes |
| 12 | Debug | test_debug_panel_clear_removes_events | tests/ui/test_debug_panel_ui.py | ui | no |
| 13 | RAG | test_rag_enabled_augments_query_in_chat | tests/integration/test_rag_chat_integration.py | integration | yes |
| 14 | RAG | test_rag_failure_degrades_transparently | tests/integration/test_rag_chat_integration.py | integration | yes |
| 15 | Startup | test_main_window_with_real_chat_widget | tests/smoke/test_app_startup.py | smoke | yes |

**Metadaten:** 15 P0-Tests | 8 UI | 3 Integration | 1 Golden Path | 1 Smoke | 7 async-sensitive | 15 regression_candidate

# P0 Implementierungsplan – QA

**Basis:** AUDIT_MATRIX.md  
**Datum:** 2025-03-15

---

## 1. test_conversation_view_message_content_visible

| Feld | Wert |
|------|------|
| **Dateipfad** | `tests/ui/test_chat_ui.py` |
| **Kategorie** | ui, regression |
| **Schichten** | UI |
| **Fixtures** | qtbot |
| **Strategie** | Echt: ConversationView, ChatMessageWidget |
| **Assertions** | add_message("user", "Hallo") → message_layout enthält Widget mit bubble.text() == "Hallo"; add_message("assistant", "Antwort") → bubble.text() == "Antwort" |
| **Fehlverhalten** | Nachricht wird hinzugefügt, aber Inhalt nicht sichtbar / falscher Inhalt |

---

## 2. test_chat_header_agent_selection_populates_and_affects_messages

| Feld | Wert |
|------|------|
| **Dateipfad** | `tests/ui/test_chat_ui.py` |
| **Kategorie** | ui, regression |
| **Schichten** | UI, Service |
| **Fixtures** | qtbot, temp_db_path, agent_repository, test_agent |
| **Strategie** | Echt: ChatHeaderWidget, AgentRegistry; Mock: ensure_seed_agents |
| **Assertions** | set_agents / _load_agents → agent_combo.count() > 1; Auswahl → currentData() == agent_id |
| **Fehlverhalten** | Agent-Combo leer; Auswahl hat keine Wirkung |

---

## 3. test_rag_toggle_enabled_context_in_response

| Feld | Wert |
|------|------|
| **Dateipfad** | `tests/golden_path/test_chat_rag_golden_path.py` (neu) |
| **Kategorie** | golden_path, async_behavior |
| **Schichten** | UI, Service |
| **Fixtures** | temp_chroma_dir, tmp_path, settings |
| **Strategie** | Fake: OllamaClient; Echt: RAGService, ChromaDB, ChatWidget; Mock: EmbeddingService für Index |
| **Assertions** | RAG an, Dokument indexiert, run_chat → current_full_response enthält Kontext-Token |
| **Fehlverhalten** | RAG aktiviert, aber Kontext nicht in Antwort |

---

## 4. test_send_while_streaming_is_blocked_or_serialized

| Feld | Wert |
|------|------|
| **Dateipfad** | `tests/integration/test_chat_streaming_behavior.py` (neu) |
| **Kategorie** | integration, async_behavior, regression |
| **Schichten** | UI, Service |
| **Fixtures** | settings, qt_event_loop |
| **Strategie** | Fake: Client mit langsamem Stream; prüfen: _streaming=True → _on_send early return |
| **Assertions** | Während Stream: run_chat erneut aufrufen → return ohne zweite Anfrage; oder: Composer disabled |
| **Fehlverhalten** | Doppelte Sends, Race Conditions, korrupte Antworten |

---

## 5. test_agent_new_button_creates_agent_in_list

| Feld | Wert |
|------|------|
| **Dateipfad** | `tests/ui/test_agent_hr_ui.py` |
| **Kategorie** | ui, regression |
| **Schichten** | UI, Service |
| **Fixtures** | qtbot, temp_db_path, patch ensure_seed_agents |
| **Strategie** | Echt: AgentManagerPanel, AgentService, AgentRepository |
| **Assertions** | Vorher: list_widget.count() = N; Neu klicken; Nachher: count() = N+1, neuer Agent in Liste |
| **Fehlverhalten** | Neu-Button ohne Effekt |

---

## 6. test_agent_delete_removes_from_list_widget

| Feld | Wert |
|------|------|
| **Dateipfad** | `tests/regression/test_agent_delete_removes_from_list.py` |
| **Kategorie** | ui, regression |
| **Schichten** | UI, Service, Persistenz |
| **Fixtures** | qtbot, temp_db_path, patch QMessageBox |
| **Assertions** | Agent erstellen, auswählen, löschen → list_widget enthält Agent-ID nicht mehr (iterate items) |
| **Fehlverhalten** | Agent aus DB gelöscht, aber noch in UI-Liste |

---

## 7. test_deleted_selected_agent_falls_back_cleanly

| Feld | Wert |
|------|------|
| **Dateipfad** | `tests/regression/test_agent_delete_removes_from_list.py` |
| **Kategorie** | ui, regression |
| **Schichten** | UI, Service |
| **Fixtures** | qtbot, temp_db_path, ChatHeaderWidget mit Agent-Combo |
| **Strategie** | Agent in Header ausgewählt, dann in HR gelöscht → Header muss "Standard" oder keinen stale Agent zeigen |
| **Assertions** | Nach Delete: header.agent_combo.currentData() is None oder currentText != gelöschter Agent |
| **Fehlverhalten** | Stale Agent-Referenz in Chat/Header |

---

## 8–10. Prompt P0 (save, load, delete)

| Test | Dateipfad | Assertions |
|------|-----------|------------|
| test_prompt_manager_panel_save_appears_in_list | tests/ui/test_prompt_manager_ui.py (neu) | Neu, Editor füllen, Speichern → prompt_list.count() >= 1, Item-Text enthält Titel |
| test_prompt_manager_panel_load_shows_in_editor | tests/ui/test_prompt_manager_ui.py | Prompt in Liste, klicken → editor.title_edit.text() == prompt.title |
| test_prompt_manager_panel_delete_removes_from_list | tests/ui/test_prompt_manager_ui.py | Prompt auswählen, Löschen (QMessageBox patch) → nicht mehr in Liste |

---

## 11. test_event_timeline_shows_event_content

| Feld | Wert |
|------|------|
| **Dateipfad** | `tests/ui/test_debug_panel_ui.py` |
| **Kategorie** | ui, async_behavior, regression |
| **Schichten** | UI, Event/Debug |
| **Fixtures** | qtbot, EventBus, DebugStore |
| **Assertions** | Event emittieren, store.get_event_history() hat es; View.refresh(); View enthält Label mit event.message |
| **Fehlverhalten** | Event in Store, aber nicht in Timeline sichtbar |

---

## 12. test_debug_panel_clear_removes_events

| Feld | Wert |
|------|------|
| **Dateipfad** | `tests/ui/test_debug_panel_ui.py` |
| **Kategorie** | ui, regression |
| **Schichten** | UI, Event/Debug |
| **Fixtures** | qtbot, EventBus, DebugStore mit Events |
| **Assertions** | Events vor Clear; Clear klicken; store.get_event_history() == [] |
| **Fehlverhalten** | Clear-Button ohne Wirkung |

---

## 13. test_rag_enabled_augments_query_in_chat

| Feld | Wert |
|------|------|
| **Dateipfad** | `tests/integration/test_rag_chat_integration.py` (neu) |
| **Kategorie** | integration, async_behavior |
| **Schichten** | Service |
| **Fixtures** | temp_chroma_dir, tmp_path, settings |
| **Strategie** | Mock RAGService.augment_if_enabled → prüfen ob aufgerufen wenn rag_enabled=True |
| **Assertions** | ChatWidget mit rag_enabled=True, run_chat → augment_if_enabled aufgerufen mit enabled=True |
| **Fehlverhalten** | RAG aktiviert, aber augment nicht aufgerufen |

---

## 14. test_rag_failure_degrades_transparently

| Feld | Wert |
|------|------|
| **Dateipfad** | `tests/integration/test_rag_chat_integration.py` |
| **Kategorie** | integration, async_behavior |
| **Schichten** | Service, UI |
| **Strategie** | RAGService.augment_if_enabled wirft Exception → (query, False) zurück; Chat läuft mit Original-Query |
| **Assertions** | RAG wirft → augment returns (original_query, False); run_chat liefert Antwort (ohne RAG-Kontext) |
| **Fehlverhalten** | RAG-Fehler bricht Chat ab; keine transparente Degradation |

---

## 15. test_main_window_with_real_chat_widget

| Feld | Wert |
|------|------|
| **Dateipfad** | `tests/smoke/test_app_startup.py` |
| **Kategorie** | smoke, async_behavior |
| **Schichten** | UI, Service, Persistenz |
| **Fixtures** | temp_db_path, FakeOllamaClient, AppSettings |
| **Strategie** | MainWindow mit echtem ChatWidget, FakeClient, Temp-DB; keine ChatWidget-Mock |
| **Assertions** | MainWindow erstellt; chat_widget ist ChatWidget; chat_widget.chat_id kann gesetzt werden |
| **Fehlverhalten** | Künstlich geglätteter Startpfad; echte Verkabelung nicht getestet |

---

## Marker-Ergänzung (pytest.ini)

```
async_behavior: Async-sensitive Tests (Event-Loop, Race Conditions)
cross_layer: Prüft mehrere Schichten (UI↔Service↔Persistenz)
```

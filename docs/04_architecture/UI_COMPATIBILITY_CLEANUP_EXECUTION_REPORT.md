# UI Compatibility Cleanup – Execution Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Basis:** UI_COMPATIBILITY_CLEANUP_AUDIT.md

---

## 1. Gelöschte Dateien je Phase

### Phase 1 – app/ui/sidepanel/

| Datei | Status |
|-------|--------|
| `app/ui/sidepanel/__init__.py` | Gelöscht |
| `app/ui/sidepanel/chat_side_panel.py` | Gelöscht |
| `app/ui/sidepanel/model_settings_panel.py` | Gelöscht |
| `app/ui/sidepanel/prompt_manager_panel.py` | Gelöscht |
| Verzeichnis `app/ui/sidepanel/` | Entfernt (leer) |

### Phase 2 – app/ui/agents/ (ohne legacy/)

| Datei | Status |
|-------|--------|
| `app/ui/agents/__init__.py` | Gelöscht |
| `app/ui/agents/agent_manager_panel.py` | Gelöscht |
| `app/ui/agents/agent_list_panel.py` | Gelöscht |
| `app/ui/agents/agent_profile_panel.py` | Gelöscht |
| `app/ui/agents/agent_avatar_widget.py` | Gelöscht |
| `app/ui/agents/agent_form_widgets.py` | Gelöscht |
| `app/ui/agents/agent_list_item.py` | Gelöscht |
| `app/ui/agents/agent_performance_tab.py` | Gelöscht |

### Phase 3 – app/ui/chat/ (ohne chat_list_item.py)

| Datei | Status |
|-------|--------|
| `app/ui/chat/__init__.py` | Gelöscht |
| `app/ui/chat/chat_composer_widget.py` | Gelöscht |
| `app/ui/chat/chat_header_widget.py` | Gelöscht |
| `app/ui/chat/conversation_view.py` | Gelöscht |
| `app/ui/chat/chat_topic_section.py` | Gelöscht |
| `app/ui/chat/chat_message_widget.py` | Gelöscht |
| `app/ui/chat/chat_item_context_menu.py` | Gelöscht |
| `app/ui/chat/topic_actions.py` | Gelöscht |
| `app/ui/chat/topic_editor_dialog.py` | Gelöscht |

### Phase 4 – app/ui/debug/

| Datei | Status |
|-------|--------|
| `app/ui/debug/agent_debug_panel.py` | Gelöscht |
| `app/ui/debug/agent_activity_view.py` | Gelöscht |
| `app/ui/debug/model_usage_view.py` | Gelöscht |
| `app/ui/debug/tool_execution_view.py` | Gelöscht |
| `app/ui/debug/task_graph_view.py` | Gelöscht |
| `app/ui/debug/event_timeline_view.py` | Gelöscht |
| `app/ui/debug/__init__.py` | Gelöscht |
| Verzeichnis `app/ui/debug/` | Entfernt (leer) |

---

## 2. Durchgeführte Import-Umstellungen

| Datei | Alt | Neu |
|-------|-----|-----|
| `scripts/qa/checks.py` | `from app.ui.debug.event_timeline_view import _event_display_text` | `from app.gui.domains.runtime_debug.panels.event_timeline_view import _event_display_text` |
| `tests/meta/test_event_type_drift.py` | `from app.ui.debug.event_timeline_view import _event_display_text` | `from app.gui.domains.runtime_debug.panels.event_timeline_view import _event_display_text` |

---

## 3. Nicht gelöschte Dateien mit Begründung

| Datei | Begründung |
|-------|------------|
| `app/ui/agents/legacy/__init__.py` | MANUAL_REVIEW – nicht in diesem Sprint löschen |
| `app/ui/agents/legacy/agent_skills_panel.py` | MANUAL_REVIEW |
| `app/ui/agents/legacy/agent_activity_panel.py` | MANUAL_REVIEW |
| `app/ui/agents/legacy/agent_editor_panel.py` | MANUAL_REVIEW |
| `app/ui/agents/legacy/agent_runs_panel.py` | MANUAL_REVIEW |
| `app/ui/chat/chat_list_item.py` | MANUAL_REVIEW – Duplikat zu gui, bewusst behalten |

---

## 4. Verbleibende MANUAL_REVIEW-Dateien

| Pfad | Status |
|------|--------|
| `app/ui/agents/legacy/__init__.py` | Unverändert |
| `app/ui/agents/legacy/agent_skills_panel.py` | Unverändert |
| `app/ui/agents/legacy/agent_activity_panel.py` | Unverändert |
| `app/ui/agents/legacy/agent_editor_panel.py` | Unverändert |
| `app/ui/agents/legacy/agent_runs_panel.py` | Unverändert |
| `app/ui/chat/chat_list_item.py` | Unverändert |

---

## 5. Teststatus

### Auszuführende Tests (manuell)

```bash
pytest tests/architecture
pytest tests/ui/test_chat_ui.py
pytest tests/ui/test_prompt_manager_ui.py
pytest tests/state_consistency/test_prompt_consistency.py
pytest tests/ui/test_debug_panel_ui.py
pytest tests/cross_layer/test_debug_view_matches_failure_events.py
pytest tests/async_behavior/test_debug_clear_during_refresh.py
pytest tests/meta/test_event_type_drift.py
pytest tests/smoke/test_basic_chat.py
pytest tests/regression
```

**Hinweis:** pytest/PySide6 waren im Ausführungskontext nicht verfügbar. Der Nutzer sollte die Tests lokal ausführen.

---

## 6. Risiken

| Risiko | Bewertung | Mitigation |
|--------|-----------|------------|
| chat_list_item.py ist jetzt orphan | Niedrig | MANUAL_REVIEW – bewusst behalten; gui nutzt eigene Version |
| agents/legacy ohne __init__-Parent | Niedrig | agents/__init__ wurde gelöscht; legacy/ hat eigenes __init__ |
| Import-Pfade in anderen Modulen | Niedrig | Alle Konsumenten nutzen bereits gui; keine weiteren Anpassungen nötig |

---

## 7. Empfohlener nächster Schritt

1. **Tests lokal ausführen** – Bestätigung, dass alle genannten Test-Suites PASS
2. **MANUAL_REVIEW in späterem Sprint** – agents/legacy und chat_list_item.py prüfen:
   - agents/legacy: Toter Code; nach Bestätigung entfernen
   - chat_list_item.py: Duplikat; prüfen ob Migration nach gui oder Löschung sinnvoll

---

## Erfolgskriterien

| Kriterium | Status |
|-----------|--------|
| app/ui/sidepanel/ entfernt | ✓ |
| app/ui/agents/ enthält nur noch legacy/ | ✓ |
| app/ui/chat/ enthält nur noch chat_list_item.py | ✓ |
| app/ui/debug/ entfernt | ✓ |
| Import-Umstellungen durchgeführt | ✓ |
| MANUAL_REVIEW-Dateien unangetastet | ✓ |

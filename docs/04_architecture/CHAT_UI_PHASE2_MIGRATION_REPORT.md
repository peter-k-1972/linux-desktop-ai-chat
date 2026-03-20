# Chat UI Phase 2 – Migrationsbericht

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Referenz:** CHAT_UI_PHASE1_ANALYSIS.md

---

## 1. Erweiterungen an gui chat_list_item

**Datei:** `app/gui/domains/operations/chat/panels/chat_list_item.py`

### Änderungen

| Erweiterung | Beschreibung |
|-------------|--------------|
| **preview** | Optionaler Parameter `preview: Optional[str] = None` nach `parent`. Zeigt kurzen Text-Preview (max. 80 Zeichen) unter dem Titel. |
| **context_menu_requested** | Neues Signal `Signal(int)` – emittiert `chat_id` bei Rechtsklick. |
| **contextMenuEvent** | Override, ruft `context_menu_requested.emit(self._chat_id)` auf. |
| **format_relative_time** | Öffentlicher Alias für `_format_relative_time` – Kompatibilität mit ChatTopicSection und ui.chat. |

### Rückwärtskompatibilität

- Bestehende Aufrufe `ChatListItemWidget(chat_id, title, time_str, active, parent)` funktionieren unverändert.
- `session_explorer_panel` nutzt weiterhin die 5-Parameter-Signatur ohne preview.
- Keine Änderung an `_format_relative_time` – session_explorer_panel importiert weiterhin `_format_relative_time`.

---

## 2. Migration von chat_topic_section nach gui

**Neue Datei:** `app/gui/domains/operations/chat/panels/chat_topic_section.py`

### Inhalt

- Vollständige Übernahme der Logik aus `app/ui/chat/chat_topic_section.py`.
- Imports umgestellt:
  - `ChatListItemWidget`, `format_relative_time` aus `app.gui.domains.operations.chat.panels.chat_list_item`
  - Keine Imports aus `app.ui.chat`.
- Entfernt: ungenutzter Import `QScrollArea`.
- Keine funktionalen Erweiterungen.

### ChatListItemWidget-Aufruf

```python
item = ChatListItemWidget(
    chat_id, title, time_str, active=active, parent=self, preview=preview
)
```

---

## 3. Umstellung von chat_navigation_panel

**Datei:** `app/gui/domains/operations/chat/panels/chat_navigation_panel.py`

### Änderung

```diff
- from app.ui.chat.chat_topic_section import ChatTopicSection
+ from app.gui.domains.operations.chat.panels.chat_topic_section import ChatTopicSection
```

- Keine weiteren Änderungen.
- Kein ui-Import mehr in dieser Datei.

---

## 4. Verbleibende gui→ui Violations

| Datei | Import | Status |
|-------|--------|--------|
| `gui/legacy/chat_widget.py` | app.ui.chat.conversation_view, chat_composer_widget, chat_header_widget | Unverändert (Phase 3) |

**chat_navigation_panel** wurde aus `KNOWN_GUI_UI_VIOLATIONS` entfernt.

---

## 5. Angepasste Tests

- Keine Testanpassungen erforderlich.
- Tests importieren weiterhin über `app.ui.chat` (z.B. ConversationView, ChatComposerWidget, ChatHeaderWidget) – diese Module wurden in Phase 2 nicht migriert.
- `app.ui.chat.chat_topic_section` ist Re-Export; `from app.ui.chat import ChatTopicSection` funktioniert weiterhin.

---

## 6. Teststatus

| Test-Suite | Ergebnis |
|------------|----------|
| tests/architecture | 13 passed |
| tests/architecture/test_gui_does_not_import_ui | PASS |
| tests/regression | Alle relevanten passed |
| tests/ui/test_chat_ui | 9 passed (1 deselected: test_prompt_apply_to_chat_visible – Prompt-Model-Änderung, unabhängig) |

**Hinweis:** 6 Fehler in `tests/ui/test_prompt_manager_ui.py` und 1 in `test_chat_ui.py::test_prompt_apply_to_chat_visible` sind vorbestehend (Prompt-Model fehlt `scope`, `project_id`) und nicht durch diese Migration verursacht.

---

## 7. Risiken

| Risiko | Bewertung | Mitigation |
|--------|-----------|------------|
| session_explorer_panel bricht | Niedrig | ChatListItemWidget-Signatur rückwärtskompatibel; preview optional. |
| ChatTopicSection-Verhalten ändert sich | Niedrig | 1:1-Migration, keine Logikänderung. |
| ui-Re-Export-Kette | Niedrig | ui/chat/chat_topic_section.py re-exportiert aus gui; Legacy-Konsumenten erhalten weiterhin ChatTopicSection. |

---

## 8. Erfolgskriterien (Phase 2)

| Kriterium | Status |
|-----------|--------|
| app/gui/domains/operations/chat/panels/chat_topic_section.py existiert | ✓ |
| chat_navigation_panel importiert kein app.ui.chat mehr | ✓ |
| app/ui/chat/chat_topic_section.py ist nur noch Re-Export | ✓ |
| chat_navigation_panel aus KNOWN_GUI_UI_VIOLATIONS entfernt | ✓ |
| Architekturtests PASS | ✓ |
| Keine neue Parallelimplementierung | ✓ |

---

## 9. Nächste Schritte (Phase 3)

- conversation_view, chat_header_widget, chat_composer_widget nach gui migrieren
- gui/legacy/chat_widget auf gui-Imports umstellen
- KNOWN_GUI_UI_VIOLATIONS leeren (chat_widget entfernen)

# Chat UI Phase 3 – Migrationsbericht

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Referenz:** CHAT_UI_PHASE2_MIGRATION_REPORT.md, CHAT_UI_PHASE1_ANALYSIS.md

---

## 1. Migration von conversation_view nach gui

**Neue Datei:** `app/gui/domains/operations/chat/panels/conversation_view.py`

### Inhalt

- Vollständige Übernahme der Logik aus `app/ui/chat/conversation_view.py`.
- Import von `ChatMessageWidget` aus `app.gui.domains.operations.chat.panels.chat_message_widget` (bereits gui).
- Keine ui-Imports.
- Keine funktionalen oder Design-Änderungen.

### Re-Export

`app/ui/chat/conversation_view.py` → Re-Export von `ConversationView` aus gui.

---

## 2. Migration von chat_header_widget nach gui

**Neue Datei:** `app/gui/domains/operations/chat/panels/chat_header_widget.py`

### Inhalt

- Vollständige Übernahme der Logik aus `app/ui/chat/chat_header_widget.py`.
- Imports: `app.core.models.roles`, `app.resources.styles` – keine ui-Abhängigkeiten.
- Keine funktionalen oder Design-Änderungen.

### Re-Export

`app/ui/chat/chat_header_widget.py` → Re-Export von `ChatHeaderWidget` aus gui.

---

## 3. Migration von chat_composer_widget nach gui

**Neue Datei:** `app/gui/domains/operations/chat/panels/chat_composer_widget.py`

### Inhalt

- Vollständige Übernahme inkl. interner Klasse `ChatInput`.
- Imports: `app.help.tooltip_helper`, PySide6 – keine ui-Abhängigkeiten.
- Keine funktionalen oder Design-Änderungen.

### Re-Export

`app/ui/chat/chat_composer_widget.py` → Re-Export von `ChatComposerWidget`, `ChatInput` aus gui.

---

## 4. Umstellung von gui/legacy/chat_widget.py

### Änderungen

```diff
- from app.ui.chat.conversation_view import ConversationView
- from app.ui.chat.chat_composer_widget import ChatComposerWidget
- from app.ui.chat.chat_header_widget import ChatHeaderWidget
+ from app.gui.domains.operations.chat.panels.conversation_view import ConversationView
+ from app.gui.domains.operations.chat.panels.chat_composer_widget import ChatComposerWidget
+ from app.gui.domains.operations.chat.panels.chat_header_widget import ChatHeaderWidget
```

- Keine weiteren Änderungen.
- **Verbleibender ui-Import:** `app.ui.sidepanel.chat_side_panel.ChatSidePanel` (nicht Teil dieser Phase).

---

## 5. Änderungen an Tests

| Testdatei | Änderung |
|-----------|----------|
| `tests/ui/test_chat_ui.py` | Imports von `app.ui.chat.*` auf `app.gui.domains.operations.chat.panels.*` umgestellt |
| `tests/smoke/test_basic_chat.py` | `ConversationView`-Import auf gui-Pfad umgestellt |
| `tests/regression/test_agent_delete_removes_from_list.py` | `ChatHeaderWidget`-Import auf gui-Pfad umgestellt |
| `tests/regression/test_chat_composer_send_signal_actually_emits.py` | `ChatComposerWidget`, `ChatInput`-Import auf gui-Pfad umgestellt |

---

## 6. Verbleibende gui→ui Violations

| Datei | Import | Status |
|-------|--------|--------|
| `gui/legacy/chat_widget.py` | app.ui.sidepanel.chat_side_panel | Unverändert (Sidepanel-Migration separat) |

**Chat-spezifische Violations:** Keine mehr. Alle app.ui.chat-Imports wurden entfernt.

---

## 7. Teststatus

| Test-Suite | Ergebnis |
|------------|----------|
| tests/architecture | 13 passed |
| tests/architecture/test_gui_does_not_import_ui | PASS |
| tests/ui/test_chat_ui | 9 passed |
| tests/regression | 16 passed |
| tests/smoke/test_basic_chat | 4 passed |

**Hinweis:** 1 Test (test_prompt_apply_to_chat_visible) deselektiert – vorbestehender Prompt-Model-Fehler.

---

## 8. Risiken

| Risiko | Bewertung | Mitigation |
|--------|-----------|------------|
| ui-Re-Export-Kette bricht | Niedrig | ui/chat/* re-exportiert aus gui; Legacy-Konsumenten (z.B. ui/chat/__init__) erhalten weiterhin Klassen |
| ChatWidget-Verhalten ändert sich | Niedrig | Nur Importpfade geändert; gleiche Klassen aus gui |
| Sidepanel-Violation bleibt | Bekannt | chat_widget importiert weiterhin ChatSidePanel aus ui; separate Migration erforderlich |

---

## 9. Erfolgskriterien (Phase 3)

| Kriterium | Status |
|-----------|--------|
| conversation_view existiert unter gui/panels | ✓ |
| chat_header_widget existiert unter gui/panels | ✓ |
| chat_composer_widget existiert unter gui/panels | ✓ |
| gui/legacy/chat_widget.py importiert kein app.ui.chat mehr | ✓ |
| ui/chat/{conversation_view,chat_header_widget,chat_composer_widget}.py sind nur Re-Exports | ✓ |
| Architekturtests PASS | ✓ |
| Chat-Violations aus KNOWN_GUI_UI_VIOLATIONS entfernt oder deutlich reduziert | ✓ (keine Chat-Violations mehr) |
| Keine funktionale Vereinheitlichung | ✓ |

---

## 10. Nächste Schritte

- **Sidepanel-Migration:** ChatSidePanel nach gui migrieren, chat_widget umstellen
- **KNOWN_GUI_UI_VIOLATIONS:** chat_widget entfernen, sobald Sidepanel migriert ist

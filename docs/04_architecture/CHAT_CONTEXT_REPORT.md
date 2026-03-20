# Chat-Kontext – Abschlussreport

**Stand:** 2026-03-17  
**Ziel:** Chat kontextbewusst machen – Projekt, Chat, Topic sichtbar.

---

## 1. Analysierter Ist-Zustand

### 1.1 ChatWorkspace-Layout (vorher)

```
[ ChatNavigationPanel ] | [ Conversation + Input ] | [ ChatDetailsPanel ]
```

- **ChatConversationPanel:** Kein Header, nur Nachrichten
- **Breadcrumb (Shell):** Projekt / Chat / Detail – aber Shell-Level
- **ChatDetailsPanel:** Projekt, Topic – rechts, collapsible

### 1.2 Lücke

Der Chat-Bereich selbst zeigte keinen Kontext – Nutzer sah nur Nachrichten.

---

## 2. Umgesetzte Änderungen

### 2.1 ChatContextBar

**Neue Komponente:** `app/gui/domains/operations/chat/panels/chat_context_bar.py`

- Leichte Kontextleiste über dem Nachrichtenbereich
- Zeigt: `[ Projekt: XYZ ] [ Chat: Titel ] [ Topic: optional ]`
- API: `set_context(project_name, chat_title, topic_name)`
- Theme-integriert via `#chatContextBar`, `#chatContextProject`, etc.

### 2.2 Integration in ChatWorkspace

- ChatContextBar in Center-Spalte über ChatConversationPanel
- `_refresh_context_bar()` holt Kontext aus:
  - Projekt: `get_project_of_chat()` oder `get_active_project()`
  - Chat: `get_chat_info(chat_id)`
  - Topic: `get_chat_info(chat_id).topic_name`
- Bei keinem Projekt: „Globale Chats“

### 2.3 Kontextbindung

| Ereignis | Aktion |
|----------|--------|
| Projektwechsel | `_restore_project_selection` → `_refresh_context_bar` |
| Chat-Auswahl | `_on_session_selected` → `_refresh_context_bar` |
| Chat gelöscht | `_refresh_context_bar` (oder erstes verbleibendes) |
| Neuer Chat | `_run_send` → `_refresh_context_bar` |
| Details-Update (Rename, etc.) | `_on_details_chat_updated` → `_refresh_context_bar` |
| Initial | `QTimer.singleShot(50, _refresh_context_bar)` |
| Nach Streaming | `_refresh_context_bar` (Titel-Update) |

### 2.4 UX-Regeln

- Kontext sichtbar, aber nicht dominant (font_size_xs, color_text_secondary)
- Klare Hierarchie: Projekt → Chat → Topic
- Keine visuelle Überladung

---

## 3. Tests

**Neu:** `tests/structure/test_chat_context_bar.py`

- `test_context_bar_set_project_and_chat`
- `test_context_bar_set_with_topic`
- `test_context_bar_clear`
- `test_context_bar_project_switch`
- `test_context_bar_chat_switch`

---

## 4. Geänderte Dateien

| Datei | Änderung |
|-------|----------|
| `chat_context_bar.py` | Neu |
| `chat_workspace.py` | ChatContextBar integriert, `_refresh_context_bar` |
| `shell.qss` | Styles für #chatContextBar |
| `panels/__init__.py` | ChatContextBar exportiert |

---

## 5. Ergebnis

Der Chat ist nicht mehr nur ein Eingabe-/Ausgabefeld, sondern ein **kontextgebundenes Arbeitswerkzeug**:

- Nutzer sieht im Chat: Projekt, Chat-Titel, optional Topic
- Kontext aktualisiert sich bei Projekt-/Chat-Wechsel
- Keine Inkonsistenzen durch zentrale `_refresh_context_bar`-Logik

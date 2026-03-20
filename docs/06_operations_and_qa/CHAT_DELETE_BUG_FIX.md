# Chat-Delete-Bug – Analyse und Fix

**Datum:** 2026-03-16  
**Problem:** Beim Löschen eines einzelnen Chats aus der Sidebar verschwinden offenbar alle Chats oder die gesamte Chatliste.

---

## Verifizierter Delete-Pfad

| Stufe | Datei | Komponente |
|-------|-------|------------|
| UI | `chat_list_item.py` | `contextMenuEvent` → `context_menu_requested.emit(chat_id)` |
| UI | `chat_topic_section.py` | `set_chats` → `connect(context_menu_requested)` → `chat_context_menu_requested.emit(cid, …)` |
| UI | `chat_navigation_panel.py` | `_on_chat_context_menu` → `build_chat_item_context_menu` |
| UI | `chat_item_context_menu.py` | `_do_delete(chat_id, …)` → `get_chat_service().delete_chat(chat_id)` |
| Service | `chat_service.py` | `delete_chat(chat_id)` |
| DB | `db.py` | `delete_chat(chat_id)` → DELETE WHERE chat_id=? |

**Ergebnis:** Der Pfad ist korrekt. `chat_id` wird durch den gesamten Ablauf durchgereicht. Die SQL-Statements sind korrekt (nur genau ein Chat wird gelöscht).

---

## Mögliche Ursachen (ohne Reproduktion)

1. **Lambda-Closure:** `chat_id` könnte in einer Schleife falsch gebunden sein → Fix: `lambda cid=chat_id:` in der Delete-Lambda.
2. **Chat-Workspace:** Nach dem Löschen des aktiven Chats bleibt die Conversation-View erhalten → Nutzer könnte denken, „alles weg“ ist.
3. **Ungültige Ids:** Wenn `chat_id` versehentlich `None`, `0` oder `project_id` ist, könnte `delete_chat` falsch reagieren → Validierung ergänzt.

---

## Implementierter Fix

### 1. Lambda-Closure (`chat_item_context_menu.py`)

```python
lambda cid=chat_id: _do_delete(cid, chat_title, parent_widget, on_action, on_chat_deleted)
```

`chat_id` wird explizit als Default-Argument gebunden, um späte Bindung zu vermeiden.

### 2. Validierung (`chat_item_context_menu.py`, `chat_service.py`, `db.py`)

```python
if not isinstance(chat_id, int) or chat_id <= 0:
    return
```

Ungültige `chat_id`-Werte führen zu keinem Löschvorgang.

### 3. Workspace nach Delete (`chat_workspace.py`)

- Neues Signal: `chat_deleted = Signal(int)` in `ChatNavigationPanel`
- Callback `on_chat_deleted` in `build_chat_item_context_menu`
- `ChatWorkspace._on_chat_deleted`: Wenn der gelöschte Chat der aktive war, wird Conversation geleert und der erste verbleibende Chat ausgewählt.

### 4. Keine weiteren Änderungen

- Keine Änderung in der Architektur
- Kein Refactoring außerhalb des betroffenen Pfads
- Keine Änderung an SQL oder Foreign-Key-Logik

---

## Betroffene Dateien

| Datei | Änderung |
|-------|----------|
| `app/ui/chat/chat_item_context_menu.py` | `lambda cid=chat_id`, `on_chat_deleted`, Validierung |
| `app/ui/chat/chat_navigation_panel.py` | `chat_deleted` Signal, `get_first_chat_id()`, `on_chat_deleted` |
| `app/gui/domains/operations/chat/chat_workspace.py` | `_on_chat_deleted`, Verbindung mit `chat_deleted` |
| `app/services/chat_service.py` | Validierung in `delete_chat` |
| `app/db.py` | Validierung in `delete_chat` |
| `tests/regression/test_chat_delete_single.py` | Neu: Regressionstests |

---

## Regressionstest

```bash
pytest tests/regression/test_chat_delete_single.py -v
```

- `test_delete_single_chat_leaves_others_intact`: Erstellt 3 Chats, löscht einen, prüft, dass nur dieser entfernt wurde.
- `test_delete_chat_removes_messages_only_for_that_chat`: Prüft, dass Nachrichten anderer Chats erhalten bleiben.
- `test_delete_chat_rejects_invalid_id`: Prüft, dass ungültige IDs keinen Löschvorgang auslösen.

---

## Warum keine Nebenwirkungen

- **Lambda:** Nur explizite Default-Bindung für `chat_id`; keine Änderung an anderen Logik.
- **Validierung:** Kein Löschvorgang bei ungültigen IDs; keine Änderung an gültigen Fällen.
- **Signal:** `chat_deleted` wird nur bei tatsächlichem Löschen emittiert; `_on_chat_deleted` reagiert nur, wenn der gelöschte Chat der aktive war.
- **Keine Änderung an:** SQL, Foreign Keys, Projektstruktur, anderen Workspaces.

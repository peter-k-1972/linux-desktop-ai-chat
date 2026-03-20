# Projektbezogene Chat-Listen-UX

**Version:** 1.1  
**Datum:** 2026-03-16  
**Status:** Implementiert  
**Ergänzung:** docs/CHAT_GLOBAL_MODE.md – Chat unterstützt Global Mode (ohne Projekt)

---

## 1. Überblick

Die Chat-Liste im ChatWorkspace ist ein **projektbezogener Arbeits-Explorer** mit optionalem **Global Mode**:

- Zeigt nur Chats des aktiven Projekts
- Projektkontext sichtbar im Header
- Gruppierung nach Zeit (Heute, Gestern, Diese Woche, Älter)
- Chat-Einträge mit Titel und letzter Aktivität
- Klare Markierung des aktiven Chats

---

## 2. Mentales Modell

```
Aktives Projekt
 └── Chat-Liste dieses Projekts
      ├── Heute
      │   ├── Chat A
      │   └── Chat B
      ├── Gestern
      │   └── Chat C
      └── Diese Woche
          └── Chat D
```

---

## 3. Komponenten

### ChatSessionExplorerPanel

- **Projekt-Header:** Zeigt aktives Projekt oder „Bitte Projekt auswählen“
- **Neuer Chat:** Erstellt Chat im aktiven Projekt (deaktiviert ohne Projekt)
- **Suchfeld:** Filtert Chats nach Titel (nur bei aktivem Projekt sichtbar)
- **Chat-Liste:** Gruppiert nach Heute, Gestern, Diese Woche, Älter

### ChatListItemWidget

- Titel (max. 60 Zeichen)
- Letzte Aktivität (relativ: „vor 2 Std“, „gestern“, etc.)
- Aktive Markierung (blauer Rahmen, hervorgehobener Titel)

### ChatContextInspector

- Chat-Titel
- Projekt
- Letzte Aktivität (formatiert)
- Modell, Nachrichtenanzahl, Status

---

## 4. Service-Integration

### ChatService – neue Methoden

```python
list_chats_for_project(project_id, filter_text="") -> list
# Chats mit last_activity, sortiert nach letzter Aktivität

create_chat_in_project(project_id, title="Neuer Chat") -> int
# Erstellt Chat und ordnet ihn dem Projekt zu

get_chat_info(chat_id) -> dict | None
# id, title, created_at, last_activity
```

### DatabaseManager – neue Methoden

```python
list_chats_for_project_with_activity(project_id, filter_text) -> list
get_chat_info(chat_id) -> dict | None
```

---

## 5. Titelstrategie

- **Explizit gespeichert:** `chats.title`
- **Fallback:** Erste Nachricht (erste 50 Zeichen) bei „Neuer Chat“
- **Default:** „Neuer Chat“

---

## 6. Projektintegration

- **Ohne Projekt (Global Mode):** Header „Globale Chats“, Neuer Chat aktiv, Topics deaktiviert. Siehe docs/CHAT_GLOBAL_MODE.md
- **Mit Projekt:** Chat-Liste zeigt nur Chats des Projekts
- **Projektwechsel:** Chat-Liste wird neu geladen
- **Neuer Chat:** Mit oder ohne Projekt möglich (create_chat / create_chat_in_project)
- **Senden ohne Chat:** Erstellt Chat im Projekt oder global

---

## 7. UX-Entscheidungen

1. **Global Mode** – Ohne Projekt: „Globale Chats“, create_chat() nutzbar (docs/CHAT_GLOBAL_MODE.md)
2. **Zeitgruppierung** – Heute, Gestern, Diese Woche, Älter
3. **Relative Zeit** – „vor 2 Std“, „gestern“ statt Datum
4. **Titel aus erster Nachricht** – Automatisch bei „Neuer Chat“
5. **Suchfeld** – Nur bei aktivem Projekt sichtbar

---

## 8. Dateien

| Datei | Zweck |
|-------|-------|
| `app/gui/domains/operations/chat/panels/session_explorer_panel.py` | Projektbezogener Chat-Explorer |
| `app/gui/domains/operations/chat/panels/chat_list_item.py` | Chat-Eintrag mit Titel + Zeit |
| `app/gui/domains/operations/chat/chat_workspace.py` | Integration, Projektpflicht |
| `app/gui/inspector/chat_context_inspector.py` | Titel, letzte Aktivität |
| `app/services/chat_service.py` | list_chats_for_project, create_chat_in_project, get_chat_info |
| `app/db.py` | list_chats_for_project_with_activity, get_chat_info |

---

## 9. Start

```bash
.venv/bin/python run_gui_shell.py
```

1. Projekt in der TopBar auswählen
2. Operations → Chat
3. Chat-Liste zeigt nur Chats des Projekts
4. „Neuer Chat“ legt Chat im Projekt an
5. Erste Nachricht setzt Chat-Titel

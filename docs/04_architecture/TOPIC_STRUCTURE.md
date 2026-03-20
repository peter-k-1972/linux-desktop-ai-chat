# Topic-Struktur für projektbezogene Chats

**Version:** 1.0  
**Datum:** 2026-03-15

## Übersicht

Topics sind flache, arbeitsorientierte Container für Chats innerhalb eines Projekts. Sie gruppieren Chats thematisch, ohne tiefe Ordnerstrukturen.

## Datenmodell

### Topics-Tabelle

| Spalte      | Typ     | Beschreibung                    |
|-------------|---------|---------------------------------|
| id          | INTEGER | Primärschlüssel                 |
| project_id  | INTEGER | Zugehöriges Projekt             |
| name        | TEXT    | Topic-Name                      |
| description | TEXT    | Optionale Beschreibung          |
| created_at  | DATETIME| Erstellungszeitpunkt            |
| updated_at  | DATETIME| Letzte Aktualisierung           |

### project_chats (erweitert)

| Spalte     | Typ     | Beschreibung                    |
|------------|---------|---------------------------------|
| topic_id   | INTEGER | Optional. NULL = Ungrouped      |

## Services

### TopicService

- `list_topics_for_project(project_id)` – Topics eines Projekts
- `create_topic(project_id, name, description)` – Neues Topic anlegen
- `get_topic(topic_id)` – Topic-Details
- `update_topic(topic_id, name, description)` – Topic bearbeiten
- `delete_topic(topic_id)` – Topic löschen (Chats werden ungrouped)
- `move_chat_to_topic(project_id, chat_id, topic_id)` – Chat zuordnen (topic_id=None = Ungrouped)

### ChatService (erweitert)

- `create_chat_in_project(project_id, title, topic_id=None)` – Chat mit optionalem Topic
- `move_chat_to_topic(project_id, chat_id, topic_id)` – Chat einem Topic zuordnen

## UX-Struktur

```
Aktives Projekt
[+ Neuer Chat] [+ Neues Topic]

Topics
────────────────

RAG Architecture [+]
   Chat A
   Chat B

QA System [+]
   Chat C

Ungrouped [+]
   Chat D
```

- **Neuer Chat**: Erstellt Chat ohne Topic (Ungrouped)
- **Neues Topic**: Dialog für Topic-Namen
- **Topic [+]** : Erstellt Chat direkt in diesem Topic
- **Inspector**: Topic-Dropdown zum Zuordnen/Verschieben

## Migration

Bestehende Datenbanken werden automatisch migriert:

- `topics`-Tabelle wird angelegt, falls nicht vorhanden
- `topic_id` wird zu `project_chats` hinzugefügt, falls nicht vorhanden
- Bestehende Chats bleiben ungrouped (topic_id = NULL)

## Wichtige Klassen

| Klasse                  | Datei                          | Zweck                                      |
|-------------------------|--------------------------------|--------------------------------------------|
| TopicService            | services/topic_service.py      | CRUD für Topics, Zuordnungen               |
| ChatSessionExplorerPanel| chat/panels/session_explorer_panel.py | Topic-aware Chat-Liste             |
| TopicSectionHeader      | session_explorer_panel.py       | Topic-Header mit +-Button                  |
| ChatContextInspector    | inspector/chat_context_inspector.py | Topic-Anzeige, Dropdown-Zuordnung   |

## Startanweisung

```bash
python run_gui_shell.py
# oder
python -m app
```

1. Projekt auswählen (Project Switcher in der TopBar)
2. Zu Chat wechseln (Sidebar: WORKSPACE → Chat)
3. „Neues Topic“ klicken, Namen eingeben
4. „Neuer Chat“ oder [+] neben Topic für neuen Chat
5. Im Inspector: Topic-Dropdown zum Zuordnen bestehender Chats

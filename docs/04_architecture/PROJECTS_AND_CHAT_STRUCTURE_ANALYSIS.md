# Projekt-/Chat-/Workspace-Struktur – Analyse

**Stand:** 2026-03-17  
**Ziel:** Klare, produktive Projekt-/Chat-Organisation.

---

## 1. Was bereits existiert

### 1.1 Kontext-System

| Komponente | Ort | Rolle |
|------------|-----|-------|
| **ProjectContextManager** | `app/core/context/project_context_manager.py` | Zentrale Quelle für aktives Projekt; lädt aus DB; emittiert project_context_changed |
| **ActiveProjectContext** | `app/core/context/active_project.py` | State-Holder; synchron mit ProjectContextManager |
| **project_events** | `app/gui/events/project_events.py` | EventBus: subscribe_project_events, emit_project_context_changed |

### 1.2 Services

| Service | API | Persistenz |
|---------|-----|------------|
| **ProjectService** | list_projects, create_project, get_project, add_chat_to_project, get_project_of_chat, list_chats_of_project | DatabaseManager |
| **ChatService** | create_chat, create_chat_in_project, list_chats_for_project, load_chat, save_message | DatabaseManager |
| **TopicService** | list_topics_for_project, create_topic, set_chat_topic | DatabaseManager |

### 1.3 Datenmodell

| Tabelle | Beziehung |
|---------|-----------|
| projects | project_id, name, description, status |
| project_chats | project_id, chat_id, topic_id, pinned, archived |
| topics | project_id, name |
| chats | id, title |

**Chat → Projekt:** 1:1 (ein Chat höchstens einem Projekt zugeordnet via project_chats).

### 1.4 UI-Komponenten

| Komponente | Rolle |
|------------|-------|
| **ProjectSwitcherButton** | TopBar; zeigt aktives Projekt; öffnet ProjectSwitcherDialog |
| **ProjectSwitcherDialog** | Projekt wechseln, Neues Projekt, Recent/All |
| **ChatNavigationPanel** | Abonniert project_context_changed; zeigt Projektname; lädt Chats via list_chats_for_project |
| **ChatWorkspace** | Abonniert project_context_changed; erstellt Chats in Projekt; speichert letzte Auswahl pro Projekt |
| **ChatDetailsPanel** | Zeigt project_name des aktuellen Chats |
| **ChatContextInspector** | Zeigt project_id, project_name |

---

## 2. Was produktiv nutzbar ist

- **Projekt wechseln:** TopBar → ProjectSwitcherDialog → ProjectContextManager.set_active_project
- **Chats pro Projekt:** ChatNavigationPanel lädt list_chats_for_project(project_id)
- **Neuer Chat im Projekt:** create_chat_in_project bei aktivem Projekt
- **Neuer Chat ohne Projekt:** create_chat wenn kein Projekt aktiv
- **Projektwechsel:** Workspace cleared, letzte Auswahl pro Projekt wiederhergestellt
- **Chat → Projekt:** get_project_of_chat, in Details/Inspector sichtbar

---

## 3. Was fehlt oder schwach ist

| Aspekt | Befund |
|--------|--------|
| **Sichtbarkeit aktives Projekt im Chat** | Nur TopBar; Chat-Bereich selbst zeigt kein aktives Projekt-Label |
| **ChatNavigationPanel Styles** | Hardcoded (#64748b, #1f2937, #f8fafc) – nicht theme-integriert |
| **Projekt-Header** | "Bitte Projekt auswählen" nur initial; wird durch "Globale Chats" / Projektname ersetzt |
| **Tests** | Keine gezielten Tests für Projekt-Kontext-Sync, Chat-Listen-Konsistenz |

---

## 4. Legacy / Übergang

| Komponente | Status |
|------------|--------|
| **ProjectChatListWidget** | Legacy (main.py); nicht Teil Shell/ChatWorkspace |
| **main.py** | Legacy; display_project, open_chat, project_chat_list_widget |

---

## 5. Größte Inkonsistenz

- **Zwei Kontext-Systeme:** ProjectContextManager und ActiveProjectContext – bereits synchronisiert (Phase 3 Fix).
- **ChatNavigationPanel:** Hardcoded Styles statt Theme-Tokens.
- **Fehlende Tests:** Projekt-Wechsel, Chat-Listen-Konsistenz.

---

## 6. Empfohlene Zielstruktur

### 6.1 Begriffe

| Begriff | Definition |
|---------|------------|
| **Projekt** | Container für Chats, Topics, Dateien, Prompts |
| **Chat** | Gespräch/Thread; gehört zu 0 oder 1 Projekt |
| **Aktiver Projektkontext** | Projekt, dessen Chats im ChatWorkspace angezeigt werden |
| **Globale Chats** | Chats ohne Projekt oder alle Chats wenn kein Projekt aktiv |

### 6.2 Beziehungen

```
Projekt 1 ──* Chat (via project_chats)
Projekt 1 ──* Topic
Chat 0..1 ──* Topic (via project_chats.topic_id)
```

### 6.3 Zustandsfluss

```
ProjectSwitcherDialog / ProjectsWorkspace
    → ProjectContextManager.set_active_project(project_id)
    → emit_project_context_changed(project_id)
    → ChatNavigationPanel, ChatWorkspace, ProjectSwitcherButton
```

---

## 7. Priorisierte Maßnahmen

1. **ChatNavigationPanel:** Theme-Integration (hardcoded Styles entfernen)
2. **Tests:** Projekt-Kontext-Sync, Chat-Listen bei Projektwechsel
3. **Optional:** Aktives Projekt im Chat-Bereich sichtbar (z. B. in ChatNavigationPanel-Header)

# Projekt-/Chat-/Workspace-Struktur – Abschlussreport

**Stand:** 2026-03-17  
**Task:** Saubere Projekt-/Workspace-/Chat-Struktur für die Anwendung.

---

## 1. Analysierter Ist-Zustand

### 1.1 Kontext-System (stabil)

| Komponente | Rolle |
|------------|-------|
| **ProjectContextManager** | Zentrale Quelle für aktives Projekt; lädt aus DB; emittiert project_context_changed |
| **ActiveProjectContext** | State-Holder; synchron mit ProjectContextManager |
| **project_events** | EventBus: subscribe_project_events, emit_project_context_changed |

### 1.2 Services (produktiv)

| Service | API |
|---------|-----|
| **ProjectService** | list_projects, create_project, get_project, add_chat_to_project, get_project_of_chat, list_chats_of_project |
| **ChatService** | create_chat, create_chat_in_project, list_chats_for_project, load_chat, save_message |
| **TopicService** | list_topics_for_project, create_topic, set_chat_topic |

### 1.3 Datenmodell

- **projects:** project_id, name, description, status
- **project_chats:** project_id, chat_id, topic_id, pinned, archived
- **topics:** project_id, name
- **chats:** id, title

**Chat → Projekt:** 1:1 via project_chats.

### 1.4 UI-Komponenten

- **ProjectSwitcherButton** (TopBar): Projekt wechseln
- **ChatNavigationPanel**: Projektname / „Globale Chats“; lädt Chats pro Projekt
- **ChatWorkspace**: Abonniert project_context_changed; erstellt Chats im Projekt; speichert letzte Auswahl pro Projekt
- **ChatDetailsPanel**: Zeigt project_name des aktuellen Chats

---

## 2. Zielmodell

### 2.1 Begriffe

| Begriff | Definition |
|---------|-------------|
| **Projekt** | Container für Chats, Topics, Dateien, Prompts |
| **Chat** | Gespräch/Thread; gehört zu 0 oder 1 Projekt |
| **Aktiver Projektkontext** | Projekt, dessen Chats im ChatWorkspace angezeigt werden |
| **Globale Chats** | Chats ohne Projekt oder alle Chats wenn kein Projekt aktiv |

### 2.2 Beziehungen

```
Projekt 1 ──* Chat (via project_chats)
Projekt 1 ──* Topic
Chat 0..1 ──* Topic (via project_chats.topic_id)
```

### 2.3 Zustandsfluss

```
ProjectSwitcherDialog / ProjectsWorkspace
    → ProjectContextManager.set_active_project(project_id)
    → emit_project_context_changed(project_id)
    → ChatNavigationPanel, ChatWorkspace, ProjectSwitcherButton
```

---

## 3. Umgesetzte Härtungen / Ergänzungen

### 3.1 UI-Struktur (Theme-Integration)

**ChatNavigationPanel:**

- Hardcoded Styles entfernt
- Styles in `app/gui/themes/base/shell.qss` mit Theme-Tokens integriert:
  - `#chatNavigationPanel`, `#chatNavProjectHeader`, `#chatNavProjectLabel`
  - `#chatNavSearch`, `#chatNavFilterTopic`, `#chatNavFilterRecent`
  - `#chatNavNewChatButton`, `#chatNavNewTopicButton`
  - `#chatNavigationPanel QCheckBox` für Filter-Checkboxen
- Projekt-Label: dynamische Farbe über `projectMode`-Property (true/false) und QSS-Attributselektor

### 3.2 Chat-Kontext und Projektkontext

- Bereits verbunden: ChatWorkspace abonniert project_context_changed
- ChatNavigationPanel zeigt Projektname oder „Globale Chats“
- Neuer Chat: create_chat_in_project bei aktivem Projekt, create_chat bei globalem Modus
- Projektwechsel: Workspace cleared, letzte Auswahl pro Projekt wiederhergestellt

### 3.3 Service-/Persistenz-Konsistenz

- Keine Änderungen nötig; bestehende Struktur trägt das Zielmodell
- ProjectService, ChatService, TopicService mit klaren Zuständigkeiten

### 3.4 Tests

**Neu:** `tests/structure/test_project_chat_structure.py`

- `test_projects_exist_and_load`: Projekte werden geladen
- `test_chats_assignable_to_projects`: Chats sind Projekten zuordenbar
- `test_project_switch_chat_list_consistency`: Chat-Listen pro Projekt getrennt
- `test_chat_list_no_regression`: Chat-Grundpfad funktioniert

**Bestehend:** `tests/regression/test_chat_without_project.py` (Chat ohne Projekt)

---

## 4. Verbleibende Restpunkte

| Aspekt | Status |
|--------|--------|
| **Legacy ProjectChatListWidget** | In main.py; nicht Teil Shell/ChatWorkspace |
| **ChatDetailsPanel** | Enthält noch hardcoded Styles; separate Theme-Integration möglich |
| **Projekt-Auto-Select** | Beim Start wird kein Projekt vorausgewählt; Nutzer sieht „Globale Chats“ |

---

## 5. Empfohlene nächste produktive Ausbaustufen

1. **Legacy bereinigen:** ProjectChatListWidget aus main.py entfernen, wenn nicht mehr genutzt
2. **ChatDetailsPanel:** Theme-Tokens statt hardcoded Styles (analog ChatNavigationPanel)
3. **Projekt-Auswahl beim Start:** Optional erstes Projekt automatisch aktivieren
4. **Projekt-zu-Chat-Zuordnung:** UI zum Verschieben eines Chats in ein anderes Projekt (falls gewünscht)

---

## 6. Deliverables (abgeschlossen)

| Deliverable | Status |
|-------------|--------|
| PROJECTS_AND_CHAT_STRUCTURE_ANALYSIS.md | ✓ |
| Gehärtete Projekt-/Chat-/Workspace-Struktur im Code | ✓ |
| Gezielte Tests | ✓ |
| PROJECTS_AND_CHAT_STRUCTURE_REPORT.md | ✓ |

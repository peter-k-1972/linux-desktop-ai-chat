# Chat-Kontext – Analyse

**Stand:** 2026-03-17  
**Ziel:** Chat kontextbewusst machen – Projekt, Chat, Topic sichtbar.

---

## 1. Wo wird der Chat gerendert?

### 1.1 ChatWorkspace-Layout

```
[ ChatNavigationPanel ] | [ Center ] | [ ChatDetailsPanel ]
       (links)              (Mitte)          (rechts)
```

**Center-Spalte:**
- `ChatConversationPanel` – Nachrichtenbereich (ScrollArea + Message-Bubbles)
- `ChatInputPanel` – Eingabefeld

### 1.2 Komponenten

| Komponente | Rolle |
|------------|-------|
| **ChatConversationPanel** | `conversation_panel.py` – nur Nachrichten, kein Header |
| **ChatInputPanel** | `input_panel.py` – Eingabe |
| **ChatDetailsPanel** | Rechts – Metadaten (Projekt, Topic, etc.), collapsible |
| **ChatNavigationPanel** | Links – Projekt-Header + Chat-Liste |

---

## 2. Bestehende Header / Meta-Bereiche

| Ort | Inhalt |
|-----|--------|
| **Breadcrumb (Shell)** | Projekt / Chat / Session-Titel (wenn Projekt aktiv) |
| **ChatNavigationPanel** | Projektname oder „Globale Chats“ |
| **ChatDetailsPanel** | Projekt, Topic, Modell, Agent, erstellt, aktualisiert |
| **ChatConversationPanel** | Kein Header – nur Nachrichten |

---

## 3. Wo könnte Kontext sinnvoll angezeigt werden?

### 3.1 Option A: Kontextleiste über dem Nachrichtenbereich

**Position:** In der Center-Spalte, direkt über `ChatConversationPanel`.

**Vorteil:** Kontext ist im Chat-Bereich sichtbar, ohne die Sidebar zu öffnen.

**Beispiel:**
```
[ Projekt: XYZ ]  [ Chat: Debug Session ]  [ Topic: API ]
─────────────────────────────────────────────────────────
  User: ...
  Assistant: ...
```

### 3.2 Option B: Breadcrumb erweitern

Breadcrumb zeigt bereits Projekt / Chat / Detail. Allerdings:
- Breadcrumb ist Shell-Level, nicht „im Chat“
- Bei globalem Modus fehlt Projekt-Info

### 3.3 Option C: ChatDetailsPanel als primäre Kontextquelle

ChatDetailsPanel zeigt bereits Projekt, Topic, etc. – aber:
- Collapsible, kann zugeklappt sein
- Rechts positioniert, nicht im Fokus

---

## 4. Empfehlung

**Option A:** Leichte Kontextleiste (`ChatContextBar`) über dem Nachrichtenbereich.

- Immer sichtbar, aber zurückhaltend
- Klare Hierarchie: Projekt → Chat → (Topic)
- Keine neue komplexe UI
- Nutzt bestehende Projekt-/Chat-Daten

---

## 5. Kontextquellen

| Kontext | Quelle |
|---------|--------|
| Projekt | ProjectContextManager.get_active_project() oder get_project_of_chat(chat_id) |
| Chat-Titel | ChatService.get_chat_info(chat_id).title |
| Topic | ChatService.get_chat_info(chat_id).topic_name |

**Aktualisierung bei:**
- Projektwechsel → project_context_changed
- Chat-Auswahl → chat_selected
- Chat gelöscht → chat_deleted
- Neuer Chat erstellt → refresh

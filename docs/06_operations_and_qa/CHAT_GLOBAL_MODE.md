# Chat Global Mode – Dokumentation

**Version:** 1.0  
**Datum:** 2026-03-16  
**Status:** Intentional, implementiert  
**Referenz:** tests/regression/test_chat_without_project.py

---

## 1. Entscheidung

**Chat Global Mode ist intentional.** Chat ist der einzige Operations-Workspace, der ohne aktives Projekt nutzbar ist. Dies ermöglicht:

- Schnellstart ohne Projekt-Setup
- Grundfunktion Chat als Einstieg
- Globale Chats für Ad-hoc-Konversationen

---

## 2. Konsistente Empty-State Darstellung

| Workspace | Ohne Projekt | Mit Projekt |
|-----------|---------------|-------------|
| **Chat** | Header: „Globale Chats“ – Neuer Chat aktiv, Topics deaktiviert | Header: Projektname – volle Funktion |
| **Knowledge** | „Bitte Projekt auswählen“ – Add deaktiviert | Projektname – volle Funktion |
| **Prompt Studio** | „Bitte Projekt auswählen“ – Neuer Prompt deaktiviert | Projektname – volle Funktion |

---

## 3. Chat Global Mode – Verhalten

### 3.1 Header

- **Ohne Projekt:** „Globale Chats“ (nicht „Alle Chats“)
- **Mit Projekt:** Projektname

### 3.2 Features ohne Projekt

| Feature | Ohne Projekt | Mit Projekt |
|---------|--------------|-------------|
| Neuer Chat | Aktiv | Aktiv |
| Neues Topic | Deaktiviert | Aktiv |
| Pinned | Ausgeblendet | Sichtbar |
| Archiv | Ausgeblendet | Sichtbar |
| Topic-Filter | Ausgeblendet | Sichtbar |
| Recent-Filter | Sichtbar | Sichtbar |

### 3.3 Service

- `create_chat(title)` – erstellt Chat ohne Projekt (project_id = NULL)
- `list_chats_for_project(None)` – liefert globale Chats
- Chat-Send-Pipeline: `pid is None` → `create_chat()` (keine Fehler)

---

## 4. Abgrenzung zu anderen Workspaces

| Workspace | Projekt erforderlich | Begründung |
|-----------|----------------------|------------|
| Chat | Nein (Global Mode) | Grundfunktion, Einstieg |
| Knowledge | Ja | RAG/Collections sind per Projekt organisiert |
| Prompt Studio | Ja | Prompts sind per Projekt organisiert |
| Agent Tasks | Nein (Global Agents) | Agenten sind global |

---

## 5. Dateien

| Datei | Zweck |
|-------|-------|
| `app/ui/chat/chat_navigation_panel.py` | Header „Globale Chats“, Topic-Features deaktiviert |
| `app/gui/domains/operations/chat/chat_workspace.py` | create_chat() bei pid=None |
| `app/services/chat_service.py` | create_chat(), list_chats_for_project(None) |
| `tests/regression/test_chat_without_project.py` | Regression-Tests für Global Mode |

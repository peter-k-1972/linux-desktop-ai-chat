# Project Switcher & Project Overview – Implementierung

**Version:** 1.0  
**Datum:** 2026-03-15  
**Status:** Implementiert

---

## 1. Überblick

Die Anwendung bietet nun eine vollständige UX für den Projektkontext:

- **Project Switcher** – globales UI-Element in der TopBar
- **Project Overview** – Dashboard-Screen für das aktive Projekt
- **Integration** – Breadcrumbs, Workspaces, ActiveProjectContext

---

## 2. Project Switcher

### Position: TopBar (empfohlene Variante)

**Bewertung der Varianten:**

| Position | Vorteile | Nachteile |
|----------|----------|-----------|
| **TopBar** | Immer sichtbar, prominent, natürlicher Klickbereich, kein Extra-Platz | — |
| Sidebar oben | Nahe an Projekt-Navigation | Weniger Platz, Konkurrenz mit Hauptnav |
| TopBar + Sidebar | Doppelte Sichtbarkeit | Redundanz, mehr Wartungsaufwand |

**Entscheidung:** TopBar – der Projektkontext ist bereits dort, ein Dropdown beim Klick ist intuitiv.

### Funktionen

1. **Aktives Projekt anzeigen** – Name + Icon
2. **Dropdown** – Projektliste zum schnellen Wechsel
3. **Neues Projekt anlegen** – Dialog im Dropdown
4. **Projektkontext aufheben** – Option im Menü
5. **Projektwechsel** – aktualisiert alle projektbezogenen Workspaces

### Komponenten

- `ProjectSwitcherButton` – `app/gui/project_switcher/project_switcher_button.py`
- `NewProjectDialog` – integriert im Switcher
- TopBar nutzt den Switcher statt des bisherigen `ProjectContextWidget`

---

## 3. Project Overview Screen

### Konzept

Der Project Overview ist **kein Begrüßungsscreen**, sondern ein **Kontext-Hub** für das aktive Projekt.

### Inhalt

1. **Projektkopf (ProjectHeaderCard)**
   - Projektname
   - Beschreibung
   - Erstellt / Geändert / Status

2. **Kennzahlen (ProjectStatsPanel)**
   - Anzahl Chats
   - Anzahl Knowledge-Quellen
   - Anzahl Prompts

3. **Letzte Aktivität (ProjectActivityPanel)**
   - Zuletzt bearbeitete Chats (mit Timestamp)
   - Zuletzt geänderte Prompts
   - Hinzugefügte Quellen

4. **Quick Actions (ProjectQuickActionsPanel)**
   - Neuer Chat → navigiert zu Chat-Workspace
   - Quelle hinzufügen → Knowledge-Workspace
   - Neuer Prompt → Prompt Studio
   - Agents → Agent Tasks

5. **Als aktives Projekt setzen** – Button für schnelle Aktivierung

### Komponenten

- `ProjectOverviewPanel` – `app/gui/domains/operations/projects/panels/project_overview_panel.py`
- `ProjectHeaderCard` – `project_header_card.py`
- `ProjectStatsPanel` – `project_stats_panel.py`
- `ProjectActivityPanel` – `project_activity_panel.py`
- `ProjectQuickActionsPanel` – `project_quick_actions_panel.py`

---

## 4. Service-Integration

### ProjectService – neue Methoden

```python
get_project_summary(project_id) -> dict
# Liefert Projekt + chat_count, source_count, prompt_count

get_recent_project_activity(project_id, chat_limit=5, prompt_limit=5) -> dict
# Liefert recent_chats, recent_prompts, sources
```

### DatabaseManager – neue Methode

```python
get_recent_chats_of_project(project_id, limit=5) -> list
# Chats sortiert nach letzter Nachricht
```

### ActiveProjectContext

- Unverändert: `set_active()`, `set_none()`, `active_project_changed`
- Alle UI-Komponenten reagieren auf dieses Signal

---

## 5. GUI-Integration

- **TopBar:** Project Switcher ersetzt ProjectContextWidget
- **ProjectsWorkspace:** Sync mit ActiveProjectContext, zeigt Overview für aktives Projekt
- **Breadcrumbs:** Zeigen „Projekt: [Name]“ als Kontext, wenn ein Projekt aktiv ist
- **Projektwechsel:** Aktualisiert Overview, Liste, Inspector, Breadcrumbs

---

## 6. UX-Entscheidungen

1. **TopBar für Switcher** – Projektkontext ist global, TopBar ist der logische Ort
2. **Dashboard statt Liste** – Project Overview ist Arbeitsraum-Einstieg, nicht nur Projektliste
3. **Quick Actions** – Direkte Navigation zu den relevanten Workspaces
4. **Breadcrumbs mit Projekt** – Sichtbarer Kontext in der gesamten App
5. **Kein zweites Navigationssystem** – Switcher ist Kontext, keine parallele Nav

---

## 7. Startanweisung

```bash
# Mit virtuellem Environment
cd Linux-Desktop-Chat
.venv/bin/python run_gui_shell.py

# Optional: Theme
.venv/bin/python run_gui_shell.py --theme dark_default
```

**Testablauf:**

1. App starten
2. TopBar: Auf Projekt-Button klicken → Dropdown mit Projekten
3. Projekt wählen oder „Neues Projekt anlegen“
4. Navigation: Operations → Projekte
5. Project Overview: Dashboard mit Kennzahlen, Aktivität, Quick Actions
6. Quick Action „Neuer Chat“ → Wechsel zu Chat-Workspace
7. Breadcrumbs: „Projekt: [Name] › Operations › Chat“

---

## 8. Dateien (Übersicht)

| Datei | Zweck |
|-------|-------|
| `app/gui/project_switcher/project_switcher_button.py` | Project Switcher Button + Dropdown |
| `app/gui/shell/top_bar.py` | TopBar mit Project Switcher |
| `app/gui/domains/operations/projects/panels/project_overview_panel.py` | Project Overview Dashboard |
| `app/gui/domains/operations/projects/panels/project_header_card.py` | Projektkopf |
| `app/gui/domains/operations/projects/panels/project_stats_panel.py` | Kennzahlen |
| `app/gui/domains/operations/projects/panels/project_activity_panel.py` | Letzte Aktivität |
| `app/gui/domains/operations/projects/panels/project_quick_actions_panel.py` | Quick Actions |
| `app/gui/domains/operations/projects/projects_workspace.py` | Integration + Sync |
| `app/gui/breadcrumbs/manager.py` | Projektkontext in Breadcrumbs |
| `app/services/project_service.py` | get_project_summary, get_recent_project_activity |
| `app/db.py` | get_recent_chats_of_project |

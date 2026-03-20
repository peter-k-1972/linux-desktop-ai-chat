# Project-Subsystem: UI → GUI Migration – Ist-Analyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Phase:** 1 – Ist-Analyse

---

## 1. Ausgangslage

### 1.1 Legacy-Bereich

| Pfad | Typ | Inhalt |
|------|-----|--------|
| `app/ui/project/` | Verzeichnis | Re-Exports aus `app.gui.project_switcher` und `app.gui.domains.project_hub` |

### 1.2 Bereits migriert (kanonisch unter gui)

- **app/gui/domains/project_hub/** – Project Hub (Übersicht aktives Projekt):
  - `project_hub_page.py` – ProjectHubPage
  - `project_hub_screen.py` – ProjectHubScreen

- **app/gui/project_switcher/** – Project Switcher (Button + Dialog):
  - `project_switcher_button.py` – ProjectSwitcherButton
  - `project_switcher_dialog.py` – ProjectSwitcherDialog, NewProjectDialog

- **app/gui/domains/operations/projects/** – Projects Workspace (Projektliste, -verwaltung):
  - `projects_workspace.py` – ProjectsWorkspace
  - `panels/` – project_list_panel, project_header_card, etc.

---

## 2. Analyse `app/ui/project/`

### 2.1 Enthaltene Dateien

| Datei | Inhalt | Klassifikation |
|-------|--------|----------------|
| `__init__.py` | Re-Export aller Komponenten aus gui | REMOVE_DEAD |
| `project_hub_page.py` | Re-Export ProjectHubPage | REMOVE_DEAD |
| `project_switcher_dialog.py` | Re-Export ProjectSwitcherDialog, NewProjectDialog | REMOVE_DEAD |
| `project_switcher_button.py` | Re-Export ProjectSwitcherButton | REMOVE_DEAD |

### 2.2 Externe Konsumenten

**Keine.** Kein produktiver Code importiert `app.ui.project` oder Untermodule.

- `app.gui.shell.top_bar` importiert `from app.gui.project_switcher.project_switcher_button import ProjectSwitcherButton`
- `app.gui.domains.project_hub.project_hub_screen` importiert aus `app.gui.domains.project_hub.project_hub_page`
- `app.gui.bootstrap` registriert ProjectHubScreen aus gui

---

## 3. Zielstruktur

### 3.1 Gewählte Struktur

Die kanonische Struktur existiert bereits:

```
app/gui/
├── domains/
│   ├── project_hub/           # Project Hub (Übersicht)
│   │   ├── project_hub_page.py
│   │   └── project_hub_screen.py
│   └── operations/
│       └── projects/          # Projects Workspace (Projektliste)
│           ├── projects_workspace.py
│           └── panels/
└── project_switcher/          # Project Switcher (Button + Dialog)
    ├── project_switcher_button.py
    └── project_switcher_dialog.py
```

**Keine neue Struktur unter `app/gui/domains/project/`.**  
Das Project-Subsystem ist aufgeteilt in:
- **project_hub** – Übersicht des aktiven Projekts (Screen)
- **project_switcher** – Button und Dialog zum Wechseln (TopBar)
- **operations/projects** – Projektliste und -verwaltung (Workspace)

### 3.2 Aktion

- **app/ui/project/** → **vollständig entfernen** (nur Re-Exports, keine Konsumenten)
- Keine physische Migration nötig – Implementierung bereits in gui

---

## 4. Zusammenfassung

| Komponente | Aktion |
|------------|--------|
| `app/ui/project/` (komplett) | Entfernen (tote Re-Exports) |
| `app/gui/domains/project_hub/` | Unverändert – kanonisch |
| `app/gui/project_switcher/` | Unverändert – kanonisch |
| `app/gui/domains/operations/projects/` | Unverändert – kanonisch |
| Übergangsbrücken | Keine nötig – direkte Entfernung möglich |

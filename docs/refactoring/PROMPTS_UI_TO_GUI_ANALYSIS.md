# Prompts-Subsystem: UI → GUI Migration – Ist-Analyse

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Phase:** 1 – Ist-Analyse

---

## 1. Ausgangslage

### 1.1 Legacy-Bereich

| Pfad | Typ | Inhalt |
|------|-----|--------|
| `app/ui/prompts/` | Verzeichnis | Re-Exports aus `app.gui.domains.operations.prompt_studio` |

### 1.2 Bereits migriert (kanonisch unter gui)

- `app/gui/domains/operations/prompt_studio/` – vollständige Implementierung:
  - `prompt_studio_workspace.py` – PromptStudioWorkspace, NewPromptDialog
  - `panels/prompt_navigation_panel.py` – PromptNavigationPanel
  - `panels/prompt_list_panel.py` – PromptListPanel
  - `panels/prompt_list_item.py` – PromptListItem, PromptListItemWidget
  - `panels/prompt_editor_panel.py` – PromptEditorPanel
  - `panels/prompt_version_panel.py` – PromptVersionPanel
  - `panels/prompt_test_lab.py` – PromptTestLab
  - `panels/prompt_templates_panel.py` – PromptTemplatesPanel
  - `panels/prompt_manager_panel.py`, `library_panel.py`, `editor_panel.py`, `preview_panel.py`

---

## 2. Analyse `app/ui/prompts/`

### 2.1 Enthaltene Dateien

| Datei | Inhalt | Klassifikation |
|-------|--------|----------------|
| `__init__.py` | Re-Export aller Komponenten aus gui | REMOVE_DEAD |
| `prompt_studio_workspace.py` | Re-Export PromptStudioWorkspace | REMOVE_DEAD |
| `prompt_navigation_panel.py` | Re-Export PromptNavigationPanel, SECTION_* | REMOVE_DEAD |
| `prompt_list_panel.py` | Re-Export PromptListPanel | REMOVE_DEAD |
| `prompt_list_item.py` | Re-Export PromptListItem, PromptListItemWidget | REMOVE_DEAD |
| `prompt_editor_panel.py` | Re-Export PromptEditorPanel | REMOVE_DEAD |
| `prompt_version_panel.py` | Re-Export PromptVersionPanel | REMOVE_DEAD |
| `prompt_test_lab.py` | Re-Export PromptTestLab | REMOVE_DEAD |
| `prompt_templates_panel.py` | Re-Export PromptTemplatesPanel | REMOVE_DEAD |

### 2.2 Externe Konsumenten

**Keine.** Kein produktiver Code importiert `app.ui.prompts` oder Untermodule.

- `app.gui.domains.operations.operations_screen` importiert `from app.gui.domains.operations.prompt_studio import PromptStudioWorkspace`
- `app.gui.inspector.prompt_studio_inspector` importiert aus `app.gui.domains.operations.prompt_studio.panels`
- `tests/behavior/ux_regression_tests` importiert aus `app.gui.domains.operations.prompt_studio.prompt_studio_workspace`

---

## 3. Zielstruktur

### 3.1 Gewählte Struktur

Die kanonische Struktur existiert bereits unter:

```
app/gui/domains/operations/prompt_studio/
├── __init__.py
├── prompt_studio_workspace.py
└── panels/
    ├── __init__.py
    ├── prompt_navigation_panel.py
    ├── prompt_list_panel.py
    ├── prompt_list_item.py
    ├── prompt_editor_panel.py
    ├── prompt_version_panel.py
    ├── prompt_test_lab.py
    ├── prompt_templates_panel.py
    ├── prompt_manager_panel.py
    ├── library_panel.py
    ├── editor_panel.py
    └── preview_panel.py
```

**Keine neue Struktur unter `app/gui/domains/prompts/`.**  
Das Prompts-Subsystem (Prompt Studio) ist Teil der Operations-Domain und liegt korrekt unter `operations/prompt_studio`.

### 3.2 Aktion

- **app/ui/prompts/** → **vollständig entfernen** (nur Re-Exports, keine Konsumenten)
- Keine physische Migration nötig – Implementierung bereits in gui

---

## 4. Zusammenfassung

| Komponente | Aktion |
|------------|--------|
| `app/ui/prompts/` (komplett) | Entfernen (tote Re-Exports) |
| `app/gui/domains/operations/prompt_studio/` | Unverändert – kanonische Implementierung |
| Übergangsbrücken | Keine nötig – direkte Entfernung möglich |

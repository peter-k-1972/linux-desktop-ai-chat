# Prompts-Subsystem: UI → GUI Migration Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Abschlussklassifikation:** `DONE`

---

## 1. Ausgangslage

- **app/ui/prompts/** – Verzeichnis mit ausschließlich Re-Exports aus `app.gui.domains.operations.prompt_studio`
- Keine produktiven Konsumenten von `app.ui.prompts`
- Kanonische Implementierung bereits unter `app/gui/domains/operations/prompt_studio/`

---

## 2. Migrierte Dateien/Klassen

**Keine physische Migration.** Die Implementierung lag bereits vollständig unter gui. Es wurden nur die Legacy-Re-Exports entfernt.

| Komponente | Kanonischer Pfad |
|------------|------------------|
| PromptStudioWorkspace | `app.gui.domains.operations.prompt_studio.prompt_studio_workspace` |
| PromptNavigationPanel | `app.gui.domains.operations.prompt_studio.panels.prompt_navigation_panel` |
| PromptListPanel | `app.gui.domains.operations.prompt_studio.panels.prompt_list_panel` |
| PromptListItem, PromptListItemWidget | `app.gui.domains.operations.prompt_studio.panels.prompt_list_item` |
| PromptEditorPanel | `app.gui.domains.operations.prompt_studio.panels.prompt_editor_panel` |
| PromptVersionPanel | `app.gui.domains.operations.prompt_studio.panels.prompt_version_panel` |
| PromptTestLab | `app.gui.domains.operations.prompt_studio.panels.prompt_test_lab` |
| PromptTemplatesPanel | `app.gui.domains.operations.prompt_studio.panels.prompt_templates_panel` |

---

## 3. Alte → neue Pfade

| Alt | Neu |
|-----|-----|
| `app.ui.prompts.*` (entfernt) | `app.gui.domains.operations.prompt_studio.*` |

Alle produktiven Imports nutzten bereits die gui-Pfade.

---

## 4. Angepasste Importstellen

**Keine.** Kein Code importierte `app.ui.prompts`.

---

## 5. Entfernte Legacy-Dateien

| Datei/Verzeichnis | Grund |
|-------------------|-------|
| `app/ui/prompts/` (komplett) | Nur Re-Exports, keine Konsumenten |
| `app/ui/prompts/__init__.py` | |
| `app/ui/prompts/prompt_studio_workspace.py` | |
| `app/ui/prompts/prompt_navigation_panel.py` | |
| `app/ui/prompts/prompt_list_panel.py` | |
| `app/ui/prompts/prompt_list_item.py` | |
| `app/ui/prompts/prompt_editor_panel.py` | |
| `app/ui/prompts/prompt_version_panel.py` | |
| `app/ui/prompts/prompt_test_lab.py` | |
| `app/ui/prompts/prompt_templates_panel.py` | |

---

## 6. Verbleibende temporäre Bridges

**Keine.** Vollständige Bereinigung ohne Übergangsbrücken.

---

## 7. Testläufe + Ergebnisse

| Test | Ergebnis |
|------|----------|
| `tests/architecture/test_gui_does_not_import_ui.py` | ✓ PASSED |
| `tests/behavior/ux_regression_tests.py::test_project_context_isolation` | ✓ PASSED |
| Import-Check: PromptStudioWorkspace, OperationsScreen | ✓ OK |

---

## 8. Bekannte Restrisiken

- **tests/ui/test_prompt_manager_ui.py**, **tests/unit/test_prompt_system.py**: Bestehende Fehler (Prompt-Schema, Fixtures) – unabhängig von dieser Migration.

---

## 9. Abschlussklassifikation

**DONE**

- Prompts-Subsystem liegt kanonisch unter `app/gui/domains/operations/prompt_studio/`
- `app/ui/prompts/` vollständig entfernt
- Keine gui→ui-Verletzung
- Keine temporären Bridges
- Architekturguard grün

---

## Konsole-Zusammenfassung

```
=== PROMPTS UI → GUI MIGRATION ===

Migriert:
  - Keine physische Migration – Implementierung bereits unter app/gui/domains/operations/prompt_studio/

Gelöscht:
  - app/ui/prompts/ (komplett: __init__, prompt_studio_workspace, prompt_navigation_panel,
    prompt_list_panel, prompt_list_item, prompt_editor_panel, prompt_version_panel,
    prompt_test_lab, prompt_templates_panel)

Tests:
  - test_gui_does_not_import_ui: PASSED
  - test_project_context_isolation: PASSED

Blocker: Keine
```

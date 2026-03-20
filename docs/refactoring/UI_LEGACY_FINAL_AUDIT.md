# UI Legacy – Finaler Audit

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Phase:** Abschlussphase UI→GUI-Migration

---

## 1. Bestand unter app/ui/

| Verzeichnis | Inhalt | Klassifikation |
|-------------|--------|----------------|
| `app/ui/agents/` | Nur `__pycache__`, keine .py | REMOVE_DEAD |
| `app/ui/chat/` | Nur `__pycache__`, keine .py | REMOVE_DEAD |
| `app/ui/debug/` | Nur `__pycache__`, keine .py | REMOVE_DEAD |
| `app/ui/events/` | Nur `__pycache__`, keine .py | REMOVE_DEAD |
| `app/ui/sidepanel/` | Nur `__pycache__`, keine .py | REMOVE_DEAD |
| `app/ui/widgets/` | Nur `__pycache__`, keine .py | REMOVE_DEAD |
| `app/ui/__pycache__/` | Bytecode (settings_dialog) | REMOVE_DEAD |

**Keine .py-Dateien mehr unter app/ui/.** Alle Implementierungen wurden in vorherigen Phasen nach gui migriert.

---

## 2. Projektweite Import-Prüfung

| Suchmuster | Treffer (produktiv) |
|------------|---------------------|
| `from app.ui` | Keine |
| `import app.ui` | Keine |
| `app.ui.` (in Code) | Nur Kommentare, Test-Guards, Docstrings |

**app.main** importiert ausschließlich von:
- `app.gui.legacy`
- `app.gui.domains.command_center`
- `app.gui.domains.settings.settings_dialog`

---

## 3. Abhängige Stellen

| Datei | Bezug | Aktion |
|-------|-------|--------|
| `tools/generate_feature_registry.py` | Prüft `app/ui/settings/categories` | REPOINT auf `app/gui/domains/settings/categories` |
| `tests/architecture/arch_guard_config.py` | ALLOWED_UI_IMPORTER_PATTERNS, FORBIDDEN_PARALLEL_PACKAGES | Nach ui-Entfernung: Patterns ggf. bereinigen |
| `tests/architecture/test_app_package_guards.py` | test_ui_only_imported_by_allowed | Test bleibt; prüft weiterhin, dass niemand app.ui importiert |
| `tests/architecture/test_gui_does_not_import_ui.py` | Guard: gui importiert nicht ui | Unverändert |

---

## 4. Fazit

- **app/ui/** ist vollständig obsolet (nur leere Verzeichnisse + __pycache__)
- Keine produktiven Konsumenten
- Vollständige Eliminierung technisch sicher möglich

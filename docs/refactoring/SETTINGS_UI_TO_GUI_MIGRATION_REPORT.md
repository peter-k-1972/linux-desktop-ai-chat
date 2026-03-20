# Settings-Subsystem: UI → GUI Migration Report

**Projekt:** Linux Desktop Chat  
**Datum:** 2026-03-16  
**Abschlussklassifikation:** `DONE`

---

## 1. Ausgangslage

- **app/ui/settings/** – Verzeichnis mit Re-Exports aus `app.gui.domains.settings` (keine produktiven Konsumenten)
- **app/ui/settings_dialog.py** – `SettingsDialog` (modal), einziger Konsument: `app.main.py` (Legacy MainWindow)

---

## 2. Migrierte Dateien/Klassen

| Alte Datei | Neue Datei | Aktion |
|------------|------------|--------|
| `app/ui/settings_dialog.py` | `app/gui/domains/settings/settings_dialog.py` | Verschieben (1:1) |
| – | `app/gui/domains/settings/__init__.py` | Erweitert um `SettingsDialog`-Re-Export |

---

## 3. Alte → neue Pfade

| Komponente | Alt | Neu |
|------------|-----|-----|
| SettingsDialog | `app.ui.settings_dialog.SettingsDialog` | `app.gui.domains.settings.settings_dialog.SettingsDialog` |
| SettingsDialog (Paket) | – | `app.gui.domains.settings.SettingsDialog` |

---

## 4. Angepasste Importstellen

| Datei | Änderung |
|-------|----------|
| `app/main.py` | `from app.ui.settings_dialog import SettingsDialog` → `from app.gui.domains.settings.settings_dialog import SettingsDialog` |

---

## 5. Entfernte Legacy-Dateien

| Datei/Verzeichnis | Grund |
|-------------------|-------|
| `app/ui/settings_dialog.py` | Nach gui migriert |
| `app/ui/settings/` (komplett) | Nur Re-Exports, keine Konsumenten |
| `app/ui/settings/__init__.py` | |
| `app/ui/settings/settings_navigation.py` | |
| `app/ui/settings/settings_workspace.py` | |
| `app/ui/settings/categories/__init__.py` | |
| `app/ui/settings/categories/base_category.py` | |
| `app/ui/settings/categories/application_category.py` | |
| `app/ui/settings/categories/appearance_category.py` | |
| `app/ui/settings/categories/ai_models_category.py` | |
| `app/ui/settings/categories/data_category.py` | |
| `app/ui/settings/categories/privacy_category.py` | |
| `app/ui/settings/categories/advanced_category.py` | |
| `app/ui/settings/categories/project_category.py` | |
| `app/ui/settings/categories/workspace_category.py` | |

---

## 6. Verbleibende temporäre Bridges

**Keine.** Vollständige Migration ohne Übergangsbrücken.

---

## 7. Testläufe + Ergebnisse

| Test | Ergebnis |
|------|----------|
| `tests/architecture/test_gui_does_not_import_ui.py` | ✓ PASSED |
| `tests/regression/test_settings_theme_tokens.py` | ✓ PASSED |
| `tests/integration/test_model_settings_chat.py` | ✓ PASSED |
| `tests/behavior/ux_regression_tests.py` (test_settings_breadcrumb_correctness) | ✗ FAILED (vor Migration bereits fehlerhaft – Fehler in `navigation_registry._build_registry`, nicht settings-spezifisch) |
| Import-Check: `SettingsDialog`, `MainWindow` | ✓ OK |

---

## 8. Bekannte Restrisiken

- **Legacy MainWindow** (`app.main.MainWindow`): Wird nur über `run_legacy_gui.py` bzw. `archive/run_legacy_gui.py` gestartet. Nutzt weiterhin `SettingsDialog` – nun aus gui.
- **ux_regression_tests.test_settings_breadcrumb_correctness**: Fehlschlag unabhängig von dieser Migration (navigation_registry/BreadcrumbManager).

---

## 9. Abschlussklassifikation

**DONE**

- Settings-Subsystem vollständig unter `app/gui/domains/settings/`
- `app/ui/settings/` und `app/ui/settings_dialog.py` entfernt
- Keine gui→ui-Verletzung
- Keine temporären Bridges
- Architekturguard grün

---

## Konsole-Zusammenfassung

```
=== SETTINGS UI → GUI MIGRATION ===

Migriert:
  - SettingsDialog: app/ui/settings_dialog.py → app/gui/domains/settings/settings_dialog.py
  - app.main.py: Import auf app.gui.domains.settings.settings_dialog umgestellt

Gelöscht:
  - app/ui/settings_dialog.py
  - app/ui/settings/ (komplett: __init__, settings_navigation, settings_workspace, categories/*)

Tests:
  - test_gui_does_not_import_ui: PASSED
  - test_settings_theme_tokens: PASSED
  - test_model_settings_chat: PASSED

Blocker: Keine
```

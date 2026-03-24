# Abschlussbericht: Governance & Produktintegration (Alternative QML-GUI)

**Datum:** 2026-03-24  
**Phase:** Schließung der Blocker B-01–B-04 (Manifest, Matrix, Registry, Switching/Fallback) aus dem ersten QML-Audit — **Iteration/Verdichtung** auf kanonische `gui_id`, Bridge-Kompatibilität und fail-closed Validator.

## 1. Neue / geänderte Dateien

| Datei | Rolle |
|-------|--------|
| `app/gui_registry.py` | **Neu strukturiert:** `REGISTERED_GUIS_BY_ID`, `GuiDescriptor` mit `gui_id` / `display_name` / `is_default_fallback`, Aliase, `resolve_user_gui_choice` |
| `app/gui_bootstrap.py` | Kanonische `gui_id` in QSettings; Legacy-Hilfen für alte Aufrufer |
| `app/application_release_info.py` | **`BRIDGE_INTERFACE_VERSION`** |
| `app/qml_theme_governance.py` | Pflichtfeld **`compatible_bridge_versions`**, **Domain-Key-Set**, `bridge_version`-Parameter |
| `app/qml_alternative_gui_validator.py` | **Neu:** zentraler Launch-Validator inkl. `theme_id` == `gui_id` |
| `qml/theme_manifest.json` | **`compatible_bridge_versions`** |
| `run_gui_shell.py` | `--gui` frei wählbar + Validierung unbekannter Werte (**Exit 2**); generischer Qt-Quick-Start; Fallback-Text |
| `run_qml_shell.py` | Nutzung von `validate_library_qml_gui_launch_context` |
| `app/core/config/settings.py` | `preferred_gui` speichert **`default_widget_gui` \| `library_qml_gui`** |
| `docs/release/GUI_COMPATIBILITY_MATRIX.md` | Erweiterte Spalten (Bridge, QA, Freigabe) |
| `docs/architecture/GUI_REGISTRY.md` | An neue Registry angepasst |
| `docs/release/ALTERNATIVE_GUI_GOVERNANCE.md` | **Neu** |
| `tests/gui/test_gui_registry.py` | Registry, Validator, CLI-Fehlfall, Bridge, Domains |

## 2. Registry-Struktur

- **`default_widget_gui`**: `pyside6`, kein QML-Manifest, `is_default_fallback=True`
- **`library_qml_gui`**: `qt_quick`, `run_qml_shell.py`, `qml/theme_manifest.json`

## 3. Manifest-Struktur

Siehe `qml/theme_manifest.json` und `REQUIRED_TOP_LEVEL_KEYS` / `REQUIRED_DOMAIN_KEYS` in `qml_theme_governance.py`.

## 4. Kompatibilitätsprüfung

Abgleich von Manifest-Listen mit:

- `APP_RELEASE_VERSION`, `BACKEND_BUNDLE_VERSION`, `UI_CONTRACTS_RELEASE_VERSION`, `BRIDGE_INTERFACE_VERSION`

## 5. CLI / Settings

- **CLI:** `--gui` mit Aliases (`default`, `library_qml`, `qml`, …) und kanonischen IDs; ungültig → **Exit-Code 2**
- **Env:** `LINUX_DESKTOP_CHAT_GUI`
- **Settings:** `AppSettings.preferred_gui` + QSettings `preferred_gui` (kanonisch; Legacy-Eingaben werden beim Lesen normalisiert)

## 6. Fallback / Rollback

Validierungs- oder Subprozessfehler → Logging, Stderr-Hinweis, **`preferred_gui` auf `default_widget_gui`**, Start der Widget-GUI bei Aufruf über `run_gui_shell.py`.

## 7. Tests

`pytest tests/gui/test_gui_registry.py` sowie relevante QML-/Settings-Smokes (lokal ausgeführt: grün).

## 8. Bewusst offen

- Weitere Qt-Quick-GUI: eigener `gui_id` + Validator-Zweig in `_try_start_qt_quick_gui`
- Semver-Ranges statt expliziter Listen (Policy-Entscheidung)
- Dediziertes Settings-UI-Feld „GUI wählen“ (aktuell: Persistenz über `preferred_gui` / CLI / Env)

## 9. QA-Bezug früherer Blocker

| Blocker | Status |
|---------|--------|
| B-01 QML-Manifest | **Geschlossen** (`qml/theme_manifest.json` + Validierung) |
| B-02 Matrix | **Geschlossen** (`docs/release/GUI_COMPATIBILITY_MATRIX.md`) |
| B-03 Registry | **Geschlossen** (`app/gui_registry.py`) |
| B-04 Switching / Rollback | **Geschlossen** (`run_gui_shell.py`, fail-closed, Fallback) |

Der nächste QA-Lauf kann diese Artefakte **direkt** gegen den Code prüfen.

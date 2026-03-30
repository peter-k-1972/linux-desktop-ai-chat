# GUI-Registry

## Zweck

Das Produkt kennt **registrierte GUI-Varianten** neben der Standard-Widget-Shell. Der kanonische Produktvertrag (`app.core.startup_contract`) definiert **`gui_id`**, Anzeigenamen, Entrypoint-Skript, GUI-Typ und optional den Pfad zum **QML-Governance-Manifest**.

## Aufbau

- **`GuiDescriptor`**
  - **`gui_id`**: stabile ID (`default_widget_gui`, `library_qml_gui`)
  - **`display_name`**: Anzeige-/Dokumentationsname
  - **`gui_type`**: `pyside6` | `qt_quick`
  - **`entrypoint`**: Dateiname im **Repo-Root** (z. B. `run_qml_shell.py`)
  - **`manifest_path`**: relativ zur Repo-Wurzel oder `null` (Widget-GUI)
  - **`capabilities`**: :class:`~app.core.startup_contract.GuiCapabilities` — produktrelevante Fähigkeiten (keine Theme-Dekoration)
  - **`is_default_fallback`**: genau eine GUI ist der **sichere Rückfall** bei Fehlern

- **`REGISTERED_GUIS_BY_ID`**: Map `gui_id` → Deskriptor

- **`GUI_CLI_ALIASES`**: Map Alias (Kleinbuchstaben) → `gui_id` für `--gui` und Umgebungsvariable

Hilfsfunktionen: `get_gui_descriptor`, `resolve_user_gui_choice`, `list_valid_gui_cli_tokens`, `get_default_fallback_gui_id`.

## Capabilities (Produktintegration)

Modul: `app.core.startup_contract`. Jede registrierte GUI trägt einen festen Satz Booleans (Deskriptor + kanonische Konstanten `CAPABILITIES_*` / `CANONICAL_GUI_CAPABILITIES`).

| Feld | Bedeutung (Kurz) |
|------|-------------------|
| `supports_chat` | Chat-Raum / Chat-Port nutzbar |
| `supports_projects` | Projekte-Integration |
| `supports_workflows` | Workflows |
| `supports_prompts` | Prompt Studio / Prompts |
| `supports_agents` | Agenten |
| `supports_deployment` | Deployment-Studio |
| `supports_settings` | Einstellungen |
| `supports_theme_switching` | Produktseitiger Wechsel der GUI-Themes (nicht: einzelne QML-Asset-Dateien) |
| `supports_command_palette` | Command Palette (optional im Produkt) |
| `supports_safe_mode_actions` | Safe-Mode-/Recovery-Aktionen (optional) |

**Auswertung im Hauptprogramm:** `gui_supports(gui_id, "supports_workflows")` bzw. `get_capabilities_for_gui_id(gui_id)`.

**Global Overlay:** Keine GUI-Capability — das **Global Overlay** installiert das Produkt (`run_gui_shell` / `run_qml_shell`) nach erfolgreichem Shell-Start. Status siehe Diagnostics „Global overlay (product)“ und [GLOBAL_OVERLAY_PRODUCT_GOVERNANCE.md](../04_architecture/GLOBAL_OVERLAY_PRODUCT_GOVERNANCE.md).

**Governance:** `validate_registered_gui_capabilities(REGISTERED_GUIS_BY_ID)` (Tests) stellt Abgleich mit `CANONICAL_GUI_CAPABILITIES` sicher — bei neuer GUI Konstante + Registry-Zeile + Eintrag in `CANONICAL_GUI_CAPABILITIES`.

### Kanonische Werte (Stand)

- **`default_widget_gui`**: alle Domänen `True`; `supports_theme_switching` und `supports_command_palette` `True`; `supports_safe_mode_actions` `False`.
- **`library_qml_gui`**: Domänen `True` (ViewModels angebunden); `supports_theme_switching` und `supports_command_palette` `False` (QML-Shell ohne Widget-Palette / ohne produktseitigen Theme-Switch wie die Standard-Shell).

## GUI Smoke Harness

Einheitlicher QA-Lauf: `app/gui_smoke_harness.py` (Programm-API) und CLI `scripts/qa/run_gui_smoke.py`.

**Schritte pro GUI:** registriert → Entrypoint vorhanden → Manifest-Pfad (falls gesetzt) → Laufzeit-Kompatibilität (qt_quick: wie `validate_library_qml_gui_launch_context`) → optional Subprozess-Kurzstart.

**Kurzstart:** Umgebung `LINUX_DESKTOP_CHAT_GUI_SMOKE=1`, `LINUX_DESKTOP_CHAT_SINGLE_INSTANCE=0`, standardmäßig `QT_QPA_PLATFORM=offscreen`. `run_gui_shell.py` und `run_qml_shell.py` beenden die App kurz nach Anzeige der Basis-Oberfläche.

```bash
python scripts/qa/run_gui_smoke.py
python scripts/qa/run_gui_smoke.py --no-subprocess
python scripts/qa/run_gui_smoke.py --gui library_qml_gui
```

**Pytest:** Marker `gui_smoke` — Subprozess-Lauf für alle registrierten GUIs (`pytest -m gui_smoke`).

## Neue GUI registrieren

1. Neues Skript im Repo-Root (oder bestehenden Pfad nutzen).
2. `REGISTERED_GUIS_BY_ID` und ggf. `GUI_CLI_ALIASES` erweitern; **`GuiCapabilities`** in `app.core.startup_contract` definieren und in `CANONICAL_GUI_CAPABILITIES` eintragen.
3. Bei Qt Quick: Governance-Manifest + Zeile in `docs/release/GUI_COMPATIBILITY_MATRIX.md`.
4. Validator in `app/qml_alternative_gui_validator.py` erweitern, falls nicht dasselbe Manifest-Schema genutzt wird.
5. Harness: für neue **qt_quick**-GUI ggf. `check_manifest_runtime_compatible` in `app/gui_smoke_harness.py` erweitern; Entrypoint Smoke-Exit wie in `run_qml_shell.py`.
6. Tests unter `tests/gui/` ergänzen.

## Pflichtfelder (QML-Alternative)

Siehe `docs/release/ALTERNATIVE_GUI_GOVERNANCE.md` und `qml/theme_manifest.json`.

## Kompatibilitätsprüfung (fail-closed)

- Vor Start der alternativen GUI: `validate_library_qml_gui_launch_context` (Manifest + Listen + `theme_id` == `gui_id`).
- Bei Fehler: **keine** Aktivierung; Logging; Fallback auf **`default_widget_gui`** (siehe `run_gui_shell.py`).

## Auswahl der GUI

1. CLI `--gui` (Aliases oder `gui_id`) — unbekannter Wert → **Exit-Code 2**, kein Start
2. Umgebung `LINUX_DESKTOP_CHAT_GUI`
3. QSettings `preferred_gui` (kanonische `gui_id`; Legacy `default` / `library_qml` wird gelesen)
4. `AppSettings.preferred_gui` (gleiche Kanonisierung beim Speichern)

Siehe auch: `docs/04_architecture/ALTERNATIVE_GUI_THEME_RELEASE_GOVERNANCE.md`.

## Nutzung (CLI)

```bash
python run_gui_shell.py --gui default_widget_gui
python run_gui_shell.py --gui library_qml_gui
python run_gui_shell.py --gui library_qml   # Alias
```

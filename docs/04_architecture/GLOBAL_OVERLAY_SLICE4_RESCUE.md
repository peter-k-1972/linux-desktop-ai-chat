# Global Overlay — Slice 4 (Rescue Actions)

**Projekt:** Linux Desktop Chat  
**Status:** implementiert

## Aktionsmodell

Rescue-Aktionen sind **Produkt-/Runtime-Funktionen** (`app/global_overlay/overlay_rescue_port.py`). Keine Domänenlogik, keine Theme-Eigenimplementierung.

| Aktion | Wirkung |
|--------|---------|
| **Revert to default GUI (relaunch)** | `preferred_gui` → Registry-Default, dann `run_gui_shell.py` + `app.quit()` (Slice 3) |
| **Reset preferred GUI** | Nur Persistenz auf Default; **kein** Relaunch (laufende Session unverändert) |
| **Reset preferred theme** | QSettings `theme_id`/`theme` → `light_default` / `light`; optional `AppSettings.save()` + `ThemeManager` wenn Widget-GUI aktiv |
| **Safe mode next launch** | One-Shot-Flag in QSettings (`safe_mode_next_launch`) |
| **Restart application** | `run_gui_shell.py --gui <aktuell gespeicherte Präferenz>` + `app.quit()` |

Alle persistierenden Aktionen laufen über **Bestätigungsdialoge** (Qt `QMessageBox`) im Overlay.

## Safe Mode (one-shot)

- **Speicherort:** `QSettings` (Org `OllamaChat`, App `LinuxDesktopChat`), Schlüssel `safe_mode_next_launch`.
- **Setzen:** `write_safe_mode_next_launch_flag(True)` (Rescue-Aktion).
- **Auswertung:**
  - **`run_gui_shell.py`:** direkt nach `parse_args()` — `consume_safe_mode_next_launch()`: wenn gesetzt, ohne explizites `--gui` → `preferred_gui` = `default_widget_gui`; ohne `--theme` → `write_product_theme_defaults_to_qsettings()` und `args.theme = light_default`. Anschließend normale Auflösung (CLI überschreibt weiterhin).
  - **`run_qml_shell.py`:** wenn Flag **pending** (nur lesen), werden Default-GUI/Theme geschrieben und per `run_gui_shell.py` relauncht; **`consume_safe_mode_next_launch()` nur nach erfolgreichem** `startDetached`. Schlägt Relaunch fehl → **Flag bleibt**, Exit 1 (Retry möglich).

## Zurücksetzen welcher Settings

- **GUI:** `preferred_gui` (kanonische `gui_id`).
- **Theme:** `theme_id`, Legacy `theme` (wie `AppSettings`).

## Relaunch / Exit

- Relaunch ausschließlich über **`QProcess.startDetached`** → `run_gui_shell.py` (gleicher Produktpfad wie Slice 3).
- **Quit:** `QApplication.quit()` nach erfolgreichem Detach.

## UI

- **Emergency-Overlay (Alt+Shift+Z):** primärer Rescue-Bereich mit allen Aktionen.
- **Normales Overlay:** gleiche Aktionen in Gruppe **Rescue**, ruhiger platziert; **GUI** / **Theme** bleiben getrennt.

## Siehe auch

- Slice 3: [`GLOBAL_OVERLAY_SLICE3_GUI.md`](GLOBAL_OVERLAY_SLICE3_GUI.md)  
- Konzept: [`GLOBAL_OVERLAY_MENU_ARCHITECTURE.md`](GLOBAL_OVERLAY_MENU_ARCHITECTURE.md)

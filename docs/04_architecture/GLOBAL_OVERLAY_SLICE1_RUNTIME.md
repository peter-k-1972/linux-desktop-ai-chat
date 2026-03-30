# Global Overlay — Slice 1 (Runtime)

**Projekt:** Linux Desktop Chat  
**Status:** implementiert (Grundgerüst)

## Zweck des Overlay-Hosts

Der **Global Overlay Host** (`app/global_overlay/overlay_host.py`) ist eine **Produkt-Shell-Komponente**: er besitzt Tastenkürzel, den UI-Zustand (normal vs. emergency) und die Modal-Dialoge. Er hängt **nicht** an Themes oder Domänen.

## Normales vs. Emergency-Overlay

| Aspekt | Normal (`Alt+Z`) | Emergency (`Alt+Shift+Z`) |
|--------|------------------|----------------------------|
| **Inhalt** | Vollständige Statusfläche (GUI, Theme-Hinweis, Release-Labels, geplante Folgeslices) | Minimale Rescue-Fläche, Hinweis auf künftige Recovery-Aktionen |
| **Aktionen** | Nur Schließen (keine Wechsel, kein Settings-Schreiben) | Schließen, **Quit application** (`QApplication.quit`) |
| **Ziel** | Systemmenü / Orientierung | möglichst kleine, robuste Oberfläche |

Es ist **höchstens eines** der beiden Overlays sichtbar; beim Öffnen des einen wird das andere geschlossen.

## Reservierte Hotkeys

Kanonische QKeySequence-Strings: **`app/global_overlay/overlay_product_shortcuts.py`** (Single Source of Truth). Kurz:

- **`Alt+Z`**: normales Overlay toggeln  
- **`Alt+Shift+Z`**: Emergency-Overlay toggeln  

Siehe auch [GLOBAL_OVERLAY_PRODUCT_GOVERNANCE.md](GLOBAL_OVERLAY_PRODUCT_GOVERNANCE.md).

Registrierung mit `Qt.ApplicationShortcut` am Host-`QObject`, damit sie **produktweit** gelten (Widget- und QML-Shell, sobald `QApplication` existiert).

## Technische Darstellung (Slice 1)

**`QDialog` + `ApplicationModal`**: robuster Fokusfang, wenig Abhängigkeit vom Theme-Stylesheet (Systemrahmen). Keine QML-Overlay-Implementierung in diesem Slice.

Ohne passendes Parent-Fenster (z. B. QML-Shell) wird der Dialog **auf dem primären Bildschirm zentriert**.

## Integration

- **Widget-Shell:** `run_gui_shell.py` → nach `ShellMainWindow.show()`: `install_global_overlay_host(..., GUI_ID_DEFAULT_WIDGET, primary_window=win)` (nicht im GUI-Smoke-Modus).
- **QML-Shell:** `run_qml_shell.py` → nach `runtime.activate()`: `install_global_overlay_host(..., GUI_ID_LIBRARY_QML, primary_window=None)` (nicht im Smoke-Modus).

## Statusdaten

`collect_overlay_status(active_gui_id)` (`overlay_status.py`) nutzt u. a.:

- `app.core.startup_contract` (GUI-Deskriptoren, Default-Fallback, bevorzugte GUI aus QSettings)
- Widget-Pfad: `ThemeManager.get_current_id()`  
- QML-Pfad: `AppSettings.theme_id` oder erklärender String  
- `app.application_release_info` (App-, Backend-, Contract-, Bridge-Version)

## Watchdog-Basis

Modul `app/global_overlay/gui_launch_watchdog.py`:

- Session-Startzeit (monotonic), letzter Launch-Zeitpunkt, Zähler für aufeinanderfolgende Fehlstarts, erfolgreiche Launches.
- **`SUGGESTED_LAUNCH_FAILURE_THRESHOLD = 3`**: dokumentierte Schwelle für **künftige** Auto-Safe-Mode-Logik — in Slice 1 **keine** automatische Heilung.
- Hooks: `on_app_session_start()` beim App-Start; `note_successful_gui_launch()` nach erfolgreichem Hauptfenster-Start; `note_failed_gui_launch()` bei fehlgeschlagenem alternativen GUI-Start (`run_gui_shell`).

## Slice 2 (Theme Switching)

Siehe [`GLOBAL_OVERLAY_SLICE2_THEME.md`](GLOBAL_OVERLAY_SLICE2_THEME.md): Theme-Status, Auswahl und Apply über ThemeManager + `ServiceSettingsAdapter` (Widget-GUI); QML-GUI read-only / gesperrt.

## Slice 3 (GUI Switching)

Siehe [`GLOBAL_OVERLAY_SLICE3_GUI.md`](GLOBAL_OVERLAY_SLICE3_GUI.md): Registry-Liste, Validierung wie beim Produktstart, `preferred_gui` + Relaunch über `run_gui_shell.py`, Revert auf Default.

## Slice 4 (Rescue)

Siehe [`GLOBAL_OVERLAY_SLICE4_RESCUE.md`](GLOBAL_OVERLAY_SLICE4_RESCUE.md): Resets, Safe-Mode-Flag (one-shot), Restart; Emergency-Overlay als primärer Recovery-Ort.

## Bewusst noch nicht implementiert (Folgeslices)

- GUI-Wechsel, persistierte Resets, Safe-Mode-Flags  
- Diagnose-Panel, Log-Viewer, QA-Smoke aus dem Overlay  
- Auto-Safe-Mode bei Watchdog-Schwellen  

## Siehe auch

- Konzept: `GLOBAL_OVERLAY_MENU_ARCHITECTURE.md`  
- GUI-Registry: `docs/architecture/GUI_REGISTRY.md`

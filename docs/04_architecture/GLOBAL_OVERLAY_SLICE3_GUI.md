# Global Overlay — Slice 3 (GUI Switching + Fallback)

**Projekt:** Linux Desktop Chat  
**Status:** implementiert

## Trennung GUI vs. Theme

| Bereich | Inhalt | Wirksam nach |
|---------|--------|----------------|
| **GUI** | Registry-Einträge, `preferred_gui`, Relaunch über `run_gui_shell.py` | **Relaunch** (neuer Prozess) |
| **Theme** | ThemeManager + `ServiceSettingsAdapter` (nur Widget-GUI) | **Sofort** (Stylesheet) oder gesperrt (QML) |

Die Overlay-UI hat **zwei getrennte Gruppen** („GUI“ und „Theme“); keine gemeinsame Liste.

## Architektur

Modul: `app/global_overlay/overlay_gui_port.py`

1. **Status:** `build_gui_overlay_snapshot(active_gui_id)` — Registry + QSettings (`read_preferred_gui_id_from_qsettings`), Prüfung ob `run_gui_shell.py` unter `resolve_repo_root()` existiert.
2. **Validierung (fail-closed):** `validate_gui_switch_target(gui_id, repo_root=…)`  
   - Deskriptor aus `REGISTERED_GUIS_BY_ID`  
   - Entrypoint-Datei vorhanden  
   - `assert_descriptor_matches_manifest_paths`  
   - `qt_quick`: `validate_library_qml_gui_launch_context` für `library_qml_gui`; andere `qt_quick`-IDs ohne Validator → abgelehnt  
3. **Wechsel:** `apply_gui_switch_via_product(active_gui_id, target_gui_id)`  
   - Bei `target == active`: nur `write_preferred_gui_id_to_qsettings` (Sync), **kein** Relaunch  
   - Sonst: validieren → `write_preferred_gui_id_to_qsettings(target)` → `relaunch_via_run_gui_shell(target)`  
   - Wenn Relaunch **fehlschlägt**: `preferred_gui` wird auf den **vorherigen** Wert zurückgesetzt  
   - Wenn Relaunch **startet**: `QApplication.quit()` im alten Prozess  
4. **Revert:** `revert_to_default_gui_via_product(active_gui_id)` → Wechsel auf `get_default_fallback_gui_id()` (typisch `default_widget_gui`).

## Relaunch-/Fallback-Verhalten

- Relaunch nutzt **denselben Mechanismus** wie der manuelle Start:  
  `python run_gui_shell.py --gui <kanonische_gui_id>` mit Arbeitsverzeichnis = Repo-Wurzel.  
- `run_gui_shell` enthält weiterhin die Qt-Quick-Validierung und den Subprozess-Pfad für `library_qml_gui` — das Overlay **dupliziert** diese Logik nicht beim Start, wendet sie aber **vor** dem Schreiben von `preferred_gui` an, damit keine ungültige Präferenz persistiert wird (fail-closed).

## Rolle von `default_widget_gui`

- In der Registry als `is_default_fallback=True` markiert.  
- „Revert to default GUI“ setzt genau diese ID und relauncht wie oben.

## Emergency-Overlay

- Read-only **GUI**- und **Theme**-Zeilen.  
- Button **Revert to default GUI (relaunch)** — gleiche Produktfunktion wie im normalen Overlay; bei blockiertem Switching (fehlendes `run_gui_shell.py`) deaktiviert.

## Fail-closed

- Unbekannte `gui_id`, fehlender Entrypoint, Manifest-/Kompatibilitätsfehler → **kein** Schreiben von `preferred_gui`.  
- Relaunch-Fehler → **Rollback** der Präferenz auf den Stand vor dem Versuch.

## Siehe auch

- Slice 1: [`GLOBAL_OVERLAY_SLICE1_RUNTIME.md`](GLOBAL_OVERLAY_SLICE1_RUNTIME.md)  
- Slice 2: [`GLOBAL_OVERLAY_SLICE2_THEME.md`](GLOBAL_OVERLAY_SLICE2_THEME.md)  
- Slice 4 (Rescue): [`GLOBAL_OVERLAY_SLICE4_RESCUE.md`](GLOBAL_OVERLAY_SLICE4_RESCUE.md)  
- Konzept: [`GLOBAL_OVERLAY_MENU_ARCHITECTURE.md`](GLOBAL_OVERLAY_MENU_ARCHITECTURE.md)  
- Registry: `docs/architecture/GUI_REGISTRY.md`

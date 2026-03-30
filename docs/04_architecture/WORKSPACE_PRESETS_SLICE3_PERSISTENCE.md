# Workspace Presets — Slice 3 (Persistenz + Aktivierungsfluss)

**Projekt:** Linux Desktop Chat  
**Umfang:** Produktzustand `active_workspace_preset_id` in QSettings, Aktivierungs-API, sofort persistierte Begleitfelder, Overlay ruft Produkt-API — **ohne** GUI-Hotswap, **ohne** Theme-Orchestrierung über alle GUIs, **ohne** Relaunch-Automatik.

Vorgänger: [WORKSPACE_PRESETS_SLICE2_OVERLAY.md](WORKSPACE_PRESETS_SLICE2_OVERLAY.md) · Konzept: [WORKSPACE_PRESETS_ARCHITECTURE.md](WORKSPACE_PRESETS_ARCHITECTURE.md)

## Aktiver Preset-Zustand

| Konzept | Implementierung |
|---------|-----------------|
| Autoritative ID | `resolve_valid_active_workspace_preset_id()` in `preset_state.py` |
| Objekt | `get_active_workspace_preset()` / `get_active_workspace_preset_id()` in `preset_activation.py` |
| Fallback | Unbekannt / ungültig / deprecated / nicht approved → Registry-Default (`chat_focus`) und **Korrektur** der Speicherung (fail-closed) |

## Persistenz (QSettings)

Org/App wie `app.core.startup_contract.product_qsettings()` (`OllamaChat` / `LinuxDesktopChat`).

| Schlüssel | Inhalt |
|-----------|--------|
| `active_workspace_preset_id` | Kanonische `preset_id` |
| `workspace_preset_preferred_start_domain` | `preset.start_domain` (Nav-Entry-ID) |
| `workspace_preset_context_profile` | `preset.context_profile` |
| `workspace_preset_overlay_mode` | `preset.overlay_mode` |

Schreiben nur über `write_active_workspace_preset_bundle_to_storage` (nach erfolgreicher Aktivierung).  
Tests können `preset_state._qs` monkeypatchen (INI-Datei).

## Aktivierungs-API

Modul `app/workspace_presets/preset_activation.py`:

| Funktion | Rolle |
|----------|--------|
| `evaluate_workspace_preset_activation(...)` | Nur Auswertung, **kein** Schreiben |
| `apply_workspace_preset_activation(...)` | Auswertung + bei Erfolg Persistenz |
| `set_active_workspace_preset(...)` | Alias von `apply_workspace_preset_activation` |
| `clear_active_workspace_preset(...)` | Setzt Bundle auf Registry-Default (Safe-Mode-Check) |

Parameter **`running_gui_id`** und optional **`running_theme_id`**: für Abgleich mit Preset-Zielen und für `restart_required_for_full_effect` / Status (kein automatischer Wechsel).

## Aktivierungsstatus (`WorkspacePresetActivationResult`)

| `status` | Bedeutung |
|----------|------------|
| `rejected` | Keine Änderung der Speicherung |
| `accepted_immediate` | Persistiert; laufende Shell entspricht den deklarierten GUI/Theme-Zielen (und Preset erzwingt keinen Restart) |
| `accepted_pending_restart` | Persistiert; **vollständige** Wirkung erfordert später Relaunch/Theme-Pfad (Slice 4) |

Zusätzlich: `restart_required_for_full_effect` (bool), `message`, `active_preset_id`.

## Sofort vs. vollständig angewendet (Slice-3-Grenze)

**Sofort (Slice 3):**

- Persistenz des Presets und der deklarativen Felder oben
- Overlay liest Zustand über `build_workspace_preset_overlay_snapshot(...)`

**Noch nicht (Slice 4+):**

- `preferred_gui` / Theme aus Preset automatisch setzen und Relaunch triggern
- Navigation zur `start_domain` erzwingen
- Layout-Engine
- Safe-Mode-spezifische Feinpolitik über Blockierung hinaus

## Minimale Konfliktregeln

- **Safe Mode** (`read_safe_mode_watchdog_banner` oder `read_safe_mode_next_launch_pending`): Aktivierung und `clear_active_workspace_preset` werden **abgelehnt**.
- **Deprecated** / nicht **approved** / strukturell ungültig: **reject**, keine Speicherung.
- **Unbekannte `preset_id`**: **reject**.

## Overlay

`StandardOverlayDialog` ruft nur `request_preset_activation(..., running_gui_id=..., running_theme_id=...)` aus `workspace_preset_port.py` — keine direkten QSettings-Zugriffe im Dialog. Hinweistext: `SLICE3_OVERLAY_NOTICE_HTML`.

## Slice 4

Restart-/Relaunch-Grenzen, Pending-Marker, BoundaryReport: [WORKSPACE_PRESETS_SLICE4_RESTART_BOUNDARIES.md](WORKSPACE_PRESETS_SLICE4_RESTART_BOUNDARIES.md).

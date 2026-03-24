# Workspace Presets — Slice 4 (Restart-/Relaunch-Grenzen)

**Projekt:** Linux Desktop Chat  
**Umfang:** Explizite Boundary-Auswertung pro Preset-Feld, QSettings-Marker `workspace_preset_full_effect_pending_restart`, Overlay-Kommunikation, Safe-Mode-Klassifikation — **kein** erzwungener GUI-Hotswap; Relaunch bleibt der sichere Pfad über die bestehende GUI-Sektion / `run_gui_shell.py`.

Vorgänger: [WORKSPACE_PRESETS_SLICE3_PERSISTENCE.md](WORKSPACE_PRESETS_SLICE3_PERSISTENCE.md) · Konzept: [WORKSPACE_PRESETS_ARCHITECTURE.md](WORKSPACE_PRESETS_ARCHITECTURE.md)

## Boundary-Modul

`app/workspace_presets/preset_restart_boundaries.py`

- `PresetEffectCategory`: `immediate` · `restart_required` · `ignored_in_safe_mode` · `unsupported`
- `PresetFieldBoundary`: `field_name`, `category`, `detail` (QA-/Nutzerlesbar)
- `WorkspacePresetBoundaryReport`: `entries`, `overall_requires_restart`, `safe_mode_runtime_override_active`
- `build_workspace_preset_boundary_report(preset, *, running_gui_id, running_theme_id, safe_mode_runtime_override=None)`
- `format_workspace_preset_boundary_report_rich_html(report)` — Overlay-HTML
- `safe_mode_runtime_active()` — Watchdog-Banner oder Safe-Mode-Next-Launch pending

## Feld-Klassifikation (Ist-Stand)

| Feld | Regel (kurz) |
|------|----------------|
| **gui_id** | Safe Mode → `ignored_in_safe_mode`. Sonst: Shell = Preset → `immediate`, sonst `restart_required` (GUI-Sektion / Relaunch). |
| **theme_id** | Safe Mode → `ignored_in_safe_mode`. GUI ≠ Preset-Ziel → `restart_required`. GUI ohne `supports_theme_switching` → `restart_required`. Sonst: Theme gleich → `immediate`; sonst `immediate` mit Hinweis: Anwendung über **Theme-Sektion** (kein Auto-Apply in Slice 4). |
| **start_domain** | GUI ≠ Preset → `restart_required`; sonst `immediate` (nur gespeichert, kein Auto-Nav). |
| **layout_mode** | `unsupported` (kein Layout-Engine-Verbraucher). |
| **context_profile** | `immediate` (deklarativ persistiert). |
| **overlay_mode** | `immediate`; `rescue_minimal` erhält Zusatzhinweis. |
| **rescue_bias** | `immediate` (Policy-Hint; hebelt Safe Mode nicht aus). |

**overall_requires_restart** = `preset.requires_restart` **oder** mindestens ein Eintrag `restart_required`.  
`unsupported` zählt **nicht** als Relaunch-Pflicht.

## Persistenter Marker

- Schlüssel: `workspace_preset_full_effect_pending_restart` (bool, QSettings)
- Nach erfolgreicher **apply_workspace_preset_activation**: gesetzt auf `boundary_report.overall_requires_restart`
- **resync_full_effect_pending_restart_from_runtime**: beim Overlay (über `build_active_workspace_preset_boundary_report_for_overlay`) — wenn **kein** Safe Mode, Neuberechnung aus aktivem Preset + laufender Shell; aktualisiert den Marker

Im Safe Mode wird **nicht** resynchronisiert (Marker bleibt stabil bis Recovery).

## Aktivierungs-API

`WorkspacePresetActivationResult` enthält optional `boundary_report` (bei Erfolg, außerhalb Safe-Mode-Block vor Aktivierung: bei Reject `None`).

Nach **Apply**: Nutzerhinweis + persistierter Pending-Marker; **kein** automatischer Relaunch.

## Overlay

- Block **Restart boundaries**: HTML aus `format_workspace_preset_boundary_report_rich_html`
- **Active preset**: `full_effect_pending_restart` lesbar erklärt; bei Safe Mode zusätzlicher Hinweis, dass Runtime GUI/Theme dem Preset folgen, sobald Recovery abgeschlossen ist
- Hinweistext: `SLICE4_OVERLAY_NOTICE_HTML` (ersetzt Slice-3-Text inhaltlich)

## Safe Mode

- **Aktivierung** eines Presets bleibt **blockiert**, solange Watchdog-Banner oder Safe-Mode-Next-Launch pending (Slice 3 Verhalten)
- **Anzeige**: Boundary mit `ignored_in_safe_mode` für `gui_id` / `theme_id`, wenn `safe_mode_runtime_override_active`

## Bewusst nicht live umgeschaltet

- GUI (nur Relaunch-Pfad)
- Theme automatisch beim Preset-Apply (nur Klassifikation + ggf. manuelle Theme-Sektion)
- Navigation zur `start_domain`
- `layout_mode`

## Nächste Schritte (optional)

- Auto-Navigation / Layout-Consumer
- Relaunch-Button „Apply preset targets now“ auf gleichen Launcher wie GUI-Switch
- Diagnostics-Zeile zum aktiven Preset + Boundary-Kurzform

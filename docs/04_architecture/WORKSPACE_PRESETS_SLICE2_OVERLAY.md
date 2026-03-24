# Workspace Presets — Slice 2 (Overlay-Integration)

**Projekt:** Linux Desktop Chat  
**Umfang:** Standard-Overlay-UI; Produkt-Aktivierung über Port (siehe Slice 3 für Persistenz). **Kein** GUI-Hotswap / **keine** Relaunch-Orchestrierung in diesem Layer.

**Slice 3:** [WORKSPACE_PRESETS_SLICE3_PERSISTENCE.md](WORKSPACE_PRESETS_SLICE3_PERSISTENCE.md).

Architekturüberblick: [WORKSPACE_PRESETS_ARCHITECTURE.md](WORKSPACE_PRESETS_ARCHITECTURE.md)  
Registry/Modell (Slice 1): [WORKSPACE_PRESETS_SLICE1_IMPLEMENTATION.md](WORKSPACE_PRESETS_SLICE1_IMPLEMENTATION.md)

## Darstellung im Overlay

Das **normale** System-Overlay (`StandardOverlayDialog`) enthält eine eigene Gruppe **Workspace Presets** — **zwischen** Theme und Rescue, nicht als Unterpunkt von GUI oder Theme.

| UI-Element | Zweck |
|------------|--------|
| **Active preset (product state)** | Persistierter aktiver Preset (QSettings), plus Hinweis „full effect“ / Restart. |
| **Available presets** | `QComboBox`, gefüllt aus der Registry über `list_selectable_presets_for_overlay()`. |
| **Details** | Read-only HTML aus `format_workspace_preset_detail_rich_html` für die aktuelle Kombobox-Auswahl. |
| **Activate preset** | Ruft `request_preset_activation(..., running_gui_id, running_theme_id)` auf. |
| **Hinweisbox** | `SLICE3_OVERLAY_NOTICE_HTML` (Alias `SLICE2_PRELIMINARY_NOTICE_HTML`). |

**Emergency-Overlay:** keine Preset-Steuerung (Slice 2); Fokus bleibt Rescue.

## Ausgewählt vs. aktiv

| Begriff | Technik |
|---------|---------|
| **Ausgewählt (Liste)** | `QComboBox.currentData()` — nur Detailansicht bis „Activate“. |
| **Aktiv (Produkt)** | `resolve_valid_active_workspace_preset_id()` / QSettings; Anzeige über `build_workspace_preset_overlay_snapshot`. |

## Aktivierungssemantik (ab Slice 3)

`request_preset_activation(preset_id, *, running_gui_id, running_theme_id=…)` delegiert an `apply_workspace_preset_activation` (siehe Slice-3-Doku): Persistenz + Statusobjekt, **kein** GUI-/Theme-Hotswap.

## Sichtbare / aktivierbare Presets

Slice 2 zeigt **ausschließlich** `approved` Presets (`list_approved_workspace_presets()`). `candidate` / `draft` / `deprecated` sind standardmäßig **nicht** auswählbar.

## Produkt-Fassade

Modul: `app/workspace_presets/workspace_preset_port.py`

- Overlay und spätere Slices sollen Presets **nicht** ad hoc aus Registry zusammenbauen, sondern über diese Port-API lesen und Aktivierung melden.
- Bewusst klein gehalten — keine „Preset-Runtime“.

## Trennung zu GUI- und Theme-Switching

| Mechanismus | Slice 2 |
|-------------|---------|
| GUI wechseln | Unverändert: eigene Sektion + Relaunch. |
| Theme anwenden | Unverändert: eigene Sektion + Capability-Regeln. |
| Workspace Preset | Persistenz + Status (Slice 3); **keine** automatische Kopplung an GUI-/Theme-Relaunch (Slice 4). |

## Bewusst noch offen (Slice 4+)

- Relaunch-/Restart-Orchestrierung aus Preset-Zielen
- Erzwingende Anwendung von `start_domain` / Layout
- Overlay-Diagnostics-Zeile für aktives Preset
- Settings-/CLI-Einstieg

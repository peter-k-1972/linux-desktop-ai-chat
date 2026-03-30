# Workspace Presets — Slice 1 (Implementierung)

**Projekt:** Linux Desktop Chat  
**Umfang:** Preset-Objektmodell, Registry, strukturelle Validierung, erste kanonische Presets, Tests.  
**Nicht enthalten (Slice 1):** Overlay-Sektion, vollständige Aktivierung, Persistenz, Relaunch, Safe-Mode-Override, Layout-Umbauten.

**Slice 2 (Overlay):** [WORKSPACE_PRESETS_SLICE2_OVERLAY.md](WORKSPACE_PRESETS_SLICE2_OVERLAY.md).  
**Slice 3 (Persistenz + Aktivierung):** [WORKSPACE_PRESETS_SLICE3_PERSISTENCE.md](WORKSPACE_PRESETS_SLICE3_PERSISTENCE.md).

Konzeptüberblick: [WORKSPACE_PRESETS_ARCHITECTURE.md](WORKSPACE_PRESETS_ARCHITECTURE.md).

## Was ein Workspace Preset im Produkt ist

Ein **Workspace Preset** ist ein **deklaratives Produktobjekt** (`WorkspacePreset`), das einen intendierten **Arbeitsmodus** beschreibt: welche GUI (`gui_id`), welches **Built-in-Theme** (`theme_id`), welche **Startdomäne** (`start_domain` = ID aus der Navigations-Registry), sowie Token für Layout-Kontext, Overlay-Modus und Rescue-Tendenz.

Es ist **weder** eine GUI-Registry-Zeile **noch** ein Theme — es **referenziert** beides.

## Paketstruktur

| Modul | Rolle |
|-------|--------|
| `app/workspace_presets/preset_models.py` | `WorkspacePreset`, `PresetReleaseStatus`, erlaubte Token-Mengen, Defaults |
| `app/workspace_presets/preset_registry.py` | `REGISTERED_PRESETS_BY_ID`, Lookup, Listen, kanonische IDs |
| `app/workspace_presets/preset_validation.py` | `validate_workspace_preset`, Registry-Konsistenz |
| `app/workspace_presets/__init__.py` | Öffentliche Exporte |

**Entscheidung Slice 1:** **codebasierte Registry** (kein JSON-Manifest) — wenig bewegliche Teile, Import-Zeit-Validierung, einfache Tests.

## Preset-Modell (Felder)

| Feld | Pflicht | Default / Anmerkung |
|------|---------|---------------------|
| `preset_id` | ja | wird getrimmt, nicht leer |
| `display_name`, `description` | ja | — |
| `gui_id` | ja | muss im kanonischen Produktvertrag `app.core.startup_contract` registriert sein |
| `theme_id` | ja | Slice 1: nur **Built-ins** (`BUILTIN_THEME_IDS` in `app.core.config.builtin_theme_ids`) |
| `start_domain` | ja | muss `navigation_registry.get_entry(id)` finden |
| `requires_restart` | ja | bool (deklarativ; keine Orchestrierung in Slice 1) |
| `release_status` | ja | `draft` / `candidate` / `approved` / `deprecated` |
| `compatible_app_versions` | ja | nicht-leeres Tuple (z. B. `APP_RELEASE_VERSION`) |
| `layout_mode` | nein | `default` |
| `context_profile` | nein | `balanced` |
| `overlay_mode` | nein | `standard` |
| `rescue_bias` | nein | `none` |
| `tags` | nein | `()` |

**Theme-Hinweis:** Später kann Theme-Validierung GUI-Capabilities (`supports_theme_switching`) bei **Aktivierung** berücksichtigen. Slice 1 prüft nur **bekannte Built-in-IDs**, damit QML-/Widget-Unterschiede nicht überkompliziert werden.

## Kanonische Presets (Slice 1)

| `preset_id` | Startdomäne (Nav) | Kurzbeschreibung |
|-------------|-------------------|------------------|
| `chat_focus` | `operations_chat` | Chat-Fokus, `light_default` |
| `workflow_studio` | `operations_workflows` | Workflows, `workbench` |
| `project_command_center` | `command_center` | Systemübersicht, `dark_default` |
| `agent_operations` | `operations_agent_tasks` | Agent Tasks, `dark_default` |
| `rescue_minimal` | `settings` | Support-orientiert, `light_default`, `rescue_oriented` |

Alle nutzen in Slice 1 `default_widget_gui` und `release_status=approved`.

## API (Auszug)

- `get_workspace_preset(preset_id)` → `WorkspacePreset` oder `KeyError`
- `list_workspace_preset_ids()`, `list_workspace_presets()`, `list_approved_workspace_presets()`
- `get_default_workspace_preset_id()` → derzeit `chat_focus`
- `canonical_workspace_preset_ids()` — die fünf Slice-1-IDs
- `validate_workspace_preset(p)` → Liste von Fehlermeldungen

Beim Import von `preset_registry` wird `assert_registered_presets_valid` ausgeführt — inkonsistente Registry bricht früh ab.

## Bewusst noch nicht umgesetzt

- Overlay-UI, Settings-UI, CLI
- Schreiben/Lesen eines aktiven Presets in QSettings
- Anwendung von GUI/Theme/Navigation zur Laufzeit
- Relaunch / Safe Mode / Watchdog-Interaktion
- Erweiterung `theme_id` auf importierte Benutzer-Themes (Validierung dann Aktivierungszeit)

## Tests

`tests/workspace_presets/test_workspace_presets_slice1.py` — Modell-, Registry- und Validierungsfälle.

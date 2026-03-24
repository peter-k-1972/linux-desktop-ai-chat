# Workspace Presets — Slice 5: Produktintegration & Runtime

**Projekt:** Linux Desktop Chat  
**Status:** Implementiert (Slice 5)  
**Bezug:** [WORKSPACE_PRESETS_ARCHITECTURE.md](WORKSPACE_PRESETS_ARCHITECTURE.md), Slices 1–4

---

## 1. Was sich ändert

Workspace Presets sind ein **Arbeitsmodus** (Komposition aus GUI-Ziel, Theme-Ziel, Startdomäne, Overlay-/Kontext-Hinweisen). Slice 5 verdrahtet diesen Modus in:

- **Produktstart** (`run_gui_shell.py` Widget-Shell, `run_qml_shell.py` Qt-Quick-Einstieg)
- **Erste Navigation** (`ShellMainWindow`)
- **QSettings-Präferenzen** (`preferred_gui`, `theme_id`) beim Start, sofern keine höhere Priorität greift
- **Overlay** (aktives Preset, Auswahl, Tags, Boundaries, Restart-Marker)
- **Settings → Workspace** (nur **Lesen**, keine Bearbeitung)
- **Kompatibilitätsprüfung** bei Aktivierung (Reject vs. Partial mit dokumentierter Grenze)

---

## 2. Startreihenfolge (Widget-GUI)

1. Safe-Mode-One-Shot (unverändert, Slice 4)
2. Optional `--gui` → schreibt `preferred_gui`
3. **Ohne `--gui` (nur `run_gui_shell`):** `sync_workspace_preset_preferences_before_gui_resolution(argv)`  
   - Nur wenn `active_workspace_preset_id` in QSettings gesetzt ist  
   - Überspringt bei Safe-Mode-Laufzeitblock  
   - **Immer:** Preset-Bundle-Felder (`start_domain`, `context_profile`, `overlay_mode`, …) werden geschrieben, sobald die GUI-Kompatibilität des Presets passt  
   - **Pro Dimension:** `preferred_gui` nur ohne explizites GUI-Override (`--gui` / `LINUX_DESKTOP_CHAT_GUI`); `theme_id` nur ohne explizites Theme-Override (`--theme` / `LINUX_DESKTOP_CHAT_THEME`)
4. `resolve_active_gui_id` (CLI > Env > QSettings)
5. `init_infrastructure` → Theme aus Settings / Args
6. `apply_workspace_preset_runtime_after_infrastructure` → `full_effect_pending_restart` aus BoundaryReport (kein erzwungener Relaunch)
7. `ShellMainWindow` → `resolve_shell_startup_navigation_targets()` für ersten `show_area`

**Hinweis:** Produktstart ist der Moment, in dem **sofortige** Preset-Effekte (Theme, gespeicherte Präferenzen, Startdomäne) voll angewendet werden dürfen; **Restart-pflichtige** Dimensionen (z. B. GUI-Wechsel) bleiben dokumentiert im Boundary-Report / Marker, ohne Auto-Relaunch.

### 2b. Qt-Quick-Einstieg (`run_qml_shell.py`)

Nach Safe-Mode-Relaunch-Pfad und **vor** Validierung der QML-Umgebung:

- derselbe `sync_workspace_preset_preferences_before_gui_resolution(sys.argv)` (dimensionale Overrides wie oben)
- nach `init_infrastructure`: `apply_workspace_preset_runtime_after_infrastructure(running_gui_id=library_qml_gui, …)` für den Pending-Restart-Marker

**Scope-Grenze (ehrlich):** Die QML-Shell mappt `start_domain` **nicht** auf einen initialen QML-Screen beim Kaltstart; das Token wird persistiert und im **Boundary-Report** so kommuniziert. Automatische erste Navigation aus dem Navigations-Registry gilt für die **Widget-Shell** (`ShellMainWindow`).

---

## 3. Safe Mode & Overrides

- **P0 Safe Mode:** Aktivierung blockiert (Slice 3–4 unverändert). Navigation beim Widget-Shell-Start geht bei aktivem Safe-Mode-Laufzeitpfad auf **Kommandozentrale**.
- **CLI / Env — dimensional:** Ein Override betrifft nur die betroffene Dimension. Ein Theme-Override blockiert **nicht** mehr den gesamten Sync; Bundle und ggf. `preferred_gui` aus dem Preset werden weiterhin angewendet, soweit Kompatibilität und Overrides es erlauben.

---

## 3b. Logging & Fehlerbehandlung (Startup)

In `run_gui_shell.py` (Preset-Sync vor GUI-Auflösung, Runtime nach Theme), `run_qml_shell.py` (analoge Preset-Hooks) und `ShellMainWindow` (erste Navigation): Fehler werden mit `logging.exception` protokolliert; der Start läuft mit definiertem Fallback weiter (bestehende QSettings / Kommandozentrale), **ohne** stilles `except Exception: pass` in diesen Preset-spezifischen Pfaden.

---

## 3c. `start_domain` — Boundary-Text vs. Laufzeit

- **Widget shell, laufende GUI = Preset-`gui_id`:** Boundary meldet **Immediate**: gespeicherte `start_domain` wird beim **Widget-Startup** als erste Workspace-Ansicht angewendet (Navigations-Registry).
- **Qt Quick library GUI, laufende GUI = Preset-`gui_id`:** Boundary meldet **Immediate** mit klarer Erklärung: Token ist in QSettings/produktseitig relevant, aber **keine** automatische QML-Route aus dem Registry-Token beim Kaltstart.
- **GUI-Mismatch:** weiter **Restart required** wie in Slice 4.

---

## 3d. Theme-Validierung (Slice 1 vs. Laufzeit)

`theme_id_valid_for_workspace_preset_registry` in `preset_validation.py` erlaubt **Built-in-IDs** oder IDs, die über die Theme-Registry erkennbar sind (gleiche Idee wie `is_registered_theme_id`). Schlägt die Registry-Abfrage fehl (sehr früher Import), gelten vorerst nur Built-ins — konsistent dokumentiert im Docstring.

---

## 4. Kompatibilität (Slice 5)

Modul `app.workspace_presets.preset_compatibility`:

| Prüfung        | Reject | Partial |
|----------------|--------|---------|
| `gui_id` registriert | Ja (kein Apply) | — |
| `theme_id` verfügbar (Built-in / Registry) | — | Theme wird ggf. nicht persistiert |
| `start_domain` in Nav-Registry | — | Persistenz nutzt Fallback `operations_chat` |

`WorkspacePresetActivationResult` enthält `partial_activation` und `compatibility_report` für Overlay/Diagnostics.

---

## 5. Relevante Dateien

| Bereich | Datei |
|---------|--------|
| Kompatibilität | `app/workspace_presets/preset_compatibility.py` |
| Start-Hooks | `app/workspace_presets/preset_startup.py` |
| Bundle + GUI/Theme-Sync | `app/workspace_presets/preset_state.py`, `app/workspace_presets/preset_activation.py` |
| QSettings-Zentralisierung | `app/gui_bootstrap.py` (`read`/`write` preferred GUI über `product_qsettings`) |
| Launcher | `run_gui_shell.py`, `run_qml_shell.py` |
| Shell | `app/gui/shell/main_window.py` |
| Overlay | `app/global_overlay/overlay_dialogs.py`, `app/workspace_presets/workspace_preset_port.py` |
| Settings (read-only) | `app/gui/domains/settings/categories/workspace_category.py` |

---

## 6. Tests

`tests/workspace_presets/test_workspace_preset_slice5_product_integration.py` und bestehende Slice-2–4-Tests (angepasst: gemeinsames `product_qsettings`-Ini für isolierte Läufe).

---

## 7. Nicht Teil von Slice 5

Preset-Editor, User-Custom-Presets, Import/Export, Shortcuts — bewusst ausgeschlossen (siehe Produkt-Slice-Ziel).

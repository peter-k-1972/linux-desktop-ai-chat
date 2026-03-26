# Hybrid-Segmente — governed transition

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **Übergangs**-Governance — Hybrid ist **kein** dauerhafter Architekturzustand und **kein** Freifahrtschein für neue `app.gui.*`-Kopplung.  
**Kanonische Segment-Landkarte:** [`PACKAGE_MAP.md`](PACKAGE_MAP.md).  
**Maschinenlesbarer Hybrid-Katalog:** `HYBRID_PRODUCT_SEGMENTS` in `tests/architecture/segment_dependency_rules.py` (Vertrags-Tests in `test_package_map_contract.py`).  
**Segment-AST (pauschales `(segment, gui)`):** `segment_dependency_rules.py` — für die genannten fünf Segmente **nicht** pauschal `→ gui` gesperrt; **kein** zusätzlicher AST-Whitelist-Guard für Hybrid-Importe (bewusst schlank gehalten).

---

## 1. Gui-nahe Root-Brücken (Querschnitt)

Diese Module liegen unter `app/*.py` (nicht `app/gui/`), werden aber wie eine **Produkt-Grenzschicht** genutzt — Hybrid-Segmente dürfen sich hieran orientieren, solange die jeweiligen **tolerierten** Welten eingehalten werden:

| Modul | Rolle (kurz) |
|--------|----------------|
| `app.gui_registry` | GUI-IDs, Deskriptoren, Repo-Pfad |
| `app.gui_bootstrap` | QSettings-Produktkeys, Safe-Mode-Flags, `argv`-Hilfen, Qt-App-Lifecycle-Hooks |
| `app.gui_capabilities` | Fähigkeits-Matrix pro GUI-ID |

Weitere Root-Dateien mit `gui`-Präfix (z. B. `gui_smoke_harness.py`, `gui_smoke_constants.py`): bei neuen Kopplungen aus Hybrid-Segmenten in dieses Modell einordnen oder explizit im Architektur-Review erweitern.

---

## 2. `global_overlay`

**Warum hybrid:** Produktstart, Multi-GUI-Registry und Theme-Rescue sitzen **zwischen** Root-Brücken und Teilen von `app.gui.themes` — fachlich notwendig, aber split-blockierend, solange Theme-Zugriff nicht gebündelt ist.

**Derzeit toleriert:** Importe über `app.gui_registry`, `app.gui_bootstrap`, `app.gui_capabilities` und die in den Port-Modellen vorgesehenen `app.gui.themes` / `app.gui.themes.*`-Kanten (siehe Ist-Auszug unten).

**Nicht weiter ausbreiten:** Keine neuen direkten Kanten zu `app.gui.domains.*`, `app.gui.shell.*`, `app.gui.workspace.*`, `app.gui.workbench.*`. Kein zusätzliches „quer durch die Shell“ ohne Port.

**Entkopplungsrichtung:** Theme und Status über **eine** Facade (`overlay_theme_port` o. ä.); Produkt-Orchestrierung bleibt bei Registry + Bootstrap + Capabilities — siehe [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §5.1.

### 2.1 Teilbäume (intern heterogen)

| Bereich | Dateien (Auszug) | Funktion |
|---------|------------------|----------|
| **Ports / Orchestrierung** | `overlay_gui_port.py`, `overlay_theme_port.py`, `overlay_rescue_port.py`, `overlay_status.py`, `product_launcher.py` | GUI-Auswahl, Theme-Kompatibilität, Rescue, Status |
| **Watchdog / Prozess** | `gui_launch_watchdog.py` | Startüberwachung, Safe Mode, QApplication |
| **Dialoge / Diagnose** | `overlay_dialogs.py`, `overlay_diagnostics.py` | Nutzerhinweise, Diagnose |

### 2.2 Ist-Importe (Referenz, gruppiert)

- **`app.gui_registry`:** durchgehend (Deskriptoren, Konstanten, `resolve_repo_root`, …).
- **`app.gui_bootstrap`:** QSettings/Safe-Mode/Theme-Defaults, `ensure_qsettings_core_application`, `product_qsettings`, Watchdog.
- **`app.gui_capabilities`:** `get_capabilities_for_gui_id`, `gui_supports` (Theme-Port).
- **`app.gui.themes` / `app.gui.themes.*`:** `get_theme_manager`, `theme_id_utils` (Rescue/Status/Theme-Port).

### 2.3 Ziel-Importwelten (Soll)

**Erlaubt (Übergang):** `app.gui_registry`, `app.gui_bootstrap`, `app.gui_capabilities`, `app.gui.themes.theme_id_utils`, `app.gui.themes` nur **gebündelt** über Port-Module statt verstreut `get_theme_manager`.

**Unerwünscht:** `app.gui.domains.*`, `app.gui.shell.*`, `app.gui.workspace.*`, `app.gui.workbench.*`.

---

## 3. `workspace_presets`

**Warum hybrid:** Produkt- und Presetzustand (QSettings, GUI-/Theme-IDs) muss mit Bootstrap/Registry und Theme-Validierung sprechen; **ein** bekanntes Ausreißer-Tier (`NavArea`) koppelt an die Shell-Navigation.

**Derzeit toleriert:** `app.gui_bootstrap`, `app.gui_registry`, `app.gui_capabilities`, `app.gui.themes.theme_id_utils`, `app.core.navigation` (Daten/Registry), sowie **`app.gui.navigation.nav_areas`** nur dort, wo heute `NavArea` benötigt wird.

**Nicht weiter ausbreiten:** Keine weiteren `app.gui.navigation.*`- oder `domains`/`shell`-Importe. Neue Startlogik nicht über wachsende PySide-Nav-Hierarchie lösen.

**Entkopplungsrichtung:** Navigationstyp als **ID/Contract** (`ui_contracts` oder `core.navigation`), nicht als Shell-Modul — siehe [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §5.2.

### 3.1 Teilbäume (intern heterogen)

| Bereich | Dateien (Auszug) | Funktion |
|---------|------------------|----------|
| **Persistenz / QSettings** | `preset_state.py` | Schreiben/Lesen Produktkeys (GUI/Theme/Preset) |
| **Validierung / Kompatibilität** | `preset_validation.py`, `preset_compatibility.py` | Registrierte GUIs, Theme-IDs |
| **Aktivierung / Grenzen** | `preset_activation.py`, `preset_restart_boundaries.py` | Safe Mode, Restart-Policy |
| **Start-Routing** | `preset_startup.py` | Start-Domain, Overrides — **koppelt `core.navigation` und GUI-Navigation** |

### 3.2 Ist-Importe (Referenz)

- **`app.gui_bootstrap`**, **`app.gui_registry`**, **`app.gui_capabilities`**, **`app.gui.themes.theme_id_utils`**
- **`app.gui.navigation.nav_areas`:** `NavArea` in `preset_startup.py` — dokumentierter Ausreißer.

### 3.3 Ziel-Importwelten (Soll)

**Erlaubt (Übergang):** Bootstrap, Registry, Capabilities, `theme_id_utils` wie oben.

**Ersetzen / nicht verbreitern:** `app.gui.navigation.*` → stabile IDs/Contracts statt PySide-Nav-Module.

**Unerwünscht:** `app.gui.domains.*`, `app.gui.shell.*`, `app.gui.workbench.*`.

---

## 4. `help`

**Warum hybrid:** Eingebettetes Hilfefenster ist **bewusst** UI-integriert und teilt Markdown-Komponenten mit der Shell — fachlich „Help-UI“, keine reine Library.

**Derzeit toleriert:** `app.gui.components.markdown_widgets`, `app.gui.components.doc_search_panel`, `app.gui.shared.markdown` sowie `app.help.*` und `app.resources.styles` wo bereits genutzt.

**Nicht weiter ausbreiten:** Keine neuen Importe aus `app.gui.domains.*`, `app.gui.shell.*`, `app.gui.workbench.*`.

**Entkopplungsrichtung:** Schmale Widget-/Render-Schicht oder Port-Modul; Inhalte über Contracts/DTOs — siehe [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §5.4.

### 4.1 Teilbäume

- **`help_window.py`:** eingebettetes Hilfefenster (Markdown, Suche).

### 4.2 Ist-Importe (Referenz)

- `app.gui.components.markdown_widgets`, `app.gui.components.doc_search_panel`, `app.gui.shared.markdown`

Weitere `app/help/*.py`: keine zusätzlichen `app.gui*`-Treffer außerhalb der tolerierten Schicht — bei Erweiterung Review.

---

## 5. `devtools`

**Warum hybrid:** Theme-Visualisierung und Kontrast-Tools **müssen** die kanonische Theme-Implementierung unter `app.gui.themes.*` sehen.

**Derzeit toleriert:** Ausschließlich Importe unter **`app.gui.themes.*`** (inkl. lazy `get_theme_manager` im Visualizer).

**Nicht weiter ausbreiten:** Jeder neue Import außerhalb `app.gui.themes` ist **Regressions-Blocker** für ein späteres Auslagern.

**Entkopplungsrichtung:** DevTools bleiben Theme-Diagnose-IDE; keine zweite Tür in Shell-Domänen — siehe [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §5.5.

### 5.1 Teilbäume

| Bereich | Dateien | Rolle |
|---------|---------|-------|
| **Theme-Visualisierung / QA** | `theme_visualizer_window.py`, `theme_preview_widgets.py`, `theme_token_groups.py`, `theme_contrast.py` | Token-, Kontrast-, Preview-Tools |

### 5.2 Ist-Importe (Referenz)

Unter **`app.gui.themes.*`**: u. a. `canonical_token_ids`, `definition`, `loader`, `registry`, `contrast`, `get_theme_manager`.

### 5.3 Ziel-Importwelten (Soll)

**Erlaubt (Übergang):** gesamter Unterbaum `app.gui.themes` (oder explizite Whitelist der genannten Submodule).

**Unerwünscht:** `app.gui.domains.*`, `app.gui.shell.*`, `app.gui.navigation.*`, `app.gui.workbench.*`.

---

## 6. `ui_application`

**Warum hybrid (Theme-Teil):** Presenter/Adapter brauchen **kanonische Theme-IDs**; bis ein Theme-Read-Port oder DTO existiert, ist eine **kleine**, dokumentierte Kopplung an `app.gui.themes` akzeptiert.  
**Nicht hybrid im Sinne „alles GUI“:** Der Großteil der Schicht arbeitet über `app.ui_contracts`, `app.services`, Domänenmodule — das folgt den normalen `FORBIDDEN_IMPORT_RULES` / Package-Guards. Hybrid-Status betrifft hier **v. a. die dokumentierte Theme-Brücke**, nicht eine generelle Erlaubnis für Shell-Widgets.

**Derzeit toleriert (Theme):** `app.gui.themes.get_theme_manager`, `app.gui.themes.theme_id_utils` in den dafür vorgesehenen Adaptern (z. B. Settings).

**Nicht weiter ausbreiten:** Keine neuen `app.gui.domains.*`, `app.gui.shell.*`, `app.gui.components.*` für Presenter-Zwecke.

**Entkopplungsrichtung:** Theme-Read-Port / Snapshot in `ui_contracts` oder Service-API — siehe [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §5.3.

### 6.1 Teilbäume (Auszug)

- **`adapters/service_settings_adapter.py`:** Bridge Presenter ↔ Services (Settings); enthält die dokumentierte Theme-Kopplung.

### 6.2 Ist-Importe (Theme — Referenz)

- `app.gui.themes.get_theme_manager`
- `app.gui.themes.theme_id_utils.theme_id_to_legacy_light_dark`

---

## 7. Guard- und Metadaten-Modell (aktueller Stand)

1. **Hybrid-Katalog:** `HYBRID_PRODUCT_SEGMENTS` in `segment_dependency_rules.py` — bei neuer Hybrid-Einstufung **PACKAGE_MAP**, diese Notiz und die Konstante gemeinsam anpassen; Vertrags-Tests in `test_package_map_contract.py`.
2. **Segment-Verbote:** unverändert `FORBIDDEN_SEGMENT_EDGES` + `SEGMENT_IMPORT_EXCEPTIONS` (kein zweiter AST-Guard für Hybrid-Allowlists).
3. **Vollständiger Segment-Katalog:** `KNOWN_PRODUCT_SEGMENTS` = `TARGET_PACKAGES` ∪ `EXTENDED_APP_TOP_PACKAGES` (gleicher Test).

---

## 8. Kurzfassung

| Segment | Dominante Kopplung | Engster Fokus | Größtes Risiko bei Verletzung |
|---------|-------------------|---------------|-------------------------------|
| `global_overlay` | Registry + Bootstrap + Capabilities + `themes` | Orchestrierungs-Ports, Theme gebündelt | Verstreute `get_theme_manager`-Calls |
| `workspace_presets` | Bootstrap + Registry + Capabilities + `theme_id_utils` + **`navigation.nav_areas`** | Produktkeys + Contracts für Start | Ausbreitung `app.gui.navigation` / `domains` |
| `help` | `components` + `shared.markdown` | Schmale Widget-/Render-Schicht | Zugriff auf `shell` / `domains` |
| `devtools` | nur `gui.themes.*` | Theme-Subsystem bleibt Grenze | Import außerhalb `themes` |
| `ui_application` | `gui.themes` (Theme-IDs in Adaptern) | Theme-Read-Port / DTO | Zusätzliche Shell-Widgets / Domains |

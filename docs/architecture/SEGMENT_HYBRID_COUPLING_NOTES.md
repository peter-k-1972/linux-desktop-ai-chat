# Hybrid-Segmente — governed transition

**Projekt:** Linux Desktop Chat  
**Status:** Verbindliche **Übergangs**-Governance — Hybrid ist **kein** dauerhafter Architekturzustand und **kein** Freifahrtschein für neue `app.gui.*`-Kopplung.  
**Kanonische Segment-Landkarte:** [`PACKAGE_MAP.md`](PACKAGE_MAP.md).  
**Maschinenlesbarer Hybrid-Katalog:** `HYBRID_PRODUCT_SEGMENTS` in `tests/architecture/segment_dependency_rules.py` (Vertrags-Tests in `test_package_map_contract.py`).  
**Segment-AST (pauschales `(segment, gui)`):** `segment_dependency_rules.py` — **`ui_application`**, **`global_overlay`** und **`workspace_presets`** sind jetzt auf **`(segment, gui)` verboten** verschärft; **`help`** und **`devtools`** bleiben Hybrid-Segmente mit schmalem, dokumentiertem GUI-Rand.

---

## 1. Kanonischer Produktvertrag (Querschnitt)

Die früheren Root-Brücken `app.gui_registry`, `app.gui_bootstrap` und `app.gui_capabilities` sind entfernt. Der kanonische Produktvertrag für Hybrid-Segmente liegt jetzt ausschließlich unter `app.core.startup_contract`; Rückfälle auf die entfernten Modulpfade werden per Guard verhindert.

Weitere Root-Dateien mit `gui`-Präfix (z. B. `gui_smoke_harness.py`, `gui_smoke_constants.py`) sind keine Ersatz-Facades für Produktstart-/Theme-Verhalten; neue Kopplungen aus Hybrid-Segmenten dorthin brauchen weiterhin ein explizites Architektur-Review.

---

## 2. `global_overlay`

**Warum hybrid:** Produktstart, Multi-GUI-Registry und Theme-Rescue sitzen **zwischen** Root-Brücken und Theme-/Statuslogik. Der Split-Blocker war die verteilte Theme-/Registry-Kopplung.

**Stand nach Entkopplung:** Direkte `app.gui.*`-Importe im Segment sind entfernt. Root-Brücken wurden aus dem Segment entfernt; `global_overlay` nutzt jetzt `app.core.startup_contract` plus Overlay-spezifische Ports (`overlay_gui_port.py`, `overlay_theme_port.py`, `overlay_rescue_port.py`).

**Nicht weiter ausbreiten:** Keine neuen direkten Kanten zu `app.gui.domains.*`, `app.gui.shell.*`, `app.gui.workspace.*`, `app.gui.workbench.*`. Kein zusätzliches „quer durch die Shell“ ohne Port.

**Entkopplungsrichtung:** Theme und Status über Overlay-Ports; produktweite GUI-/Theme-/Safe-Mode-Metadaten über `app.core.startup_contract` — siehe [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §5.1.

### 2.1 Teilbäume (intern heterogen)

| Bereich | Dateien (Auszug) | Funktion |
|---------|------------------|----------|
| **Ports / Orchestrierung** | `overlay_gui_port.py`, `overlay_theme_port.py`, `overlay_rescue_port.py`, `overlay_status.py`, `product_launcher.py` | GUI-Auswahl, Theme-Kompatibilität, Rescue, Status |
| **Watchdog / Prozess** | `gui_launch_watchdog.py` | Startüberwachung, Safe Mode, QApplication |
| **Dialoge / Diagnose** | `overlay_dialogs.py`, `overlay_diagnostics.py` | Nutzerhinweise, Diagnose |

### 2.2 Ist-Importe (Referenz, gruppiert)

- **Direkt auf `app.gui.*`:** keine.
- **Produktvertrag:** `app.core.startup_contract`, `gui_launch_watchdog.py`.
- **Theme-Zugriff:** nur noch über `overlay_theme_port.py` plus Core-Contract.

### 2.3 Ziel-Importwelten (Soll)

**Erlaubt (Übergang):** `app.core.startup_contract`; Theme nur über `overlay_theme_port.py`.

**Unerwünscht:** `app.gui.domains.*`, `app.gui.shell.*`, `app.gui.workspace.*`, `app.gui.workbench.*`.

---

## 3. `workspace_presets`

**Warum hybrid:** Produkt- und Presetzustand (QSettings, GUI-/Theme-IDs) muss mit Bootstrap/Registry und Theme-Validierung sprechen; früher blockierte zusätzlich `app.gui.navigation.nav_areas`.

**Stand nach Entkopplung:** Direkte `app.gui.*`-Importe im Segment sind entfernt. Root-Brücken wurden entfernt; `workspace_presets` nutzt direkt `app.core.startup_contract`, Navigation läuft über `app.core.navigation`.

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

- **Direkt auf `app.gui.*`:** keine.
- **Produktvertrag:** `app.core.startup_contract`.
- **Navigation:** `preset_startup.py` nutzt `app.core.navigation.nav_areas.NavArea`.

### 3.3 Ziel-Importwelten (Soll)

**Erlaubt (Übergang):** `app.core.startup_contract`; Navigation über `app.core.navigation`.

**Ersetzt:** `app.gui.navigation.nav_areas` → `app.core.navigation.nav_areas`.

**Unerwünscht:** `app.gui.domains.*`, `app.gui.shell.*`, `app.gui.workbench.*`.

---

## 4. `help`

**Warum hybrid:** Eingebettetes Hilfefenster ist **bewusst** UI-integriert und teilt Markdown-Komponenten mit der Shell — fachlich „Help-UI“, keine reine Library.

**Derzeit toleriert:** nur `app.help.ui_components` darf `app.gui.components.markdown_widgets`, `app.gui.components.doc_search_panel`, `app.gui.shared.markdown` importieren; übrige Help-Module bleiben auf `app.help.*` / `app.resources.styles`.

**Nicht weiter ausbreiten:** Keine neuen Importe aus `app.gui.domains.*`, `app.gui.shell.*`, `app.gui.workbench.*`.

**Entkopplungsrichtung:** Schmale Widget-/Render-Schicht oder Port-Modul; Inhalte über Contracts/DTOs — siehe [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §5.4.

### 4.1 Teilbäume

- **`help_window.py`:** eingebettetes Hilfefenster (Markdown, Suche).

### 4.2 Ist-Importe (Referenz)

- `app.help.ui_components` → `app.gui.components.markdown_widgets`, `app.gui.components.doc_search_panel`, `app.gui.shared.markdown`

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

**Warum hybrid (Theme-Teil):** Presenter/Adapter brauchen weiterhin Produkt-Theme-Metadaten, aber die direkte `app.gui.themes`-Kopplung wurde entfernt.  
**Nicht hybrid im Sinne „alles GUI“:** Der Großteil der Schicht arbeitet über `app.ui_contracts`, `app.services`, Domänenmodule; die verbleibende Grenze ist jetzt `app.core.startup_contract` als schmale Produkt-Theme- und Startup-Flaeche.

**Stand nach Entkopplung:** `service_settings_adapter.py` nutzt `app.core.startup_contract` (`list_registered_product_themes`, `current_product_theme_id`, `product_theme_id_registered`, `product_theme_id_to_legacy_bucket`). Direkte `app.gui.*`-Importe und Root-GUI-Brücken im Segment sind verboten.

**Nicht weiter ausbreiten:** Keine neuen `app.gui.domains.*`, `app.gui.shell.*`, `app.gui.components.*` für Presenter-Zwecke.

**Entkopplungsrichtung:** Theme-Read-Port / Snapshot in `ui_contracts` oder Service-API — siehe [`PACKAGE_SPLIT_PLAN.md`](PACKAGE_SPLIT_PLAN.md) §5.3.

### 6.1 Teilbäume (Auszug)

- **`adapters/service_settings_adapter.py`:** Bridge Presenter ↔ Services (Settings); enthält die dokumentierte Theme-Kopplung.

### 6.2 Ist-Importe (Theme — Referenz)

- **Direkt auf `app.gui.*`:** keine.
- **Produkt-Theme-/Startup-Contract:** `app.core.startup_contract` aus `adapters/service_settings_adapter.py`.

---

## 7. Guard- und Metadaten-Modell (aktueller Stand)

1. **Hybrid-Katalog:** `HYBRID_PRODUCT_SEGMENTS` in `segment_dependency_rules.py` — bei neuer Hybrid-Einstufung **PACKAGE_MAP**, diese Notiz und die Konstante gemeinsam anpassen; Vertrags-Tests in `test_package_map_contract.py`.
2. **Segment-Verbote:** `global_overlay`, `workspace_presets`, `ui_application` → `gui` jetzt verboten; `help` und `devtools` zusätzlich durch `test_ui_layer_guardrails.py` auf schmale GUI-Ränder begrenzt.
3. **Vollständiger Segment-Katalog:** `KNOWN_PRODUCT_SEGMENTS` = `TARGET_PACKAGES` ∪ `EXTENDED_APP_TOP_PACKAGES` (gleicher Test).

---

## 8. Kurzfassung

| Segment | Dominante Kopplung | Engster Fokus | Größtes Risiko bei Verletzung |
|---------|-------------------|---------------|-------------------------------|
| `global_overlay` | `app.core.startup_contract` + Overlay-Ports | Orchestrierungs-Ports, Theme gebündelt | neue Direktimporte an `app.gui.domains` / Shell |
| `workspace_presets` | `app.core.startup_contract` + `core.navigation` | Produktkeys + Startnavigation ohne Shell-Modul | neue Direktimporte an `app.gui.navigation` / `domains` |
| `help` | `components` + `shared.markdown` | Schmale Widget-/Render-Schicht | Zugriff auf `shell` / `domains` |
| `devtools` | nur `gui.themes.*` | Theme-Subsystem bleibt Grenze | Import außerhalb `themes` |
| `ui_application` | `app.core.startup_contract` | Theme-Read-Port / DTO | Rückfall auf direkte `app.gui.*`-Importe oder Root-GUI-Brücken |

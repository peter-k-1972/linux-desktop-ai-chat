# Hybrid-Segmente und Kopplung (Ist / Soll-Skizze — kein Guard)

**Projekt:** Linux Desktop Chat  
**Status:** Konkretisierte Architektur-Notiz — **keine** pytest-Implementierung in diesem Dokument  
**Bezug:** `tests/architecture/segment_dependency_rules.py` (pauschales `(segment, gui)` greift hier **nicht**), [`PACKAGE_MAP.md`](PACKAGE_MAP.md) § Segment Dependency Rules

---

## 1. Gui-nahe Root-Brücken (Querschnitt)

Diese Module liegen unter `app/*.py` (nicht `app/gui/`), werden aber wie eine **Produkt-Grenzschicht** genutzt:

| Modul | Rolle (kurz) |
|--------|----------------|
| `app.gui_registry` | GUI-IDs, Deskriptoren, Repo-Pfad |
| `app.gui_bootstrap` | QSettings-Produktkeys, Safe-Mode-Flags, `argv`-Hilfen, Qt-App-Lifecycle-Hooks |
| `app.gui_capabilities` | Fähigkeits-Matrix pro GUI-ID |

Weitere Root-Dateien mit `gui`-Präfix (z. B. `gui_smoke_harness.py`, `gui_smoke_constants.py`): derzeit **ohne** direkte Importe aus den unten genannten Hybrid-Segmenten im Ist-Scan; bei neuen Kopplungen ebenfalls in dieses Modell einordnen.

---

## 2. `global_overlay`

### 2.1 Teilbäume (intern heterogen)

| Bereich | Dateien (Auszug) | Funktion |
|---------|------------------|----------|
| **Ports / Orchestrierung** | `overlay_gui_port.py`, `overlay_theme_port.py`, `overlay_rescue_port.py`, `overlay_status.py`, `product_launcher.py` | GUI-Auswahl, Theme-Kompatibilität, Rescue, Status |
| **Watchdog / Prozess** | `gui_launch_watchdog.py` | Startüberwachung, Safe Mode, QApplication |
| **Dialoge / Diagnose** | `overlay_dialogs.py`, `overlay_diagnostics.py` | Nutzerhinweise, Diagnose |

### 2.2 Ist-Importe (gruppiert)

- **`app.gui_registry`:** durchgehend (Deskriptoren, Konstanten, `resolve_repo_root`, …).
- **`app.gui_bootstrap`:** QSettings/Safe-Mode/Theme-Defaults, `ensure_qsettings_core_application`, `product_qsettings`, Watchdog.
- **`app.gui_capabilities`:** `get_capabilities_for_gui_id`, `gui_supports` (Theme-Port).
- **`app.gui.themes` / `app.gui.themes.*`:** `get_theme_manager`, `theme_id_utils` (Rescue/Status/Theme-Port).

### 2.3 Bewertung

| Kategorie | Einschätzung |
|-----------|--------------|
| Registry / Bootstrap / Capabilities | **Fachlich legitim** — Kern des Multi-GUI-/Produktstarts. |
| `app.gui.themes` | **Legitim** für Theme-Rescue und Registry-Kohärenz; **perspektivisch eng** über `overlay_theme_port` bündeln, damit nicht jede Datei den Theme-Manager direkt lädt. |

### 2.4 Soll-Skizze (Präfixe)

**Erlaubt (Zielbild Hybrid-Guard, später):**

- `app.gui_registry` (gesamtes Paket / explizite API)
- `app.gui_bootstrap`
- `app.gui_capabilities`
- `app.gui.themes.theme_id_utils`
- `app.gui.themes` — nur über **eine** klare Facade-Schicht (`overlay_theme_port` o. ä.) statt verstreut `get_theme_manager`

**Perspektivisch unerwünscht:**

- `app.gui.domains.*`
- `app.gui.shell.*`
- `app.gui.workspace.*`, `app.gui.workbench.*`

**Zielbild:** Produkt-Orchestrierung bleibt über **Registry + Bootstrap + Capabilities**; Theme-Zugriff über **einen Port**; keine Shell-Domänen-Logik im Overlay.

---

## 3. `workspace_presets`

### 3.1 Teilbäume (intern heterogen)

| Bereich | Dateien (Auszug) | Funktion |
|---------|------------------|----------|
| **Persistenz / QSettings** | `preset_state.py` | Schreiben/Lesen Produktkeys (GUI/Theme/Preset) |
| **Validierung / Kompatibilität** | `preset_validation.py`, `preset_compatibility.py` | Registrierte GUIs, Theme-IDs |
| **Aktivierung / Grenzen** | `preset_activation.py`, `preset_restart_boundaries.py` | Safe Mode, Restart-Policy |
| **Start-Routing** | `preset_startup.py` | Start-Domain, Overrides — **koppelt `core.navigation` und GUI-Navigation** |

### 3.2 Ist-Importe

- **`app.gui_bootstrap`:** `product_qsettings`, Schreibfunktionen für GUI/Theme, Safe-Mode/Argv-Hilfen.
- **`app.gui_registry`:** Listen/Defaults für GUI-IDs.
- **`app.gui_capabilities`:** `gui_supports`.
- **`app.gui.themes.theme_id_utils`:** `is_registered_theme_id`, `theme_id_to_legacy_light_dark` (Kompatibilität + dynamischer Import in Validierung).
- **`app.gui.navigation.nav_areas`:** **`NavArea`** in `preset_startup.py` — **Ausreißer**: Shell-Navigationstyp im Preset-Startpfad (heterogen).

### 3.3 Bewertung

| Import | Einschätzung |
|--------|--------------|
| Bootstrap / Registry / Capabilities / `theme_id_utils` | **Legitim** — Produktzustand und Theme-Gültigkeit. |
| `app.gui.navigation.nav_areas` | **Heute nachvollziehbar** (Start-Domain), aber **breiter als Bootstrap**; **perspektivisch riskant**, wenn weitere `navigation`- oder `domains`-Importe dazukommen. |

### 3.4 Soll-Skizze (Präfixe)

**Erlaubt (später):**

- `app.gui_bootstrap`
- `app.gui_registry`
- `app.gui_capabilities`
- `app.gui.themes.theme_id_utils`

**Perspektivisch unerwünscht / ersetzen:**

- `app.gui.navigation.*` → **Ziel:** neutraler Typ oder Contract unter `ui_contracts` / `core.navigation` (bereits `get_entry` genutzt), sodass Presets nicht die PySide-Nav-Modulhierarchie kennen.

**Unerwünscht allgemein:** `app.gui.domains.*`, `app.gui.shell.*`, `app.gui.workbench.*`.

**Zielbild:** Presets = **Produkt- und Persistenzschicht**; Navigation nur über **stabile IDs/Contracts**, nicht über wachsende Shell-Imports.

---

## 4. `help`

### 4.1 Teilbäume

- **`help_window.py`:** eingebettetes Hilfefenster (Markdown, Suche).

### 4.2 Ist-Importe

- `app.gui.components.markdown_widgets` (`MarkdownDocumentView`)
- `app.gui.components.doc_search_panel` (`DocSearchPanel`)
- `app.gui.shared.markdown` (`markdown_to_html`)

Weitere `app/help/*.py`: **keine** weiteren `app.gui*`/`app.gui_*`-Treffer im Ist-Scan.

### 4.3 Bewertung

**Legitim:** Help ist **bewusst UI-integriert**; Wiederverwendung gemeinsamer Markdown-Komponenten vermeidet Duplikate.

**Risiko:** Wenn Help später `domains` oder `shell` importiert, wächst die Kopplung zur Haupt-Shell unnötig.

### 4.4 Soll-Skizze (Präfixe)

**Erlaubt (später):**

- `app.gui.components.markdown_widgets`
- `app.gui.components.doc_search_panel`
- `app.gui.shared.markdown` (bzw. ein dediziertes `help`- oder `markdown`-Port-Modul, das diese aufsaugt)

**Perspektivisch unerwünscht:**

- `app.gui.domains.*`
- `app.gui.shell.*`
- `app.gui.workbench.*`

**Zielbild:** **Schmale Widget-/Render-Schicht**; Inhalte und Navigation idealerweise über **Contracts** oder reine Daten-DTOs.

---

## 5. `devtools`

### 5.1 Teilbäume

| Bereich | Dateien | Rolle |
|---------|---------|--------|
| **Theme-Visualisierung / QA** | `theme_visualizer_window.py`, `theme_preview_widgets.py`, `theme_token_groups.py`, `theme_contrast.py` | Token-, Kontrast-, Preview-Tools |

### 5.2 Ist-Importe

Ausschließlich unter **`app.gui.themes.*`**:

- `canonical_token_ids`, `definition`, `loader`, `registry`, `contrast`, `get_theme_manager` (lazy in Visualizer).

### 5.3 Bewertung

**Legitim:** DevTools sind **Theme- und Rendering-Diagnose** — Kopplung an die kanonische Theme-Implementierung ist intendiert.

**Risiko:** Einzige in `devtools` erlaubte Welt darf nicht stillschweigend auf **gesamte** `app.gui` ausweiten.

### 5.4 Soll-Skizze (Präfixe)

**Erlaubt (später):**

- `app.gui.themes` (Untermodulbaum als Ganzes **oder** explizite Whitelist der genannten Submodule)

**Perspektivisch unerwünscht:**

- `app.gui.domains.*`
- `app.gui.shell.*`
- `app.gui.navigation.*`
- `app.gui.workbench.*`

**Zielbild:** DevTools bleiben **Theme-IDE** für das Produkt; keine zweite Einstiegstür in die Shell-Domänen.

---

## 6. `ui_application`

### 6.1 Teilbäume

- **`adapters/service_settings_adapter.py`:** Bridge Presenter ↔ Services (Settings).

### 6.2 Ist-Importe

- `app.gui.themes.get_theme_manager`
- `app.gui.themes.theme_id_utils.theme_id_to_legacy_light_dark`

### 6.3 Bewertung

**Legitim (MVP):** Theme-IDs für Settings-UI müssen mit **kanonischer Theme-Registry** übereinstimmen.

**Perspektivisch enger:** Theme-Zustand über **Port** aus `ui_contracts` oder schmale **Theme-Read-API** statt direktem `get_theme_manager`, um Presenter von Qt-Singleton zu entkoppeln.

### 6.4 Soll-Skizze (Präfixe)

**Erlaubt (Übergang):**

- `app.gui.themes.theme_id_utils`
- `app.gui.themes` — nur so lange, bis ein **ThemeSnapshot**/**ReadPort** existiert

**Perspektivisch unerwünscht:**

- `app.gui.domains.*`
- `app.gui.shell.*`
- `app.gui.components.*` (Presenter sollten nicht frei Widgets aus der Shell holen)

**Zielbild:** **Presenter/Adapter** konsumieren **Contracts + Ports**; Theme nur als **DTO oder Service-API**.

---

## 7. Mögliche spätere Guard-Strategie (nur Konzept)

1. **Zweiter Regelblock** (eigenes Modul, z. B. `hybrid_segment_import_rules.py`) mit Struktur:
   - Pro Segment: `allowed_prefixes: tuple[str, ...]`, optional `denied_prefixes: tuple[str, ...]`.
2. **AST** wie beim Segment-Guard, aber Filter nur auf Dateien unter `app/<hybrid>/`.
3. **Keine** pauschale `(segment, gui)`-Kante; Verletzungen = Import-Präfix nicht in Allowlist **oder** explizit in Denylist.
4. **Schrittweise:** zuerst ein Segment (z. B. `devtools` — engste Welt), dann `help`, dann `global_overlay`/`workspace_presets` nach Klärung von `NavArea`.

---

## 8. Kurzfassung Tabelle

| Segment | Dominante Ist-Kopplung | Engster Soll-Fokus | Größtes perspektivisches Risiko |
|---------|------------------------|-------------------|----------------------------------|
| `global_overlay` | Registry + Bootstrap + Capabilities + `themes` | Orchestrierungs-Ports, Theme nur geführt | Verstreute `get_theme_manager`-Calls |
| `workspace_presets` | Bootstrap + Registry + Capabilities + `theme_id_utils` + **`navigation.nav_areas`** | Produktkeys + Contracts für Start | Ausbreitung `app.gui.navigation` / `domains` |
| `help` | `components` + `shared.markdown` | Schmale Widget-/Render-Schicht | Zugriff auf `shell` / `domains` |
| `devtools` | nur `gui.themes.*` | Theme-Subsystem bleibt Grenze | Jeder Import außerhalb `themes` |
| `ui_application` | `gui.themes` (Adapter) | Theme-Read-Port / DTO | Direkte Shell-Widgets |

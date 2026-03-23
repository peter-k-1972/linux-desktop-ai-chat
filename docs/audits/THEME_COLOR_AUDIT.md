# Theme- und Farb-Audit — Linux Desktop Chat / Obsidian Core GUI

**Stand der Analyse:** automatisierte und manuelle Durchsicht des Repos (ohne Code-Umstellung).  
**Messungen:** Python 3, Pfad `app/`; QSS unter `assets/themes/` und Duplikaten; ergänzend `tests/` wo farbbezogen.

---

## 0. Checkpoint Phase 0 — Ist-Stand (aktualisiert)

*Dieser Abschnitt ergänzt die ursprüngliche Analyse um eine kurze, wiederholbare Architektur- und QA-Sicht. Detaillierte Zahlen in §1 können sich leicht unterscheiden, wenn sich das Repo ändert.*

| Thema | Ist (kanonisch) |
|--------|-----------------|
| **Zentrale Code-Basis** | `app/gui/themes/` — `ThemeManager`, `ThemeRegistry`, `ThemeDefinition`, `ThemeTokens`, `loader.load_stylesheet`, `canonical_token_ids` / `resolved_spec_tokens` |
| **QSS (Laufzeit)** | `assets/themes/base/{base,shell,workbench}.qss` — Platzhalter `{{…}}`, keine Roh-Hex in diesen drei Dateien |
| **Theme-IDs** | `light_default`, `dark_default`, `workbench` (Registry + semantische Profile) |
| **Legacy-Pfad** | `app/resources/styles.py` (`get_stylesheet` / `get_theme_colors`) — weiterhin von Teilen der GUI und Legacy-`app/main.py` genutzt |
| **Theme Guard** | `tools/theme_guard.py` — Exit 0/1; erlaubte Pfade in `ALLOW_*`; **Gesamtverstöße im Repo derzeit hoch** (v. a. `app/gui/**`, Skripte, Tests — siehe Guard-Lauf) |
| **Theme Visualizer** | `tools/theme_visualizer.py`, `app/devtools/theme_visualizer_window.py`; Shell-Integration gated: `LINUX_DESKTOP_CHAT_DEVTOOLS=1` |
| **Doku-SoT** | Dieses Audit, `docs/design/THEME_TARGET_MODEL.md`, `THEME_TOKEN_SPEC.md`, `THEME_MIGRATION_PLAN.md`, `THEME_CONTRAST_RULES.md` |
| **Migrations-Realität** | Vollständige Entfernung harter Farben aus Produktivcode ist **nicht** abgeschlossen; siehe `THEME_MIGRATION_FINAL_REPORT.md` (Repo-Root) |

**Andockpunkte für weitere Migration:** `ThemeManager.get_tokens()` / `color()`, QSS-Erweiterung in `assets/themes/base/`, schrittweiser Ersatz von `get_theme_colors` durch Token-Map, Entfernung Duplikat-`app/gui/themes/base/*.qss` nach Abschluss der Vereinheitlichung.

---

## 1. Executive Summary

| Metrik | Wert | Quelle / Methode |
|--------|------|------------------|
| **Aktive token-basierte QSS-Dateien (Laufzeit)** | 3 | `assets/themes/base/base.qss`, `shell.qss`, `workbench.qss` — geladen via `app/gui/themes/loader.py` → `get_themes_dir()` = `assets/themes` (`app/utils/paths.py`) |
| **Roh-Hex in diesen aktiven QSS** | 0 | Alle Farben als `{{color_*}}` bzw. `{{fg_*}}`-Aliases; Verifikation per Suche |
| **Python-Dateien unter `app/` mit mindestens einem Hex-Literal** | 153 | Skript: Regex `#([0-9A-Fa-f]{3}\|[0-9A-Fa-f]{6}\|[0-9A-Fa-f]{8})` |
| **Hex-Vorkommen gesamt in `app/**/*.py`** | 1199 | gleiches Skript (inkl. Strings in `setStyleSheet`, Fallbacks, Profile) |
| **`setStyleSheet(`-Aufrufe in `app/**/*.py`** | 722 | Zählung per Regex |
| **Zentrale Theme-Einstiegspunkte (logisch)** | 2 parallele Systeme | siehe Abschnitt 2 — **Fragmentierung: hoch** |

**Kernaussage:** Es existiert ein **modernes Token-QSS-System** (`ThemeManager` + `SemanticPalette` → `ThemeTokens` → Substitution in QSS), das die **Shell** (`run_gui_shell.py`) steuert. Parallel existiert ein **Legacy-Pfad** (`app/resources/styles.py`: `get_stylesheet` / `get_theme_colors`) mit **eigenen Farbtabellen** und **nur binärer Light/Dark-Semantik**, den viele Widgets und Hilfe-Komponenten noch nutzen. Zusätzlich sind **hunderte widget-lokale Styles** mit Tailwind-ähnlichen Hex-Werten** verteilt — teils hell-optimiert — und damit **nicht** an `light_default` / `dark_default` / `workbench` gekoppelt.

---

## 2. Theme-Architektur — Ist-Zustand

### 2.1 Produktiver Shell-Pfad (kanonisch für Haupt-GUI)

1. **Start:** `run_gui_shell.py` → `get_theme_manager().set_theme(theme_id)` (`light_default`, `dark_default`, `workbench`).
2. **Registry:** `app/gui/themes/registry.py` → `ThemeDefinition` mit `ThemeTokens` aus `semantic_palette_to_theme_tokens`.
3. **Semantische Quelle:** `app/gui/themes/builtin_semantic_profiles.py` (`light_semantic_profile`, `dark_semantic_profile`, `workbench_semantic_profile`) + `app/gui/themes/semantic_palette.py` (`SemanticPalette`).
4. **Zusatzauflösung:** `app/gui/themes/palette_resolve.py` überschreibt u. a. `color_monitoring_*` und `color_qa_nav_*` **profilabhängig** mit festen Hex-Werten (zweite Farbebene neben SemanticPalette).
5. **Flaches Dict für QSS:** `ThemeDefinition.get_tokens_dict()` → `merge_semantic_aliases_for_qss` (`fg_primary`, `bg_app`, … als Aliase).
6. **Anwendung:** `ThemeManager.set_theme` → `load_stylesheet` → `QApplication.setStyleSheet(combined_qss)`.
7. **Kontrast-Hilfe:** `app/gui/themes/contrast.py` (WCAG-Rechner; primär für Tests/Validierung).

**Kette:** `SemanticPalette` (+ domain override) → `ThemeTokens` → `{{token}}` in QSS → globales App-Stylesheet.

### 2.2 Legacy-Pfad (Chat-orientiert, weiterhin referenziert)

- **`app/resources/styles.py`**
  - `get_stylesheet(theme: str)` baut **komplettes QSS in Python-Strings** für `theme in ("light", "dark")` — **kein** Bezug zu `ThemeManager` oder `theme_id`.
  - `get_theme_colors(theme)` liefert kleines Dict (`fg`, `muted`, `accent`, `top_bar_bg`, `top_bar_border`) — ebenfalls nur light/dark.
  - `ModernStyle` Klasse mit statischen Hex-Konstanten (Kompatibilität).
- **Verwendung von `get_stylesheet`:** ausschließlich **`app/main.py`** (explizit als **LEGACY** markiert; nicht Standard-Start).
- **Verwendung von `get_theme_colors`:** u. a. `command_center_view.py`, alle `app/gui/domains/command_center/*_view.py`, `help_window.py`, `guided_tour.py`, `chat_message_widget.py`, `chat_side_panel.py`, `chat_header_widget.py`, `model_settings_panel.py`, `agent_avatar_widget.py`, Runtime-Debug-Views (`agent_activity_view.py`, `task_graph_view.py`, …), `legacy/message_widget.py`.

### 2.3 Mapping Theme-ID → Legacy-Bucket

- **`app/gui/themes/theme_id_utils.py` — `theme_id_to_legacy_light_dark`:** nur `light_default` → `"light"`; **`dark_default` und `workbench` → beide `"dark"`**.
- **Folge:** Alle Stellen mit `get_theme_colors("dark")` können **Workbench visuell nicht unterscheiden** (gleicher Farbbucket), während globales QSS workbench-spezifisch ist → **systematische Inkonsistenz** zwischen Shell-QSS und Inline-Styles.

### 2.4 Persistenz

- **`app/core/config/settings.py`:** `theme_id` normalisiert über `is_registered_theme_id`; Legacy-Feld `theme` wird aus `theme_id` zurückgespiegel (`theme_id_to_legacy_light_dark`).

### 2.5 Icons

- **`app/gui/icons/manager.py`:** SVG-Färbung via `currentColor` → Hex aus `get_theme_manager().get_tokens()` (`color_token`), Fallback-Hex `#1f2937` / `#cbd5e1`.

### 2.6 Duplikate und verwaiste QSS

| Pfad | Rolle |
|------|--------|
| `assets/themes/base/*.qss` | **von Loader verwendet** |
| `app/gui/themes/base/*.qss` | Kopien; `base.qss` **identisch** zu `assets`; **`shell.qss` und `workbench.qss` weichen ab** (lokal geprüft mit `diff`) → **Drift-Risiko** bei manueller Bearbeitung der falschen Kopie |
| `assets/themes/legacy/light.qss`, `dark.qss` | Hardcoded Hex; **nicht** von `loader.py` eingebunden |
| `app/resources/light.qss`, `dark.qss` | Enthalten rgba/Gradients; **keine Python-Referenz** im Repo (Suche nach Pfad/Dateiname) → **verwaiste Duplikate** relativ zu Dokumentation (`docs/05_developer_guide/PHASE1_CHANGES.md` erwähnt Migration) |
| `app/resources.qrc` | nur Legacy-SVG-Icons, **keine** QSS |

---

## 3. Inventarliste — Farbquellen (strukturiert)

*Vollständige Rohliste aller Hex-Stellen in Python:* `docs/audits/THEME_COLOR_INVENTORY.csv` (1199 Zeilen, eine pro Vorkommen in `app/**/*.py`).

### 3.1 Zentrale Theme-Definition (semantisch + Token-Defaults)

| Datei | Symbol / Artefakt | Art | Inhalt / Regel |
|-------|-------------------|-----|----------------|
| `app/gui/themes/semantic_palette.py` | `SemanticPalette` | semantische Rollen (Dataclass-Felder) | keine Literalfarben — Schema |
| `app/gui/themes/builtin_semantic_profiles.py` | `light_semantic_profile`, `dark_semantic_profile`, `workbench_semantic_profile` | **zentrale Theme-Definition** | je ~34+ Hex pro Profil |
| `app/gui/themes/tokens.py` | `ThemeTokens` | **Default-Tokens** + Schema | Default-Hex für alle `color_*`, Schrift, Abstand |
| `app/gui/themes/palette_resolve.py` | `_domain_monitoring_qa`, `semantic_palette_to_theme_tokens` | **profilabhängige Overrides** + Mapping | feste Hex für Monitoring/QA-Navigation |
| `app/gui/themes/registry.py` | `ThemeRegistry._load_builtin_themes` | Registrierung | 3 built-in IDs |
| `app/gui/themes/definition.py` | `ThemeDefinition.get_tokens_dict` | Aggregation | ruft `merge_semantic_aliases_for_qss` |
| `app/gui/themes/manager.py` | `ThemeManager` | **Einstieg Anwendung** | `set_theme` → global QSS |
| `app/gui/themes/loader.py` | `load_stylesheet` | QSS-Zusammenbau | 3 Dateien aus `assets/themes/base/` |

**Bewertung:** Das ist die **tragfähigste** zentrale Schicht; Domain-Overrides in `palette_resolve` sind eine **zweite** Definitionsstelle (bewusst, aber zu dokumentieren).

### 3.2 Legacy-QSS-Generator (nicht Token-QSS)

| Datei | Funktion | Art |
|-------|----------|-----|
| `app/resources/styles.py` | `get_stylesheet`, `_light_stylesheet`, `_dark_stylesheet` | **hart codiertes QSS** (große f-strings), inkl. vereinzelter Roh-Hex (z. B. `#d0d0d0`, `#chatSidePanel` Hintergründe) |
| `app/resources/styles.py` | `get_theme_colors`, `ModernStyle` | **Legacy-Farb-Dict** / Konstanten |

### 3.3 QSS-Dateien (Filesystem)

| Datei | Art | Hex |
|-------|-----|-----|
| `assets/themes/base/base.qss` | Token-QSS | 0 |
| `assets/themes/base/shell.qss` | Token-QSS | 0 |
| `assets/themes/base/workbench.qss` | Token-QSS | 0 |
| `assets/themes/legacy/*.qss` | Legacy-Datei | je 4 Hex (nicht im Loader) |
| `app/resources/light.qss`, `dark.qss` | unbenutzt | viele rgba/hex |

### 3.4 Ableitung aus ThemeManager (gut)

| Datei | Stelle | Art |
|-------|--------|-----|
| `app/gui/components/markdown_widgets.py` | `chat_context_menu_stylesheet()` | Token aus `get_theme_manager().get_tokens()`; Fallback **dunkle** Hex wenn Exception |
| `app/gui/workbench/console/console_panel.py` | `QTextCharFormat` / `setForeground` | Token-Keys mit Fallback-Hex |
| `app/gui/navigation/command_palette.py` | dynamisches Stylesheet | Tokens |
| `app/gui/commands/palette.py` | dynamisches Stylesheet | Tokens |
| `app/gui/navigation/workspace_graph.py` | Dialog-Styling | Tokens + vereinzelte Fallback-Hex in Strings |

### 3.5 Harte Direktdefinition / widget-lokales QSS (Auswahl nach Muster)

**Control Center — wiederkehrendes Muster „heller Karten-Stil“:**  
`providers_panels.py`, `models_panels.py`, `data_stores_panels.py`, `tools_panels.py`, `model_quota_policy_panel.py`, `local_assets_panel.py` — Funktionen wie `_cc_panel_style()` mit `background: white; border: 1px solid #e2e8f0;` unabhängig vom aktiven `theme_id`.

**Inspector-Cluster (gleiche Hex-Muster in vielen Dateien):**  
`app/gui/inspector/*_inspector.py` (u. a. `model_inspector`, `project_context_inspector`, `knowledge_inspector`, …): typisch `QGroupBox { ... color: #374151 }`, Labels `#6b7280`, leer `#9ca3af` — **~20+ Dateien**, jeweils 2–12 Hex (siehe CSV).

**Operations / Chat:** `chat_details_panel.py` (sehr viele Hex für Header, Gruppen, Status-Farben), `chat_list_item.py`, `chat_topic_section.py`, `topic_editor_dialog.py`, `chat_message_widget.py` (Mischung `get_theme_colors` + eigene rgba/hex).

**Operations / Projekte:** `project_overview_panel.py`, `project_header_card.py`, `project_quick_actions_panel.py`, `project_stats_panel.py`, `project_activity_panel.py` — überwiegend **rgba**-Glasmorphismus / Buttons (blau/grün/rot).

**Operations / Knowledge:** `source_details_panel.py`, `knowledge_source_explorer_panel.py`, `index_status_page.py`, `chunk_viewer_panel.py`, … — hohe Hex-Dichte.

**Operations / Prompt Studio:** `prompt_templates_panel.py`, `prompt_list_panel.py`, `prompt_editor_panel.py`, `prompt_version_panel.py`, `prompt_test_lab.py`, …

**QA & Governance:** `test_inventory_panels.py`, `gap_analysis_panels.py`, `coverage_map_panels.py`, `incidents_panels.py`, `replay_lab_panels.py`

**Runtime / Debug:** `system_graph_panels.py`, `metrics_panels.py`, `logs_panels.py`, `eventbus_panels.py`, `agent_status_panel.py`, `agent_activity_stream_panel.py`, diverse `*_view.py` unter `runtime_debug/panels/`

**Command Center:** `command_center_view.py` — Mischung `get_theme_colors` und **eingebettete** dunkle Hex (`#2a2a2a`, `#505050`, …) für frühe UI-Zustände.

**Sonstiges:** `doc_search_panel.py` (konsequent **Light-Only**-Palette), `settings_dialog.py` (`gray`, `green`, `#c44`), `infrastructure_snapshot.py` (Service-Zusammenfassung: `#64748b`, `#10b981`, `#ef4444`), `agents/departments.py` (Domain-Farben für Abteilungen).

### 3.6 Custom Paint / Graphics / Charts

| Datei | Mechanik | Steuerbar zentral? |
|-------|----------|---------------------|
| `workflow_node_item.py` | `QColor` Hex für Füllung/Rand/Schrift nach `NodeRunStatus` + Auswahl | Nein — komplett hardcoded |
| `workflow_edge_item.py` | `QPen(QColor("#64748b"))` | Nein |
| `ai_canvas_scene.py` | `QPen`/`QBrush` Hex | Nein |
| `canvas_tabs.py` | `QColor(R,G,B)` für Status-Punkte auf Tabs | Nein (RGB) |
| `agent_performance_tab.py` | `chart.setBackgroundBrush(QColor("#0a0a14"))` u. a. | Nein |
| `workflow_view.py` | `QPainter` nur RenderHints | — |

### 3.7 Markdown / Rich Text (HTML inline)

| Datei | Art |
|-------|-----|
| `app/gui/shared/markdown/markdown_renderer.py` | **Keine** Theme-Anbindung: durchgängig `rgba(...)` für Code, Tabellen, Blockquotes, HR — fest für hell und dunkel gleich |
| `app/help/help_window.py` | `get_theme_colors` für Widget-QSS; HTML-Inhalt mit Inline `#555` bei „Siehe auch“ |

### 3.8 Tests (Farben erwähnt)

| Datei | Zweck |
|-------|--------|
| `tests/regression/test_settings_theme_tokens.py` | Erwartungen an Light/Dark-Tokens |
| `tests/unit/test_infrastructure_snapshot.py` | erwartete Status-Farben |
| `tests/ui/test_chat_theme.py`, `test_chat_input_theme.py` | UI-Theme-Verhalten |

---

## 4. Inventar — farblich relevante UI-Bereiche

### 4.1 App-Chrome / Shell

- **Quelle:** primär `assets/themes/base/shell.qss` + `workbench.qss` (Tokens).
- **Zentral steuerbar:** ja für alles, was **nur** QSS nutzt.
- **Konflikt:** TopBar/Nav vs. Widgets, die `get_theme_colors` mit Legacy-Werten mischen.

### 4.2 Navigation / Sidebar / Breadcrumbs

- Token-QSS (`#navigationSidebar`, `#breadcrumbBar`, …).
- Zusätzlich: `workspace_graph.py`, `sidebar.py` — teils transparente ScrollAreas, teils Token.

### 4.3 Panels / Cards / GroupBoxes

- Globales `#basePanel` in `base.qss` (Token).
- **Viele** Domain-Panels überschreiben mit **weißem** Hintergrund (`_cc_panel_style`, Projekt-Karten) → **nicht** theme-synchron.

### 4.4 Buttons / Inputs / Tabellen

- Basis in `base.qss` (Token).
- Control-Center-Tabellen: eigene `gridline-color`, `#fafafa` Hintergrund — **Light-assumptiv**.

### 4.5 Chat / Markdown

- Blasen: `chat_message_widget.py` + `markdown_renderer.py` (HTML).
- **Markdown:** Code/Tabellen **dunkel-transparent auf hellem Substrat gedacht** — auf dunklem Theme potenziell **schlechter Kontrast** (gleiche rgba-Schichten).

### 4.6 Status / Badges / Alerts

- `chat_details_panel.py`: statusabhängige Titel-Farben (`#b45309`, `#991b1b`, …).
- `system_status_panel.py`: `#b45309`.
- `infrastructure_snapshot.py`: Ampelfarben.
- `agent_status_panel.py` / `active_agents_panel.py`: `_status_color` → Hex + `QColor`.

### 4.7 Dialoge / Hilfe / Tour

- `help_window.py`, `guided_tour.py`: Legacy `get_theme_colors`.
- `CommandPalette` / `command_palette.py`: Token-basiert.

### 4.8 Workspaces domain-spezifisch

- Große Flächen in Operations, QA, Knowledge, Prompt Studio — überwiegend **Inline-QSS**.

### 4.9 Diagramme / Canvas

- Workflow-Canvas, AI-Canvas, Performance-Charts — **hart codiert**.

### 4.10 Icons

- `IconManager`: Token-basiert; SVGs mit `currentColor`.

---

## 5. Inkonsistenzen und Problemklassen

1. **Zwei Theme-Systeme:** `ThemeManager` (`theme_id`) vs. `get_theme_colors` / `get_stylesheet` (`light`|`dark`) — dokumentiert in `app/main.py` vs. `run_gui_shell.py`.
2. **Workbench kollabiert zu „dark“ in Legacy-Hilfsfunktionen** — `theme_id_to_legacy_light_dark` (`theme_id_utils.py`).
3. **Control-Center- und viele Operations-Panels: Light-only-Karten** (`white`, `#e2e8f0`) bei aktivem `dark_default` / `workbench`.
4. **`markdown_renderer.py`:** rgba unabhängig vom Theme → **nicht theme-fähig**; Risiko auf dunklen Flächen.
5. **`doc_search_panel.py`:** durchgängig helles UI — **fester visueller Bruch** im dunklen Theme.
6. **Duplizierte QSS-Pfade:** `app/gui/themes/base/shell.qss` ≠ `assets/themes/base/shell.qss` — **Loader liest nur `assets/`**; Änderungen am falschen Ort wirken nicht.
7. **Verwaiste QSS:** `app/resources/light.qss`, `dark.qss` ohne Code-Referenz; `assets/themes/legacy/*.qss` ohne Loader.
8. **Doppelte semantische Definition:** `SemanticPalette` + `palette_resolve._domain_monitoring_qa` (zusätzliche Hex-Tabelle).
9. **Gleiche visuelle Rollen, verschiedene Hex:** z. B. „muted text“ mal `#64748b`, mal `#6b7280`, mal `#94a3b8` — siehe CSV-Häufung.
10. **QSS vs. Python:** globales Token-QSS kann durch `setStyleSheet` auf Widget-Ebene **überstimmt** werden — viele Stellen tun das.
11. **`markdown_widgets` Kontextmenü-Fallback:** bei Exception **dunkles** Menü (`#374151`) — potenziell falsch bei Light.
12. **Legacy `ModernStyle` und `get_stylesheet`:** eigene Akzent-Farben (#2563eb light / #4a90d9 dark) — weichen von `ThemeTokens` ab.

---

## 6. Konsolidierungs-Matrix (Auszug)

| Ist-Fundstelle | Aktuell | Betroffene UI | Zielrolle (semantisch) | Zentralisierbar | Priorität |
|----------------|---------|---------------|------------------------|-----------------|-----------|
| `app/resources/styles.py` `get_theme_colors` | light/dark Dict | Command Center, Help, Chat-Header, Runtime-Views, Legacy Message | `fg_primary`, `border_subtle`, `bg_elevated`, … | ja | hoch |
| `theme_id_to_legacy_light_dark` | 2 Buckets | alle `get_theme_colors`-Nutzer | pro `theme_id` echte Token | ja | hoch |
| `_cc_panel_style` in Control-Center-Panels | `white` / `#e2e8f0` | Provider/Models/Data Stores/Tools | `color_bg_surface`, `color_border` | ja | hoch |
| `markdown_renderer.py` rgba | fest | Chat + Hilfe HTML | `code_bg`, `table_border`, `quote_border` | ja (Injection) | hoch |
| `doc_search_panel.py` | Light-Hex | Dokumentensuche | volle Token-Nutzung | ja | mittel |
| `workflow_node_item.py` | Status-Hex | Workflow-Editor | `status_*` + `color_text` | ja | mittel |
| `agent_performance_tab.py` | Chart-Hintergrund | Agent-Performance | `color_monitoring_bg` o. ä. | teilweise | mittel |
| `canvas_tabs.py` RGB | Tab-Badge | Workbench-Tabs | `status_*` mapping | ja | niedrig |
| `inspector/*_inspector.py` Cluster | #374151 / #6b7280 | Inspector-Inhalt | `color_text`, `color_text_secondary` | ja (Helper) | mittel |
| `palette_resolve._domain_monitoring_qa` | extra Hex | QA/Runtime-Chrome | in SemanticPalette integrieren oder dokumentieren | ja | niedrig |
| Verwaiste `app/resources/*.qss` | unbenutzt | — | löschen oder Generator | ja | niedrig |

---

## 7. Vorschlag — kanonisches Theme-Modell (ohne Umsetzung)

### 7.1 Ebenen

1. **SemanticPalette** (bereits vorhanden) — **einzige** Stelle für produktive Marken-/Statusfarben; optional Monitoring-Unterpalette statt separater Dict-Overrides.
2. **ThemeTokens** — flache Exporte für QSS + Runtime.
3. **QSS** — ausschließlich `{{token}}`; keine Roh-Hex in produktiven `assets/themes/base/*.qss`.
4. **Runtime (Python)** — Farben nur via `get_theme_manager().get_tokens()` oder typisierte Helper (`token("color_error")`).

### 7.2 Rollen (erweitert)

- **Basis:** `bg_app`, `bg_panel`, `bg_surface`, `bg_elevated`, `bg_input`, `bg_hover`, `bg_selected`, `bg_disabled`
- **Text:** `fg_primary`, `fg_secondary`, `fg_muted`, `fg_disabled`, `fg_on_selected`, `fg_on_accent`, `fg_on_success|warning|error`
- **Rand:** `border_subtle`, `border_default`, `border_strong`
- **Interaktion:** `accent_primary`, `accent_hover`, `accent_active`, `accent_muted_bg`, `focus_ring`
- **Status:** `status_success`, `status_warning`, `status_error`, `status_info`
- **Domain:** `monitoring_*`, `qa_nav_*` (oder in SemanticPalette integriert)
- **Markdown/Code:** neu: `markdown_code_bg`, `markdown_table_border`, `markdown_blockquote_border`, `markdown_hr` (als Hex oder rgba-Basis + Opacity)

### 7.3 QSS vs. Python

- **QSS:** Widget-Typen, Pseudo-States, Layout-Chrome, wiederkehrende ObjectNames.
- **Python:** dynamische Zusammensetzung (z. B. Chart-Palette), `QColor` für Painter, QTextCharFormat, setForeground auf Items — **Werte aus Tokens**, keine Literale.

### 7.4 Künftig zu vermeiden (API-Disziplin)

- Neue Hex/RGB-Literale in `app/gui/domains/**` und `app/gui/inspector/**` ohne Token-Bezug.
- Neue Nutzung von `get_theme_colors` — Migration auf `theme_id` + Tokens.
- Bearbeitung von `app/gui/themes/base/*.qss` ohne Synchronisierung mit `assets/themes/base/` (besser: Duplikat entfernen).

---

## 8. Refactoring-Empfehlung in Phasen

Siehe **`THEME_COLOR_REFACTOR_PLAN.md`** (kurz, operationalisierbar).

---

## Anhang A — Zählungen (Reproduktion)

Im Repo-Root (analog zur Erzeugung von `THEME_COLOR_INVENTORY.csv`):

```python
import re, pathlib
root = pathlib.Path("app")
hex_pat = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
ss_pat = re.compile(r"setStyleSheet\s*\(")
print("hex:", sum(len(hex_pat.findall(p.read_text(encoding="utf-8", errors="replace"))) for p in root.rglob("*.py")))
print("setStyleSheet:", sum(len(ss_pat.findall(p.read_text(encoding="utf-8", errors="replace"))) for p in root.rglob("*.py")))
```

---

## Anhang B — Kurzlisten (wie angefragt)

### Top 10 kritischste Inkonsistenzen

1. Zwei parallele Theme-Systeme (`ThemeManager` vs. `app/resources/styles.py`).
2. `workbench` und `dark_default` teilen Legacy-Bucket `get_theme_colors("dark")`.
3. Control-Center-Panels visuell **light-locked** bei dark/workbench.
4. `markdown_renderer.py` theme-unabhängige rgba → Lesbarkeit auf dunklem UI.
5. `doc_search_panel.py` komplett light — Bruch im Shell-Dark-Theme.
6. Abweichende `shell.qss`/`workbench.qss` zwischen `assets/` und `app/gui/themes/base/`.
7. Viele hunderte Inline-`setStyleSheet` überschreiben globales Token-QSS.
8. Workflow-/Chart-Painter ohne Token — permanente Sonderpalette.
9. `palette_resolve` dupliziert Domainfarben neben SemanticPalette.
10. Verwaiste `app/resources/*.qss` + ungenutzte `assets/themes/legacy/*.qss` verwirren die „Source of truth“.

### Top 10 zentrale Theme-Einstiegspunkte

1. `app/gui/themes/manager.py` — `ThemeManager.set_theme`
2. `app/gui/themes/registry.py` — Theme-Registrierung
3. `app/gui/themes/builtin_semantic_profiles.py` — visuelle Profile
4. `app/gui/themes/palette_resolve.py` — Mapping + Domain-Overrides
5. `app/gui/themes/tokens.py` — `ThemeTokens` Defaults
6. `app/gui/themes/loader.py` — QSS-Load + Substitution
7. `assets/themes/base/{base,shell,workbench}.qss` — globales Styling
8. `run_gui_shell.py` — initial theme apply
9. `app/core/config/settings.py` — `theme_id` Persistenz
10. `app/gui/icons/manager.py` — Icon-Farbe aus Tokens

### Top 10 Stellen, die Refactoring blockieren oder verzögern

1. Breite Kopplung an `get_theme_colors` (viele Dateien).
2. `theme_id_to_legacy_light_dark` — verhindert feingranulare Inline-Styles bis zur Migration.
3. Massenhafte identische Inspector-Styles (ohne gemeinsamen Helper).
4. `markdown_renderer` als zentrale HTML-Pipeline — Änderung berührt Chat + Hilfe.
5. Duplikat-QSS-Pfade — Gefahr, falsche Datei zu pflegen.
6. Verwaiste QSS-Dateien — unklar, ob extern referenziert (Dokumentation/Build).
7. Tests, die konkrete Hex erwarten (`test_infrastructure_snapshot`, Token-Regression).
8. Legacy `app/main.py` Pfad — solange existent, muss `get_stylesheet` konsistent bleiben oder entfernt werden.
9. ChartKit/QtCharts in `agent_performance_tab` — eigene Farblogik.
10. Sehr große Panel-Dateien mit gemischten Concerns (Layout + viele Farbstrings) — hoher Merge-Konflikt-Risiko bei mechanischem Replace.

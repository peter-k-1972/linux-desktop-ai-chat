# Visual System Audit (Ist-Zustand)

**Zweck:** Bestandsaufnahme visueller Konstanten und Konflikte für PySide6/QSS + Python-Layouts.  
**Quellen:** `app/gui/themes/base/*.qss`, `app/gui/themes/tokens.py`, `app/gui/shared/layout_constants.py`, `app/gui/themes/control_center_styles.py`, `app/gui/workbench/ui/design_tokens.py`, ausgewählte Widgets mit Inline-`setStyleSheet`.

**Legende `conflict_status`:** `aligned` = eine klare Quelle; `split` = zwei legitime Systeme (QSS vs. Layout); `drift` = abweichende Magic Numbers / Duplikate; `legacy` = nicht tokenisiert, historisch.

---

## Typografie

| value_type | value | locations | current_usage | conflict_status |
|------------|-------|-----------|---------------|-----------------|
| font-size | 11px | `ThemeTokens.font_size_xs`, `font_size_meta`; QSS `#runtimeNavSubtitle`; Python `chat_details_panel`, `source_details_panel`, `project_stats_panel`, `legacy/sidebar_widget` | Captions, Meta, Runtime-Nav, viele Inline-Styles | `drift` (QSS token vs. harte 11px in Python) |
| font-size | 12px | `ThemeTokens.font_size_sm`; QSS `#runtimeNavTitle` (hart 12px statt Token); CC-Styles `cc_refresh_button`, `cc_body` | Sekundärtext, kleine UI | `drift` (`#runtimeNavTitle` umgeht `font_size_sm`) |
| font-size | 13px | `ThemeTokens.font_size_base`, `font_size_panel_title`; CC `cc_section_title`, `cc_name_emphasis`; Markdown-Renderer | Panel-Titel, Body leicht kleiner als QLabel-Default | `aligned` (mit kleinen Ausnahmen) |
| font-size | 14px | `ThemeTokens.font_size_md`, `font_size_section_title`; Default `QLabel` in `base.qss` | Fließtext-Labels, Buttons, Inputs | `aligned` |
| font-size | 16px | `ThemeTokens.font_size_lg` | Command-Palette-Titel, Empty-State Workbench | `aligned` |
| font-size | 18px | `ThemeTokens.font_size_primary_title` | Workspace-/Primary-Titel | `aligned` |
| font-size | 20px | `ThemeTokens.font_size_xl`; `project_stats_panel` (hart) | KPI-Werte vs. Token-xl | `drift` (KPI nicht an Token gebunden) |
| font-weight | 400 / 500 / 600 / 700 | `ThemeTokens.font_weight_*` | Buttons medium, GroupBox semibold, primary title bold | `aligned` |
| font-weight | 600 (literal) | `shell.qss` `#runtimeNavTitle` (`font-weight: 600`) | Sollte `font_weight_semibold` Token sein | `drift` |
| line-height | 1.35 | `workbench.qss` `#workbenchInspectorBody` | Inspector-Fließtext | `split` (nur Workbench, kein globales Token) |
| line-height | 1.4 / 1.5 | `shell.qss` Empty-State | Beschreibungstexte | `split` |
| letter-spacing | 0.5px | `shell.qss` `#navSectionHeader`, Workbench Section-Card-Titel | Uppercase-Sektionsköpfe | `split` (kein Token) |
| font-family (mono) | `{{font_family_mono}}` | `workbench.qss` Konsole | Log-Ausgabe | `aligned` |

---

## Abstände (Padding / Margin / Gap)

| value_type | value | locations | current_usage | conflict_status |
|------------|-------|-----------|---------------|-----------------|
| spacing scale 4–32px | `spacing_xs`…`spacing_2xl` | `ThemeTokens`; breit in QSS | Einheitliche Rhythmik in QSS | `aligned` |
| panel padding | 20px | `ThemeTokens.panel_padding`; `layout_constants.PANEL_PADDING` | Karten, Bottom-Panel-Pane, `apply_panel_layout` | `split` (gleicher Wert, zwei Namensräume) |
| section / card | 24px / 16px | `ThemeTokens.section_spacing`, `card_spacing`; Kommentar `shell.qss` | Dokumentiert, Python parallel `SECTION_SPACING`, `CARD_SPACING` | `split` |
| workspace padding | 20px / 16px | `layout_constants.WORKSPACE_*` | Code-Layouts | `split` (nicht alle QSS-Panels) |
| sidebar padding | 12px / 10px | `SIDEBAR_PADDING`, `SIDEBAR_SPACING` | Kompakter als Panel | `drift` vs. `nav_item_padding_*` 12×16 — ähnlich aber nicht identisch zu „Sidebar gap“ |
| nav item padding | 12px × 16px | `nav_item_padding_v/h` | Listen, Domain-Navs | `aligned` |
| list item (layout) | 10×12px | `LIST_ITEM_PADDING_*` | Python-Listen-Layouts | `drift` vs. QSS-Nav 12×16 |
| empty state | 24px / 16px | `EMPTY_STATE_*` | `EmptyStateWidget` | `aligned` mit `spacing_xl` / `spacing_lg` |
| harte Padding-Paare | 6px 12px | `shell.qss` `#projectSwitcherButton`, `#chatNavNewTopicButton`, Chat-Model-Combo; `control_center_styles.cc_refresh_button_style` | Kompakte Chips/Buttons | `drift` (sollte `spacing_sm`×`spacing_md` oder dediziertes Component-Token sein) |
| harte Padding-Paare | 4px 8px | `shell.qss` Breadcrumb, Filter-Chips; `workbench.qss` Mode-Badge | Ultra-kompakt | `drift` |
| harte Margins | 2px, 4px | QSS `navItemList`, Scrollbar, Tab close, Palette-Items | Feintuning | `drift` |
| message bubble margin | 4px 0 | `shell.qss` `#messageBubble` | Chat | `split` (könnte `space.stack.gap.sm` werden) |

---

## Größen (Höhen, Mindesthöhen, Icon)

| value_type | value | locations | current_usage | conflict_status |
|------------|-------|-----------|---------------|-----------------|
| control / combo min-height | 32px | `base.qss` `QComboBox`; `workbench.qss` Palette-Items | Standard-Eingabehöhe | `aligned` mit `layout_constants.CONTROL_HEIGHT` |
| tree item min-height | 26px | `workbenchExplorerTree` | Explorer-Zeilen | `drift` vs. 28px Node-Library vs. 32px Palette |
| list item min-height | 28px | `workbenchNodeLibrary` | AI Canvas Library | `drift` |
| list item min-height | 32px | Command-Palette-Liste | Palette | `drift` |
| scrollbar | width 12px, handle min-height 48px, radius 6px | `base.qss` | Globale Scrollbars | `drift` (6px = `radius_sm`, aber nicht als Token referenziert) |
| toolbar icon-size | 18px | `workbench.qss` | Workbench-Toolbar | `drift` vs. `IconManager` Default 24 |
| icon pixmap (code) | 20px | `chat_composer_widget` `setIconSize(QSize(20,20))` | Send-Icon | `drift` |
| icon empty state | 32px | `empty_state_widget.py` | Empty-State-Illustration | `drift` vs. 18/24/32 Mix |
| tab min-width | 7em | `workbench.qss` Canvas-Tabs | Relative Breite | `split` (nicht px-basiert) |

---

## Radius

| value_type | value | locations | current_usage | conflict_status |
|------------|-------|-----------|---------------|-----------------|
| radius sm/md/lg/xl | 6 / 8 / 10 / 12px | `ThemeTokens` | Buttons, Inputs, Karten, Tabs | `aligned` |
| harte 6px | mehrere Python-Inline-Styles (`source_details_panel`, `chat_details_panel`) | Knowledge/Chat-Details | Duplikat von `radius_sm` | `drift` |
| harte 10px | `cc_panel_frame_style`, `project_stats_panel` | CC-Karten | Entspricht `radius_lg` | `drift` (nicht über Token-String) |

---

## Border

| value_type | value | locations | current_usage | conflict_status |
|------------|-------|-----------|---------------|-----------------|
| border width | 1px | Dominant in QSS | Rahmen fast überall | `aligned` |
| border width | 2px | `workbench.qss` Command-Palette-Suche (normal + focus) | Fokus-Accent für modales Eingabefeld | `split` (sollte `border.width.focus` / default sein) |
| border style | dashed | `workbenchAiEmptyBanner` | Leerer Graph-Zustand | `split` |

---

## Schatten / Elevation

| value_type | value | locations | current_usage | conflict_status |
|------------|-------|-----------|---------------|-----------------|
| box-shadow | — | Keine relevanten QSS-`box-shadow` in `app/gui/themes/base` | Qt/QSS: Schatten eingeschränkt / plattformabhängig | `aligned` — **kein Schatten-System**; Tiefe über Hintergrundstufen + Border |

---

## Dialog / Panel / Karten

| value_type | value | locations | current_usage | conflict_status |
|------------|-------|-----------|---------------|-----------------|
| settings panel padding | `spacing_lg` (16px) | `shell.qss` `#settingsPanel` | Innenabstand Kategorie | `split` vs. `panel_padding` 20px auf anderen Flächen |
| placeholder padding | `spacing_xl` (24px) | `#settingsPlaceholder` | Leerer Settings-State | `aligned` mit `EMPTY_STATE_PADDING` |
| base panel | `panel_padding` + `radius_xl` | `base.qss` `#basePanel` | Generische Karte | `aligned` |

---

## Farben (kurz, Detail in THEME_TOKEN_SPEC)

| value_type | value | locations | current_usage | conflict_status |
|------------|-------|-----------|---------------|-----------------|
| Hex inline | `#64748b`, `#1f2937`, … | `project_stats_panel`, `source_details_panel`, `chat_details_panel`, `agent_performance_tab` | Umgehen ThemeManager | `legacy` / `drift` |
| Token-basiert | `ThemeTokens` + Resolver | QSS-Platzhalter, `control_center_styles` | Soll-Zustand | `aligned` |

---

## Zusammenfassung der größten Inkonsistenzen

1. **Zwei Metrik-Systeme:** `ThemeTokens` (String, px für QSS) und `layout_constants` (int, Layouts) — oft gleiche Zahlen, verschiedene Namen.
2. **Magic Numbers in QSS:** `6px 12px`, `4px 8px`, `12px`/`11px` bei Runtime-Nav, `icon-size: 18px`, Scrollbar-Geometrie.
3. **Icon-Größen:** 18 / 20 / 24 / 32 je nach Kontext ohne Katalog.
4. **Zeilenhöhen / Letter-Spacing:** nur lokal in QSS, nicht als wiederverwendbare Tokens.
5. **Listen-/Tree-Zeilenhöhen:** 26 / 28 / 32 ohne gemeinsame Regel.
6. **Inline-Styles in Domains:** Operations/Knowledge/Chat widersprechen dem tokenisierten Pfad.

---

*Nächste Schritte:* [DESIGN_TOKEN_ARCHITECTURE.md](./DESIGN_TOKEN_ARCHITECTURE.md), [DESIGN_TOKEN_SPEC.md](./DESIGN_TOKEN_SPEC.md), [DESIGN_TOKEN_MIGRATION_PLAN.md](./DESIGN_TOKEN_MIGRATION_PLAN.md).

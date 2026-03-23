# Design-Token-Migrationsplan

**Prinzip:** Inkrementell, testbar, ohne Big-Bang. QSS bleibt die visuelle Hauptquelle; Python übernimmt Layout-Zahlen aus derselben logischen Skala.

---

## 1. Reihenfolge: Was zuerst?

| Phase | Inhalt | Warum zuerst |
|-------|--------|--------------|
| A | **Spacing-Integer** aus `app/gui/theme/design_metrics.py` in `layout_constants` einbinden (Import statt Duplikat) | Größter Drift Python↔QSS |
| B | **Icon-Größen** vereinheitlichen: Workbench `icon-size` → `icon.size.md` (20px); `IconManager`-Default bleibt 24 als `lg` | Sofort sichtbare Konsistenz |
| C | **QSS-Magic-Numbers** ersetzen: `6px 12px`, `4px 8px`, Runtime-Nav `font-size` → Tokens (`spacing_sm`/`spacing_md`, `font_size_*`) | Weniger technische Schulden |
| D | **Radius** in Python-Inline-Styles durch `ThemeManager.get_tokens()` oder feste Konstanten aus `design_metrics` | Knowledge/Chat-Panels |
| E | **Farb-Hex** in Domains entfernen → `ThemeManager.color(ThemeTokenId.*)` oder QSS object names | Dark/Light-Sicherheit |
| F | **Markdown-Renderer** (`markdown_renderer.py`): px durch Import aus `design_metrics` / Registry | Einheit mit GUI |
| G | **ThemeTokens erweitern** um optionale Aliase `text_size_*`, `space_*` parallel zu Legacy `font_size_*`, `spacing_*` | Sanfte kanonische Namen |

Farben bleiben im bestehenden **THEME_TOKEN_SPEC**-Pfad; keine parallele Farbdefinition.

---

## 2. Welche Altwerte werden ersetzt?

| Alt | Neu |
|-----|-----|
| Loose `20`, `16`, `12` in `layout_constants` | `design_metrics.SPACE_*` / `PANEL_PADDING` = `SPACE_PANEL` |
| `18px` Toolbar-Icon | `20px` (`icon.size.md`) gemäß Defaults |
| `#runtimeNavTitle` feste 12px/600 | `{{font_size_sm}}`, `{{font_weight_semibold}}` |
| `cc_panel_frame_style` feste `10px`, `12px` padding | Tokens `radius_lg`, `spacing_md` aus Theme-Dict |
| `project_stats_panel`, `source_details_panel`, … Hex | `ThemeTokenId` + Resolver |
| Explorer `26px` / Node `28px` / Palette `32px` | Einheit **32px** Mindestzeile oder dokumentierte Ausnahme „kompakt 28“ nur für Library |

---

## 3. Python und QSS anbinden

1. **QSS:** Weiterhin `load_stylesheet` + flaches Dict; Platzhalter nur aus einem generierten Merge: `ThemeTokens` + künftige `space_*` Aliase.
2. **Python Layouts:** `from app.gui.theme.design_metrics import SPACE_MD, PANEL_PADDING_PX` (oder Registry-Methode `space_px("space.md")`).
3. **Farben in Python:** unverändert `get_theme_manager().color(ThemeTokenId.FG_PRIMARY)` etc.
4. **IconManager:** optionale Konstante `DEFAULT_ICON_SIZE = design_metrics.ICON_LG` wenn gewünscht; Aufrufer explizit `size=ICON_MD` für Toolbar.

**Single source:** Zahlen **einmal** in `design_metrics`; `ThemeTokens` Strings bauen aus denselben Ints (optional Helper `px(n) -> f"{n}px"` beim Theme-Build).

---

## 4. Regression vermeiden

- **Visuelle Snapshots:** manuelle Checkliste pro Phase (Light + Dark): Sidebar, Workbench, Chat, Settings, Control Center.
- **Keine gleichzeitige** Änderung von Farbe und Metrik in einem Commit.
- **Feature-Flags:** nicht nötig bei kleinen Schritten; bei großer QSS-Umstellung optional Theme-Variante `light_default_v2` vermeiden — lieber iterative PRs.
- **Tests:** bestehende Theme-Load-Tests erweitern um „Stylesheet enthält keine rohen `#[0-9a-fA-F]{6}` außer in Kommentaren“ als **optional** `grep`-Test (kann false positives haben — nur als CI-Warnung).

---

## 5. Guard / QA (Zielbild)

| Mechanismus | Beschreibung |
|-------------|--------------|
| Lint / Script | `scripts/check_design_tokens.py`: verbotene Muster `setStyleSheet("...#[` in `app/gui/domains/` |
| Resolver-Validierung | Bereits vorhandene semantic validation für Farben — erweiterbar um „jeder `ThemeTokens`-Key ist bekannt“ |
| Dokumentation | Änderungen an Defaults nur gemeinsam mit Update [DESIGN_TOKEN_DEFAULTS.md](./DESIGN_TOKEN_DEFAULTS.md) |
| Storybook/Dev | Theme Visualizer um Spacing-/Typo-Swatches erweitern (optional) |

---

## 6. Abhängigkeiten

- **Blockiert durch nichts:** Phase A–B (Metrics + Icons).
- **Blockiert C:** kurze Abstimmung ob `radius.input` 10 oder 12px Soll ist.
- **Blockiert E:** manche Panels brauchen objectName + QSS-Selektor statt Inline.

---

*Siehe Abschluss:* [DESIGN_TOKEN_SYSTEM_REPORT.md](../../DESIGN_TOKEN_SYSTEM_REPORT.md).

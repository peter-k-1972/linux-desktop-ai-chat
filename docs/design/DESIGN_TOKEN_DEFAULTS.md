# Design-Token-Defaults (Desktop-Workbench)

**Zielbild:** ruhig, **kompakt**, professionell, arbeitsflächenorientiert — **nicht** mobil/web-aufgblasen.  
**Basis:** [VISUAL_SYSTEM_AUDIT.md](./VISUAL_SYSTEM_AUDIT.md) + bestehende `ThemeTokens` / `layout_constants`.

Alle Werte **4px-Raster** außer bewussten 2px-Feintuning (Scrollbar-Margin, Tab-Abstand).

---

## 1. Raster & Spacing (empfohlene Kanon-Werte)

| Token | px | Bemerkung |
|-------|-----|-----------|
| `space.2xs` | 2 | Splitter-Naht, Micro-Gap |
| `space.xs` | 4 | Icon↔Text, enge Stacks |
| `space.sm` | 8 | Standard-Zwischenraum in Gruppen |
| `space.md` | 12 | Formular-Zeilengliederung, Nav-Padding vertikal |
| `space.lg` | 16 | Karteninnenrand, große Gruppen |
| `space.xl` | 24 | Dialog/Settings-äußerer Rand, Empty-State |
| `space.2xl` | 32 | Selten; große Luft zwischen Sektionen |

**Spezial (Semantic):**

| Token | px |
|-------|-----|
| `space.panel.padding` | 20 |
| `space.card.padding` | 16 |
| `space.dialog.padding` | 24 |
| `space.form.row_gap` | 12 |
| `space.form.label_gap` | 8 |
| `space.toolbar.gap` | 12 |
| `space.sidebar.item_gap` | 4 |
| `space.inline.gap.sm` | 8 |
| `space.inline.gap.md` | 12 |
| `space.stack.gap.sm` | 4 |
| `space.stack.gap.md` | 8 |
| `space.stack.gap.lg` | 12 |

**Python-Layouts:** `layout_constants` soll numerisch **dieselben** Werte tragen wie oben (Refactor: Konstanten aus `design_metrics` importieren).

---

## 2. Typografie

| Token | Wert | Verwendung |
|-------|------|------------|
| `text.size.xs` | 11px | Captions, Meta, Checkbox-Labels in Chat-Nav |
| `text.size.sm` | 12px | Sekundärtext, Tabellen-Header, Breadcrumbs |
| `text.size.base` | 13px | Inspector-Primary, kompakte Labels |
| `text.size.md` | 14px | Body, Standard-`QLabel`, Buttons, Inputs |
| `text.size.lg` | 16px | Dialog-/Palette-Titel |
| `text.size.xl` | 20px | KPI-Zahlen, Hero (sparsam) |
| `text.size.primary_title` | 18px | Workspace-H1 |
| `text.size.section_title` | 14px | Panel-/Settings-Überschriften (fett) |

Gewichte: **400 / 500 / 600 / 700** wie heute in `ThemeTokens`.

**Line-height:** Inspector-Body **1.35** (`text.line_height.normal`); Fließtext in Empty-State **1.5** (`relaxed`). Uppercase-Sektionstitel: **letter-spacing 0.5px** (Component-Token, nicht global).

---

## 3. Radius

| Token | px |
|-------|-----|
| `radius.sm` | 6 |
| `radius.md` | 8 |
| `radius.lg` | 10 |
| `radius.xl` | 12 |
| `radius.pill` | 9999 |
| `radius.button` | **12** (= `radius.xl`, Ist-QSS) |
| `radius.input` | 12 oder 10 — **Empfehlung:** 10 (`radius.lg`) für visuelle Ruhe; Migration separat |
| `radius.card` | 10 |
| `radius.dialog` | 8 |
| `radius.badge` | 6 |

---

## 4. Border

| Token | Wert |
|-------|------|
| `border.width.subtle` / `default` / `strong` | **1px** (Stärke über Farbe) |
| `border.width.focus` | **2px** (Palette-Suche, explizite Fokus-Ringe) |
| `border.style.default` | `solid` |

---

## 5. Größen (komponentennah)

| Token | px | Notiz |
|-------|-----|--------|
| `size.icon.xs` | 14 | optional |
| `size.icon.sm` | 16 | Nav |
| `size.icon.md` | **20** | **Workbench-Toolbar-Soll** (ersetzt 18px für bessere Lesbarkeit) |
| `size.icon.lg` | 24 | `IconManager`-Default, große Aktionen |
| `size.input.md` | **32** | Combo/LineEdit-Zielhöhe |
| `size.button.md` | **32** | Gleiche Höhe wie Input in Formularen |
| `size.tab.row` | **~34** | aus Padding `sm`+`lg` vertikal ableitbar |
| `size.toolbar.min_height` | **40** | kompakt mit `space.sm` vertikal |
| `size.sidebar.nav_item_min` | **32** | vereinheitlicht 26/28/32 → **32** als Minimum |
| `size.dialog.min_width` | 480 | Standard-Dialog |
| `size.panel.header_height` | 40 | Explorer/Inspector-Kopf |

---

## 6. Elevation / Schatten

- **Standard:** `shadow.none` — keine Box-Shadows im Basisthema.
- **Tiefe:** über `surface.level.*` + `color.border.*`.
- **Modal:** Kontrast durch `color.bg.overlay` + helle/dunkle Surface, optional 2px Focus auf primärem Feld.

---

## 7. Icon-State-Farben

Unverändert aus `ICON_STATE_TO_TOKEN` — keine neuen Hex-Werte.

---

*Umsetzung:* [DESIGN_TOKEN_MIGRATION_PLAN.md](./DESIGN_TOKEN_MIGRATION_PLAN.md).

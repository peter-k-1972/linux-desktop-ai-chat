# Design-Token-Spezifikation (vollständiger Katalog)

**Gültigkeit:** GUI (PySide6), QSS + Python.  
**Farben:** Autoritativ weiterhin [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md); dieser Katalog **referenziert** sie und ergänzt **Icon, Typo, Layout, Größe, Oberfläche, Zustände**.

**Konvention:** Spalte **canonical** = logischer Name; **flat** = Platzhalter/Dict-Key für QSS (`{{flat}}`) nach gleicher Regel wie Farben (`text.size.sm` → `text_size_sm`).

---

## COLOR

Alle Farb-Tokens sind in **THEME_TOKEN_SPEC** definiert. Wichtigste Gruppen (keine Wertduplikation hier):

| Gruppe | Beispiele canonical | Verwendung |
|--------|----------------------|------------|
| Flächen | `color.bg.app`, `color.bg.surface`, `color.bg.panel` | Fenster, Workspace, Sidebar |
| Text | `color.fg.primary`, `color.fg.secondary`, `color.fg.muted` | Hierarchie |
| Rahmen | `color.border.default`, `color.border.focus` | Trennung, Fokus |
| Interaktion | `color.interaction.hover`, `color.interaction.selected` | Listen, Tabs |
| State | `color.state.accent`, `color.state.success`, … | Accent + Semantic |
| Domain | `color.domain.monitoring.*`, `color.domain.qa_nav.*` | Runtime/QA-Räume |

**Konsolidierung:** Legacy-Keys (`color_bg`, `color_text`, …) bleiben bis Resolver-Migration; neue Arbeit nur `color.*` kanonisch.

---

## ICON

| canonical | flat | Typ | Beschreibung |
|-----------|------|-----|----------------|
| `icon.size.xs` | `icon_size_xs` | size (px) | Inline mit Text, Meta-Zeilen (Default-Vorschlag **14**) |
| `icon.size.sm` | `icon_size_sm` | size | Nav-Items, kompakte Buttons (**16**) |
| `icon.size.md` | `icon_size_md` | size | Standard-Toolbar/Listen (**20**) |
| `icon.size.lg` | `icon_size_lg` | size | Empty-States, prominente Aktionen (**24**) |

**State → Farbe** (kein separates Icon-Pixel-Token): Nutzung über `IconManager` + [icon_states.py](../../app/gui/icons/icon_states.py).

| canonical | Beschreibung | Token für Tint |
|-----------|--------------|----------------|
| `icon.state.default` | Standard | `color.fg.secondary` |
| `icon.state.active` | Hover/fokussierte Aktion | `color.state.accent` |
| `icon.state.disabled` | Deaktiviert | `color.fg.disabled` |
| `icon.state.success` | Erfolg | `color.state.success` |
| `icon.state.warning` | Warnung | `color.state.warning` |
| `icon.state.error` | Fehler | `color.state.error` |

*Hinweis:* Zusätzliche States (`primary`, `selected`) bleiben im Code als Alias bis vereinheitlicht.

---

## TYPOGRAPHY

| canonical | flat | Default (Desktop) | Rolle |
|-----------|------|-------------------|--------|
| `font.family.base` | `font_family_base` | System UI stack | Alle UI-Widgets |
| `font.family.mono` | `font_family_mono` | Monospace | Konsole, Code, Logs |

| canonical | flat | Default |
|-----------|------|---------|
| `text.size.xs` | `text_size_xs` | 11px |
| `text.size.sm` | `text_size_sm` | 12px |
| `text.size.md` | `text_size_md` | 14px |
| `text.size.lg` | `text_size_lg` | 16px |
| `text.size.xl` | `text_size_xl` | 20px |

| canonical | flat | Default |
|-----------|------|---------|
| `text.weight.regular` | `text_weight_regular` | 400 |
| `text.weight.medium` | `text_weight_medium` | 500 |
| `text.weight.semibold` | `text_weight_semibold` | 600 |
| `text.weight.bold` | `text_weight_bold` | 700 |

| canonical | flat | Default |
|-----------|------|---------|
| `text.line_height.tight` | `text_line_height_tight` | 1.25 |
| `text.line_height.normal` | `text_line_height_normal` | 1.35 |
| `text.line_height.relaxed` | `text_line_height_relaxed` | 1.5 |

**Rollen** (Semantic-Typo — Mapping auf Größe/Gewicht):

| canonical | Empfehlung (kompakt Desktop) |
|-----------|------------------------------|
| `text.role.caption` | `text.size.xs` + `fg.muted` |
| `text.role.body` | `text.size.md` + `fg.primary` |
| `text.role.label` | `text.size.sm` + `weight.medium` |
| `text.role.section_title` | `text.size.sm` + `weight.semibold` + optional uppercase/letter-spacing Component |
| `text.role.panel_title` | `text.size.base`* + `weight.semibold` |
| `text.role.window_title` | `text.size.primary_title`* + `weight.bold` |

\*`text.size.base` / `text.size.primary_title` als Erweiterung: aligniert mit heutigen `font_size_base` (13px) und `font_size_primary_title` (18px) — in Registry als Aliase zu dokumentieren.

---

## SPACING

| canonical | flat | Default |
|-----------|------|---------|
| `space.2xs` | `space_2xs` | 2px |
| `space.xs` | `space_xs` | 4px |
| `space.sm` | `space_sm` | 8px |
| `space.md` | `space_md` | 12px |
| `space.lg` | `space_lg` | 16px |
| `space.xl` | `space_xl` | 24px |
| `space.2xl` | `space_2xl` | 32px |

| canonical | flat | Default |
|-----------|------|---------|
| `space.inline.gap.sm` | `space_inline_gap_sm` | 8px |
| `space.inline.gap.md` | `space_inline_gap_md` | 12px |
| `space.stack.gap.sm` | `space_stack_gap_sm` | 4px |
| `space.stack.gap.md` | `space_stack_gap_md` | 8px |
| `space.stack.gap.lg` | `space_stack_gap_lg` | 12px |

| canonical | flat | Default |
|-----------|------|---------|
| `space.panel.padding` | `space_panel_padding` | 20px |
| `space.card.padding` | `space_card_padding` | 16px |
| `space.dialog.padding` | `space_dialog_padding` | 24px |
| `space.form.row_gap` | `space_form_row_gap` | 12px |
| `space.form.label_gap` | `space_form_label_gap` | 8px |
| `space.toolbar.gap` | `space_toolbar_gap` | 12px |
| `space.sidebar.item_gap` | `space_sidebar_item_gap` | 4px |

**Migration:** Bestehende `spacing_*` in `ThemeTokens` entsprechen `space.xs` … `space.2xl` (ohne `space.2xs`).

---

## RADIUS

| canonical | flat | Default |
|-----------|------|---------|
| `radius.sm` | `radius_sm` | 6px |
| `radius.md` | `radius_md` | 8px |
| `radius.lg` | `radius_lg` | 10px |
| `radius.pill` | `radius_pill` | 9999px |

| canonical | flat | Default (Alias) |
|-----------|------|-----------------|
| `radius.button` | `radius_button` | = `radius.xl` (**12px**, entspricht heutigem `QPushButton` in `base.qss`) |

*Optional später:* auf `radius.lg` (10px) vereinheitlichen für strengeres Karten/Button-Raster — siehe [DESIGN_TOKEN_DEFAULTS.md](./DESIGN_TOKEN_DEFAULTS.md).

| canonical | Default |
|-----------|---------|
| `radius.input` | = `radius.lg` |
| `radius.card` | = `radius.lg` |
| `radius.dialog` | = `radius.md` |
| `radius.badge` | = `radius.sm` |

---

## BORDER

| canonical | flat | Default |
|-----------|------|---------|
| `border.width.subtle` | `border_width_subtle` | 1px |
| `border.width.default` | `border_width_default` | 1px |
| `border.width.strong` | `border_width_strong` | 1px (andere Farbe) |
| `border.width.focus` | `border_width_focus` | 2px |

| canonical | flat | Default |
|-----------|------|---------|
| `border.style.default` | `border_style_default` | `solid` |

**Hinweis:** „Strong“ ist bei Desktop oft **Farbe** (`color.border.strong`), nicht Dicke.

---

## SIZE

| canonical | flat | Default (px) |
|-----------|------|--------------|
| `size.icon.xs` | `size_icon_xs` | = `icon.size.xs` |
| `size.icon.sm` | `size_icon_sm` | 16 |
| `size.icon.md` | `size_icon_md` | 20 |
| `size.icon.lg` | `size_icon_lg` | 24 |

| canonical | Default |
|-----------|---------|
| `size.button.sm` | min-height **28**, padding **6×12** |
| `size.button.md` | min-height **32**, padding **8×12** |
| `size.button.lg` | min-height **36**, padding **10×16** |

| canonical | Default |
|-----------|---------|
| `size.input.sm` | min-height **28** |
| `size.input.md` | min-height **32** |
| `size.input.lg` | min-height **40** |

| canonical | Default |
|-----------|---------|
| `size.sidebar.item_height` | mind. **32** (touch-friendly optional aus; Desktop kompakt **30**) |
| `size.tab.height` | auto aus Padding; Ziel **32–36** |
| `size.toolbar.height` | aus Padding + Icon **md**; Ziel **40–44** |
| `size.dialog.min_width` | **480** |
| `size.panel.header_height` | **40** (kompakt) |

---

## ELEVATION / SURFACE

Qt/QSS limitiert Schatten. **Ehrliche Default-Strategie:** Stufen über **Hintergrund-Semantik** + **Border**; Schatten nur optional/plattformspezifisch.

| canonical | Bedeutung |
|-----------|-------------|
| `surface.level.app` | `color.bg.app` |
| `surface.level.panel` | `color.bg.panel` |
| `surface.level.card` | `color.bg.surface` + `border.default` |
| `surface.level.modal` | `color.bg.surface` / `color.bg.window` + starker Rand oder `color.bg.overlay` dahinter |
| `surface.level.overlay` | `color.bg.overlay` |

| canonical | Nutzung |
|-----------|---------|
| `shadow.none` | Standard Desktop-Chrome |
| `shadow.subtle` | reserviert; default **kein CSS-Schatten** |
| `shadow.raised` | optional für schwebende Popups — nur wenn plattformüblich |
| `shadow.modal` | idem |

Wenn später Schatten: als **optionale** Theme-Property (String), nicht als Pflicht im Basisthema.

---

## STATE STYLING

Zustände sind **Kombination** aus Farb-Semantic + ggf. Border/Opacity:

| State | Farb-Hooks (Beispiele) | Nicht-Farb |
|-------|------------------------|------------|
| `state.hover` | `color.interaction.hover` | leichter BG-Wechsel |
| `state.pressed` | `color.interaction.pressed` | — |
| `state.selected` | `color.interaction.selected`, `color.fg.on_selected` | — |
| `state.focus` | `color.border.focus` oder `color.interaction.focus_ring` | `border.width.focus` |
| `state.disabled` | `color.fg.disabled`, `color.button.disabled.*` | reduzierte Kontrastregeln |
| `state.success` | `color.state.success` | Badges, Icons |
| `state.warning` | `color.state.warning` | — |
| `state.error` | `color.state.error` | — |

---

## Abgleich mit bestehendem Code

| Katalog | Code heute |
|---------|------------|
| `space.*` | `ThemeTokens.spacing_*`, `panel_padding`, `nav_item_padding_*` |
| `text.size.*` | `ThemeTokens.font_size_*` |
| `radius.*` | `ThemeTokens.radius_*` |
| `size.input.md` | `QComboBox min-height: 32px` in `base.qss` |
| `icon.size.*` | `IconManager` default 24, Workbench `icon-size: 18px` — **vereinheitlichen** |

---

*Siehe:* [DESIGN_COMPONENT_TOKEN_MAPPING.md](./DESIGN_COMPONENT_TOKEN_MAPPING.md), [DESIGN_TOKEN_DEFAULTS.md](./DESIGN_TOKEN_DEFAULTS.md).

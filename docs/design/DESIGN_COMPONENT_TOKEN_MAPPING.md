# Component → Design-Token-Mapping

**Konvention:** Pro Komponente: Typo, Spacing, Radius, Größe, Border, **color hooks** (semantic), **icon hooks** (Größe + state).

Farben verweisen auf [COLOR_USAGE_MAP.md](./COLOR_USAGE_MAP.md) und [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md).

---

## MainWindow (Shell)

| Aspekt | Tokens / Werte |
|--------|----------------|
| typography | — (erbt `text.role.body` für Kinder) |
| spacing | — |
| radius | — |
| size | — |
| borders | — |
| color hooks | `color.bg.app`, `color.fg.primary` |
| icon hooks | — |

---

## TopBar

| Aspekt | Tokens |
|--------|--------|
| typography | `text.role.section_title` für `#topBarAppTitle` |
| spacing | `space.md` vertikal, `space.lg` horizontal; `space.inline.gap.md` zwischen Gruppen |
| radius | — |
| size | implizit aus Padding + Inhalt |
| borders | `border.width.default` + `color.border.default` unten |
| color hooks | `color.nav.bg`, `color.fg.primary` |
| icon hooks | — |

---

## Sidebar (Hauptnavigation)

| Aspekt | Tokens |
|--------|--------|
| typography | `text.size.sm` Sektionsheader, `text.role.label` Items |
| spacing | Item `space.md`×`space.lg` Padding; `space.sidebar.item_gap` zwischen Einträgen |
| radius | `radius.md` Item |
| size | `size.sidebar.nav_item_min` |
| borders | `border.width.default` rechts, `color.border.default` |
| color hooks | `color.nav.*`, `color.interaction.hover`, `color.interaction.selected` |
| icon hooks | `icon.size.sm`, `icon.state.default` / `icon.state.active` wenn selektiert |

---

## Breadcrumbs

| Aspekt | Tokens |
|--------|--------|
| typography | `text.size.sm` |
| spacing | Kapsel `space.xs`×`space.sm`; Bar ohne Extra-Padding (flach) |
| radius | `radius.sm` |
| size | — |
| borders | Bar unten `border.default` |
| color hooks | `color.bg.surface_alt`, `color.fg.primary`, Hover `color.fg.link` |
| icon hooks | — |

---

## Workspace Host

| Aspekt | Tokens |
|--------|--------|
| typography | Titel `text.size.primary_title` + `text.weight.semibold`; Subtitle `text.size.sm` + `color.fg.secondary` |
| spacing | `space.panel.padding` für innere Content-Wrapper (Python) |
| radius | — |
| size | — |
| borders | — |
| color hooks | `color.bg.app` |
| icon hooks | kontextabhängig `icon.size.md` |

---

## Inspector

| Aspekt | Tokens |
|--------|--------|
| typography | Labels `text.size.sm` + `color.fg.secondary`; Werte `text.size.base` + `color.fg.primary`; GroupBox `text.role.panel_title` |
| spacing | `space.card.padding` innen; `space.stack.gap.md` zwischen Feldern |
| radius | Cards `radius.card` |
| size | `size.panel.header_height` für optionale Kopfzeile |
| borders | links `border.default`; Karten `border.default` |
| color hooks | `color.bg.surface_alt`, Fokus `color.border.focus` |
| icon hooks | `icon.size.sm` |

---

## Bottom Panel

| Aspekt | Tokens |
|--------|--------|
| typography | Tab `text.size.md`; Placeholder `text.size.sm` |
| spacing | Tab-Padding `space.md`×`space.lg`; Pane `space.panel.padding` |
| radius | — |
| size | Tab-Höhe ~ `size.tab.row` |
| borders | Tab-Pane oben `border.default` |
| color hooks | Host `color.bg.surface_alt`, Pane `color.bg.surface`, aktiver Tab `color.tab.active_*` |
| icon hooks | — |

---

## Cards (`#basePanel`, Settings-Karten, Workbench Section)

| Aspekt | Tokens |
|--------|--------|
| typography | Titel `text.role.section_title` |
| spacing | `space.card.padding` oder `space.panel.padding` je Kontext |
| radius | `radius.card` / `radius.xl` (Legacy-Angleichung) |
| size | — |
| borders | `border.width.default` + `color.border.default` |
| color hooks | `color.bg.surface` |
| icon hooks | — |

---

## Buttons (Standard / Secondary / Primary CTA)

| Aspekt | Tokens |
|--------|--------|
| typography | `text.size.md`, `text.weight.medium`; CTA `text.weight.semibold` |
| spacing | Padding `space.md`×`space.lg`; kompakt `space.sm`×`space.md` für Toolbars |
| radius | `radius.button` |
| size | `size.button.md` |
| borders | Sekundär `border.default`; Primär oft borderless |
| color hooks | `color.button.secondary.*`, `color.button.primary.*`, disabled `color.button.disabled.*` |
| icon hooks | `icon.size.sm` neben Text |

---

## Inputs (LineEdit, Combo, PlainText / Composer)

| Aspekt | Tokens |
|--------|--------|
| typography | `text.size.md` |
| spacing | Padding `space.md`×`space.lg` (Combo ggf. `space.sm`×`space.md`) |
| radius | `radius.input` |
| size | `size.input.md` |
| borders | `border.width.default` + `color.input.border`; Fokus `color.input.border_focus` |
| color hooks | `color.input.bg`, `color.input.fg` |
| icon hooks | — |

---

## Tables

| Aspekt | Tokens |
|--------|--------|
| typography | Header `text.size.sm` + `text.weight.semibold` |
| spacing | Zellen-Padding `space.md`×`space.lg` |
| radius | — (Tabelle meist eckig) |
| size | Zeile min ~ `size.sidebar.nav_item_min` |
| borders | Grid `color.table.grid` |
| color hooks | `color.table.*`, Selection `color.table.selection_*` |
| icon hooks | `icon.size.xs` in Zellen optional |

---

## Trees (Explorer, generisch)

| Aspekt | Tokens |
|--------|--------|
| typography | `text.size.sm` |
| spacing | Item-Padding `space.2xs`×`space.sm` oder `space.sm` horizontal — **Ziel:** vereinheitlicht |
| radius | `radius.sm` |
| size | `size.sidebar.nav_item_min` |
| borders | keine / transparent |
| color hooks | `color.bg.panel`, Selection wie Nav |
| icon hooks | `icon.size.sm` |

---

## Tabs (Workbench Canvas)

| Aspekt | Tokens |
|--------|--------|
| typography | `text.size.sm`, selected `text.weight.semibold` |
| spacing | `space.sm`×`space.lg`, Tab-Abstand `space.2xs` |
| radius | `radius.md` oben |
| size | `min-width` eher `size`-Token in `em` sparsam behalten |
| borders | `color.tab.*`, Pane `color.border.default` |
| color hooks | vollständig über `color.tab.*` |
| icon hooks | Close `icon.size.xs` |

---

## Dialogs

| Aspekt | Tokens |
|--------|--------|
| typography | Titel `text.role.window_title` oder `text.size.lg` |
| spacing | `space.dialog.padding` |
| radius | `radius.dialog` (Fenster-Decko abhängig vom WM) |
| size | `size.dialog.min_width` |
| borders | — |
| color hooks | `color.bg.window`, `color.fg.primary` |
| icon hooks | `icon.size.md` in Header optional |

---

## Menus

| Aspekt | Tokens |
|--------|--------|
| typography | `text.size.md` |
| spacing | Eintrag-Padding wie `space.sm`×`space.md` |
| radius | plattformtypisch |
| size | — |
| borders | `color.border.default` |
| color hooks | Menu BG/FG, Hover `color.interaction.hover` |
| icon hooks | `icon.size.sm` |

---

## Tooltips

| Aspekt | Tokens |
|--------|--------|
| typography | `text.size.sm` |
| spacing | `space.xs`×`space.sm` |
| radius | `radius.sm` |
| size | — |
| borders | `border.width.default` |
| color hooks | dedizierte Tooltip-Surface (siehe THEME_TOKEN_SPEC) |
| icon hooks | selten `icon.size.xs` |

---

## Chat Bubbles

| Aspekt | Tokens |
|--------|--------|
| typography | Role `text.size.sm` semibold; Content `text.size.md` |
| spacing | `space.md`×`space.lg`; Stack `space.stack.gap.sm` zwischen Blasen |
| radius | `radius.xl` |
| size | max-width Policy im Widget |
| borders | User `color.chat.user_border`; Assistant `color.chat.assistant_border` |
| color hooks | `color.chat.user_*`, `color.chat.assistant_*`, System `color.chat.system_*` |
| icon hooks | Status `icon.size.xs` + `icon.state.*` |

---

## Markdown

| Aspekt | Tokens |
|--------|--------|
| typography | Body `text.size.base`/`md`, Code `font.family.mono`, Links `color.fg.link` |
| spacing | Absatz `space.stack.gap.md`; Listen gemäß Spec im Renderer aus Metriken |
| radius | Code-Blöcke `radius.sm` |
| size | — |
| borders | Blockquote links `color.border.default` |
| color hooks | `color.markdown.*` falls definiert; sonst `color.fg.*` |
| icon hooks | — |

---

## Status / Badges

| Aspekt | Tokens |
|--------|--------|
| typography | `text.size.xs`–`text.size.sm`, `text.weight.medium` |
| spacing | Chip-Padding `space.2xs`×`space.sm` |
| radius | `radius.badge` |
| size | auto |
| borders | semantic 1px |
| color hooks | `color.badge.*` / `color.state.*` |
| icon hooks | `icon.size.xs` + passender `icon.state.*` |

---

## Monitoring Panels (Runtime / Debug)

| Aspekt | Tokens |
|--------|--------|
| typography | Wie Sidebar; Titel auf `text.size.sm` + Monitoring-FG (kein separates px-Override) |
| spacing | wie Haupt-Sidebar |
| radius | wie Sidebar |
| size | gleiche Nav-Mindesthöhe |
| borders | `color.domain.monitoring.*` für Ränder |
| color hooks | `color.domain.monitoring.bg/surface/border/text/accent` |
| icon hooks | `icon.size.sm`, States wie global |

---

## Workbench-spezifisch (Toolbar, Palette, Konsole)

| Komponente | Kurz-Mapping |
|------------|----------------|
| Toolbar | `space.toolbar.gap`, `size.icon.md`, `color.bg.surface`, `radius.sm` Buttons |
| Command Palette | `space.dialog.padding`, Suche `border.width.focus`, Liste `size.input.md` Zeilenhöhe |
| Konsole | `font.family.mono`, `text.size.sm`, `radius.sm`, `color.console.*` für Logs |

---

*Implementierung:* Runtime-Layer `app/gui/theme/`, Migration [DESIGN_TOKEN_MIGRATION_PLAN.md](./DESIGN_TOKEN_MIGRATION_PLAN.md).

# Default Accent Strategy

**Entscheidung:** Die Standard-Produktpalette nutzt **Slate + Teal** — ruhige neutrale Flächen, dezentes **Teal** als einheitlicher Interaktions-Faden (Fokus, Links, Primary-Button, Accent-State).  
**Alternativ abgelehnt für Default:** Reines **Blue** — höhere Verwechslungsgefahr mit generischen „Office-Blue“-UIs und mit **Info**-Semantic.

---

## 1. Rollen → Tokens

| Rolle | Kanonischer Token | Legacy QSS-Key (Beispiel) |
|-------|-------------------|---------------------------|
| Primary | `color.state.accent` | `color_accent` |
| Hover | `color.state.accent_hover` | `color_accent_hover` |
| Pressed / Active | `color.state.accent_pressed` oder aktives Dunkel | `color_button_primary_pressed` leitet aus Palette ab |
| Muted Fläche (Selektionstint) | `color.state.accent_muted_bg` | `color_accent_bg` |

`color.fg.link` ist **semantisch** „Link“, wird in der Resolver-Kette zunächst aus dem Accent gespeist; künftig darf Link leicht gedämpfter sein als Button-Accent.

---

## 2. Default-Werte (implementiert: `light_default`)

| Stufe | Hex | Hinweis |
|-------|-----|---------|
| **Primary** | `#0f766e` | Teal 700 — ruhig, gut auf hellen Flächen |
| **Hover** | `#0d9488` | Teal 600 |
| **Pressed / Active** | `#115e59` | Teal 800 |
| **Muted BG** | `#ccfbf1` | Teal 100 — u. a. User-Bubble-Rahmen, Chips |
| **Selektion Zeile** | `bg_selected` `#99f6e4` + `fg_on_selected` `#134e4a` | Gleiches Hue-Fenster wie Accent, weniger Sättigung als CTA |

Quelle: `light_semantic_profile()` in `app/gui/themes/builtin_semantic_profiles.py`.

---

## 3. Default-Werte (implementiert: `dark_default`)

| Stufe | Hex | Hinweis |
|-------|-----|---------|
| **Primary** | `#2dd4bf` | Teal 300 — lesbar auf dunklen Surfaces |
| **Hover** | `#5eead4` | Teal 200 |
| **Pressed / Active** | `#14b8a6` | Teal 500 |
| **Muted BG** | `#115e59` | Teal 800 |
| **On-Accent-Text** | `#042f2e` | Dunkel auf heller CTA |
| **Selektion** | `bg_selected` `#134e4a` + `fg_on_selected` `#ecfdf5` |

Quelle: `dark_semantic_profile()` in `app/gui/themes/builtin_semantic_profiles.py`.

---

## 4. Fokus-Ring

- Light: `focus_ring` `#0d9488` (an Hover gekoppelt, gut sichtbar).  
- Dark: `focus_ring` `#2dd4bf` (Primary gleich, konsistent).

Fokus nutzt in QSS bevorzugt `color_border_focus` / `color_input_border_focus`, nicht Roh-`color_accent` auf großen Flächen.

---

## 5. Abgrenzung

- **Workbench-Theme** (`workbench`) bleibt eigenes Profil (cyan-lastig) — für Canvas-fokussierte Ansichten.  
- **Emerald / Purple** sind dokumentierte Varianten in [THEME_COLOR_PALETTES.md](./THEME_COLOR_PALETTES.md); Registrierung als weitere `ThemeDefinition` optional.

---

*Ende Default Accent Strategy.*

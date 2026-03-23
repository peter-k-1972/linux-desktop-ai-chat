# Color System — Final Strategy

**Status:** Leitdokument zur GUI-Farbstrategie (Linux Desktop Chat / Obsidian Core).  
**Detail-Dokumente:** [DEFAULT_ACCENT_STRATEGY.md](./DEFAULT_ACCENT_STRATEGY.md), [ACCENT_USAGE_RULES.md](./ACCENT_USAGE_RULES.md), [THEME_COLOR_PALETTES.md](./THEME_COLOR_PALETTES.md), [CHART_COLOR_PALETTE.md](./CHART_COLOR_PALETTE.md), [SEMANTIC_COLOR_USAGE.md](./SEMANTIC_COLOR_USAGE.md).

---

## 1. Ziele

- **Ruhige GUI** — ca. 90 % neutrale Flächen.  
- **Klare Interaktion** — ca. 7 % Accent nur auf Selektion, Fokus, eine Primary-CTA, Links.  
- **Hohe Wiedererkennbarkeit** — **ein** Accent-Kanal im Haupt-Chrome; kein paralleles „Zweit-Blau“ in benachbarten Navs.  
- **Semantic getrennt** — ca. 3 % für Status (Success, Warning, Error, Info).

---

## 2. Default Accent

- **Familie:** **Slate + Teal** (siehe [DEFAULT_ACCENT_STRATEGY.md](./DEFAULT_ACCENT_STRATEGY.md)).  
- **Implementierung:** `light_semantic_profile()` / `dark_semantic_profile()` in `app/gui/themes/builtin_semantic_profiles.py`.  
- **Primary / Hover / Pressed:** dort tabellarisch; Fokus-Ring an Hover/Primary gekoppelt.

---

## 3. Neutral Palette

- Struktur und Hex: **Abschnitt 0** in [THEME_COLOR_PALETTES.md](./THEME_COLOR_PALETTES.md) (`bg.app`, `surface`, `surface_alt`, `surface_elevated`, `border`, `fg.primary|secondary|muted`).  
- **Technisch:** `SemanticPalette` → `semantic_palette_to_theme_tokens` → QSS `{{color_*}}`.

---

## 4. Semantic Palette

- Unverändert aus `SemanticPalette.status_*` + Badge-/Console-Tokens.  
- **Regeln:** [SEMANTIC_COLOR_USAGE.md](./SEMANTIC_COLOR_USAGE.md).  
- Accent **ersetzt** keine Fehler-/Warnfarben.

---

## 5. Chart Palette

- **Nicht** accent-basiert; eigene Serienfarben (Indigo / Orange / Violet …).  
- Vorschlagswerte: [CHART_COLOR_PALETTE.md](./CHART_COLOR_PALETTE.md).  
- Code: Chart-Tokens in `canonical_token_ids.py` — Werte künftig in Theme-Resolve befüllen, wenn Charts produktiv nutzen.

---

## 6. Theme Variants

| Theme | Rolle |
|-------|--------|
| `light_default` | Standard Hell — Teal Accent |
| `dark_default` | Standard Dunkel — Teal Accent |
| `workbench` | Canvas-fokussiert, cyan-lastig |
| *Emerald* / *Purple* | Spezifikation in [THEME_COLOR_PALETTES.md](./THEME_COLOR_PALETTES.md), Registrierung optional |

---

## 7. Accent Usage Rules (Kurzfassung)

- **Ein-Kanal-Modell:** Alle Haupt-Nav-Selektionen (inkl. Control Center & QA) → `nav_selected_*`.  
- **Fokus:** `border_focus` / `input_border_focus`, nicht Vollflächen-Accent.  
- **CTA:** `button_primary_*` in QSS.  
- **Links / Breadcrumb-Hover:** `color_fg_link`.  
- **Tab-Indikator (Spec-Default):** neutral (`border_medium`), nicht Brand-Accent (`resolved_spec_tokens.py`).  
- **Runtime/Debug:** eigener Monitoring-Palette-Raum.  

Vollständig: [ACCENT_USAGE_RULES.md](./ACCENT_USAGE_RULES.md).

---

## 8. Code-Änderungen (Umsetzung dieser Strategie)

| Bereich | Änderung |
|---------|----------|
| `assets/themes/base/shell.qss` | CC-Nav = `nav_selected_*`; Breadcrumb-Hover = `color_fg_link`; Project Switcher Hover-Rand = `color_border_focus`; Chat-Nav + Chat-Input Fokus/CTA = `input_border_focus` / `button_primary_*`; Chat-Nav-Block aus Duplikat übernommen |
| `app/gui/themes/palette_resolve.py` | `color_qa_nav_selected_*` = `color_nav_selected_*` |
| `app/gui/themes/resolved_spec_tokens.py` | `TAB_INDICATOR` default → neutral |
| `app/gui/themes/builtin_semantic_profiles.py` | Light/Dark → Slate+Teal Accent + angepasste Selektion |

---

*Ende Final Strategy.*

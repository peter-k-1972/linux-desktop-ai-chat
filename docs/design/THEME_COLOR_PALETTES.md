# Theme Color Palettes

Übersicht der **Paletten-Rollen** und konkreter Hex-Werte. **Implementiert** in `ThemeRegistry`: `light_default`, `dark_default`, `workbench`. **Emerald** und **Purple** sind **Spezifikation** für zusätzliche Themes (gleiche `SemanticPalette`-Struktur).

---

## 0. Neutrale Struktur (Light / Dark identisch im Aufbau)

Ziel: **ruhige Oberfläche** — gleiche Hierarchie der Ebenen, nur Luminanz invertiert.

| Token (Spec) | Rolle | Light (`light_default`) | Dark (`dark_default`) |
|--------------|-------|-------------------------|------------------------|
| `color.bg.app` | Fenster-Canvas, Workspace-Host | `#e8edf3` | `#0a0f1a` |
| `color.bg.surface` | Karten, Eingabe-Innenfläche | `#ffffff` | `#1a2438` |
| `color.bg.surface_alt` | Inspector-muted, Breadcrumb-Leiste | `#f1f5f9` (`bg_elevated`) | `#243047` |
| `color.bg.surface_elevated` | Tabellenkopf, leichte Erhebung | `#f1f5f9` | `#243047` |
| `color.border.default` | Standard-Ränder | `#94a3b8` | `#475569` |
| `color.border.subtle` | dezente Trenner | `#cbd5e1` | `#334155` |
| `color.fg.primary` | Fließtext, Titel | `#0f172a` | `#f8fafc` |
| `color.fg.secondary` | Metadaten | `#475569` | `#cbd5e1` |
| `color.fg.muted` | Platzhalter, Randtext | `#64748b` | `#94a3b8` |

*Hinweis:* `surface_alt` wird im Resolver aus `bg_elevated` / Legacy `color_bg_muted` gespeist — siehe `resolved_spec_tokens.py`.

---

## 1. Default Light (`light_default`)

| Rolle | Hex | Token (semantic) |
|-------|-----|------------------|
| App | `#e8edf3` | `bg_app` |
| Panel / Nav | `#dce4ee` | `bg_panel` |
| Surface | `#ffffff` | `bg_surface` |
| Elevated / muted BG | `#f1f5f9` | `bg_elevated` |
| Accent Primary | `#0f766e` | `accent_primary` |
| Accent Hover | `#0d9488` | `accent_hover` |
| Accent Active | `#115e59` | `accent_active` |
| Accent Muted BG | `#ccfbf1` | `accent_muted_bg` |
| Selected row BG | `#99f6e4` | `bg_selected` |
| On selected FG | `#134e4a` | `fg_on_selected` |
| Success / Warning / Error | `#059669` / `#d97706` / `#dc2626` | `status_*` |

---

## 2. Default Dark (`dark_default`)

| Rolle | Hex | Token (semantic) |
|-------|-----|------------------|
| App | `#0a0f1a` | `bg_app` |
| Panel | `#121a2c` | `bg_panel` |
| Surface | `#1a2438` | `bg_surface` |
| Elevated | `#243047` | `bg_elevated` |
| Accent Primary | `#2dd4bf` | `accent_primary` |
| Accent Hover | `#5eead4` | `accent_hover` |
| Accent Active | `#14b8a6` | `accent_active` |
| Accent Muted BG | `#115e59` | `accent_muted_bg` |
| On Accent FG | `#042f2e` | `fg_on_accent` |
| Selected row BG | `#134e4a` | `bg_selected` |
| On selected FG | `#ecfdf5` | `fg_on_selected` |

---

## 3. Workbench (`workbench`) — Kurz

Eigenes dunkles Profil, stärker **Cyan/Teal** (`accent_primary` `#22d3ee`, …). Für Workbench-Canvas; nicht identisch mit Default Dark.

---

## 4. Emerald Theme (Spezifikation, optional registrieren)

Ruhige **Grün-Accent**-Variante; Success-Semantic **nicht** identisch mit Accent (Success dunkler/satter).

| Rolle | Light (Vorschlag) | Dark (Vorschlag) |
|-------|-------------------|------------------|
| Accent Primary | `#047857` | `#34d399` |
| Accent Hover | `#059669` | `#6ee7b7` |
| Accent Active | `#065f46` | `#10b981` |
| Accent Muted BG | `#d1fae5` | `#064e3b` |

Neutralstufen wie Default übernehmen, nur `accent_*` + ggf. `focus_ring` anpassen; **Kontrast-Tests** mit `semantic_validation.validation_errors` Pflicht.

---

## 5. Purple Theme (Spezifikation, optional registrieren)

**Violet** als Accent; Semantic-Farben unverändert aus Default übernehmen.

| Rolle | Light (Vorschlag) | Dark (Vorschlag) |
|-------|-------------------|------------------|
| Accent Primary | `#6d28d9` | `#a78bfa` |
| Accent Hover | `#7c3aed` | `#c4b5fd` |
| Accent Active | `#5b21b6` | `#8b5cf6` |
| Accent Muted BG | `#ede9fe` | `#4c1d95` |

`fg_on_accent` in Light typisch `#ffffff`, in Dark ggf. `#1e1b4b` — je nach Kontrastmessung.

---

## 6. Implementierung

1. Neue `SemanticPalette`-Instanz (oder Kopie von `light_semantic_profile` mit Overrides).  
2. `assert_palette_accessible(palette)` in Tests.  
3. `ThemeRegistry.register(ThemeDefinition(..., tokens=semantic_palette_to_theme_tokens("…", palette)))` — `ProfileKey` in `palette_resolve` ggf. erweitern, wenn domain-spezifische Overrides nötig sind.

---

*Ende Theme Palettes.*

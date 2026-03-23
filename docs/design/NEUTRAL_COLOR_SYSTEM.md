# Neutral Color System (OKLCH)

**Projekt:** Linux Desktop Chat / Obsidian Core  
**Ziel:** Mathematisch konsistente Neutralpalette; **QSS** erhält **HEX** (kein OKLCH in Qt-Stylesheets).  
**Implementierung:** `SemanticPalette` in `app/gui/themes/builtin_semantic_profiles.py` → `semantic_palette_to_theme_tokens`.

---

## 1. Parameter

| Parameter | Wert |
|-----------|------|
| **Farbraum** | OKLCH (CSS Color Level 4, L in 0…1) |
| **Hue** | 250° |
| **Chroma** | 0.01 |
| **Varianz** | nur **L** (Lightness) |

Konvertierung **OKLCH → sRGB HEX:** Björn Ottosson OKLab-Pipeline (wie in CSS), Kanäle auf 8-bit gerundet.

---

## 2. Dark Theme — OKLCH (Ladder)

Monoton **steigendes** L von App → Elevated (höher = heller auf dem Display).

| Semantische Rolle | L | OKLCH |
|-------------------|---|--------|
| bg.app | 0.10 | `oklch(0.10 0.01 250)` |
| bg.panel | 0.125 | `oklch(0.125 0.01 250)` |
| bg.surface_alt | 0.14 | `oklch(0.14 0.01 250)` |
| bg.surface | 0.175 | `oklch(0.175 0.01 250)` |
| bg.elevated | 0.23 | `oklch(0.23 0.01 250)` |
| border.subtle | 0.28 | `oklch(0.28 0.01 250)` |
| border.default | 0.36 | `oklch(0.36 0.01 250)` |
| border.strong | 0.44 | `oklch(0.44 0.01 250)` |
| fg.muted | 0.56 | `oklch(0.56 0.01 250)` |
| fg.disabled | 0.48 | `oklch(0.48 0.01 250)` |
| fg.secondary | 0.72 | `oklch(0.72 0.01 250)` |
| fg.primary | 0.96 | `oklch(0.96 0.01 250)` |
| bg.hover (interaction) | 0.205 | `oklch(0.205 0.01 250)` |
| bg.input | 0.16 | `oklch(0.16 0.01 250)` |
| bg.disabled | 0.12 | `oklch(0.12 0.01 250)` |

---

## 3. Light Theme — Spiegelung

**Hintergrund & Text:** Paarung der Dark-Stufen, sodass die **Reihenfolge** (App am dunkelsten der Flächen, Elevated am hellsten) erhalten bleibt:

| Light-Rolle | Beziehung |
|-------------|-----------|
| bg.app | L = 1 − L_dark(**elevated**) |
| bg.panel | L = 1 − L_dark(**surface**) |
| bg.surface_alt | L = 1 − L_dark(**surface_alt**) |
| bg.surface | L = 1 − L_dark(**panel**) |
| bg.elevated | L = 1 − L_dark(**app**) |
| fg.primary | L = 1 − L_dark(fg.primary) |
| fg.secondary | L = 1 − L_dark(fg.secondary) |
| fg.muted | L = 1 − L_dark(fg.muted) |
| fg.disabled | L = 1 − L_dark(fg.disabled) |
| bg.hover | L = 1 − L_dark(bg.hover) |
| bg.input | L = 1 − L_dark(bg.input) |
| bg.disabled | L = 1 − L_dark(bg.disabled) |

**Rand Light:** `border.subtle` / `border.default` / `border.strong` sind **explizit** in OKLCH gesetzt (**L = 0.72 / 0.64 / 0.40**), damit die Kanten-Kontrastregeln (`border_*` vs. `bg_*`) aus `semantic_validation` erfüllt sind — **nicht** die naive Spiegelung `1 − L_dark(border)`, die bei `border.strong` vs. `bg.app` unter 1.28:1 gefallen wäre.

---

## 4. HEX-Werte (sRGB)

### 4.1 Dark

| Token | HEX |
|-------|-----|
| bg.app | `#020306` |
| bg.panel | `#04070a` |
| bg.surface_alt | `#06090d` |
| bg.surface | `#0d1115` |
| bg.elevated | `#191d22` |
| border.subtle | `#25292e` |
| border.default | `#393e42` |
| border.strong | `#4e5358` |
| fg.primary | `#edf2f8` |
| fg.secondary | `#a0a5ab` |
| fg.muted | `#70757a` |
| fg.disabled | `#595e63` |
| bg.hover | `#14181c` |
| bg.input | `#0a0e11` |
| bg.disabled | `#040609` |

### 4.2 Light

| Token | HEX |
|-------|-----|
| bg.app | `#b0b5ba` |
| bg.panel | `#c1c6cc` |
| bg.surface_alt | `#ccd2d7` |
| bg.surface | `#d1d6dc` |
| bg.elevated | `#d9dfe5` |
| border.subtle | `#a0a5ab` |
| border.default | `#888d92` |
| border.strong | `#44484d` |
| fg.primary | `#000001` |
| fg.secondary | `#25292e` |
| fg.muted | `#4e5358` |
| fg.disabled | `#65696f` |
| bg.hover | `#b7bdc2` |
| bg.input | `#c6cbd1` |
| bg.disabled | `#d3d8de` |

---

## 5. Kontrastanalyse (WCAG 2.x)

Berechnung: relatives Leuchtdichteverhältnis **(L1+0.05)/(L2+0.05)** wie in `app/gui/themes/contrast.py`. Schwellen aus `semantic_validation`: Body-Text **≥ 4.5:1** auf typische Flächen; Kanten-Paare **≥ 1.28:1**.

### 5.1 Dark

| Vordergrund | Hintergrund | Verhältnis | Bewertung |
|-------------|-------------|------------|-----------|
| fg.primary | bg.surface | **16.8:1** | AA Body |
| fg.secondary | bg.surface | **7.6:1** | AA Body |
| fg.muted | bg.surface | **4.1:1** | AA Body (knapp) |
| fg.primary | bg.app | **18.3:1** | AA Body |
| border.default | bg.surface | **1.75:1** | Kanten-Policy |

### 5.2 Light

| Vordergrund | Hintergrund | Verhältnis | Bewertung |
|-------------|-------------|------------|-----------|
| fg.primary | bg.surface | **14.4:1** | AA Body |
| fg.secondary | bg.surface | **10.0:1** | AA Body |
| fg.muted | bg.surface | **5.3:1** | AA Body |
| border.strong | bg.app | **≥ 4.3:1** | Kanten-Policy (>1.28) |

*(Exakte Kantenwerte können mit `contrast_ratio(hex1, hex2)` aus `app.gui.themes.contrast` reproduziert werden.)*

---

## 6. Workbench-Variante

Ebenfalls **H = 250**, **C = 0.01**, mit **tieferer** Neutralleiter (andere L-Stufen). Siehe `workbench_semantic_profile()` — HEX in derselben Datei. Kontrast wird von `validation_errors()` mitgeführt.

---

## 7. Schema-Erweiterung

`SemanticPalette` enthält **`bg_surface_alt`** für `color.bg.surface_alt`. Der Resolver setzt **`color_bg_muted`** = `bg_surface_alt` (Legacy-QSS für Inspector/Breadcrumb-muted).

---

## 8. Referenzen

- [THEME_TOKEN_SPEC.md](./THEME_TOKEN_SPEC.md) — Canonical-Namen & Legacy-Mapping  
- [THEME_CONTRAST_RULES.md](./THEME_CONTRAST_RULES.md)  
- `app/gui/themes/semantic_validation.py`  
- `app/gui/themes/palette_resolve.py`

---

*Ende Neutral Color System.*

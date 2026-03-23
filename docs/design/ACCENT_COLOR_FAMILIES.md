# Accent Color Families (Vorschläge)

**Produkt-Default:** **Slate + Teal** — siehe [DEFAULT_ACCENT_STRATEGY.md](./DEFAULT_ACCENT_STRATEGY.md) und [COLOR_SYSTEM_FINAL_STRATEGY.md](./COLOR_SYSTEM_FINAL_STRATEGY.md).

**Zweck:** Bewerbbare **Accent-Familien** für Themes — jeweils mit **Primary**, **Hover**, **Pressed** (und optional **Muted Background** für selektierte Zeilen).

Alle Werte sind **konzeptionell**; konkrete Hex kommen in Theme-JSON/Spec (`THEME_TOKEN_SPEC.md`, Resolver).  
Mapping zu Tokens: `color.state.accent` → Primary, `color.state.accent_hover`, `color.state.accent_pressed`, `color.state.accent_muted_bg`.

---

## 1. Blue (Standard / „Trust & Focus“)

| Rolle | Verwendung |
|-------|------------|
| **Primary** | Fokus, Links, aktive Tab-Indikatoren, Primary Button |
| **Hover** | +5–8 % Luminanz oder leicht gesättigter |
| **Pressed** | −5–10 % Luminanz, klarer Druck |

Geeignet für: Produktivitätstools, hohe Vertrautheit, gute Kontrast-Optionen in Hell/Dunkel.

---

## 2. Emerald („Calm Success-adjacent“)

| Rolle | Verwendung |
|-------|------------|
| **Primary** | Dezenter als klassisches Grün; nicht mit **Semantic Success** identisch |
| **Hover** | Tieferes Smaragd |
| **Pressed** | Noch eine Stufe dunkler |

**Wichtig:** `STATE_SUCCESS` / `BADGE_SUCCESS` separat halten — Accent Emerald **nicht** 1:1 für Erfolgsmeldungen verwenden.

---

## 3. Amber („Warm Attention“)

| Rolle | Verwendung |
|-------|------------|
| **Primary** | Auffälliger als Blau; sparsam einsetzen |
| **Hover** | Gold/Gelb-Ton |
| **Pressed** | Dunkleres Amber |

Geeignet für: Markenwärme; **nicht** mit **Warning**-Semantic vermischen (eigene Hue-Abstände im OKLCH).

---

## 4. Purple / Violet („Studio / Creative“)

| Rolle | Verwendung |
|-------|------------|
| **Primary** | Unterscheidung von Standard-Blue-IDEs |
| **Hover** | Aufgehellt oder mehr Sättigung |
| **Pressed** | Gedämpft dunkel |

Geeignet für: KI-/Canvas-lastige Oberflächen, wenn Blau zu „generisch“ wirkt.

---

## 5. Slate + Teal („Neutral-dominant Accent“)

| Rolle | Verwendung |
|-------|------------|
| **Primary** | Gedämpftes Teal auf fast neutralem UI |
| **Hover** | Etwas mehr Sättigung |
| **Pressed** | Dunkleres Teal |

Geeignet für: **Sehr ruhige** GUI mit minimalem Farb-Footprint (nähert sich 90 %-Neutral-Ziel an).

---

## 6. Token-Zuordnung (alle Familien gleich)

| UI-Zustand | Kanonischer Token |
|------------|-------------------|
| Accent Basis | `color.state.accent` |
| Hover | `color.state.accent_hover` |
| Pressed | `color.state.accent_pressed` |
| Selektion-Hintergrund (tinted) | `color.state.accent_muted_bg` |
| Primary Button | `color.button.primary.bg` (+ hover/pressed) — typischerweise an Accent gekoppelt |
| Fokus-Rand | `color.border.focus` / `color.input.border_focus` — oft Accent-nah, muss Kontrast erfüllen |

---

## 7. Empfehlung fürs Repo

- **Default-Light / Default-Dark:** **Blue** oder **Slate+Teal** (ruhig).  
- **Alternativ-Theme (z. B. „Obsidian“-Anmutung):** **Purple** mit strenger Accent-Allowlist.  
- **Amber** nur als zweites registriertes Theme, nicht als einzige Produktionsfarbe, wenn Warnungen ebenfalls gelb-orange sind — Konflikt vermeiden.

---

*Ende Accent-Familien.*

# Chart Color Palette

**Ziel:** Datenvisualisierungen lesbar und unterscheidbar, **ohne** die Marken-Accent-Farbe zu spiegeln — vermeidet „alles sieht wie ein CTA aus“ und hält das **90/7/3**-Ziel ein.

**Token-Ziel:** `color.chart.series.1` … `color.chart.series.other` (siehe `ThemeTokenId` in `canonical_token_ids.py`). Werte in Themes als **eigenständige** Hex setzen, **nicht** aus `color.state.accent` ableiten.

---

## 1. Prinzipien

1. **Serien ≠ Accent:** Kein Teal/Accent aus `DEFAULT_ACCENT_STRATEGY` für erste Serie verwenden, wenn dieselbe Farbe Primary-Buttons trägt.  
2. **Light vs. Dark:** Pro Theme eigene Chart-Tabelle; gleiche **Abstandshaltung** (Sättigung moderat).  
3. **Farbenblindheit:** Nicht nur Hue wechseln — Helligkeit zwischen Serien differenzieren; Linien + Muster wo möglich.  
4. **Semantic-Charts:** Wenn ein Chart „gut/schlecht“ zeigt, explizit `status_success` / `status_error` nutzen — nicht Chart-Serien-1/2.

---

## 2. Vorschlag Default Light — Serien

| Serie | Hex | Beschreibung |
|-------|-----|--------------|
| 1 | `#6366f1` | Indigo — klar von Teal-Accent entfernt |
| 2 | `#ea580c` | Orange |
| 3 | `#7c3aed` | Violet |
| Other / Rest | `#64748b` | Slate neutral |

**Achsen / Raster:** `color.chart.axis` → `fg_secondary` oder `border_default`; `color.chart.grid` → `border_subtle`.  
**Hintergrund:** `color.chart.bg` → `bg_surface` oder transparent.

---

## 3. Vorschlag Default Dark — Serien

| Serie | Hex |
|-------|-----|
| 1 | `#818cf8` |
| 2 | `#fb923c` |
| 3 | `#c4b5fd` |
| Other | `#94a3b8` |

---

## 4. Abgleich mit Accent (Default Teal)

| | Accent (Light) | Chart Serie 1 |
|--|----------------|---------------|
| Hex | `#0f766e` | `#6366f1` |

Klare Hue-Distanz → Chart wirkt **datengetrieben**, UI wirkt **interaktiv**.

---

## 5. Nächster Code-Schritt (optional)

- In `semantic_palette` / `palette_resolve` optionale Felder `chart_series_1` … ergänzen oder in Theme-JSON auslagern.  
- `resolved_spec_tokens` mappt bereits `CHART_SERIES_*` — Werte mit obiger Tabelle füllen, wenn Serien in UI genutzt werden.

---

*Ende Chart Palette.*

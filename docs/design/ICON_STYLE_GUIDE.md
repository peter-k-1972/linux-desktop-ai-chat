# Icon Style Guide

**Format:** SVG (skalierbar, `currentColor` für Theme-Anbindung)  
**Raster:** **24×24** px logischer Viewbox  
**Strich:** **1.5** px (`stroke-width="1.5"`)  
**Stil:** **Outline** (keine Vollflächen-Fills für Glyphen; Hintergrund transparent)  
**Ecken:** **round** (`stroke-linecap="round"`, `stroke-linejoin="round"`)

## Mindest-Template

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"
     fill="none" stroke="currentColor" stroke-width="1.5"
     stroke-linecap="round" stroke-linejoin="round">
  <!-- paths -->
</svg>
```

## Regeln

1. **Keine festen Fill-Farben** für UI-Icons — nur `currentColor`, damit `IconManager` einfärben kann.  
2. **Optische Gewichtung:** 1.5 px wirkt auf HiDPI konsistent; bei sehr dichten Glyphen maximal 2.0, dann global anheben.  
3. **Padding:** ca. 2 px „Leerfeld“ zum ViewBox-Rand (Icon wirkt nicht gequetscht).  
4. **Benennung:** `kleinbuchstaben_mit_unterstrich.svg` oder `konzept.svg` — pro Ordner eindeutig.  
5. **Ordner:** siehe `ICON_TAXONOMY.md` (`navigation`, `objects`, `actions`, `states`, `ai`, `workflow`, `data`, `monitoring`, `system`).

## Export / QA

- In Browser oder Viewer bei 100 % auf 24 px prüfen.  
- Auf hellem **und** dunklem Hintergrund mit Theme-`color_text` testen.  
- Keine eingebetteten Rastergrafiken.  
- Automatisiert: `python3 tools/icon_svg_guard.py` (`resources/icons/`), aggregiert `python3 tools/run_icon_guards.py` → `ICON_GUARD_REPORT.md`.

---

**Canonical Pfad (neu):** `resources/icons/<category>/<name>.svg` (Projektroot).  
**Fallback:** `assets/icons/svg/…` bleibt bis vollständiger Cutover.

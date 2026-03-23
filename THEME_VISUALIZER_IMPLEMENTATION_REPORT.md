# Theme Visualizer — Implementierungsbericht

## Neue Dateien

| Datei | Rolle |
|-------|--------|
| `tools/theme_visualizer.py` | CLI-Einstieg, `sys.path`-Anpassung, startet PySide6-Fenster |
| `app/devtools/__init__.py` | Paket-Markierung |
| `app/devtools/theme_visualizer_window.py` | Hauptfenster: Steuerung, Token-Panel, Kontrast-Liste, Inspektor |
| `app/devtools/theme_preview_widgets.py` | Komponenten-Vorschau (`ThemeComponentPreview`) |
| `app/devtools/theme_token_groups.py` | Gruppierung der kanonischen Token-IDs (ohne Farbwerte) |
| `app/devtools/theme_contrast.py` | Paar-Definitionen und grobe Bewertung (nutzt `app.gui.themes.contrast`) |
| `tests/tools/test_theme_visualizer_smoke.py` | Smoke-Test |
| `docs/devtools/THEME_VISUALIZER.md` | Bedienungsanleitung |

## Geänderte Dateien

Keine bestehenden Produktiv-Dateien wurden angepasst.

## Integrierte Theme-Schnittstellen

- `get_theme_manager()` — `set_theme`, `list_themes`, `get_tokens`, `color`, `get_current_id`
- `load_stylesheet` (indirekt über `ThemeManager.set_theme` → globales QSS)
- `ThemeTokenId` / `flat_key` — kanonische Namen und flache Keys
- `contrast_ratio` / `relative_luminance` aus `app/gui/themes/contrast.py`

## Bekannte Grenzen

- Kontrastfarben in der Kontrast-**Liste** nutzen Status-Tokens (`STATE_SUCCESS` / `WARNING` / `ERROR`) als Listen-Vordergrund — lesbarkeit hängt vom aktiven Theme ab.
- Kein Datei-Hot-Reload für Theme-Assets.
- Vergleichsmodus (zwei Themes nebeneinander) nicht umgesetzt.

## Mögliche Verbesserungen

- Anbindung an ein zukünftiges `color_profile_id` im Profil-Dropdown.
- Echte zweite Spalte für Theme-Vergleich.
- Export der Token-Tabelle als CSV.
- Optional: `ThemeRegistry.register` für externe Themes ohne Neustart (wenn API ergänzt wird).

## QA / Smoke-Test

Ausführung:

```bash
pytest tests/tools/test_theme_visualizer_smoke.py -q
```

Ergebnis (lokal): **1 passed** (Fenster erstellbar, `light_default`/`dark_default` in der Liste, Theme anwendbar, Token- und Kontrast-Bereiche vorhanden).

Hinweis: `tools/theme_guard.py` schlägt im Gesamtprojekt weiterhin an anderen, älteren Stellen fehl; die neuen `app/devtools/*`-Dateien lösen keine `QColor(`-/Hex-Verstöße aus.

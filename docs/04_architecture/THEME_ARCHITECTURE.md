# Theme-Architektur

## Übersicht

Das Theme-System ermöglicht austauschbare Themes mit zentralen Design-Tokens. Es trennt Struktur (Widgets) von Design (Farben, Abstände, Typografie).

## Verzeichnisstruktur

```
app/gui/themes/
├── __init__.py
├── tokens.py          # ThemeTokens – Design-Token-Definition
├── definition.py      # ThemeDefinition – Manifest + Tokens
├── registry.py        # ThemeRegistry – Registrierung
├── manager.py         # ThemeManager – Singleton, Aktivierung
├── loader.py          # QSS laden + Token-Substitution
├── base/
│   ├── base.qss       # Gemeinsame Widget-Styles
│   └── shell.qss      # Shell-spezifische Styles
└── (später: light_default/, dark_default/ als Verzeichnisse)
```

Aktuell sind `light_default` und `dark_default` im Code (registry.py) definiert. Später können sie in eigene Verzeichnisse mit `tokens.json` ausgelagert werden.

## Komponenten

| Komponente | Aufgabe |
|------------|---------|
| **ThemeManager** | Singleton, set_theme(), get_tokens(), get_stylesheet(), theme_changed-Signal |
| **ThemeRegistry** | Registriert Themes, list_themes(), get(theme_id) |
| **ThemeDefinition** | id, name, tokens, extends |
| **ThemeTokens** | Dataclass mit allen Design-Tokens (Farben, Typo, Spacing, Radius) |
| **Loader** | Lädt base.qss + shell.qss, substituiert {{token}} durch Token-Werte |

## Design-Tokens

Flache Struktur für QSS-Substitution:

- **Colors**: color_bg, color_bg_surface, color_text, color_accent, …
- **Domain**: color_nav_bg, color_monitoring_bg, color_qa_nav_selected_bg, …
- **Typography**: font_size_sm, font_weight_medium, font_family_mono, …
- **Spacing**: spacing_sm, spacing_md, spacing_lg, …
- **Radius**: radius_sm, radius_md, radius_lg, …

## Theme aktivieren

**Beim App-Start:**
```bash
.venv/bin/python run_gui_shell.py --theme light_default
.venv/bin/python run_gui_shell.py --theme dark_default
```

**Programmatisch:**
```python
from app.gui.themes import get_theme_manager

manager = get_theme_manager()
manager.set_theme("dark_default")
```

## Tokens in Widgets nutzen

Statt hartcodierter Farben:

```python
from app.gui.themes import get_theme_manager

tokens = get_theme_manager().get_tokens()
color = tokens.get("color_text", "#1f2937")
label.setStyleSheet(f"color: {color};")
```

Besser: Widgets nutzen `objectName` und werden über QSS gestylt. Nur wo nötig, Tokens programmatisch verwenden.

## Neues Theme hinzufügen

1. **In registry.py:** Neue Funktion `_build_mein_theme()` mit ThemeTokens
2. **In _load_builtin_themes():** `self._themes["mein_theme"] = _build_mein_theme()`
3. **Optional:** Eigenes Verzeichnis `themes/mein_theme/` mit `tokens.json` (spätere Erweiterung)

## Theme-Wechsel (später in Settings)

```python
manager.theme_changed.connect(lambda id: save_preference("theme", id))
# Beim Start:
manager.set_theme(load_preference("theme", "light_default"))
```

## QSS-Templates

- `base/base.qss`: QMainWindow, QLabel, QPushButton, QLineEdit, QListWidget, …
- `base/shell.qss`: #topBar, #navigationSidebar, #workspaceHost, #controlCenterNav, …

Platzhalter: `{{color_bg}}`, `{{spacing_md}}`, etc.

## Regeln

- Keine hartcodierten Farben/Abstände in Widgets
- Styling über QSS + objectName
- Tokens zentral in ThemeTokens
- Neue Themes durch Registry erweiterbar

# Icon-System – Architektur und Nutzung

## Übersicht

Das Icon-System bietet eine zentrale, theme-fähige Icon-Verwaltung für die Linux Desktop Chat Anwendung. Icons sind SVG-basiert, monochrom und skalierbar.

## Struktur

```
app/gui/icons/
├── __init__.py          # IconManager, get_icon_manager
├── manager.py           # IconManager – Laden, Caching, Theme-Farben
├── registry.py          # IconRegistry – semantische Namen, Pfad-Mapping
├── nav_mapping.py       # Nav-IDs → Icon-Namen
└── svg/
    ├── navigation/      # Hauptnavigation (dashboard, chat, control, …)
    ├── panels/          # Workspace-Icons (agents, models, knowledge, …)
    ├── actions/         # Aktionen (add, remove, edit, refresh, …)
    ├── status/          # Status (success, warning, error, …)
    └── runtime/         # Runtime/Debug (eventbus, logs, metrics, …)
```

## IconManager

Zentraler Zugriff auf Icons:

```python
from app.gui.icons import IconManager
from app.gui.icons.registry import IconRegistry

# Einfach
icon = IconManager.get("dashboard")

# Mit Größe
icon = IconManager.get("chat", size=20)

# Mit Theme-Farbe (Standard: color_text)
icon = IconManager.get("agents")

# Runtime-Bereich (dunkler Hintergrund)
icon = IconManager.get("eventbus", color_token="color_monitoring_text")

# Explizite Farbe
icon = IconManager.get("success", color="#10b981")
```

## IconRegistry

Alle verfügbaren Icons sind in `IconRegistry` definiert. Konstanten für typsichere Nutzung:

```python
IconRegistry.DASHBOARD   # "dashboard"
IconRegistry.CHAT        # "chat"
IconRegistry.ADD         # "add"
IconRegistry.SUCCESS     # "success"
# …
```

## Theme-Integration

- **SVG**: Alle Icons verwenden `stroke="currentColor"` oder `fill="currentColor"`.
- **Farbe**: Der IconManager ersetzt `currentColor` durch die Theme-Farbe.
- **Token**: `color_token` steuert, welche Theme-Farbe verwendet wird:
  - `color_text` – Standard (helle Themes)
  - `color_monitoring_text` – Runtime-Bereich (dunkler Hintergrund)
- **Cache**: Bei Theme-Wechsel wird `IconManager.clear_cache()` aufgerufen (automatisch in AppearanceWorkspace).

## Nav-Mapping

`nav_mapping.py` ordnet Navigations-IDs den Icon-Namen zu:

- `NAV_AREA_ICONS` – Hauptnavigation (Kommandozentrale, Operations, …)
- `CC_WORKSPACE_ICONS` – Control Center
- `OPS_WORKSPACE_ICONS` – Operations
- `QA_WORKSPACE_ICONS` – QA & Governance
- `RD_WORKSPACE_ICONS` – Runtime / Debug
- `SETTINGS_WORKSPACE_ICONS` – Settings

## Integration

### NavigationSidebar

Icons werden automatisch für alle Hauptbereiche gesetzt.

### Domain-Navs

Control Center, Operations, QA, Runtime, Settings – alle Workspace-Listen nutzen Icons.

### TopBar

Status- und Suche-Aktionen haben Icons.

### Panels

Beispiel: `SystemStatusPanel` zeigt ein Icon neben dem Titel.

## SVG-Richtlinien

- **viewBox**: `0 0 24 24` für einheitliche Proportionen
- ** stroke/fill**: `currentColor` für Theme-Anpassung
- **Stil**: Einfache Linien, stroke-width 2, round caps/joins
- **Dateinamen**: Kleinbuchstaben, Unterstriche (z.B. `data_stores.svg`)

## Erweiterung

### Neues Icon hinzufügen

1. SVG in `svg/{category}/{name}.svg` ablegen
2. In `registry.py`: Konstante + `IconEntry` ergänzen
3. Optional: In `nav_mapping.py` für Nav/Workspace zuordnen

### Neues Icon-Set

- Alternative SVG-Ordner (z.B. `svg_outlined/`, `svg_filled/`)
- IconManager um `set_icon_set(name)` erweitern
- Basis-Pfad dynamisch wählen

### Icon-Größen

- Navigation: 18–20 px
- Panel-Titel: 18 px
- Toolbar: 18 px
- Buttons: 16–24 px

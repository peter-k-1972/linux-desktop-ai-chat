# Breadcrumb Navigation – Architektur

## Übersicht

Die Breadcrumb-Leiste zeigt den aktuellen Pfad im System und ermöglicht schnelle Navigation durch Klick auf einzelne Ebenen.

## Position

```
TopBar
BreadcrumbBar
Workspace
```

Die BreadcrumbBar sitzt zwischen TopBar und Workspace im zentralen Bereich.

## Komponenten

### BreadcrumbManager

- Verwaltet den aktuellen Pfad
- Emittiert `path_changed` bei Änderung
- Methoden: `set_area()`, `set_workspace()`, `set_path_with_detail()`
- Singleton: `get_breadcrumb_manager()`, `set_breadcrumb_manager()`

### BreadcrumbBar

- UI-Widget mit Icon, Titel, Separator
- Klickbare Items navigieren
- Signal: `navigate_requested(area_id, workspace_id)`
- Theme-kompatibel (QSS)

### BreadcrumbItem

- `id`, `title`, `icon`, `action` (AREA | WORKSPACE | DETAIL)
- `area_id` für WORKSPACE (übergeordneter Bereich)

## Beispiele

| Pfad | Anzeige |
|------|---------|
| Dashboard | Kommandozentrale |
| Operations → Chat | Operations › Chat |
| QA → Coverage Map | QA & Governance › Coverage Map |
| Runtime → Logs | Runtime / Debug › Logs |

## Integration

### WorkspaceHost

- `breadcrumb_changed(area_id, workspace_id)` – workspace_id leer bei reinem Area-Wechsel
- Wird bei `show_area()` emittiert

### Screens mit Workspaces

- `get_current_workspace()` – für initiale Breadcrumb beim Anzeigen
- In `_on_nav_selected`: `get_breadcrumb_manager().set_workspace(area_id, workspace_id)`

### Detail-Breadcrumbs

Workspaces können `set_path_with_detail(area_id, workspace_id, detail_title)` aufrufen:

```python
from app.gui.breadcrumbs import get_breadcrumb_manager

# z.B. Chat mit geöffneter Session
get_breadcrumb_manager().set_path_with_detail(
    NavArea.OPERATIONS, "operations_chat", "Session: Research"
)
```

## Theme

Breadcrumb-Styles in `shell.qss`:

- `#breadcrumbBar` – Hintergrund, Border
- `#breadcrumbItem` – klickbare Items
- `#breadcrumbSeparator` – ›
- `#breadcrumbDetail` – nicht klickbare Details

## Icons

Icons über IconManager, Mapping in `nav_mapping.py`.

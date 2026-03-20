# Command Palette – Architektur

## Übersicht

Die Command Palette bietet schnellen Zugriff auf Aktionen und Navigation – inspiriert von VSCode und JetBrains "Find Action".

## Aktivierung

- **Shortcut**: `Ctrl+Shift+P`
- **TopBar**: Klick auf "Suche"

## Architektur

```
app/gui/commands/
├── __init__.py
├── model.py          # Command (id, title, description, icon, callback)
├── registry.py       # CommandRegistry (register, search, execute)
├── palette.py        # CommandPaletteDialog (Overlay-UI)
└── bootstrap.py      # register_commands() – Standard-Commands
```

## Command-Modell

```python
@dataclass
class Command:
    id: str           # z.B. "nav.dashboard"
    title: str        # "Open Dashboard"
    description: str  # "Kommandozentrale öffnen"
    icon: str        # IconManager-Name
    category: str    # navigation, system, search
    callback: Callable[[], None]  # Ausführung
```

## CommandRegistry

- `register(command)` – Command registrieren
- `search(query)` – Filtert nach Titel und Beschreibung
- `execute(command_id)` – Führt Command aus
- `get(command_id)` – Liefert Command

## CommandPaletteDialog

- Suchfeld mit Live-Filter
- Liste mit Icon, Titel, Tooltip (Beschreibung)
- Tastatur: Enter ausführen, Escape schließen, Pfeiltasten navigieren
- Theme-kompatibel (Styles aus Theme-Tokens)

## Integration

1. **MainWindow**: Registriert Shortcut, öffnet Dialog
2. **WorkspaceHost**: `show_area(area_id, workspace_id?)` – Navigation mit optionalem Sub-Workspace
3. **Screens**: `show_workspace(workspace_id)` – für direkten Workspace-Zugriff
4. **NavigationSidebar**: `set_current(area_id)` – Sync bei programmatischer Navigation

## Standard-Commands

| ID | Titel | Aktion |
|----|-------|--------|
| nav.dashboard | Open Dashboard | Kommandozentrale |
| nav.chat | Open Chat | Operations → Chat |
| nav.control_center | Open Control Center | Control Center |
| nav.qa_governance | Open QA & Governance | QA & Governance |
| nav.runtime_debug | Open Runtime / Debug | Runtime / Debug |
| nav.settings | Open Settings | Einstellungen |
| system.switch_theme | Switch Theme | Light ↔ Dark |
| system.reload_theme | Reload Theme | Theme neu laden |

## Erweiterung

### Neuer Command

```python
from app.gui.commands import Command, CommandRegistry

CommandRegistry.register(Command(
    id="my.action",
    title="My Action",
    description="Beschreibung",
    icon="add",
    category="custom",
    callback=lambda: do_something(),
))
```

### Plugin-Integration

Plugins können `CommandRegistry.register()` aufrufen. Die Commands erscheinen automatisch in der Palette.

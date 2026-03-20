# Settings – Architektur

## Übersicht

Settings ist der zentrale Bereich für globale UI-Einstellungen, Theme-Auswahl und Systempräferenzen. Er wirkt wie ein klassischer Desktop-Settingsdialog.

## Struktur

```
SettingsScreen
  ├─ SettingsNav (sekundäre Bereichsleiste links)
  └─ QStackedWidget (SettingsWorkspaceHost)
       ├─ AppearanceWorkspace
       ├─ SystemWorkspace
       ├─ ModelsWorkspace
       ├─ AgentsWorkspace
       └─ AdvancedWorkspace
```

## Klassenzuständigkeiten

| Klasse | Zuständigkeit |
|--------|----------------|
| **SettingsScreen** | Koordinator: Nav + Stack, Inspector-Delegation |
| **SettingsNav** | Sekundäre Navigation: Appearance, System, Models, Agents, Advanced |
| **BaseSettingsWorkspace** | Basis für alle fünf Workspaces |
| **AppearanceWorkspace** | Theme-Auswahl, funktional mit ThemeManager |
| **SystemWorkspace** | Application Info, Runtime Status (Platzhalter) |
| **ModelsWorkspace** | Default Model, Token Limits (Platzhalter) |
| **AgentsWorkspace** | Agent Behaviour, Permissions (Platzhalter) |
| **AdvancedWorkspace** | Debug, Experimental (Platzhalter) |

## Theme-Integration

- **ThemeSelectionPanel** nutzt `get_theme_manager()` und `manager.list_themes()`
- Theme-Wechsel über `manager.set_theme(theme_id)` – sofort sichtbar
- Keine hartcodierten Themes – alle aus ThemeRegistry

## Dateistruktur

```
app/gui/domains/settings/
├── __init__.py
├── settings_screen.py
├── settings_nav.py
├── panels/
│   ├── __init__.py
│   └── theme_selection_panel.py
└── workspaces/
    ├── __init__.py
    ├── base_settings_workspace.py
    ├── appearance_workspace.py
    ├── system_workspace.py
    ├── models_workspace.py
    ├── agents_workspace.py
    └── advanced_workspace.py
```

## Inspector

- **AppearanceWorkspace**: AppearanceInspector (Theme-Details)
- **SystemWorkspace**: SystemSettingsInspector
- **ModelsWorkspace**: ModelsSettingsInspector
- **AgentsWorkspace**: AgentsSettingsInspector
- **AdvancedWorkspace**: AdvancedSettingsInspector

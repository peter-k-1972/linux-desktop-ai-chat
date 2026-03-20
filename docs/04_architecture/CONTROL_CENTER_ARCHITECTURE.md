# Control Center – Architektur

## Übersicht

Das Control Center ist der Systemverwaltungs- und Steuerungsbereich der Plattform. Es unterscheidet sich visuell und funktional von Operations (Arbeiten) und wirkt als ruhige, professionelle Verwaltungsoberfläche.

## Struktur

```
ControlCenterScreen
  ├─ ControlCenterNav (sekundäre Bereichsleiste)
  └─ QStackedWidget (ControlCenterWorkspaceHost)
       ├─ ModelsWorkspace
       ├─ ProvidersWorkspace
       ├─ AgentsWorkspace
       ├─ ToolsWorkspace
       └─ DataStoresWorkspace
```

## Klassenzuständigkeiten

| Klasse | Zuständigkeit |
|--------|----------------|
| **ControlCenterScreen** | Koordinator: Nav + Stack, Inspector-Delegation, Signal-Verkabelung |
| **ControlCenterNav** | Sekundäre Navigation: Models, Providers, Agents, Tools, Data Stores |
| **BaseManagementWorkspace** | Basis für alle fünf Workspaces, `setup_inspector`-Schnittstelle |
| **ModelsWorkspace** | Model-Verwaltung: Installed Models, Status, Details, Actions |
| **ProvidersWorkspace** | Provider-Verwaltung: List, Status, Endpoint, Runtime |
| **AgentsWorkspace** | Agent-Verwaltung (Designsicht): Registry, Profiles, Skills, Model Assignment |
| **ToolsWorkspace** | Tool-Verwaltung: Registry, Categories, Permissions |
| **DataStoresWorkspace** | Data-Store-Verwaltung: SQLite, ChromaDB, File, Health |

## Panels (pro Workspace)

- **Models**: ModelListPanel, ModelSummaryPanel, ModelStatusPanel, ModelActionPanel
- **Providers**: ProviderListPanel, ProviderStatusPanel
- **Agents**: AgentRegistryPanel, AgentSummaryPanel
- **Tools**: ToolRegistryPanel, ToolSummaryPanel
- **Data Stores**: DataStoreOverviewPanel, DataStoreHealthPanel

## Inspectors

Jeder Workspace liefert einen kontextsensitiven Inspector-Inhalt:

- **ModelInspector**: Modellname, Status, Größe, Typ
- **ProviderInspector**: Endpoint, Verfügbarkeit, Fehlerstatus
- **AgentInspector**: Rolle, Modellbindung, Toolset, Status
- **ToolInspector**: Kategorie, Berechtigungen, Verfügbarkeit
- **DataStoreInspector**: Typ, Zustand, Nutzung, Health

## Dateistruktur

```
app/gui/domains/control_center/
├── __init__.py
├── control_center_screen.py
├── control_center_nav.py
├── panels/
│   ├── __init__.py
│   ├── models_panels.py
│   ├── providers_panels.py
│   ├── agents_panels.py
│   ├── tools_panels.py
│   └── data_stores_panels.py
└── workspaces/
    ├── __init__.py
    ├── base_management_workspace.py
    ├── models_workspace.py
    ├── providers_workspace.py
    ├── agents_workspace.py
    ├── tools_workspace.py
    └── data_stores_workspace.py

app/gui/inspector/
├── model_inspector.py
├── provider_inspector.py
├── agent_inspector.py
├── tool_inspector.py
└── data_store_inspector.py
```

## Integration

- **WorkspaceHost**: Ruft `setup_inspector` beim Wechsel zu Control Center auf.
- **ControlCenterScreen**: Delegiert an den aktuell sichtbaren Workspace.
- **BottomPanelHost**: Bleibt shell-weit; keine Duplikation im Control Center.
- **Bootstrap**: Control Center ist bereits registriert, keine Änderung nötig.

## Erweiterbarkeit

- Dummy-Daten in Tabellen und Panels sind durch echte Fachlogik ersetzbar.
- Jeder Workspace ist eigenständig; neue Panels/Inspectors können ergänzt werden.
- Keine God-Class; klare Trennung von Nav, Screen und Workspaces.

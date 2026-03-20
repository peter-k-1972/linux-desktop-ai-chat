# Runtime / Debug – Architektur

## Übersicht

Runtime / Debug ist der technische Beobachtungs- und Monitoring-Bereich der Plattform. Er dient der Laufzeitanalyse: Systemzustände, Event-Streams, Metriken, LLM-Aufrufe, Agent-Aktivitäten, System-Graphen.

Er unterscheidet sich von:
- **Operations**: Arbeiten
- **Control Center**: Verwalten / Steuern
- **QA & Governance**: Prüfen / Bewerten

## Struktur

```
RuntimeDebugScreen
  ├─ RuntimeDebugNav (sekundäre Bereichsleiste, dunkles Theme)
  └─ QStackedWidget (RuntimeDebugWorkspaceHost)
       ├─ EventBusWorkspace
       ├─ LogsWorkspace
       ├─ MetricsWorkspace
       ├─ LLMCallsWorkspace
       ├─ AgentActivityWorkspace
       └─ SystemGraphWorkspace
```

## Klassenzuständigkeiten

| Klasse | Zuständigkeit |
|--------|----------------|
| **RuntimeDebugScreen** | Koordinator: Nav + Stack, Inspector-Delegation |
| **RuntimeDebugNav** | Sekundäre Navigation (dunkles Theme, Monitoring-Optik) |
| **BaseMonitoringWorkspace** | Basis für alle sechs Workspaces |
| **EventBusWorkspace** | Event Stream, Type Filter, Event Detail |
| **LogsWorkspace** | Log Stream, Filter (Level/Module), Log Detail |
| **MetricsWorkspace** | CPU/GPU, Model Runtime, Agent Runtime, Request Counts |
| **LLMCallsWorkspace** | Call History, Model, Tokens, Duration, Status |
| **AgentActivityWorkspace** | Agent List, Current Task, Status, Last Action |
| **SystemGraphWorkspace** | Systemübersicht, Komponenten (Chat, Agents, Models, …) |

## Design

- **Dunkles Theme** (#0f172a, #1e293b) für Monitoring-/Debug-Optik
- **Grüner Akzent** (#34d399, #065f46) für Auswahl und Status
- **Monospace** für Logs, Events, Timestamps
- Systemmonitor- / Debug-Konsole-Anmutung

## Dateistruktur

```
app/gui/domains/runtime_debug/
├── __init__.py
├── runtime_debug_screen.py
├── runtime_debug_nav.py
├── panels/
│   ├── __init__.py
│   ├── eventbus_panels.py
│   ├── logs_panels.py
│   ├── metrics_panels.py
│   ├── llm_calls_panels.py
│   ├── agent_activity_panels.py
│   └── system_graph_panels.py
└── workspaces/
    ├── __init__.py
    ├── base_monitoring_workspace.py
    ├── eventbus_workspace.py
    ├── logs_workspace.py
    ├── metrics_workspace.py
    ├── llm_calls_workspace.py
    ├── agent_activity_workspace.py
    └── system_graph_workspace.py

app/gui/inspector/
├── event_inspector.py
├── log_inspector.py
├── metrics_inspector.py
├── llm_call_inspector.py
├── runtime_agent_inspector.py
└── system_node_inspector.py
```

## Integration

- **WorkspaceHost**: Ruft `setup_inspector` beim Wechsel zu Runtime / Debug auf.
- **BottomPanelHost**: Bleibt shell-weit; Runtime / Debug dupliziert nicht.
- **Bootstrap**: Bereits registriert.

## Erweiterbarkeit

- Dummy-Daten durch echte Event-/Log-/Metrics-Streams ersetzbar.
- Jeder Workspace eigenständig; spätere Backend-Integration pro Workspace möglich.

# Runtime / Debug – Implementierung

## Übersicht

Runtime / Debug zeigt reale Systeminformationen aus Logging, DebugStore, ChatService und MetricsStore.

## Workspaces

| Workspace | Datenquelle | Inhalt |
|-----------|-------------|--------|
| **LogsWorkspace** | `app.runtime.gui_log_buffer` | Python-Logs (chronologisch), Level-/Textfilter, Detail |
| **LLMCallsWorkspace** | `DebugStore` event_history (MODEL_CALL) | Modellaufrufe, Zeit, Agent, Dauer, Detail |
| **AgentActivityWorkspace** | `DebugStore` event_history, agent_status | Agentenaktionen, Status, Detail |
| **MetricsWorkspace** | `ChatService`, `DebugStore` | Chats, Agent Tasks, LLM Calls, Model Runtime, Fehler |
| **EventBusWorkspace** | `DebugStore` event_history | Alle Events, Typfilter, Detail |

## Datenflüsse

```
Python logging → GuiLogHandler → LogBuffer → LogsWorkspace / LogsMonitor
AgentTaskRunner → EventBus.emit(AgentEvent) → DebugStore
DebugStore → LLMCallsWorkspace, AgentActivityWorkspace, EventBusWorkspace, MetricsWorkspace
ChatService → MetricsWorkspace (Chat-Anzahl)
```

## Initialisierung

In `run_gui_shell.py`:
- `install_gui_log_handler()` – fängt Python-Logs ab
- `get_metrics_collector()` – schreibt Agent-Events in MetricsStore
- `get_infrastructure()` – stellt DebugStore/EventBus bereit

## Bottom Panel

Alle fünf Tabs zeigen Live-Daten:
- **Logs** – letzte 8 Log-Einträge
- **Events** – letzte 8 Events
- **Metrics** – Chats, Tasks, LLM-Calls
- **Agent Activity** – letzte Agentenaktionen
- **LLM Trace** – letzte Modellaufrufe

## Inspector

Jeder Workspace aktualisiert den Inspector bei Auswahl:
- **Logs** – vollständiger Logeintrag
- **LLM Calls** – Modell, Dauer, Status, Prompt-Auszug
- **Agent Activity** – Agent, Task, Status, Aktion
- **Metrics** – Model Runtime, Request Count
- **EventBus** – Event-Typ, Zeit, Source, Payload

## Start

```bash
.venv/bin/python run_gui_shell.py
```

Navigation: **Runtime / Debug** → Logs, LLM Calls, Agent Activity, Metrics, EventBus.
